"""替每個敬拜頁產生短網址，記錄在 short-links.json，並寫進 README 目錄的「短網址」欄。

GitHub Pages 的網址由檔名決定，內容修改不會改變網址，
所以每頁只在第一次出現時轉一次短網址，之後一律沿用 short-links.json 的紀錄。
"""
import json
import pathlib
import re
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAGES_BASE = "https://bow0314.github.io/worship/"
DIRS = ["詩歌敬拜歌曲", "詩歌主領筆記"]
LINKS_FILE = ROOT / "short-links.json"
README = ROOT / "README.md"


def page_url(path):
    return PAGES_BASE + urllib.parse.quote(path)


def shorten_url(url, alias):
    q = urllib.parse.quote(url, safe="")
    apis = [
        # 先試自訂名稱，被別人用走就退回隨機短碼
        f"https://tinyurl.com/api-create.php?url={q}&alias={alias}",
        f"https://tinyurl.com/api-create.php?url={q}",
        f"https://is.gd/create.php?format=simple&url={q}",
    ]
    for api in apis:
        try:
            r = urllib.request.urlopen(api, timeout=15)
            result = r.read().decode().strip()
            if result.startswith("http"):
                return result
        except Exception:
            continue
    return None


def alias_for(path):
    # 詩歌敬拜歌曲/2026-11-01.html → bow-worship-20261101；主領筆記加 -notes
    stem = pathlib.PurePosixPath(path).stem.replace("-", "")
    suffix = "-notes" if path.startswith("詩歌主領筆記/") else ""
    return f"bow-worship-{stem}{suffix}"


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
    links = json.loads(LINKS_FILE.read_text(encoding="utf-8")) if LINKS_FILE.exists() else {}
    for d in DIRS:
        for f in sorted((ROOT / d).glob("*.html")):
            path = f"{d}/{f.name}"
            if links.get(path):
                continue
            short = shorten_url(page_url(path), alias_for(path))
            if short:
                links[path] = short
                print(f"{path} → {short}")
            else:
                print(f"{path} → 轉短網址失敗，下次再試")
    LINKS_FILE.write_text(json.dumps(links, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_readme(links)


if __name__ == "__main__":
    main()
