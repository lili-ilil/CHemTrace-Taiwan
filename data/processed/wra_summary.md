# WRA groundwater data: wells, water quality by layer, levels

Made 2026-11-15 11:50 UTC by tools/process_wra.py.

Data: 經濟部水利署, 地下水水位觀測井井況 (data.gov.tw 32718), 地下水水位年度統計 (32717), 水利署地下水水質歷史資料 (161086); Open Government Data License, version 1.0, https://data.gov.tw/license

## Wells

- Observation wells: 1006; stations (well name without '(n)'): 433; disused: 72
- Layer codes: {'1': 391, '2': 299, '3': 157, '4': 75, '-': 51, '0': 26, '': 5, '3-1': 1, '3-2': 1}
- Confined (C) / unconfined (U): {'C': 532, 'U': 356, '': 79, '-': 38, 'L': 1}
- County name and address disagree: 207 wells (flagged in wra_wells.csv)

## Cleaning log (water quality)

| step | count |
|---|---|
| As_aso: missing code | 2117 |
| As_aso: negative value treated as missing | 1 |
| Ca: missing code | 7 |
| Cd: missing code | 4580 |
| Cd: negative value treated as missing | 5 |
| Cl: missing code | 139 |
| Cl: negative value treated as missing | 1 |
| Cr: missing code | 4560 |
| Cr: negative value treated as missing | 6 |
| Cu: missing code | 3751 |
| Cu: negative value treated as missing | 4 |
| Fe: missing code | 508 |
| HCO3: missing code | 3 |
| Hg: missing code | 1910 |
| K: missing code | 29 |
| Mg: missing code | 4 |
| Mg: negative value treated as missing | 1 |
| Mn: missing code | 888 |
| NH3N: missing code | 1224 |
| NH3N: negative value treated as missing | 7 |
| NO2N: missing code | 672 |
| NO2N: negative value treated as missing | 23 |
| NO3N: missing code | 1866 |
| NO3N: negative value treated as missing | 31 |
| Na: missing code | 73 |
| Pb: missing code | 4885 |
| Pb: negative value treated as missing | 5 |
| SO4: missing code | 454 |
| TOC: missing code | 455 |
| TOC: negative value treated as missing | 6 |
| Zn: missing code | 2028 |
| Zn: negative value treated as missing | 1 |
| pH outside 0-14 treated as missing | 2 |
| quality records | 9509 |
| quality records whose well is not in the well list | 34 |
| sulfide: missing code | 1852 |
| sulfide: negative value treated as missing | 5 |

Records dated YYYY-01-01 (year only): 2928 of 9509; years 1992–2025

## Arsenic (aso) by district and aquifer layer

Median over wells of each well's median; share of records above 0.01, 0.05 and 0.1 mg/L. aso is taken to be arsenic in mg/L (unconfirmed).

| district | layer | wells | records | median of well medians | >0.01 | >0.05 | >0.1 |
|---|---|---|---|---|---|---|---|
| 嘉南平原 | 1 | 54 | 482 | 0.05 | 88% | 45% | 24% |
| 嘉南平原 | 2 | 46 | 377 | 0.122 | 85% | 66% | 58% |
| 嘉南平原 | 3 | 39 | 316 | 0.105 | 90% | 72% | 57% |
| 嘉南平原 | 4 | 29 | 297 | 0.1 | 85% | 70% | 54% |
| 濁水溪沖積扇 | 1 | 91 | 635 | 0.01 | 61% | 31% | 15% |
| 濁水溪沖積扇 | 2 | 114 | 690 | 0.01 | 50% | 27% | 18% |
| 濁水溪沖積扇 | 3 | 55 | 288 | 0 (below detection?) | 29% | 6% | 3% |
| 濁水溪沖積扇 | 4 | 17 | 110 | 0 (below detection?) | 29% | 6% | 4% |
| 屏東平原 | 1 | 72 | 430 | 0 (below detection?) | 38% | 19% | 9% |
| 屏東平原 | 2 | 31 | 216 | 0 (below detection?) | 33% | 24% | 17% |
| 屏東平原 | 3 | 27 | 200 | 0 (below detection?) | 42% | 27% | 17% |
| 屏東平原 | 4 | 11 | 99 | 0 (below detection?) | 36% | 10% | 5% |
| 蘭陽平原 | 1 | 26 | 221 | 0.01 | 59% | 17% | 8% |
| 蘭陽平原 | 2 | 13 | 135 | 0.03 | 69% | 29% | 21% |
| 蘭陽平原 | 3 | 4 | 45 | 0.04 | 82% | 38% | 31% |
| 蘭陽平原 | 4 | 1 | 9 | 0.01 | 44% | 22% | 0% |

## Measured redox class (O2 unknown) in 嘉南平原 by layer

- Layer 1 (557 records): incomplete 38%, Fe(III), O2 unknown 27%, Fe(III)/SO4 (no sulfide), O2 unknown 16%, Fe(III)-SO4, O2 unknown 7%, NO3 and Fe(III), O2 unknown 5%, NO3 and Fe(III)/SO4 (no sulfide), O2 unknown 2%
- Layer 2 (433 records): incomplete 43%, Fe(III), O2 unknown 26%, Fe(III)/SO4 (no sulfide), O2 unknown 11%, Fe(III)-SO4, O2 unknown 5%, NO3 and Fe(III), O2 unknown 4%, CH4gen, O2 unknown 4%
- Layer 3 (366 records): incomplete 39%, Fe(III), O2 unknown 28%, Fe(III)/SO4 (no sulfide), O2 unknown 10%, Fe(III)-SO4, O2 unknown 5%, NO3 and Fe(III), O2 unknown 4%, SO4, O2 unknown 4%
- Layer 4 (350 records): incomplete 38%, Fe(III), O2 unknown 27%, Fe(III)-SO4, O2 unknown 10%, Fe(III)/SO4 (no sulfide), O2 unknown 7%, NO3 and Fe(III), O2 unknown 4%, CH4gen, O2 unknown 3%

## Nearest WRA station to each MOENV well

| MOENV district | wells | median distance (km) |
|---|---|---|
| 屏東平原 | 95 | 1.9 |
| 嘉南平原 | 94 | 2.4 |
| 新苗地區 | 73 | 1.9 |
| 臺北盆地 | 66 | 2.5 |
| 濁水溪沖積扇 | 44 | 2.5 |
| 臺中地區 | 39 | 2.8 |
| 桃園中壢臺地 | 24 | 2.8 |
| 蘭陽平原 | 21 | 1.1 |
| 花東縱谷 | 20 | 1.4 |
