# 兩份筆記檔案的結構規則

這份文件說明 `詩歌敬拜歌曲/` 和 `詩歌主領筆記/` 兩個資料夾裡 HTML 檔案共用的慣例。**這不是完整的 CSS/HTML 複本** —— 這套設計系統會持續演進（新增 class、調整配色），任何文件都可能落後於實際檔案。真正的做法永遠是：

> 找該資料夾裡日期最新的一份 `.html`，把它當成活的範本，直接複製整份檔案再修改內容區塊，而不是憑這份文件的記憶手刻一份新的。

## 兩份檔案的差異

| | `詩歌敬拜歌曲/YYYY-MM-DD.html` | `詩歌主領筆記/YYYY-MM-DD.html` |
|---|---|---|
| 對象 | 樂手、司琴 | 主領同工 |
| 內容 | 歌詞 + 簡易帶領筆記 | 同上，外加見證稿、詳細口白、「唱畢後說」串場稿 |
| 「進歌前先說」區塊 | 通常收合（`<details class="song-collapse">` 不帶 `open`） | 通常展開（帶 `open` 屬性），內容也更長 |

兩份檔案的歌曲數量、順序代碼、歌詞、連結必須完全一致——差別只在口白／筆記的詳細程度。**兩份都要改**，漏改一份是最常見的錯誤（這正是這個 skill 誕生的原因）。

## 整體骨架（由上到下）

1. `<style>` 內的 CSS 變數與規則 —— 照抄範本檔，不要手動精簡或「順手優化」
2. `.theme-toggle` 按鈕、`.order-float` 浮動順序面板 —— 純結構，照抄
3. `<header>`：`.eyebrow` 小標籤、`<h1>日期　主日敬拜</h1>`、`.arc-line`（用 `→` 串起整場的屬靈脈絡，例如「仰望→信靠跟隨→奔跑不放棄→宣告偉大」）
4. `.info`：服事同工名單（主領／和聲／司琴／吉他／貝斯／鼓手／投影／音控／直播）＋ 練習時間 ＋ 配置說明
5. `.spine-row`：屬靈軸線橫幅，每首歌一個色塊（`.p1`～`.p4`），中間若有公禱交接會插入 `.p-pray`
6. 每首歌一個 `.song` 區塊（見下方）
7. 需要交接給司會／其他同工時，插入 `.handoff` 卡片
8. 最後一首歌之後（僅主領筆記版常見）：`.say.after` 唱畢後說卡片
9. `.callout`：給樂團．司琴的備註（清單 + 樂譜下載連結 + 歌詞PDF 連結）
10. `<footer>`：金句 + 一句提醒

## 單首歌 `.song` 區塊

```html
<div class="song" style="--stage:var(--s1);--panel:var(--s1-panel)"
     data-song data-name="( 1 ) 仰望主"
     data-order="V–V–C1–V–C2–V"
     data-order-alt="V–C1–V"
     data-stage="s1">
  <details class="song-collapse">
    <summary class="song-bar"> ... </summary>
    <div class="say-content"><p class="say-line">進歌前先說的口白</p></div>
  </details>

  <div class="lyrics">
    <div class="lyr-lab">Verse</div>
    <p><span class="lc-verse">仰</span>望主　仰望主 ...</p>
    <div class="lyr-lab">Chorus 1</div>
    <p><span class="lc-chorus">我</span>主在寶座上 ...</p>
  </div>

  <div class="lead-notes">
    <div class="ln-head"><span class="ln-tag">帶領筆記</span>...</div>
    <div class="note-grid">
      <div class="cell"><div class="lab">屬 靈 焦 點</div><div class="val">...</div></div>
      <div class="cell"><div class="lab">情 緒 動 線</div><div class="val">...</div></div>
      <div class="cell"><div class="lab">動 態 提 示</div><div class="val">...</div></div>
      <div class="cell"><div class="lab">連 結</div><div class="val">
        <a class="link-tag" href="YOUTUBE_URL" target="_blank" rel="noopener">YouTube</a>
        <a class="link-tag" href="SHEET_MUSIC_DRIVE_URL" target="_blank" rel="noopener">歌名 <span class="sheet-tag">(樂譜)</span></a>
        <a class="link-tag" href="LYRICS_PDF_DRIVE_URL" target="_blank" rel="noopener">歌詞PDF</a>
      </div></div>
    </div>
  </div>
</div>
```

### 重點規則

