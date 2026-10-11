# reurl.cc 短網址套用指南

把任何一個用 GitHub Pages 發布網頁的專案，接上 reurl.cc 自動轉短網址。
做法和 `bow0314/worship` 一樣：頁面合併進 `main` 後，GitHub Actions 自動呼叫 reurl.cc，
結果記在 `short-links.json`。每頁只轉一次，之後頁面內容怎麼改，短網址都不變。

> 給 Claude 的規則：短網址服務一律用 **reurl.cc**，不要用 TinyURL、is.gd 或其他服務。
> API 金鑰只能放在 GitHub repo secret `REURL_API_KEY`，不能寫進程式碼、commit 或對話。

---

## 適用條件

- 專案在 GitHub 上，而且已開啟 GitHub Pages（網址是 `https://bow0314.github.io/<repo>/...`）。
- 要分享的是 repo 裡的 `.html` 頁面。

不符合的專案（LINE bot、本機工具、private repo 沒開 Pages 等）不用套。

---

## 給 Claude Code（專案 chat）的指令

把下面整段貼給該專案的 Claude Code：

```
請在這個 repo 接上 reurl.cc 自動短網址，照以下規格做，做完 commit、push、開 PR 並合併進 main：

1. 新增 .github/scripts/shorten_links.py 和 .github/workflows/short-links.yml，內容照
   https://github.com/bow0314/worship/blob/main/docs/reurl-短網址套用指南.md 的「檔案內容」一節。
2. 依這個 repo 的結構調整 workflow 裡的 SHORTEN_GLOBS（要轉短網址的 html 檔範圍），
   以及 workflow 的 paths 觸發條件。
3. 新增 short-links.json，內容為 {}。
4. 在 CLAUDE.md 加上規則：
   - 短網址一律用 reurl.cc，不要用 TinyURL、is.gd 等其他服務。
   - 金鑰放在 repo secret REURL_API_KEY，不能寫進程式碼或 commit。
   - 短網址由 GitHub Actions 產生、記在 short-links.json，不要手動編造。
   - 頁面檔名發布後不要改名（改名會變成新網址）。
   - 新頁面合併後，從 main 的 short-links.json 讀出短網址回報給我。
5. 完成後告訴我要去哪裡設定 secret、以及去哪裡按 Run workflow。
```

---

## 檔案內容

### `.github/scripts/shorten_links.py`

```python
"""用 reurl.cc 替 GitHub Pages 頁面產生短網址，記錄在 short-links.json。

GitHub Pages 的網址由檔名決定，內容修改不會改變網址，
所以每頁只在第一次出現時轉一次，之後沿用 short-links.json 的紀錄。

環境變數：
- REURL_API_KEY：reurl.cc API 金鑰（放在 repo secret）
- PAGES_BASE：Pages 網址前綴，例如 https://bow0314.github.io/my-repo/
- SHORTEN_GLOBS：要轉的檔案範圍，多個用逗號分隔，例如 "*.html,pages/*.html"
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
LINKS_FILE = ROOT / "short-links.json"
SHORT_PREFIX = "https://reurl.cc/"


def shorten_url(url, api_key):
    req = urllib.request.Request(
        "https://api.reurl.cc/shorten",
        data=json.dumps({"url": url}).encode(),
        headers={"Content-Type": "application/json", "reurl-api-key": api_key},
        method="POST",
    )
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
    except urllib.error.HTTPError as e:
        print(f"  reurl.cc 回應 HTTP {e.code}：{e.read().decode(errors='replace')[:300]}")
        return None
    except Exception as e:
        print(f"  呼叫 reurl.cc 失敗：{e}")
        return None
    if data.get("res") == "success" and str(data.get("short_url", "")).startswith(SHORT_PREFIX):
        return data["short_url"]
    print(f"  reurl.cc 回應：{data}")
    return None


def main():
    api_key = os.environ.get("REURL_API_KEY", "").strip()
    if not api_key:
        sys.exit("找不到 REURL_API_KEY：請到 repo 的 Settings → Secrets and variables → Actions 新增這個 secret。")
    base = os.environ["PAGES_BASE"].rstrip("/") + "/"
    globs = [g.strip() for g in os.environ.get("SHORTEN_GLOBS", "**/*.html").split(",") if g.strip()]

    links = json.loads(LINKS_FILE.read_text(encoding="utf-8")) if LINKS_FILE.exists() else {}
    links = {k: v for k, v in links.items() if v.startswith(SHORT_PREFIX)}
    files = sorted({p for g in globs for p in ROOT.glob(g)
                    if p.is_file() and not any(part.startswith(".") for part in p.relative_to(ROOT).parts)})
    failed = []
    for f in files:
        path = f.relative_to(ROOT).as_posix()
        if path in links:
            continue
        short = shorten_url(base + urllib.parse.quote(path), api_key)
        if short:
            links[path] = short
            print(f"{path} → {short}")
        else:
            failed.append(path)
            print(f"{path} → 轉短網址失敗，下次再試")
    LINKS_FILE.write_text(json.dumps(links, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as s:
            s.write("| 頁面 | 短網址 |\n| --- | --- |\n")
            for k, v in sorted(links.items()):
                s.write(f"| {k} | {v} |\n")
    if failed:
        sys.exit(f"{len(failed)} 頁轉短網址失敗，請看上面的訊息。")


if __name__ == "__main__":
    main()
```

