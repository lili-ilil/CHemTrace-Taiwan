# site_build：從瑞士版產生台灣版網站

`site/` 不是手改的，而是由 `build_site.py` 從 `base/docs`（瑞士版原始檔，永遠不改）產生。這樣隨時可以對照原版，也看得到每一處台灣修改。

## 用法

在 CHemTrace-TW 資料夾執行：

```
python dev-tools/site_build/build_site.py
```

它會：

1. 讀 `base/docs` 的所有檔案，但不含瑞士的 1 km 資料網格（`data/grid.bin`、`data/grid.json`）。
2. 依序套用 `STEPS` 裡的修改檔（目前是 `step_2a.py`、`step_metals.py`、`step_2c.py`、`step_2f.py`、`step_cd.py`、`step_ni.py`、`step_cr.py`、`step_coast.py`、`step_explore.py`、`step_sources.py`、`step_help_tw.py`、`step_2b.py`、`step_zh_dyn.py`、`step_grid.py`、`step_wells.py`）。
3. 寫進 `site/`。只覆寫內容有變的檔案，不會刪除任何檔案。

每一條修改都寫明「要取代的原文」和「應該出現幾次」。如果 `base/` 改了、某條修改對不上，程式會停下來並說明是哪一條，不會默默跳過。

## 各步驟

| 檔案 | 內容 |
|---|---|
| `step_2a.py` | 座標改 TWD97（EPSG:3826）；底圖改國土測繪中心 WMTS（EMAP 彩色、EMAP01 灰階、PHOTO2 正射影像，可切換）；移除瑞士的高程、河網、保護區和水文地質圖層服務；移除瑞士資料網格與 NABEL 空氣測站；瀏覽器儲存鍵改成 `cht-tw-*`；名稱 CHemTrace Taiwan 0.1.0；中文字型備援 |
| `step_metals.py` | 程式裡寫死 As、Hg、Pb 的地方改成讀 `METALS` 的全部金屬，讓後面可以加新金屬；原有三種金屬數值不變（`dev-tools/tests/t_regress.js`） |
| `step_cd.py` | 新增鎘：Kd（Sauvé et al. 2000）、懸浮物 Kd（Allison & Allison 2005）、台灣標準、EFSA 2011 TWI、探索模式 13 個介質的中英文字；出處和假設寫在檔案開頭 |
| `step_ni.py` | 新增鎳，結構同 `step_cd.py`：Kd（Sauvé et al. 2000）、懸浮物 Kd、台灣標準、EFSA 2020 TDI |
| `step_cr.py` | 新增鉻，分 Cr(III) 和 Cr(VI)：化學型態帶價態，Cr(VI) 在長期淹水土壤和缺氧含水層視為還原成 Cr(III)；Kd（Allison & Allison 2005 Table 3）、台灣總鉻標準、Cr(III) TDI（EFSA 2014）和 Cr(VI) TDI（FSCJ 2019） |
| `step_coast.py` | 台灣地理：移除冰河釋放；嘉南地下水 Hg、Pb 背景值設 0（低於偵測極限）；輔助圖層的監測井勾選項。之後放水庫或海洋、沿海效應 |
| `step_wells.py` | 選址自動填入和擴散地圖圖層：地下水（5 km 內監測井，`tools/build_well_table.py`）、背景空氣（10 km 內空品站，`tools/build_air_table.py`）、地下水分類（水源保護區，`tools/build_protection_layer.py`）、海拔（觀測井地面高程） |
| `step_2f.py` | 地區預設：嘉南平原（每個數值附出處，沒有出處的標 ASSUMED）；瑞士預設保留給 selfTest |
| `step_explore.py` | 探索模式：瑞士註記換成有出處的台灣註記或移除，瑞士地名改成通用說法 |
| `step_sources.py` | 首頁參考資料：台灣法規、資料、文獻；保留模型仍用的國際方法參考 |
| `step_help_tw.py` | 欄位說明和資料來源註記裡的瑞士內容改成台灣版（有出處才放台灣數值，否則拿掉例子或標明是瑞士的）；放在 2b 之前，中文才對得上 |
| `step_zh_dyn.py` | 執行時產生的文字的中文：新增 `trNodes()`，在分頁說明、建議、摘要、質量收支、敏感度分析等面板產生後翻譯；字串在 `zh_dyn.py`，欄位說明的中文在 `zh_help.py`；放在 2b 之後 |
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

`make_preset_doc.js`：建構後執行 `node dev-tools/site_build/make_preset_doc.js`，從網站程式產生 `12_地區預設_嘉南平原.md`（說明文字在 `preset_doc_notes.md`）。

## step_grid.py

台灣資料網格（目前只有土壤圖）。網格檔由 `python tools/build_soil_grid.py` 產生（需要 `pip install pyshp rasterio numpy`），放在 `data/grid/`；建構時複製到 `site/data/`。選點後可自動填入土壤 pH 和水分狀態。放在最後一步，因為它改的是 2b 翻譯過的程式碼。