- **`--stage` / `data-stage`**：四首歌依序用 `s1`（金／仰望）、`s2`（青綠／信靠跟隨）、`s3`（珊瑚橘／奔跑不放棄）、`s4`（靛紫／宣告偉大）。若某週超過 4 首歌，需要在 `:root` 與 `html[data-theme="dark"]` 兩個區塊都新增 `--s5` 及對應 `--s5-panel`，並比照既有的 `s1`～`s4` 補上 light/dark 模式各自的微調（有些顏色在暗黑模式需要調亮，見 CSS 裡 `html[data-theme="dark"] [data-stage="s2"] .lc-verse` 這類規則的寫法）。不要只加一半（漏了某個模式或漏了 panel 色），上線後那個顏色會在其中一種模式下看起來不對。
- **`data-order` / `data-order-alt` / `data-order-desktop`**：`data-order` 是完整敬拜順序代碼（V=Verse、C1/C2=不同副歌、B=Bridge、*尾=尾句、×2 代表重複）。`data-order-alt` 是簡化版（例如只給司琴看的簡短版本），非必要可省略。`data-order-desktop` 是桌機版換行排版，用 `&#10;` 當換行，只有代碼很長時才需要。
- **歌詞裡的段落顏色**：每段第一個字用 `<span class="lc-verse">`／`lc-chorus`／`lc-bridge`／`lc-tail` 包住，其餘文字維持一般顏色。段落之間用全形空白（　）分句，不要用半形空格，換行斷點只能在全形空白處（`word-break:keep-all` 已經處理斷行，但你打字時仍要照抄既有的分句習慣）。
- **`連結` 欄位（`.cell` 裡 `lab` 是「連 結」的那一格）** 是這個 skill 最常需要新增/更新的地方，务必包含三類：
  1. `YouTube` —— 官方或詩班 MV／演唱影片連結
  2. `歌名 <span class="sheet-tag">(樂譜)</span>` —— 該首歌樂譜的 Google Drive 連結（如果是組合曲like「你真偉大＋我神真偉大」，兩首各自一個 tag）
  3. `歌詞PDF` —— 純文字、不帶 `(樂譜)` 後綴，四首歌通常都指向同一份「當週歌詞全稿」PDF（因為那份 PDF 一次涵蓋所有歌曲），所以這個連結在四首歌的欄位裡會重複出現、網址相同
  **這三類缺一都要主動跟使用者確認**，不要因為使用者只給了歌詞 PDF 就以為 YouTube／樂譜連結不重要——這是這個 skill 存在的主要原因之一。

## `.callout`（給樂團．司琴的備註）

底部固定有一個 `<li><b>樂譜下載：</b>...資料夾連結</li>`，指向整個服事週次共用的 Google Drive 資料夾。加入歌詞全稿 PDF 時，在它後面補一行：

```html
<li><b>歌詞全稿（PDF）：</b><a href="LYRICS_PDF_DRIVE_URL" target="_blank" rel="noopener" style="color:var(--gold);word-break:break-all">四首歌詞流程稿</a></li>
```

## `詩歌主領筆記` 專屬的額外內容

- 每首歌的「進歌前先說」`<details>` 預設帶 `open`，口白通常比精簡版長很多（可能包含見證、個人故事）。
- 若某首歌之後要交回給司會或轉場，用 `.say.after` 卡片（`<span class="say-badge">唱畢後說</span>` + 幾句 `.say-line` + 可能有 `.say-alt` 小標「接著說：」再接一段）。
- 這些內容通常需要向使用者要一份口白草稿或請他們描述想講的重點——**不要憑空杜撰見證或個人故事**，這部分一定是使用者提供或明確授權你根據他們的描述改寫的。

## README.md 目錄

根目錄 `README.md` 有兩個表格，分別對應兩個資料夾，欄位是「日期｜標題｜連結」，新的一列插入在最上面（日期新到舊）：

```markdown
| 2026-08-16 | 主日敬拜 | [詩歌敬拜歌曲/2026-08-16.html](詩歌敬拜歌曲/2026-08-16.html) |
```

新增筆記檔案後記得同步更新對應表格，兩份筆記各自的表格都要加。

## 特殊場合（追思會等）不要硬套模板

如果使用者要做的不是一般主日敬拜（例如追思紀念會、特別聚會），既有檔案可能有自己的一次性排版（不一定是四首歌／s1-s4 這套邏輯）。這種情況下，把最近一份「性質相近」的檔案當風格參考即可，不必強迫套用 s1-s4 四階段色或標準的敬拜軸線結構。