### `.github/workflows/short-links.yml`

```yaml
name: 產生短網址

on:
  push:
    branches: [main]
    paths:
      - "**/*.html"                     # 依專案調整
      - ".github/scripts/shorten_links.py"
      - ".github/workflows/short-links.yml"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: short-links
  cancel-in-progress: false

jobs:
  shorten:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: 轉短網址
        env:
          REURL_API_KEY: ${{ secrets.REURL_API_KEY }}
          PAGES_BASE: https://${{ github.repository_owner }}.github.io/${{ github.event.repository.name }}/
          SHORTEN_GLOBS: "**/*.html"     # 依專案調整，例如 "index.html,pages/*.html"
        run: python .github/scripts/shorten_links.py
      - name: 有新短網址就 commit 回 main
        if: success() || failure()
        run: |
          git config core.quotepath false
          if git diff --quiet -- short-links.json; then
            echo "沒有新的短網址"
            exit 0
          fi
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add short-links.json
          git commit -m "更新短網址"
          git pull --rebase origin main
          git push origin HEAD:main
```

注意事項：

- 如果 repo 名稱是 `<帳號>.github.io`（個人主頁），`PAGES_BASE` 要改成 `https://<帳號>.github.io/`。
- 有自訂網域的話，`PAGES_BASE` 改成那個網域。
- 每次執行的結果也會顯示在該次 Actions 執行頁面的 Summary。

---

## 金鑰設定（每個 repo 都要做一次）

GitHub 個人帳號沒有「所有 repo 共用」的 secret，所以每個套用的 repo 都要設一次。用同一把金鑰就好。

### 自己做

1. 登入 https://reurl.cc，到 https://reurl.cc/dev/main/tw 複製 API Key。
2. 打開 `https://github.com/bow0314/<repo>/settings/secrets/actions`，按「New repository secret」。
   - Name：`REURL_API_KEY`（全大寫、無空白）
   - Secret：貼上金鑰
   - 要放在「Secrets」分頁的 Repository secrets，不是 Variables，也不是 Environment secrets。
3. 打開 `https://github.com/bow0314/<repo>/actions/workflows/short-links.yml`，按「Run workflow」（branch: main）。

### 交給 Cowork

把 `<repo>` 換成專案名稱後貼給 Cowork：

```
請用內建瀏覽器幫我設定 GitHub repo bow0314/<repo> 的 reurl.cc 短網址：
1. 打開 https://reurl.cc/dev/main/tw（需要的話請我登入），複製我的 API Key。
2. 打開 https://github.com/bow0314/<repo>/settings/secrets/actions
   - Repository secrets 裡已有 REURL_API_KEY 就按編輯更新成這把金鑰；沒有就按「New repository secret」，
     Name 填 REURL_API_KEY，Secret 貼上金鑰，按「Add secret」。
   - 要放在 Secrets 分頁的 Repository secrets，不是 Variables，也不是 Environment secrets。
   - 回報時不要寫出金鑰內容。
3. 打開 https://github.com/bow0314/<repo>/actions/workflows/short-links.yml，按「Run workflow」（branch: main），等它跑完。
   - 成功：讀 https://github.com/bow0314/<repo>/blob/main/short-links.json，把每頁的 reurl.cc 短網址列表回報，
     並點開 1～2 個確認會連到正確頁面。
   - 失敗：展開「轉短網址」步驟，把完整錯誤訊息回報給我，不要修改任何檔案。
```

---

## 常見錯誤

| 錯誤訊息 | 原因 | 處理 |
| --- | --- | --- |
| 找不到 REURL_API_KEY | secret 沒設、名稱打錯、放錯位置 | 照「金鑰設定」重新檢查 |
| reurl.cc 回應 HTTP 401／403 | 金鑰錯誤或失效 | 到 reurl.cc 開發者頁面重新複製金鑰並更新 secret |
| reurl.cc 回應 HTTP 429 或額度相關訊息 | 超過每日／每小時呼叫額度 | 等一段時間再按 Run workflow，已成功的不會重轉 |
| push 被拒絕（protected branch） | main 有分支保護 | 在分支保護設定允許 GitHub Actions push，或改成開 PR |

---

## 讓所有 Claude 對話都記得用 reurl.cc

在 claude.ai「Settings → Profile → 個人偏好設定」加上一句，之後所有 chat、Claude Code、Cowork 都會照做：

```
需要短網址時一律用 reurl.cc（API：POST https://api.reurl.cc/shorten，標頭 reurl-api-key），
不要用 TinyURL、is.gd 等其他服務。GitHub 專案的做法照
https://github.com/bow0314/worship/blob/main/docs/reurl-短網址套用指南.md
```
