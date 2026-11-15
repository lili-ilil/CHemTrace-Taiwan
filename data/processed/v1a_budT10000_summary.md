# V1 design A (sensitivity: budT = 10000 years): redox ladder vs measured redox process

Made 2026-11-15 11:09 UTC by tools/v1_redox.py. Ladder: redoxLadder from base/docs/assets/js/app.js (CHemTrace 0.13.0), run by tools/ladder_node.mjs.

Samples with DO, NO3-N, SO4 and TOC: 6553 (of 8698). Website defaults used for the other ladder inputs: K 0.002, grad 0.003, ne 0.2, aqFe 0.5, aqMn 0.2, budT 10000 (BASE + preset 'plateau').


## All districts (6553 samples, 482 wells)

Measured category: mixed(oxic-anoxic) 2686 (41%), oxic 1831 (28%), anoxic 1416 (22%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 273 (4%), mixed(anoxic) 262 (4%), suboxic 85 (1%)

Ladder TEAP: so4 3074 (47%), o2 2035 (31%), no3 1149 (18%), ch4 294 (4%), fe 1 (0%)

Agreement (ladder process is one of the measured processes): 4829 of 6468 (75%); not compared: 85 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| O2 | 1361 | 365 | 0 | 95 | 10 |
| O2-Fe(III)/SO4 | 276 | 36 | 0 | 1306 | 103 |
| Fe(III)/SO4 | 0 | 6 | 0 | 909 | 77 |
| O2-Mn(IV) | 268 | 276 | 0 | 355 | 10 |
| O2-NO3-Fe(III)/SO4 | 129 | 117 | 0 | 25 | 2 |
| Mn(IV) | 1 | 6 | 0 | 251 | 1 |
| NO3-Mn(IV) | 0 | 144 | 0 | 30 | 0 |
| NO3 | 0 | 128 | 0 | 14 | 1 |
| NO3-Fe(III)/SO4 | 0 | 67 | 0 | 21 | 0 |
| suboxic | 0 | 4 | 0 | 69 | 12 |
| O2-Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 0 | 56 |
| Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 0 | 22 |

## 嘉南平原 (1337 samples, 93 wells)

Measured category: mixed(oxic-anoxic) 1027 (77%), oxic 144 (11%), anoxic 113 (8%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 37 (3%), mixed(anoxic) 14 (1%), suboxic 2 (0%)

Ladder TEAP: so4 853 (64%), o2 281 (21%), no3 144 (11%), ch4 59 (4%)

Agreement (ladder process is one of the measured processes): 986 of 1335 (74%); not compared: 2 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| O2-Fe(III)/SO4 | 90 | 11 | 0 | 551 | 15 |
| O2-Mn(IV) | 87 | 68 | 0 | 169 | 5 |
| O2 | 90 | 32 | 0 | 16 | 6 |
| Fe(III)/SO4 | 0 | 0 | 0 | 85 | 1 |
| O2-NO3-Fe(III)/SO4 | 14 | 20 | 0 | 3 | 0 |
| O2-Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 0 | 31 |
| Mn(IV) | 0 | 0 | 0 | 23 | 0 |
| NO3-Mn(IV) | 0 | 4 | 0 | 3 | 0 |
| NO3-Fe(III)/SO4 | 0 | 6 | 0 | 1 | 0 |
| NO3 | 0 | 3 | 0 | 0 | 0 |
| suboxic | 0 | 0 | 0 | 2 | 0 |
| Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 0 | 1 |

## 濁水溪沖積扇 (789 samples, 43 wells)

Measured category: anoxic 392 (50%), mixed(oxic-anoxic) 235 (30%), oxic 73 (9%), mixed(anoxic) 67 (8%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 14 (2%), suboxic 8 (1%)

Ladder TEAP: so4 583 (74%), no3 128 (16%), o2 78 (10%)

Agreement (ladder process is one of the measured processes): 595 of 781 (76%); not compared: 8 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| Fe(III)/SO4 | 0 | 1 | 0 | 319 | 0 |
| O2-Fe(III)/SO4 | 16 | 2 | 0 | 123 | 0 |
| O2-Mn(IV) | 7 | 40 | 0 | 47 | 0 |
| O2 | 52 | 19 | 0 | 2 | 0 |
| Mn(IV) | 0 | 1 | 0 | 68 | 0 |
| NO3-Mn(IV) | 0 | 32 | 0 | 5 | 0 |
| NO3-Fe(III)/SO4 | 0 | 24 | 0 | 6 | 0 |
| O2-NO3-Fe(III)/SO4 | 3 | 7 | 0 | 4 | 0 |
| suboxic | 0 | 0 | 0 | 8 | 0 |
| NO3 | 0 | 2 | 0 | 1 | 0 |

## 屏東平原 (1087 samples, 91 wells)

Measured category: mixed(oxic-anoxic) 546 (50%), oxic 409 (38%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 56 (5%), anoxic 51 (5%), mixed(anoxic) 24 (2%), suboxic 1 (0%)

Ladder TEAP: o2 594 (55%), so4 298 (27%), no3 189 (17%), ch4 6 (1%)

Agreement (ladder process is one of the measured processes): 901 of 1086 (83%); not compared: 1 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| O2 | 347 | 56 | 0 | 6 | 0 |
| O2-Fe(III)/SO4 | 115 | 13 | 0 | 204 | 2 |
| O2-Mn(IV) | 109 | 71 | 0 | 28 | 1 |
| O2-NO3-Fe(III)/SO4 | 23 | 26 | 0 | 7 | 0 |
| Fe(III)/SO4 | 0 | 0 | 0 | 41 | 0 |
| NO3-Mn(IV) | 0 | 19 | 0 | 1 | 0 |
| Mn(IV) | 0 | 0 | 0 | 6 | 0 |
| NO3-Fe(III)/SO4 | 0 | 1 | 0 | 3 | 0 |
| NO3 | 0 | 3 | 0 | 1 | 0 |
| O2-Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 0 | 3 |
| suboxic | 0 | 0 | 0 | 1 | 0 |

## 蘭陽平原 (300 samples, 21 wells)

Measured category: oxic 140 (47%), anoxic 92 (31%), mixed(oxic-anoxic) 54 (18%), suboxic 11 (4%), mixed(oxic-anoxic), NO3 also >= 0.5 (not in Jurgens Table 2) 3 (1%)

Ladder TEAP: o2 137 (46%), so4 97 (32%), ch4 54 (18%), no3 11 (4%), fe 1 (0%)

Agreement (ladder process is one of the measured processes): 242 of 289 (84%); not compared: 11 (measured suboxic or incomplete)

| measured process \ ladder | O2 | NO3 | Mn(IV) | Fe(III)/SO4 | CH4gen |
|---|---|---|---|---|---|
| O2 | 131 | 5 | 0 | 4 | 0 |
| Fe(III)/SO4 | 0 | 0 | 0 | 47 | 27 |
| O2-Fe(III)/SO4 | 4 | 0 | 0 | 34 | 7 |
| Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 0 | 13 |
| suboxic | 0 | 2 | 0 | 9 | 0 |
| O2-Fe(III)/SO4 or CH4gen | 0 | 0 | 0 | 0 | 7 |
| NO3 | 0 | 3 | 0 | 0 | 0 |
| O2-NO3-Fe(III)/SO4 | 2 | 0 | 0 | 1 | 0 |
| Mn(IV) | 0 | 1 | 0 | 1 | 0 |
| O2-Mn(IV) | 0 | 0 | 0 | 2 | 0 |

## Notes

- Ladder processes are mapped as o2→O2, no3→NO3, mn→Mn(IV), fe and so4→Fe(III)/SO4, ch4→CH4gen, because the measured framework cannot separate Fe(III) and sulfate reduction without sulfide.
- 'suboxic' means different things: in McMahon & Chapelle (2008) low O2 and low nitrate with Mn and Fe below threshold (process not defined); in the ladder, nitrate reduction. Measured suboxic samples are not scored.
- Values below detection enter the ladder as 0.
