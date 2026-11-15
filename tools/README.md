# tools/：台灣版資料下載、整理與驗證

這些程式只用 Python 標準函式庫，不用另外安裝套件，需要 Python 3.8 以上。`v1_redox.py` 另外需要 Node.js，用來執行瑞士版 app.js 裡原本的氧化還原階梯。

| 檔案 | 用途 | 輸出 |
|---|---|---|
| `fetch_moenv.py` | 從環境部開放資料 API（data.moenv.gov.tw）下載資料集，要金鑰 | `data/raw/moenv/` |
| `inspect_moenv.py` | 檢查下載的環境部資料：欄位、項目、單位、年份、分區 | 原始資料夾裡的 `inspect.md` |
| `process_moenv_wells.py` | 清理環境部地下水水質，產出每次採樣和每口井的表 | `data/processed/moenv_*` |
| `fetch_wra.py` | 從水利署開放資料 API（opendata.wra.gov.tw）下載觀測井井況和水位統計 | `data/raw/wra/` |
| `process_wra.py` | 整理水利署觀測井、分層水質（161086，手動下載）、水位統計 | `data/processed/wra_*` |
| `process_gsmma.py` | 整理地調中心鑽井和岩性紀錄（16799、162478、61131，手動下載） | `data/processed/gsmma_*` |
| `ladder_node.mjs` | 在 Node.js 執行 base/ 裡原本的 `redoxLadder`，不修改 base/ | 給 v1_redox.py 用 |
| `v1_redox.py` | V1 驗證：氧化還原階梯和實測水質分類的比較 | `data/processed/v1*` |

手動下載的檔案放在：`data/raw/gsmma/16799.csv`、`162478.csv`、`61131.csv`，以及 `data/raw/wra/161086.csv`。

## 金鑰

金鑰放在 `.secret/moenv_api_key.txt`，只有一行。程式不會把金鑰印出來，也不會寫進任何輸出檔。`.secret/` 已列在 `.gitignore`，不會被上傳到 GitHub。

## 在 Windows 上執行

在 CHemTrace-TW 資料夾開「命令提示字元」或 PowerShell：

```
cd "C:\Users\Li Ling Tai\Downloads\Models\CHemTrace-TW"
python tools\fetch_moenv.py <DataID> --sample 1000
python tools\inspect_moenv.py data\raw\moenv\<DataID>\<時間戳記資料夾>
```

- `<DataID>` 是資料集代碼，可以在 `https://data.moenv.gov.tw/dataset/detail/<DataID>` 這種網址裡找到。
- `--sample 1000` 只抓前 1000 筆，先確認欄位和項目。確認沒問題後，拿掉 `--sample` 就會抓整個資料集。
- 可以一次抓好幾個資料集：`python tools\fetch_moenv.py <ID1> <ID2>`。
- 想只抓特定月份，可以加 `--param year_month=2024_06`。這個參數寫在平台的 API 說明裡，但每個資料集是否都支援還不確定。

## 輸出

每次下載存成一個新資料夾：`data/raw/moenv/<DataID>/<UTC 時間戳記>/`，內容如下：

- `page_00000.json`、`page_00001.json`…：API 回傳的原始內容，一頁一個檔，沒有任何修改
- `records.json`：所有資料合併成一個清單
- `meta.json`：下載時間、查詢參數（不含金鑰）、筆數、是否完整、授權和出處標示範本
- `inspect.md`：執行 `inspect_moenv.py` 後產生的檢查結果

`data/raw/` 也列在 `.gitignore`，原始資料不上傳。

## 次數限制

會員金鑰每個 API 每天可以呼叫 5,000 次（data.moenv.gov.tw/api-term）。程式預設每個資料集最多呼叫 4,500 次（`--max-calls`），每次間隔 1 秒（`--pause`），每次最多要求 1000 筆（`--limit`）。如果伺服器每頁給的筆數比較少，程式會依 API 回報的總筆數繼續抓。

一天抓不完時，程式會停下來並顯示 `continue with --offset N`。隔天加上 `--offset N` 再執行一次，就會從第 N 筆接著抓，結果存在新的資料夾。每個資料夾的 `meta.json` 會記錄這次的起點（`start_offset`）和終點（`next_offset`）。

## 授權

資料採政府資料開放授權條款第 1 版。公開使用處理後的資料時，要標示：提供機關與年份、資料集名稱與版本、採用此授權的聲明，以及授權連結 https://data.gov.tw/license 。`meta.json` 裡有標示文字的範本。

## fetch_chianan_extra.py

嘉南平原預設需要的環境部資料：河川水質（WQX_P_01）、水庫水質（WQX_P_03）、空氣品質監測月值（AQX_P_08），只抓嘉義縣、嘉義市、臺南市的河川與水庫，以及朴子、新港、嘉義、新營四個空品站。

```
python tools/fetch_chianan_extra.py
```

每個篩選條件會先抓 50 筆測試，確認 API 真的有篩選（`filters=欄位,EQ,值`）才整批下載；如果 API 忽略篩選，程式會停下來，不會把全國資料都抓下來。金鑰一樣從 `.secret/moenv_api_key.txt` 讀，不會印出。

## process_chianan_extra.py

把 `fetch_chianan_extra.py` 抓的資料和農業部詳細土壤圖（`data/raw/soil/`）整理成嘉南平原預設用的摘要：空品測站 PM10、PM2.5 年平均，河川懸浮固體、pH、砷汞鉛（含低於偵測極限的比例），以及平原區（坡度 0–5%）土壤酸鹼性和排水等級的面積比例。

```
python tools/process_chianan_extra.py
```

輸出 `data/processed/chianan_extra_summary.md` 和 `.csv`。
