# V1 design B (嘉南平原): redox ladder with independent inputs vs measured classes by layer

Made 2026-11-15 11:56 UTC by tools/v1_design_b.py; ladder from base/ app.js 0.13.0.

## Inputs

| input | value | source | status |
|---|---|---|---|
| recharge O2 | 8.00 mg/L (saturation at 26.8 °C) | Benson & Krause, USGS OWQ Tech. Memo. 2011.03 eq. 7; temperature = layer-1 median, WRA 161086 | saturation ASSUMED |
| recharge NO3 | 0.1 mg/L NO3-N (0.443 mg/L NO3) | layer-1 median of 54 wells, WRA 161086 | data |
| recharge SO4 | 102 mg/L | layer-1 median, WRA 161086 | data |
| DOC | layer 1: 2.21 mg/L; own layer: L2 3.41, L3 3.54, L4 3.84 | TOC medians, WRA 161086 (TOC as DOC) | data |
| time scale | 10,000 and 40,000 yr | Chen & Liu (2007) p. 986 and Fig. 7 (figure reading) | literature |
| aquifer Fe | 3 and 15 g/kg | Chen & Liu (2007) Fig. 9d (figure reading; different extraction) | literature |
| aquifer Mn 0.2 g/kg, K 0.002 m/s (and ×0.01, ×0.001), gradient 0.003, porosity 0.2 | | website defaults | ASSUMED |

## Ladder result by scenario (same for layers 2, 3 and 4 unless the DOC comes from the layer itself)

| recharge O2 | DOC from | ladder TEAP over the 36 runs (3 layers × 2 time scales × 2 Fe × 3 K) |
|---|---|---|
| saturated | layer 1 | o2 36 |
| saturated | own layer | so4 22, fe 14 |
| zero | layer 1 | so4 33, fe 3 |
| zero | own layer | so4 33, fe 3 |

## Measured classes by layer (WRA 161086, O2 unknown)

- Layer 2 (246 classified records): Fe(III), O2 unknown 45%, Fe(III)/SO4 (no sulfide), O2 unknown 19%, Fe(III)-SO4, O2 unknown 9%, NO3 and Fe(III), O2 unknown 7%, CH4gen, O2 unknown 7%
- Layer 3 (223 classified records): Fe(III), O2 unknown 47%, Fe(III)/SO4 (no sulfide), O2 unknown 16%, Fe(III)-SO4, O2 unknown 8%, NO3 and Fe(III), O2 unknown 7%, SO4, O2 unknown 7%
- Layer 4 (218 classified records): Fe(III), O2 unknown 44%, Fe(III)-SO4, O2 unknown 16%, Fe(III)/SO4 (no sulfide), O2 unknown 11%, NO3 and Fe(III), O2 unknown 7%, CH4gen, O2 unknown 6%
