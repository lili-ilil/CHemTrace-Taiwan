# MOENV regional groundwater quality: cleaning and well summary (all)

Made 2026-11-15 09:40 UTC by tools/process_moenv_wells.py from `data/raw/moenv/WQX_P_02/20261115T084026Z/records.json` and `data/raw/moenv/WQX_P_07/20261115T090605Z/records.json`.

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

## Wells and samples in all

- Wells with at least one key item measured: 496
- Wells in the wells file for this district: 732
- Wells without coordinates: 0; coordinates taken from the quality records: 0
- Status of use: {'啟用': 459, '停用': 37}
- Samples (well and sampling time): 8698; by year: 2014: 1116 · 2015: 999 · 2016: 1001 · 2017: 551 · 2018: 750 · 2019: 665 · 2020: 652 · 2021: 599 · 2022: 586 · 2023: 589 · 2024: 591 · 2025: 599

## Coverage of key items

| code | wells | samples | below detection | median of well medians* |
|---|---|---|---|---|
| As | 496 | 8670 | 3513 | 0.0031 mg/L |
| Fe | 496 | 8670 | 587 | 0.06 mg/L |
| Mn | 496 | 8670 | 1590 | 0.297 mg/L |
| DO | 482 | 6555 | 9 | 1.7 mg/L |
| ORP | 482 | 6128 | 0 | 71.9 mV |
| NO3N | 496 | 8669 | 1785 | 0.91 mg/L as N |
| NH3N | 496 | 8670 | 1624 | 0.168 mg/L as N |
| SO4 | 496 | 8669 | 117 | 59.6 mg/L |
| TOC | 496 | 8670 | 7 | 0.915 mg/L |
| pH | 496 | 8670 | 0 | 6.8  |
| WT | 496 | 8669 | 0 | 27.1 °C |
| EC | 496 | 8670 | 0 | 655 µmho/cm at 25 °C |
| Alk | 494 | 6601 | 0 | 216 mg/L as CaCO3 |
| Ca | 494 | 6601 | 0 | 74 mg/L |
| Mg | 494 | 6601 | 1 | 17.6 mg/L |
| Na | 494 | 6601 | 0 | 25.9 mg/L |
| K | 494 | 6601 | 0 | 3.21 mg/L |
| Cl | 496 | 8670 | 44 | 21.7 mg/L |
| TH | 496 | 8668 | 1 | 264 mg/L as CaCO3 |
| TDS | 496 | 8650 | 0 | 423 mg/L |
| GWT | 496 | 8698 | 0 | 3.75 m |
| Hg | 496 | 8670 | 8642 | – |
| Pb | 496 | 8667 | 7613 | 0.003 mg/L |
| Cd | 496 | 8670 | 8421 | 0.002 mg/L |
| Cr | 496 | 8668 | 7186 | 0.001 mg/L |
| Cu | 496 | 8665 | 6086 | 0.001 mg/L |
| Ni | 496 | 8670 | 7404 | 0.008 mg/L |
| Zn | 496 | 8669 | 2144 | 0.008 mg/L |

*Only wells whose median is a measured value; wells with a median below detection are left out of this column.

## Arsenic: first look (496 wells)

| threshold (mg/L) | meaning | wells with median above | wells with at least one sample above |
|---|---|---|---|
| 0.01 | drinking water standard (飲用水水質標準) | 72 | 117 |
| 0.025 | groundwater monitoring standard, class 1 (地下水污染監測標準) | 39 | 68 |
| 0.05 | groundwater control standard, class 1 (地下水污染管制標準) | 12 | 36 |
| 0.25 | groundwater monitoring standard, class 2 | 1 | 2 |
| 0.5 | groundwater control standard, class 2 | 0 | 1 |

Standards: see 05_第一階段_資料可行性與試點計畫.md, section 1.3, for sources. Medians and maxima are per well over all samples; they say nothing yet about depth, because the MOENV data have no well depth.

## Redox potential: extreme values to check by hand

Lowest: -857 mV (4257, 2016-01-26), -333.5 mV (4930, 2023-01-30), -307.5 mV (4222, 2024-10-14), -297.6 mV (4222, 2024-04-12), -296.8 mV (4930, 2022-01-10), -291 mV (4928, 2016-01-26), -290.1 mV (4930, 2022-07-02), -290 mV (4916, 2021-11-15)

Highest: 378 mV (4616, 2025-11-18), 381 mV (4145, 2023-05-31), 390.1 mV (4728, 2023-10-23), 392 mV (4365, 2016-11-22), 402 mV (4370, 2016-11-23), 410 mV (4917, 2016-11-25), 431 mV (4396, 2021-10-25), 438 mV (4603, 2019-05-13)
