"""Explore mode, Taiwan content (part 1).

- The Swiss notes under each compartment (field `swiss`, shown with a Swiss flag) are removed. Where a sourced Taiwan
  statement exists it is shown instead (field `tw`, with a TW tag). Sources: Taiwan standards (05 file, section 1.3),
  the arsenic potential areas in the annex of the Groundwater Pollution Control Standards (05 file, [S35]),
  Chen & Liu (2007) TAO 18:975 (abstract and p. 990), Liu et al. (2006) J. Environ. Qual. 35:68 (p. 68), MOENV open data 6351.
- Sentences that named Swiss places, programmes or limits are made general or point to Taiwan.
- Still to do (part 2): the schematic scene is an Alpine catchment with a glacier; Taiwan needs its own scene, and the
  glacier compartment should go.
"""
import re

JS, IDX, CSS = "assets/js/app.js", "index.html", "assets/css/styles.css"

TW_NOTES = {
    "Elevated groundwater arsenic occurs almost only in the Alps and south of the Alps, mainly in crystalline fractured aquifers (FOEN, NAQUA).":
        "In Taiwan, high groundwater arsenic is geogenic but comes from young coastal-plain sediments, not from crystalline rock. The Groundwater Pollution Control Standards marked four arsenic potential areas: the Chianan plain, the Choushui fan, the Pingtung plain and the Lanyang plain.",
    "Swiss drinking-water maximum: 10 µg/L (TBDV).":
        "Taiwan drinking-water standard: 0.01 mg/L. Arsenic in deep well water was linked to blackfoot disease on the southwestern coast (Liu et al. 2006, J. Environ. Qual. 35:68).",
    "Swiss drinking-water maximum: 1 µg/L (TBDV).":
        "Taiwan drinking-water standard: 0.001 mg/L. Groundwater control standard: 0.0020 mg/L (class 1), 0.020 mg/L (class 2).",
    "Swiss remediation value for Hg in garden and playground soil: 2 mg/kg (AltlV).":
        "Taiwan soil pollution control standard for Hg: 20 mg/kg, or 5 mg/kg on food-crop farmland (monitoring standard 10 and 2 mg/kg).",
    "Swiss remediation value for Pb in garden and playground soil: 1,000 mg/kg (AltlV).":
        "Taiwan soil pollution control standard for Pb: 2,000 mg/kg, or 500 mg/kg on food-crop farmland (monitoring standard 1,000 and 300 mg/kg).",
    "Contaminated sites are listed in the cantonal registers (Kataster der belasteten Standorte).":
        "MOENV publishes the listed soil and groundwater pollution sites as open data (data.gov.tw 6351).",
}
TW_PREFIX = {   # notes that begin with this text (they are long)
    "FOEN NAQUA: As is above the 10 µg/L drinking-water limit":
        "In the Chianan plain almost all monitoring wells exceed 0.01 mg/L, and the deeper aquifers reach about 1.2 mg/L (Chen & Liu 2007, TAO 18:975). The groundwater control standard is 0.050 mg/L for class 1 and 0.50 mg/L for class 2.",
    "FOEN NAQUA: Pb is above the 1 µg/L indicator value":
        "Taiwan groundwater control standard for Pb: 0.010 mg/L (class 1), 0.10 mg/L (class 2); drinking water 0.01 mg/L.",
    "VBBo guide value 50 mg/kg; trigger value 200 mg/kg":
        "Taiwan soil pollution control standard for Pb: 2,000 mg/kg, or 500 mg/kg on food-crop farmland (monitoring standard 1,000 and 300 mg/kg).",
}

