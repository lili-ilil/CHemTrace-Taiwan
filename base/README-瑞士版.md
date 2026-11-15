# CHemTrace

A website that traces contaminants through Swiss landscapes: their forms, pathways, threats to people and where to trap them. Arsenic, mercury and lead are available now; more contaminants are being added. (Formerly called Swiss Metal Pathways.)

Contact: Li-Ling T., ETH Zürich, litail@ethz.ch

**What it is for.** It gives an overview of the whole system (soil, air, groundwater, rivers and lakes together) so you can form assumptions and a first plan: where to act first and what to measure. The detail belongs in site investigations and specialised models; the website exports its inputs to PHREEQC, HYDRUS-1D and MODFLOW 6 for that step.

- **Explore mode** is the interactive landscape and field guide.
- **Advanced mode** is a screening calculator with Monte Carlo uncertainty, Swiss limit values and a map of Switzerland. Clicking the map fills the inputs from national datasets.
- **Mass budget** shows where the released kilograms are after 1–100 years, with optional flood scenarios. **Sensitivity** ranks which uncertain input drives each result.
- **Spread map** shows, year by year, where soil and groundwater are above the Swiss standard, with the groundwater direction set by the user and cantonal and federal maps as support.
- **Forms by phase** compares five condition scenarios (today, waterlogged, acidified, floods, anoxic lake) and shows which chemical forms the metal takes in soil and sediment, water and air.
- **Lakes and redox:** lake trophic state and season, Hg⁰ escape and methylmercury breakdown in sunlit lake water, and an optional redox ladder that works out the soil and aquifer redox state from oxygen, nitrate, sulfate and organic carbon.
- **Air and land surface:** deposition by particle size, release height, wind and rain; a wind-shaped deposition zone on the spread map; forests and mercury leaf litter; snow, firn and mercury re-emission; sealed surfaces and road-runoff drainage; road traffic (lead) and glacier melt as release types; PM10 and PM2.5 from the FOEN maps and NABEL background values.
- **Take it further:** downloads a PHREEQC input file, a HYDRUS-1D parameter sheet, a MODFLOW 6 (FloPy) script and a JSON of the whole run, filled with the current inputs. Placeholders are marked ASSUMED.
- **Validation** (`validation.html`) compares the model with published Swiss measurements.
- **Scripting:** in the browser console, `SMP.run("Pb", {...inputs})` (also available as `CHemTrace.run`) reruns any scenario and returns results, ranges, the budget and the drivers; `SMP.exportFile("phreeqc", "Pb", {...inputs})` returns an export file as text; `SMP.depositionProfile("Pb", {...inputs})` returns deposition and air concentration with distance for a release to air.
- **Code checks:** `SMP.selfTest()` in the browser console runs 18 automated checks (mass conservation including snow, forests, roads and glaciers; Kd relations; plume and deposition behaviour; lake Hg⁰ escape; redox ladder; reproducibility). Run it after every change.

Current version: 0.13.0 (3 November 2026). The version history is in `CHANGELOG.md` (not shown on the website); update `APP_VERSION` in `assets/js/app.js`, the footers and `CHANGELOG.md` together.

The site is fully static: HTML, CSS, JavaScript and two data files. It needs no build step and no server code.

## Folder layout

```
SwissMetalModel/
  README.md                    this file (not part of the website)
  tools/process_data.py        rebuilds docs/data/grid.* from the files in data/
  data/                        raw downloads (not uploaded)
  docs/                        the website: only this folder is published
    index.html                 page markup
    manual.html                user manual with examples
    validation.html            benchmark checks against published Swiss data
    assumptions.html           every default and assumption, with its basis and review priority
    assets/css/styles.css      all styles (light and dark theme)
    assets/js/app.js           model engine, Explore mode, Advanced mode, site lookup
    assets/vendor/leaflet/     Leaflet 1.9.4 map library (BSD-2 licence)
    assets/fonts/              Archivo and IBM Plex Mono, self-hosted (SIL OFL)
    data/grid.json             grid description (LV95, 1 km, 353 × 225 cells)
    data/grid.bin              17 data layers, binary
    .nojekyll                  tells GitHub Pages to serve files as they are
```

## Run it on your computer

The data files are loaded with `fetch`, so open the page through a small web server, not by double-clicking `index.html`.

```
cd docs
python -m http.server 8000
```

Then open http://localhost:8000 in a browser.

## Put it online

