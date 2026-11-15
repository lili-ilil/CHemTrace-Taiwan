# dev-tools

開發瑞士版時用過的工具，路徑已改成相對於這個資料夾。

## site_build/（產生台灣版網站）

`python dev-tools/site_build/build_site.py` 從 `base/docs` 產生 `site/`，詳見 `site_build/README.md`。

## tests/（需要 Node.js 和 Playwright）

先在 `base/docs`（或之後台灣版的網站資料夾）開本機伺服器，port 8765：

```
cd base/docs
python -m http.server 8765
```

另開一個終端機：

```
npm install playwright
npx playwright install chromium
node dev-tools/tests/t_self.js
```

| 檔案 | 用途 |
|---|---|
| `t_self.js` | 執行 `SMP.selfTest()`。瑞士版 0.13.0 有 18 項；台灣版 0.1.0 有 20 項，全部通過 |
| `t_tw.js` | 台灣版：座標查詢、設定污染源位置、地下水分類欄位，並截圖 |
| `t_pages.js` | 在桌面和手機寬度打開 manual 與 validation 頁，檢查有沒有橫向溢出、壞掉的頁內連結和 JavaScript 錯誤 |
| `t_mob.js` | 在手機寬度（淺色）和桌面寬度（深色）打開 Advanced 模式截圖檢查 |
| `t_pqnew.js`、`t_pqvar.js`、`t_pqmore.js` | 產生 PHREEQC 匯出檔。`t_pqmore.js` 產生 48 個批次案例（3 金屬 × 4 地區 × 土壤/地下水 × 有無鹼度），再用 `phreeqc/check_ph.py` 確認 pH。`t_pqnew.js` 寫入 `pq_new/`，執行前先建立該資料夾 |

## phreeqc/（需要 Python 和 phreeqpython：`pip install phreeqpython`）

- `minteq.v4.dat`：PHREEQC 隨附的 MINTEQ v4 熱力學資料庫。
- `run_pq.py`：執行匯出的 `.pqi` 檔，印出批次結果和管柱突破曲線。用法：`python run_pq.py "pq_new/*.pqi"`
- `check_ph.py`：確認每個批次案例都維持在目標 pH。用法：`python check_ph.py "pq_new/*.pqi"`

## generators/

- `assumptions.py`：產生 `assumptions.html`（83 條假設的表格）。內容是瑞士版的，台灣版要改寫內容後再用。它會讀 `base/docs/validation.html` 的頁首樣式，寫入 `base/docs/assumptions.html`。台灣版改用自己的網站資料夾時，記得改 `SITE` 路徑。
