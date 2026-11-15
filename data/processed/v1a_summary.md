# V1 design A: redox ladder vs measured redox process

Made 2026-11-15 11:09 UTC by tools/v1_redox.py. Ladder: redoxLadder from base/docs/assets/js/app.js (CHemTrace 0.13.0), run by tools/ladder_node.mjs.

Samples with DO, NO3-N, SO4 and TOC: 6553 (of 8698). Website defaults used for the other ladder inputs: K 0.002, grad 0.003, ne 0.2, aqFe 0.5, aqMn 0.2, budT 1 (BASE + preset 'plateau').


## All districts (6553 samples, 482 wells)

Measured category: mixed(oxic-anoxic) 2686 (41%), oxic 1831 (28%), anoxic 1416 (22%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 273 (4%), mixed(anoxic) 262 (4%), suboxic 85 (1%)

Ladder TEAP: mn 2542 (39%), o2 2035 (31%), no3 1149 (18%), fe 662 (10%), ch4 107 (2%), so4 58 (1%)

Agreement (ladder process is one of the measured processes): 3642 of 6468 (56%); not compared: 85 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| O2 | 1361 | 365 | 96 | 7 | 2 |
| O2-Fe(III)/SO4 | 276 | 36 | 1059 | 294 | 56 |
| Fe(III)/SO4 | 0 | 6 | 712 | 247 | 27 |
| O2-Mn(IV) | 268 | 276 | 306 | 57 | 2 |
| O2-NO3-Fe(III)/SO4 | 129 | 117 | 22 | 3 | 2 |
| Mn(IV) | 1 | 6 | 208 | 44 | 0 |
| NO3-Mn(IV) | 0 | 144 | 27 | 3 | 0 |
| NO3 | 0 | 128 | 14 | 0 | 1 |
| NO3-Fe(III)/SO4 | 0 | 67 | 18 | 3 | 0 |
| suboxic | 0 | 4 | 66 | 12 | 3 |
| O2-Fe(III)/SO4 or CH4gen | 0 | 0 | 14 | 31 | 11 |
| Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 19 | 3 |

## 嘉南平原 (1337 samples, 93 wells)

Measured category: mixed(oxic-anoxic) 1027 (77%), oxic 144 (11%), anoxic 113 (8%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 37 (3%), mixed(anoxic) 14 (1%), suboxic 2 (0%)

Ladder TEAP: mn 680 (51%), o2 281 (21%), fe 202 (15%), no3 144 (11%), so4 23 (2%), ch4 7 (1%)

Agreement (ladder process is one of the measured processes): 672 of 1335 (50%); not compared: 2 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| O2-Fe(III)/SO4 | 90 | 11 | 439 | 125 | 2 |
| O2-Mn(IV) | 87 | 68 | 145 | 28 | 1 |
| O2 | 90 | 32 | 17 | 4 | 1 |
| Fe(III)/SO4 | 0 | 0 | 43 | 42 | 1 |
| O2-NO3-Fe(III)/SO4 | 14 | 20 | 3 | 0 | 0 |
| O2-Fe(III)/SO4 or CH4gen | 0 | 0 | 9 | 20 | 2 |
| Mn(IV) | 0 | 0 | 19 | 4 | 0 |
| NO3-Mn(IV) | 0 | 4 | 3 | 0 | 0 |
| NO3-Fe(III)/SO4 | 0 | 6 | 0 | 1 | 0 |
| NO3 | 0 | 3 | 0 | 0 | 0 |
| suboxic | 0 | 0 | 2 | 0 | 0 |
| Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 1 | 0 |

## 濁水溪沖積扇 (789 samples, 43 wells)

Measured category: anoxic 392 (50%), mixed(oxic-anoxic) 235 (30%), oxic 73 (9%), mixed(anoxic) 67 (8%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 14 (2%), suboxic 8 (1%)

Ladder TEAP: mn 461 (58%), no3 128 (16%), fe 114 (14%), o2 78 (10%), so4 8 (1%)

Agreement (ladder process is one of the measured processes): 321 of 781 (41%); not compared: 8 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| Fe(III)/SO4 | 0 | 1 | 253 | 66 | 0 |
| O2-Fe(III)/SO4 | 16 | 2 | 102 | 21 | 0 |
| O2-Mn(IV) | 7 | 40 | 35 | 12 | 0 |
| O2 | 52 | 19 | 2 | 0 | 0 |
| Mn(IV) | 0 | 1 | 51 | 17 | 0 |
| NO3-Mn(IV) | 0 | 32 | 3 | 2 | 0 |
| NO3-Fe(III)/SO4 | 0 | 24 | 4 | 2 | 0 |
| O2-NO3-Fe(III)/SO4 | 3 | 7 | 4 | 0 | 0 |
| suboxic | 0 | 0 | 6 | 2 | 0 |
| NO3 | 0 | 2 | 1 | 0 | 0 |

## 屏東平原 (1087 samples, 91 wells)

Measured category: mixed(oxic-anoxic) 546 (50%), oxic 409 (38%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 56 (5%), anoxic 51 (5%), mixed(anoxic) 24 (2%), suboxic 1 (0%)

Ladder TEAP: o2 594 (55%), mn 281 (26%), no3 189 (17%), fe 23 (2%)

Agreement (ladder process is one of the measured processes): 700 of 1086 (64%); not compared: 1 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| O2 | 347 | 56 | 6 | 0 | 0 |
| O2-Fe(III)/SO4 | 115 | 13 | 190 | 16 | 0 |
| O2-Mn(IV) | 109 | 71 | 28 | 1 | 0 |
| O2-NO3-Fe(III)/SO4 | 23 | 26 | 7 | 0 | 0 |
| Fe(III)/SO4 | 0 | 0 | 35 | 6 | 0 |
| NO3-Mn(IV) | 0 | 19 | 1 | 0 | 0 |
| Mn(IV) | 0 | 0 | 6 | 0 | 0 |
| NO3-Fe(III)/SO4 | 0 | 1 | 3 | 0 | 0 |
| NO3 | 0 | 3 | 1 | 0 | 0 |
| O2-Fe(III)/SO4 or CH4gen | 0 | 0 | 3 | 0 | 0 |
| suboxic | 0 | 0 | 1 | 0 | 0 |

## 蘭陽平原 (300 samples, 21 wells)

Measured category: oxic 140 (47%), anoxic 92 (31%), mixed(oxic-anoxic) 54 (18%), suboxic 11 (4%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 3 (1%)

Ladder TEAP: o2 137 (46%), mn 95 (32%), fe 48 (16%), no3 11 (4%), ch4 8 (3%), so4 1 (0%)

Agreement (ladder process is one of the measured processes): 195 of 289 (67%); not compared: 11 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| O2 | 131 | 5 | 4 | 0 | 0 |
| Fe(III)/SO4 | 0 | 0 | 50 | 21 | 3 |
| O2-Fe(III)/SO4 | 4 | 0 | 28 | 11 | 2 |
| Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 12 | 1 |
| suboxic | 0 | 2 | 9 | 0 | 0 |
| O2-Fe(III)/SO4 or CH4gen | 0 | 0 | 1 | 4 | 2 |
| NO3 | 0 | 3 | 0 | 0 | 0 |
| O2-NO3-Fe(III)/SO4 | 2 | 0 | 0 | 1 | 0 |
| Mn(IV) | 0 | 1 | 1 | 0 | 0 |
| O2-Mn(IV) | 0 | 0 | 2 | 0 | 0 |

## Notes

- Ladder processes are mapped as o2→O2, no3→NO3, mn→Mn(IV), fe and so4→Fe(III)/SO4, ch4→CH4gen, because the measured framework cannot separate Fe(III) and sulfate reduction without sulfide.
- 'suboxic' means different things: in McMahon & Chapelle (2008) low O2 and low nitrate with Mn and Fe below threshold (process not defined); in the ladder, nitrate reduction. Measured suboxic samples are not scored.
- Values below detection enter the ladder as 0.