Publish only the `docs` folder. Everything the website needs is in it; this README, `tools` and `data` stay off the website.

- **GitHub Pages from `/docs`:** upload `docs`, `tools` and `README.md` to a repository, then open **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/docs`, and save. On the free GitHub plan the repository must be public, so `README.md` and `tools` are visible on github.com; a private repository needs a paid plan.
- **Two repositories (free):** keep `README.md`, `tools` and notes in a private repository, and upload only the contents of `docs` to a public repository published from `main`, folder `/ (root)`.
- **Cloudflare Pages (free):** connect Cloudflare Pages to a private repository, leave the build command empty and set the build output directory to `docs`.

The site address depends on the host and repository name, for example `https://<your-user>.github.io/<repository>/`. For an ethz.ch address, ask ETH IT Services or your department IT for static web hosting and upload the contents of `docs`.

## Live services used in the browser

- swisstopo map tiles: `wmts.geo.admin.ch`, layer `ch.swisstopo.pixelkarte-grau`
- swisstopo elevation service: `api3.geo.admin.ch/rest/services/height`
- swisstopo profile service (terrain for the spread map): `api3.geo.admin.ch/rest/services/profile.json`
- swisstopo river network VECTOR25 (identify service): `api3.geo.admin.ch/rest/services/api/MapServer/identify`
- FOEN layers on `wmts.geo.admin.ch`: hydrogeological map 1:100,000 and tracer tests
- Cantonal groundwater protection zones via geodienste.ch WMS (`planerischer_gewaesserschutz_v1_2_0`); coverage and terms of use vary by canton
  - To stay within the geodienste.ch fair-use rules (10 WMS requests a minute, at most 360,000 pixels per image; web applications with up to about 10,000 users a day count as fair use), the page requests one image per map view, only while the layer is switched on and after panning stops, and at most 9 a minute. If you expect more traffic, contact geodienste@kgk-cgc.ch before going live.

The federal services are free. Keep the "© swisstopo" and FOEN attributions visible, and check the geodienste.ch terms for the cantons you show.

## Data in `data/grid.bin`

| Layer | Source | Notes |
|---|---|---|
| precip, temp | MeteoSwiss spatial climate normals 1991–2020 | Source: MeteoSwiss |
| ph, clay | KOBO soil property maps, 0–30 cm, 2022 | CC BY 4.0, averaged to 1 km |
| soc | KOBO soil carbon stock 0–120 cm, 2022 | CC BY 4.0. Topsoil organic carbon ≈ stock ÷ 60 (assumes 60% of the stock in 0–30 cm and a bulk density of 1.2 t/m³) |
| atl_As, atl_Pb, atl_Hg, atl_Sb, atl_Fe, atl_Ca | FOEN/Agroscope Geochemical soil atlas of Switzerland | Percentile classes 1–8. As, Pb and Hg are converted to mg/kg with the published percentiles (Agroscope). The Fe class sets an assumed oxalate-Fe |
| hydro, rock | swisstopo/FOEN Hydrogeological map 1:500,000 (GK500 V1.3) | Aquifer class and rock type, rasterised at cell centres |
| lu4, lu_set | BFS Swiss land-use statistics (current state) | Majority land-use class per km² and settlement share |
| pm10, pm25 | FOEN annual mean maps of PM10 and PM2.5 (100 m, 2023–2025) | Mean of the three years, averaged to 1 km. Downloaded by `process_data.py pm` from data.geo.admin.ch |

All layers are on the LV95 (EPSG:2056) 1 km grid of the MeteoSwiss data. They give regional estimates, not values for a specific parcel.

## Rebuild the data

On a computer with Python 3 and `pip install numpy rasterio pyproj shapely pyogrio`, keep the downloaded files in `data` as they are now. From the `SwissMetalModel` folder, run:

```
python tools/process_data.py all
```

On the first run it extracts what it needs into `SwissMetalModel/work` (about 1.3 GB; you can delete that folder afterwards). It then writes `docs/data/grid.bin` and `docs/data/grid.json`.

## Licences and credits

- Model and site code: © 2026 Li-Ling T. ETH Zürich (litail@ethz.ch). No licence has been chosen yet.
- Data: see the table above. Credit each source as stated by its provider.
- Leaflet: BSD-2-Clause. Fonts: SIL Open Font License (licence files in `assets/fonts`).

The results are screening-level estimates from documented equations. They do not replace a site investigation, and limit values should be checked against the current text on fedlex.admin.ch.
