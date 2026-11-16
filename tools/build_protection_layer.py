#!/usr/bin/env python3
"""Drinking-water source protection zones for the site: data/grid/protection.geojson (copied to site/data/ by step_wells.py).

Usage (from the CHemTrace-TW folder; needs: pip install pyshp shapely):  python tools/build_protection_layer.py
Input: data/raw/protection/飲用水水源水質保護區及取水口一定距離.zip (MOENV GISEPA_P_13, data.gov.tw 6377, file of
2026-07-20; WGS84, EPSG:4326). 134 features: 87 protection zones (PRO_TYPE 保護區) and 47 areas within the set distance
of a drinking-water intake (PRO_TYPE 一定距離).
Output: polygons simplified with a tolerance of 0.0002 degrees (about 20 m; topology kept), coordinates rounded to
5 decimals (about 1 m). Kept attributes: name, county, basin, type, description, intake.
Use on the site: groundwater inside a protection zone is class 1 under the Groundwater Pollution Control Standards
(class 1: groundwater within drinking-water source protection zones; 05 file); the intake-distance areas are shown
on the map but do not set the class.
"""
import json, os, tempfile, zipfile
from datetime import date
from pathlib import Path
import shapefile
from shapely.geometry import shape, mapping

ROOT = Path(__file__).resolve().parent.parent
ZIP = ROOT / "data" / "raw" / "protection" / "飲用水水源水質保護區及取水口一定距離.zip"
OUT = ROOT / "data" / "grid" / "protection.geojson"
TOL = 0.0002


def rnd(c):
    if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)): return [round(c[0], 5), round(c[1], 5)]
    return [rnd(x) for x in c]


def main():
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(ZIP) as z:
        for i in z.infolist():
            name = i.filename if i.flag_bits & 0x800 else i.filename.encode("cp437").decode("big5", "replace")
            ext = "shp.xml" if name.endswith(".shp.xml") else name.rsplit(".", 1)[-1]
            (tmp / f"pz.{ext}").write_bytes(z.read(i))
    r = shapefile.Reader(str(tmp / "pz"), encoding="utf-8")
    feats, n0, n1 = [], 0, 0
    for sr in r.iterShapeRecords():
        g = shape(sr.shape.__geo_interface__)
        n0 += len(sr.shape.points)
        s = g.simplify(TOL, preserve_topology=True)
        if s.is_empty: continue
        m = mapping(s); m["coordinates"] = rnd(m["coordinates"])
        n1 += sum(len(ring) for poly in (m["coordinates"] if m["type"] == "MultiPolygon" else [m["coordinates"]]) for ring in poly)
        a = sr.record.as_dict()
        feats.append({"type": "Feature", "geometry": m, "properties": {"name": a["PRO_NAME"], "county": a["ADMIP_NAME"], "basin": a["BASIN_NAME"],
                      "type": a["PRO_TYPE"], "desc": a["PRO_PRACT"], "intake": a["GET_NAME"]}})
    doc = {"type": "FeatureCollection", "generated": date.today().isoformat(),
           "source": "MOENV 飲用水水源水質保護區及取水口一定距離 (GISEPA_P_13, data.gov.tw 6377), file of 2026-07-20, Open Government Data License 1.0; simplified 0.0002°",
           "features": feats}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{OUT}: {len(feats)} features, {n0} -> {n1} vertices, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
