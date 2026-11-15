# Chianan preset: air, river and soil summaries

Made by tools/process_chianan_extra.py; rules in the script header.

## Air quality (MOENV AQX_P_08, monthly values)

| station | PM10 2023 / 2024 / 2025 (µg/m³) | PM2.5 2023 / 2024 / 2025 (µg/m³) |
|---|---|---|
| 嘉義 | 39.3 / incomplete / 31.7 | 18.6 / incomplete / 15.3 |
| 新港 | 41.9 / incomplete / 34.9 | 19.2 / incomplete / 15.4 |
| 新營 | 38.4 / incomplete / 34.4 | 16.9 / incomplete / 15.4 |
| 朴子 | 37.7 / incomplete / 34.3 | 17.7 / incomplete / 15.1 |

PM10: median over 4 stations of the means of the complete years 2023-2025 = **36.2 µg/m³**

PM2.5: median over 4 stations of the means of the complete years 2023-2025 = **16.7 µg/m³**

## River water quality (MOENV WQX_P_01), 2021-2025, 嘉義縣, 嘉義市, 臺南市

Stations per basin: (no basin) 25, 曾文溪流域 11, 朴子溪流域 9, 急水溪流域 7, 八掌溪流域 6, 鹽水溪流域 6, 二仁溪流域 5, 北港溪流域 1

| item | samples measured | below detection | detection limits seen (mg/L) | median of station medians | stations |
|---|---|---|---|---|---|
| SS | 2454 | 0% | 1.0 | 19.6 mg/L | 69 |
| pH | 2454 | 0% | – | 8.06  | 69 |
| As | 751 | 0% | 0.0003 | 6.75 µg/L | 45 |
| Hg | 709 | 96% | 0.0003 | – | 31 |
| Pb | 751 | 75% | 0.003 | 5.5 µg/L (not used: mostly below detection) | 42 |

Metals are MOENV river monitoring values (total, not filtered), so as a 'dissolved background' they are an upper bound.

## Soil (MOA detailed soil map, 2016-10-13), 嘉義縣, 嘉義市, 臺南市, slope class 1 (0-5 %)

Mapped area 729 km². Shares of the area with data:

- topsoil pH class: 7.9-8.4 24%, 6.1-6.5 20%, 6.6-7.3 18%, 7.4-7.8 16%, 5.6-6.0 16%, 5.1-5.5 4%, 8.5-9.0 1%, < 4.5 1%, 4.6-5.0 0%
- drainage class: good 91%, imperfect 6%, poor 3%
- area-weighted median topsoil pH class: 6.6-7.3

