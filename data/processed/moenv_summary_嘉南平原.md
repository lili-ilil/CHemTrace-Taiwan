# MOENV regional groundwater quality: cleaning and well summary (嘉南平原)

Made 2026-11-15 09:25 UTC by tools/process_moenv_wells.py from `data/raw/moenv/WQX_P_02/20261115T084026Z/records.json` and `data/raw/moenv/WQX_P_07/20261115T090605Z/records.json`.

Data: Ministry of Environment (Taiwan), Regional groundwater quality monitoring data (WQX_P_02) and Basic information on regional groundwater quality monitoring wells (WQX_P_07), data.moenv.gov.tw, Open Government Data License, version 1.0, https://data.gov.tw/license

## Cleaning log

| step | records |
|---|---|
| records read | 378372 |
| date written YYYYMMDD | 33952 |
| repeated record dropped (same value) | 44998 |
| records kept | 333374 |
| value: measured | 180353 |
| value: below detection | 63948 |
| value: not measured | 89062 |
| value: missing code | 11 |
| html entity decoded | 3270 |
| ORP '<x' read as -x | 1448 |
| ORP -999 or -555 treated as missing | 11 |

## Units in the raw data (key items)

| code | item | units as written (records) | unit used |
|---|---|---|---|
| As | 砷 | 'mg/L' (10148) | mg/L |
| Fe | 鐵 | 'mg/L' (10148) | mg/L |
| Mn | 錳 | 'mg/L' (10148) | mg/L |
| DO | 溶氧(電極法) | 'mg/L' (7916) | mg/L |
| ORP | 氧化還原電位 | 'mV' (7489) | mV |
| NO3N | 硝酸鹽氮 | 'mg/L' (10148) | mg/L as N |
| NH3N | 氨氮 | 'mg/L' (10148) | mg/L as N |
| SO4 | 硫酸鹽 | 'mg/L' (10148) | mg/L |
| TOC | 總有機碳 | 'mg/L' (10148) | mg/L |
| pH | 酸鹼值 | '' (9038), 'None' (1110) |  |
| WT | 水溫 | '℃' (10148) | °C |
| EC | 導電度 | 'μmho/cm25℃' (10148) | µmho/cm at 25 °C |
| Alk | 總鹼度 | 'mg/L as CaCO3' (4783), 'mg/L' (3967) | mg/L as CaCO3 |
| Ca | 鈣 | 'mg/L' (8750) | mg/L |
| Mg | 鎂 | 'mg/L' (8750) | mg/L |
| Na | 鈉 | 'mg/L' (8750) | mg/L |
| K | 鉀 | 'mg/L' (8750) | mg/L |
| Cl | 氯鹽 | 'mg/L' (10148) | mg/L |
| TH | 總硬度 | 'mg/L as CaCO3' (6138), 'mg/L' (4010) | mg/L as CaCO3 |
| TDS | 總溶解固體物 | 'mg/L' (10148) | mg/L |
| GWT | 水面至井口深度 | 'm' (10148) | m |
| Hg | 汞 | 'mg/L' (10148) | mg/L |
| Pb | 鉛 | 'mg/L' (10148) | mg/L |
| Cd | 鎘 | 'mg/L' (10148) | mg/L |
| Cr | 鉻 | 'mg/L' (10148) | mg/L |
| Cu | 銅 | 'mg/L' (10148) | mg/L |
| Ni | 鎳 | 'mg/L' (10148) | mg/L |
| Zn | 鋅 | 'mg/L' (10148) | mg/L |

## Wells and samples in 嘉南平原

- Wells with at least one key item measured: 94
- Wells in the wells file for this district: 126
- Wells without coordinates: 0; coordinates taken from the quality records: 0
- Status of use: {'啟用': 92, '停用': 2}
- Samples (well and sampling time): 1823; by year: 2014: 249 · 2015: 223 · 2016: 211 · 2017: 114 · 2018: 153 · 2019: 135 · 2020: 131 · 2021: 122 · 2022: 119 · 2023: 122 · 2024: 120 · 2025: 124

