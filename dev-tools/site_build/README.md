# site_build：從瑞士版產生台灣版網站

`site/` 不是手改的，而是由 `build_site.py` 從 `base/docs`（瑞士版原始檔，永遠不改）產生。這樣隨時可以對照原版，也看得到每一處台灣修改。

## 用法

在 CHemTrace-TW 資料夾執行：

```
python dev-tools/site_build/build_site.py
```

它會：

1. 讀 `base/docs` 的所有檔案，但不含瑞士的 1 km 資料網格（`data/grid.bin`、`data/grid.json`）。
2. 依序套用 `STEPS` 裡的修改檔（目前是 `step_2a.py`、`step_2c.py`、`step_2f.py`、`step_explore.py`、`step_2b.py`）。
3. 寫進 `site/`。只覆寫內容有變的檔案，不會刪除任何檔案。

每一條修改都寫明「要取代的原文」和「應該出現幾次」。如果 `base/` 改了、某條修改對不上，程式會停下來並說明是哪一條，不會默默跳過。

## 各步驟

| 檔案 | 內容 |
|---|---|
| `step_2a.py` | 座標改 TWD97（EPSG:3826）；底圖改國土測繪中心 EMAP5_OPENDATA；移除瑞士的高程、河網、保護區和水文地質圖層服務；移除瑞士資料網格與 NABEL 空氣測站；瀏覽器儲存鍵改成 `cht-tw-*`；名稱 CHemTrace Taiwan 0.1.0；中文字型備援 |
| `step_2f.py` | 地區預設：嘉南平原（每個數值附出處，沒有出處的標 ASSUMED）；瑞士預設保留給 selfTest |
| `step_explore.py` | 探索模式：瑞士註記換成有出處的台灣註記或移除，瑞士地名改成通用說法 |
| `step_2b.py` | 中英雙語：建構時從 `index.html` 產生 `index.zh.html`，從 `zh_strings.py` 產生 `assets/js/i18n-zh.js`；app.js 加上 `tr()` 翻譯函式和語言切換。依序放在 2c 之後，才會翻到台灣版的文字 |
| `step_2c.py` | 台灣法規標準取代瑞士 `LIM`：飲用水、地下水第一類／第二類管制與監測、土壤管制與監測（含食用作物農地）；新增「地下水分類」輸入；地面水體和空氣標準還沒讀到數值，結果會註明「尚未查核」 |

之後的步驟（2b 雙語、2d 網格、2e 圖層、2f 地區預設、2g 英文頁面）也用同樣方式加檔案，再加進 `STEPS`。

## 中文翻譯

改 `zh_strings.py` 再重新建構。`HTML` 是頁面固定文字（英文片段 → 中文片段，每一條都必須找得到，找不到會停下來）；`T` 是 app.js 產生的文字（英文原句 → 中文）；`P` 是含數字或金屬名稱的句型。

## 測試

先在 `site/` 開本機伺服器（port 8765），再執行：

- `node dev-tools/tests/t_self.js`：`SMP.selfTest()`，台灣版 0.1.0 共 20 項（瑞士版 18 項，加了 TWD97 座標和台灣標準兩項）
- `node dev-tools/tests/t_tw.js [輸出資料夾]`：在瀏覽器裡測座標查詢、設定污染源位置、地下水分類欄位，並截圖
- `node dev-tools/tests/t_pages.js`、`t_mob.js`：原本的頁面與手機版檢查

## 底圖

國土測繪中心 WMTS，`https://wmts.nlsc.gov.tw/wmts/{圖層}/default/GoogleMapsCompatible/{z}/{y}/{x}`（y 在 x 前面）。網站提供 EMAP（彩色）、EMAP01（灰階）、PHOTO2（正射影像）三種，圖層代碼已在國土測繪中心的 GetCapabilities 文件確認。雲端測試環境連不到 wmts.nlsc.gov.tw，底圖只能在你的瀏覽器看。