TEXT = [   # (old, new, count)
    ("Geogenic: As-rich crystalline rock and ore in Valais, Graubünden and Ticino", "Geogenic: arsenic-rich young sediments of the coastal plains (Chianan, Choushui fan, Pingtung, Lanyang)", 1),
    ("Legacy chemical industry: Lonza Visp wastewater until the mid-1970s, spread with dredged canal sediment", "Legacy chemical industry, for example chlor-alkali plants with mercury cells", 1),
    ("At Swiss background levels, air is a minor route compared with water and food.", "At background levels, air is a minor route compared with water and food.", 1),
    ("Inhalation is now a minor route in Switzerland. It was the main route in the leaded-petrol era.", "Inhalation was the main route in the leaded-petrol era and is minor where leaded petrol has been phased out.", 1),
    ("Crystalline Alps and valley basement", "Mountain bedrock and ore veins", 1),
    ("Rare in Switzerland; one of the least soluble minerals", "One of the least soluble minerals", 1),
    ("Natural mercury in Swiss rocks is low. Weathering releases very little, so geogenic Hg is rarely a management target here.", "Weathering of most rocks releases little mercury; check the local geology for Hg-bearing ores.", 1),
    ("Negligible from rock in Switzerland.", "Usually small from rock; check the local geology.", 1),
    ("Swiss remediation value: 2 mg/kg.", "Taiwan soil control standard: 20 mg/kg (5 mg/kg on food-crop farmland).", 1),
    ("Excavation and disposal of hotspots (the Visp approach)", "Excavation and disposal of hotspots", 1),
    ('"SwissPRTR releases"', '"facility emission reports"', 2),
    ("Today's Swiss emissions are small compared with the legacy. Mercury thermometers, batteries and most lamps are phased out.", "Today's emissions are often small compared with the legacy stored in soils and sediments.", 1),
    ('"discharge (FOEN)"', '"discharge (WRA)"', 1),
    ("In oxic Swiss gravel aquifers it is mostly below 1 µg/L; fractured crystalline aquifers in the Alps can exceed 10 µg/L.", "In Taiwan, reducing coastal-plain aquifers carry naturally high arsenic, while oxic gravel aquifers usually stay low.", 1),
    ("Drinking water is the main exposure route for inorganic arsenic. Swiss limit: 10 µg/L.", "Drinking water is the main exposure route for inorganic arsenic. Taiwan standard: 0.01 mg/L.", 1),
    ("Swiss drinking-water limit: 1 µg/L.", "Taiwan drinking-water standard: 0.001 mg/L.", 1),
    ("No NAQUA site exceeds the 10 µg/L limit. Old lead pipes and brass fittings can add Pb at the tap.", "Old lead pipes and brass fittings can add Pb at the tap.", 1),
]


def _tw(m):
    old = m.group(1)
    if old in TW_NOTES:
        return 'tw:"' + TW_NOTES[old] + '"'
    for pre, new in TW_PREFIX.items():
        if old.startswith(pre):
            return 'tw:"' + new + '"'
    return 'swiss:""'


PATCHES = [(JS, a, b, {"count": n}) for a, b, n in TEXT] + [
    # render: Taiwan note with a TW tag instead of the Swiss flag
    (JS, '${d.swiss ? `<div class="swiss"><span class="flag" aria-label="Switzerland"></span><span>${esc(d.swiss)}</span></div>` : ""}',
     '${d.tw ? `<div class="swiss tw"><span class="tw-tag" aria-label="Taiwan">TW</span><span>${esc(tr(d.tw))}</span></div>` : ""}'),
    (IDX, "Schematic profile of an Alpine catchment.", "Schematic profile of a catchment."),
    (CSS, ".swiss .flag{", ".swiss .tw-tag{font-family:var(--f-mono); font-size:10.5px; font-weight:500; letter-spacing:.06em; color:var(--surface); background:var(--ink-2); border-radius:2px; padding:2px 5px; margin-top:1px}\n.swiss .flag{"),
]


def build(F):
    """Swap the Swiss notes for Taiwan notes (or remove them); fails if a listed note is no longer in base/."""
    s = F.get(JS)
    found = set(re.findall(r'swiss:"([^"]*)"', s))
    missing = [k for k in TW_NOTES if k not in found] + [p for p in TW_PREFIX if not any(f.startswith(p) for f in found)]
    if missing:
        raise SystemExit("[step_explore] Swiss notes not found: " + "; ".join(m[:60] for m in missing))
    F.put(JS, re.sub(r'swiss:"([^"]*)"', _tw, s))