## Coverage of key items

| code | wells | samples | below detection | median of well medians* |
|---|---|---|---|---|
| As | 94 | 1809 | 394 | 0.01 mg/L |
| Fe | 94 | 1809 | 118 | 0.268 mg/L |
| Mn | 94 | 1809 | 77 | 0.353 mg/L |
| DO | 93 | 1337 | 0 | 2.1 mg/L |
| ORP | 93 | 1251 | 0 | -42.9 mV |
| NO3N | 94 | 1809 | 593 | 0.055 mg/L as N |
| NH3N | 94 | 1809 | 258 | 0.69 mg/L as N |
| SO4 | 94 | 1809 | 49 | 93.6 mg/L |
| TOC | 94 | 1809 | 0 | 1.47 mg/L |
| pH | 94 | 1809 | 0 | 7  |
| WT | 94 | 1809 | 0 | 28.1 °C |
| EC | 94 | 1809 | 0 | 960 µmho/cm at 25 °C |
| Alk | 94 | 1403 | 0 | 332 mg/L as CaCO3 |
| Ca | 94 | 1403 | 0 | 98.1 mg/L |
| Mg | 94 | 1403 | 1 | 30.8 mg/L |
| Na | 94 | 1403 | 0 | 65.1 mg/L |
| K | 94 | 1403 | 0 | 5.16 mg/L |
| Cl | 94 | 1809 | 0 | 42 mg/L |
| TH | 94 | 1808 | 0 | 367 mg/L as CaCO3 |
| TDS | 94 | 1805 | 0 | 603 mg/L |
| GWT | 94 | 1823 | 0 | 2.59 m |
| Hg | 94 | 1809 | 1805 | – |
| Pb | 94 | 1809 | 1561 | – |
| Cd | 94 | 1809 | 1686 | 0.00325 mg/L |
| Cr | 94 | 1809 | 1714 | 0.0015 mg/L |
| Cu | 94 | 1809 | 1668 | 0.002 mg/L |
| Ni | 94 | 1809 | 1720 | 0.00625 mg/L |
| Zn | 94 | 1809 | 900 | 0.0035 mg/L |

*Only wells whose median is a measured value; wells with a median below detection are left out of this column.

## Arsenic: first look (94 wells)

| threshold (mg/L) | meaning | wells with median above | wells with at least one sample above |
|---|---|---|---|
| 0.01 | drinking water standard (飲用水水質標準) | 35 | 49 |
| 0.025 | groundwater monitoring standard, class 1 (地下水污染監測標準) | 21 | 33 |
| 0.05 | groundwater control standard, class 1 (地下水污染管制標準) | 6 | 19 |
| 0.25 | groundwater monitoring standard, class 2 | 1 | 1 |
| 0.5 | groundwater control standard, class 2 | 0 | 1 |

Standards: see 05_第一階段_資料可行性與試點計畫.md, section 1.3, for sources. Medians and maxima are per well over all samples; they say nothing yet about depth, because the MOENV data have no well depth.

## Redox potential: extreme values to check by hand

Lowest: -307.5 mV (4222, 2024-10-14), -297.6 mV (4222, 2024-04-12), -282.9 mV (4222, 2025-04-22), -260.8 mV (4263, 2018-01-12), -260.4 mV (4271, 2022-10-06), -251.2 mV (4680, 2021-10-02), -248.4 mV (4222, 2022-11-03), -247.9 mV (4222, 2018-10-29)

Highest: 252.6 mV (4211, 2016-04-28), 256.1 mV (4681, 2022-11-03), 260.8 mV (4920, 2016-04-20), 262.4 mV (4233, 2017-04-25), 263 mV (4239, 2019-11-08), 263.9 mV (4920, 2020-01-14), 277.8 mV (4921, 2020-01-14), 347.3 mV (4920, 2019-07-03)
