# GSMMA hydrogeological boreholes and lithology logs

Made 2026-11-15 09:46 UTC by tools/process_gsmma.py.

Data: 經濟部地質調查及礦業管理中心, 水文地質鑽探資料庫 (data.gov.tw 16799), 平原區鑽井資料 (162478), 平原區水文地質鑽探-鑽孔岩心紀錄 (61131); Open Government Data License, version 1.0, https://data.gov.tw/license

## Boreholes

- In 16799: 387; in 162478: 400; joined: 400 (only in 162478: 13, all without district)
- With a lithology log: 368; log wells not in either list: 2

| district | boreholes | with log | well depth median (m) | depth range (m) |
|---|---|---|---|---|
| 濁水溪沖積扇 | 97 | 86 | 200 | 60–331.5 |
| 嘉南平原 | 93 | 92 | 250 | 50–300 |
| 屏東平原 | 56 | 52 | 211.5 | 61–302 |
| 蘭陽平原 | 31 | 28 | 195 | 44–300 |
| 新苗地區 | 30 | 30 | 150 | 50–250 |
| 臺中地區 | 27 | 25 | 150.5 | 80–300 |
| 臺北盆地 | 14 | 14 | 103.5 | 43.3–273.2 |
| 桃園中壢臺地 | 14 | 14 | 200 | 150–250 |
| 花東縱谷 | 13 | 13 | 150 | 120–202 |
| (none given) | 13 | 0 | 73 | 60–230 |
| 澎湖群島 | 8 | 8 | 153 | 150–251 |
| 恆春平原 | 4 | 4 | 166.75 | 150–220 |

## Lithology intervals

- Intervals: 93635 (dropped with missing or reversed depths: 0); boreholes: 368
- Gaps between consecutive intervals: 3537; overlaps: 39

| class | logged thickness (m) | share |
|---|---|---|
| fine | 24982 | 36.0% |
| sand | 25097 | 36.1% |
| gravel | 16298 | 23.5% |
| rock | 952 | 1.4% |
| organic | 0 | 0.0% |
| fill | 8 | 0.0% |
| missing | 2083 | 3.0% |
| unclassified | 4 | 0.0% |

Parser check against the legend names (grain codes whose name ends in a grain word): agree 259, disagree 1
- ('MfGmS', '泥細砂質中礫', 'sand', 'gravel')

Codes classified with a note (code, note, class: intervals):

- Tf: case variant of a legend code, rock: 66
- Bs: case variant of a legend code, rock: 55
- BR: case variant of a legend code, rock: 20
- Ls: case variant of a legend code, rock: 15
- SS: parsed, not in legend, sand: 14
- Br: case variant of a legend code, rock: 14
- fGZ: parsed, not in legend, fine: 5
- ZM: parsed, not in legend, fine: 4
- MZ: parsed, not in legend, fine: 3
- ScG: parsed, not in legend, gravel: 3
- PZ: not in legend, unclassified: 3
- mSfS: parsed, not in legend, sand: 1
- v: not in legend, unclassified: 1
- vS: not in legend, unclassified: 1
- ZmG: parsed, not in legend, gravel: 1
- CmG: parsed, not in legend, gravel: 1
- fGC: parsed, not in legend, fine: 1
- cSfS: parsed, not in legend, sand: 1
- vcScS: parsed, not in legend, sand: 1
- MfGvfS: parsed, not in legend, sand: 1
- lst: not in legend, unclassified: 1

## Nearest borehole to each MOENV monitoring well

| MOENV district | wells | median distance (km) | 90th percentile (km) | nearest borehole in the same district |
|---|---|---|---|---|
| 屏東平原 | 95 | 1.7 | 2.8 | 91 |
| 嘉南平原 | 94 | 2.2 | 3.9 | 91 |
| 新苗地區 | 73 | 1.4 | 3.6 | 69 |
| 臺北盆地 | 66 | 3.2 | 20.3 | 61 |
| 濁水溪沖積扇 | 44 | 2.7 | 3.8 | 37 |
| 臺中地區 | 39 | 3.0 | 16.1 | 33 |
| 桃園中壢臺地 | 24 | 3.9 | 5.7 | 23 |
| 蘭陽平原 | 21 | 0.7 | 2.7 | 21 |
| 花東縱谷 | 20 | 6.3 | 25.8 | 20 |
| 澎湖地區 | 12 | 2.3 | 3.5 | 0 |
| 金門 | 6 | 26.3 | 35.0 | 0 |
| 連江 | 2 | 121.9 | 135.9 | 0 |

The MOENV wells have no depth in the open data, so the borehole profile shows the layers near the well, not the layer the well draws from.
