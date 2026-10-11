"""替每個敬拜頁用 reurl.cc 產生短網址，記錄在 short-links.json，並寫進 README 目錄的「短網址」欄。

GitHub Pages 的網址由檔名決定，內容修改不會改變網址，
所以每頁只在第一次出現時轉一次短網址，之後一律沿用 short-links.json 的紀錄。

需要環境變數 REURL_API_KEY（在 GitHub 上放在 repo secret）。
"""
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAGES_BASE = "https://bow0314.github.io/worship/"
DIRS = ["詩歌敬拜歌曲", "詩歌主領筆記"]
LINKS_FILE = ROOT / "short-links.json"
README = ROOT / "README.md"
SHORT_PREFIX = "https://reurl.cc/"  # 只接受 reurl.cc 的短網址，其他服務的舊紀錄會重新轉


def page_url(path):
    return PAGES_BASE + urllib.parse.quote(path)


def shorten_url(url, api_key):
    """呼叫 reurl.cc Web API，成功回傳短網址，失敗回傳 None。"""
    req = urllib.request.Request(
        "https://api.reurl.cc/shorten",
        data=json.dumps({"url": url}).encode(),
        headers={"Content-Type": "application/json", "reurl-api-key": api_key},
        method="POST",
    )
    try:
        r = urllib.request.urlopen(req, timeout=15)
        data = json.loads(r.read().decode())
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


def update_readme(links):
    lines = README.read_text(encoding="utf-8").split("\n")
    out = []
    for line in lines:
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells[:3] == ["日期", "標題", "連結"]:
                cells = ["日期", "標題", "連結", "短網址"]
            elif cells and set("".join(cells)) <= set("-: ") and len(cells) == 3:
                cells.append("---")
            else:
                m = re.search(r"\]\(([^)]+\.html)\)", line)
                if m and len(cells) >= 3:
                    short = links.get(m.group(1))
                    cells = cells[:3] + [f"[{short.split('://', 1)[1]}]({short})" if short else "—"]
            line = "| " + " | ".join(cells) + " |"
        out.append(line)
    README.write_text("\n".join(out), encoding="utf-8")


def main():
    api_key = os.environ.get("REURL_API_KEY", "").strip()
    if not api_key:
        sys.exit("找不到 REURL_API_KEY：請到 repo 的 Settings → Secrets and variables → Actions 新增這個 secret。")
    links = json.loads(LINKS_FILE.read_text(encoding="utf-8")) if LINKS_FILE.exists() else {}
    links = {k: v for k, v in links.items() if v.startswith(SHORT_PREFIX)}
    failed = []
    for d in DIRS:
        for f in sorted((ROOT / d).glob("*.html")):
            path = f"{d}/{f.name}"
            if path in links:
                continue
            short = shorten_url(page_url(path), api_key)
            if short:
                links[path] = short
                print(f"{path} → {short}")
            else:
                failed.append(path)
                print(f"{path} → 轉短網址失敗，下次再試")
    LINKS_FILE.write_text(json.dumps(links, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_readme(links)
    if failed:
        sys.exit(f"{len(failed)} 頁轉短網址失敗，請看上面的訊息。")


if __name__ == "__main__":
    main()
