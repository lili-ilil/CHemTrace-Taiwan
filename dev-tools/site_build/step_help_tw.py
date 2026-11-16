"""Step 2b (part 2a): field help texts and source notes that still described Switzerland.

Taiwan values are used only where a source was found; otherwise the Swiss example is removed or labelled as Swiss.
  leaded petrol   phased out in Taiwan from 1983, supply discontinued in 2000 (Yao et al. 2015, Int. J. Environ. Res.
                  Public Health 12:4602, doi 10.3390/ijerph120504602, Introduction)
  climate normal  CWA uses 1991–2020 normals (CWA, Taiwan climate monitoring report 2025, Tables 3 and 4)
  reservoirs      MOENV reservoir water quality (WQX_P_03) has total phosphorus, chlorophyll a, the Carlson index and
                  dissolved oxygen by sampling depth (download of 15 Nov 2026)
  soil drainage   MOA detailed soil map (2016), drainage class, already in data/grid
Runs before step_2b, so the Chinese strings (zh_help.py) match the new English.
"""
JS = "assets/js/app.js"

PATCHES = [
    (JS, 'help:"Average daily traffic. Swiss counts: ASTRA and cantonal traffic counting stations."', 'help:"Average daily traffic, from road traffic counts."'),
    (JS, 'src:"ASTRA traffic counts"', 'src:"Road traffic counts"'),
    (JS, 'help:"Leaded petrol was banned in Switzerland in 2000; roadside soils still hold its lead."',
         'help:"Taiwan phased out leaded petrol from 1983 and stopped supplying it in 2000 (Yao et al. 2015); roadside soils can still hold its lead."'),
    (JS, 'help:"Use the 1991–2020 normal of the nearest MeteoSwiss station."', 'help:"Use the 1991–2020 normal of the nearest Central Weather Administration station."'),
    (JS, 'help:"Swiss Plateau 1.4–2.5 m/s, inner Alpine valleys 0.9–1.6 m/s (Graf et al. 2019)."', 'help:"Annual mean wind speed at the nearest Central Weather Administration station."'),
    (JS, 'help:"Shapes the deposition footprint on the spread map. Swiss Plateau: southwest to west winds, and the Bise from the northeast; valleys follow the valley."',
         'help:"Shapes the deposition footprint on the spread map. Use the prevailing wind direction at the nearest Central Weather Administration station."'),
    (JS, 'Empty: 100% if the land use is forest, otherwise 30% (Swiss average)."', 'Empty: 100% if the land use is forest, otherwise 30% (Swiss average, not checked for Taiwan)."'),
    (JS, 'help:"Empty uses the default for the land use: 0.7 t/ha/yr on arable land (measured, Frienisberg BE)."',
         'help:"Empty uses the default for the land use: 0.7 t/ha/yr on arable land (measured at Frienisberg, Switzerland; no Taiwan value found yet)."'),
    (JS, 'help:"Lake Zurich 1.2, Lake Neuchâtel 8.2, Lake Geneva 11.4, Lake Lugano north basin 11.9. Enter 0 if no lake lies downstream."',
         'help:"Water residence time of the lake or reservoir downstream. Enter 0 if no lake lies downstream."'),
    (JS, 'src:"Canton of Schwyz (Lake Zurich); lake data summaries"', 'src:"Reservoir storage and inflow records"'),
    (JS, 'src:"Cantonal lake monitoring (phosphorus, chlorophyll)"', 'src:"MOENV reservoir water quality (WQX_P_03): total phosphorus, chlorophyll a, Carlson index"'),
    (JS, 'src:"Cantonal lake monitoring"', 'src:"MOENV reservoir water quality (WQX_P_03): dissolved oxygen by sampling depth"'),
    (JS, 'src:"Site observation; BLW soil suitability map (waterlogging)"', 'src:"Site observation; MOA detailed soil map (drainage class)"'),
    (JS, 'help:"Empty: from elevation (Hydrological Atlas of Switzerland, shortened for today\'s climate). Above about 3200 m snow stays all year and the metal is stored in firn."',
         'help:"Empty: from elevation, with the Swiss relation (Hydrological Atlas of Switzerland, shortened for today\'s climate); in Taiwan snow is limited to the high mountains. Above about 3200 m the Swiss relation keeps snow all year and stores the metal in firn."'),
    (JS, 'help:"Swiss glaciers covered 861 km² in 2023 (GLAMOS)."', 'help:"Swiss glaciers covered 861 km² in 2023 (GLAMOS). Taiwan has no glaciers; this release type is kept from the Swiss version."'),
]
