"""Sources section of index.html: Taiwan regulations, data and literature instead of the Swiss list.

International method references that the model still uses (NJDEP, Allison & Allison, EFSA, WHO) are kept from the
original list; Swiss sources are dropped. Links are the ones checked in the 05 file ([S27]-[S41]) and in this project.
"""
import re

IDX = "index.html"

TW = r'''    <h3 class="srcs-h">Taiwan regulations</h3>
    <ul class="srcs">
      <li><a href="https://law.moj.gov.tw/LawClass/LawAll.aspx?PCODE=O0040019" target="_blank" rel="noopener">飲用水水質標準 Drinking Water Quality Standards (amended 25 Nov 2024)</a></li>
      <li><a href="https://oaout.moenv.gov.tw/law/LawContent.aspx?id=FL015529" target="_blank" rel="noopener">地下水污染管制標準 Groundwater Pollution Control Standards (amended 23 Dec 2025)</a></li>
      <li><a href="https://www.epb.taichung.gov.tw/media/354279/地下水污染管制標準修正總說明.pdf" target="_blank" rel="noopener">地下水污染管制標準修正總說明: arsenic potential areas (2013 annex)</a></li>
      <li><a href="https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=O0110013" target="_blank" rel="noopener">地下水污染監測標準 Groundwater Pollution Monitoring Standards</a></li>
      <li><a href="https://law.moj.gov.tw/LawClass/LawAll.aspx?PCODE=O0110005" target="_blank" rel="noopener">土壤污染管制標準 Soil Pollution Control Standards (2011)</a></li>
      <li><a href="https://www.epb.taichung.gov.tw/media/520975/土壤污染監測標準.pdf" target="_blank" rel="noopener">土壤污染監測標準 Soil Pollution Monitoring Standards (2011)</a></li>
    </ul>
    <h3 class="srcs-h">Taiwan data (Open Government Data License, version 1.0)</h3>
    <ul class="srcs">
      <li><a href="https://data.gov.tw/en/datasets/6348" target="_blank" rel="noopener">MOENV: regional groundwater quality monitoring</a></li>
      <li><a href="https://data.moenv.gov.tw/dataset/detail/WQX_P_01" target="_blank" rel="noopener">MOENV: river water quality monitoring (WQX_P_01)</a></li>
      <li><a href="https://data.moenv.gov.tw/dataset/detail/AQX_P_08" target="_blank" rel="noopener">MOENV: air quality monthly values (AQX_P_08)</a></li>
      <li><a href="https://data.gov.tw/en/datasets/6351" target="_blank" rel="noopener">MOENV: soil and groundwater pollution sites</a></li>
      <li><a href="https://data.gov.tw/en/datasets/161086" target="_blank" rel="noopener">WRA: groundwater quality of the layered observation wells</a></li>
      <li><a href="https://data.gov.tw/en/datasets/32718" target="_blank" rel="noopener">WRA: groundwater observation wells</a></li>
      <li><a href="https://data.gov.tw/en/datasets/16799" target="_blank" rel="noopener">GSMMA: hydrogeological boreholes</a></li>
      <li><a href="https://data.gov.tw/en/datasets/55747" target="_blank" rel="noopener">MOA: detailed soil map</a></li>
      <li><a href="https://maps.nlsc.gov.tw/S09SOA/pro/Wmts_ajax_main.jsp" target="_blank" rel="noopener">NLSC: map tile service (WMTS), base maps</a></li>
      <li><a href="https://data.gov.tw/license" target="_blank" rel="noopener">Open Government Data License, version 1.0</a></li>
    </ul>
    <h3 class="srcs-h">Taiwan literature</h3>
    <ul class="srcs">
      <li><a href="https://doi.org/10.3319/TAO.2007.18.5.975(TT)" target="_blank" rel="noopener">Chen &amp; Liu (2007): Arsenic in the groundwater and sediments of the Chianan coastal plain, TAO 18:975</a></li>
      <li><a href="https://doi.org/10.2134/jeq2005.0129" target="_blank" rel="noopener">Liu, Wang, Jang &amp; Lin (2006): Arsenic in groundwater of the Choushui River alluvial fan, J. Environ. Qual. 35:68</a></li>
      <li><a href="https://doi.org/10.1017/S0033822200031027" target="_blank" rel="noopener">Liu (1995): Groundwater flow and recharge in western Taiwan from radiocarbon and tritium, Radiocarbon 37:531</a></li>
      <li><a href="https://doi.org/10.1016/j.jhydrol.2019.123975" target="_blank" rel="noopener">Liu &amp; Wu (2019): Arsenic in groundwater of the Lanyang plain, J. Hydrol. 577:123975</a></li>
      <li><a href="https://doi.org/10.1007/s10040-007-0209-6" target="_blank" rel="noopener">Lu et al. (2008): Hydrogeology of the Chianan plain, Hydrogeol. J. 16:139</a></li>
    </ul>
    <h3 class="srcs-h">Methods and health references</h3>
    <ul class="srcs">
      <li><a href="https://pubs.usgs.gov/of/2009/1004/" target="_blank" rel="noopener">Jurgens, McMahon, Chapelle &amp; Eberts (2009): redox assignment workbook, USGS Open-File Report 2009-1004</a></li>
'''

NOTE = '''    <p class="note">Some comparison values in the results (marked “Measured”) still come from Swiss studies used by the original CHemTrace; they are being replaced with Taiwan measurements.</p>
'''

KEEP = ("NJDEP", "Allison", "EFSA", "WHO")


def build(F):
    s = F.get(IDX)
    m = re.search(r'(<section class="sec" id="sources">\s*<div class="sec-head"><h2>Sources</h2></div>\n)\s*<ul class="srcs">\n(.*?)\n\s*</ul>', s, flags=re.S)
    if not m:
        raise SystemExit("[step_sources] Sources list not found in index.html")
    items = [li for li in m.group(2).split("\n") if li.strip().startswith("<li>")]
    keep = [li for li in items if any(re.search(r">\s*" + k, li) for k in KEEP)]
    if len(keep) < 4:
        raise SystemExit(f"[step_sources] expected the NJDEP, Allison, EFSA and WHO items, found {len(keep)}")
    new = m.group(1) + TW + "\n".join(keep) + "\n    </ul>\n" + NOTE.rstrip("\n")
    F.put(IDX, s[:m.start()] + new + s[m.end():])


PATCHES = [
    ("assets/css/styles.css", ".leaflet-container{font-family:var(--f-body); background:var(--chip)}",
     ".leaflet-container{font-family:var(--f-body); background:var(--chip)}\n.srcs-h{font-size:13px; font-family:var(--f-mono); font-weight:500; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-3); margin:18px 0 6px}"),
]
