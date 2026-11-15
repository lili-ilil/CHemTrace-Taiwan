#!/usr/bin/env python3
"""Rasterise the MOA detailed soil map (詳測土壤圖, 2016-10-13) into the site's data grid.

Usage (from the CHemTrace-TW folder; needs: pip install pyshp rasterio numpy):
    python tools/build_soil_grid.py [path/to/詳測土壤圖20161013.shp]
Output: data/grid/grid.bin and data/grid/grid.json (copied into site/data/ by dev-tools/site_build/step_grid.py)

Grid: TWD97 / TM2 121° (EPSG:3826, as the shapefile's .prj), 250 m cells; a cell takes the polygon that covers its
centre. Layers (u8, 0 = no soil map):
    soil_ph     topsoil pH class 1-10 (code book: 1 <4.5, 2 4.6-5.0, 3 5.1-5.5, 4 5.6-6.0, 5 6.1-6.5, 6 6.6-7.3,
                7 7.4-7.8, 8 7.9-8.4, 9 8.5-9.0, 10 >9.1)
    soil_drain  drainage: 1 good, 2 imperfect, 3 poor, 4 very poor, 5 flooded (map code 23)
    soil_tex    texture of the 0-30 cm layer, map codes 1-11 (sand ... clay, 11 gravel)
    soil_lime   calcareous: 1 none, 2 calcareous, 3 lime nodules (map codes 15, 3, 13)
Codes from 詳測土壤圖屬性資料代碼說明20161013.doc. Field names in the .dbf are Big5.
"""
import json, sys
from datetime import date
from pathlib import Path
import numpy as np
import shapefile
from rasterio.features import rasterize
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parent.parent
SHP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "raw" / "soil" / "詳測土壤圖20161013" / "詳測土壤圖20161013.shp"
OUT = ROOT / "data" / "grid"
RES = 250
DRAIN = {1: 1, 2: 2, 3: 3, 4: 4, 23: 5}
LIME = {15: 1, 3: 2, 13: 3}

r = shapefile.Reader(str(SHP), encoding="big5")
names = [f[0] for f in r.fields[1:]]
ix = {k: names.index(k) for k in ("表土酸鹼性", "排水等級", "第一層質地", "石灰性")}
x0, y0, x1, y1 = r.bbox
x0, y1 = np.floor(x0 / RES) * RES, np.ceil(y1 / RES) * RES
ncols, nrows = int(np.ceil((x1 - x0) / RES)), int(np.ceil((y1 - y0) / RES))
tf = from_origin(x0, y1, RES, RES)
shapes = {k: [] for k in ("ph", "drain", "tex", "lime")}
for sr in r.iterShapeRecords():
    rec, geo = sr.record, sr.shape.__geo_interface__
    val = lambda k: int(float(rec[ix[k]] or 0))
    ph, dr, tx, li = val("表土酸鹼性"), DRAIN.get(val("排水等級"), 0), val("第一層質地"), LIME.get(val("石灰性"), 0)
    if 1 <= ph <= 10: shapes["ph"].append((geo, ph))
    if dr: shapes["drain"].append((geo, dr))
    if 1 <= tx <= 11: shapes["tex"].append((geo, tx))
    if li: shapes["lime"].append((geo, li))
OUT.mkdir(parents=True, exist_ok=True)
layers, blob = [], b""
for name, key in (("soil_ph", "ph"), ("soil_drain", "drain"), ("soil_tex", "tex"), ("soil_lime", "lime")):
    a = rasterize(shapes[key], out_shape=(nrows, ncols), transform=tf, fill=0, dtype="uint8") if shapes[key] else np.zeros((nrows, ncols), "uint8")
    layers.append({"name": name, "type": "u8", "scale": 1, "offset": 0, "nodata": 0, "byteOffset": len(blob)})
    blob += a.tobytes()
    print(name, "cells with data:", int((a > 0).sum()))
(OUT / "grid.bin").write_bytes(blob)
meta = {"crs": "EPSG:3826", "x0": float(x0), "y1": float(y1), "res": RES, "ncols": ncols, "nrows": nrows, "generated": date.today().isoformat(),
        "source": "MOA detailed soil map 詳測土壤圖 2016-10-13 (data.gov.tw 55747), Open Government Data License 1.0", "layers": layers}
(OUT / "grid.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print(ncols, nrows, len(blob), "bytes")
