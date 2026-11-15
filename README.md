# CHemTrace Taiwan

Screening tool for arsenic, mercury and lead pathways through soil, air, groundwater, rivers and lakes in Taiwan, with an English and a Traditional Chinese interface (`site/index.html`, `site/index.zh.html`). In development (version 0.1.0). It is the Taiwan version of [CHemTrace](https://lili-ilil.github.io/CHemTrace/).

台灣版 CHemTrace：篩選評估砷、汞、鉛在土壤、空氣、地下水、河川與湖泊之間的傳輸，介面有英文和繁體中文。開發中。

## Folders

| Folder | Content |
|---|---|
| `site/` | The website (published with GitHub Pages). Generated, do not edit by hand. |
| `base/` | The Swiss version 0.13.0, the unchanged starting point. |
| `dev-tools/site_build/` | Builds `site/` from `base/docs`: `python dev-tools/site_build/build_site.py`. Every Taiwan change is a patch in a step file. |
| `dev-tools/tests/` | Browser tests (Node.js + Playwright), e.g. `t_self.js` runs the built-in self-test (20 checks). |
| `tools/` | Data download and processing scripts (MOENV, WRA, GSMMA) and the validation prototypes. |
| `data/processed/` | Processed open data and model results; raw downloads are not in the repository. |
| `data/literature/` | Values transcribed from journal articles, each row with its source and page. |
| `00_…` to `12_…` | Project notes in Traditional Chinese: data feasibility, validation, model changes, terms, presets. |

Changes: `CHANGELOG-台灣版.md`. Swiss history: `base/CHANGELOG-瑞士版.md`.

## Data and sources

Taiwan open government data are used under the Open Government Data License, version 1.0 (OGDL-Taiwan-1.0), with attribution: Ministry of Environment (MOENV), Water Resources Agency (WRA), Geological Survey and Mining Management Agency (GSMMA), National Land Surveying and Mapping Center (NLSC, base maps). Every number in the site cites its source; values without a Taiwan source are marked ASSUMED. Journal articles are not included, only reading notes and transcribed values with page numbers.

## Run locally

```
cd site
python -m http.server 8765
```

Then open http://localhost:8765/index.html (or index.zh.html).

Contact: litail@ethz.ch
