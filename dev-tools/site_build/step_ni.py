"""Step 3 (part 2): nickel (Ni). Same structure as step_cd.py; runs after it.

Sourced values
  soil Kd       log10 Kd = 0.72 pH - 1.75, SEE 0.70, range 8.9-256,842 L/kg (Sauvé et al. 2000, Tables 2 and 1, p. 1128)
  suspended Kd  log10 Kd 4.3 (median; Allison & Allison 2005, Table 5, p. 3-16)
  standards     drinking water 0.02 mg/L; groundwater control 0.10 / 1.0 mg/L (class 1 / 2), monitoring half;
                soil control 200 mg/kg, monitoring 130 mg/kg (no separate farmland value)   (05 file)
  air           EU target value for Ni in PM10: 20 ng/m³ (Directive 2004/107/EC); Taiwan value not checked
  health        tolerable daily intake 13 µg/kg bw (EFSA CONTAM 2020, EFSA J. 18(11):e06268, doi 10.2903/j.efsa.2020.6268)
  molar mass    58.69 g/mol (minteq.v4.dat); PHREEQC minerals Ni(OH)2, NiCO3, NiS(alpha) (names in minteq.v4.dat)
  Chianan       river Ni: MOENV WQX_P_01 2021-2025, 467 of 719 samples below 0.005 mg/L -> background 0;
                groundwater Ni: MOENV WQX_P_02, 94 wells 2014-2025, 1,720 of 1,809 samples below 0.005 mg/L -> 0
                (WRA 161086 has no Ni column); soil background unknown -> 0 (ASSUMED)
Assumptions as for Cd (sulfide +0.5 log Kd; forms and form rules following lead; indicative Explore weights set between
Cd and Pb, since the median soil Kd of Ni (2,333 L/kg) lies between Cd (390) and Pb (102,410), Sauvé 2000 Table 1).
"""
import re
from step_cd import J, entry_js

JS, IDX, CSS = "assets/js/app.js", "index.html", "assets/css/styles.css"

METAL = {
    "name": ("Nickel", "鎳"), "site": ("Plating site", "電鍍場址"),
    "sig": ("A metal of plating and stainless steel. Ni²⁺ binds to oxides and organic matter more weakly than lead but more strongly than cadmium; it becomes mobile in acidic soils and aquifers.",
            "電鍍和不鏽鋼使用的金屬。Ni²⁺ 與氧化物和有機質的結合比鉛弱、比鎘強；在酸性土壤和含水層中會變得容易移動。"),
    "forms": [("Ni²⁺ sorbed to oxides, clay and humus", "吸附在氧化物、黏土和腐植質上的 Ni²⁺"), ("Dissolved Ni²⁺ and organic complexes", "溶解態 Ni²⁺ 和有機錯合物"),
              ("Nickel sulfide NiS (reduced conditions)", "硫化鎳 NiS（還原條件）"), ("Ni in serpentine rock and its soils", "蛇紋岩及其土壤中的鎳")],
    "sources": [("Electroplating and metal-finishing wastewater", "電鍍和金屬表面處理廢水"), ("Stainless steel and alloy industry", "不鏽鋼和合金工業"),
                ("Serpentine rock, which weathers to Ni-rich soils", "蛇紋岩風化形成富鎳土壤"), ("Fuel oil combustion and waste incineration", "燃料油燃燒和廢棄物焚化")],
    "health": ("med", "Nickel is a common skin allergen. Long-term intake from food and water is compared with a tolerable daily intake of 13 µg/kg body weight (EFSA 2020); some inhaled nickel compounds cause lung cancer.",
               "鎳是常見的皮膚過敏原。由食物和水長期攝入的量，以每日容許攝入量 13 µg/kg 體重比較（EFSA 2020）；部分吸入的鎳化合物會導致肺癌。"),
    "lever": ("Treat plating wastewater at the source, keep it out of irrigation channels, and keep soil pH near neutral.",
              "在源頭處理電鍍廢水，不讓它進入灌溉渠道，並讓土壤 pH 維持在接近中性。"),
}
TW_SOIL = ("Taiwan soil pollution control standard for Ni: 200 mg/kg (monitoring standard 130 mg/kg); no separate value for farmland.",
           "台灣土壤污染管制標準（鎳）：200 mg/kg（監測標準 130 mg/kg）；農地沒有另訂數值。")
TW_GW = ("Taiwan drinking-water standard for Ni: 0.02 mg/L. Groundwater control standard: 0.10 mg/L (class 1), 1.0 mg/L (class 2).",
         "台灣飲用水水質標準（鎳）：0.02 mg/L。地下水污染管制標準：0.10 mg/L（第一類）、1.0 mg/L（第二類）。")
TW_SITE = ("MOENV publishes the listed soil and groundwater pollution sites as open data (data.gov.tw 6351).",
           "環境部以開放資料公布列管的土壤及地下水污染場址（data.gov.tw 6351）。")

def E(forms, what, risk, trap, inputs, **kw):
    d = {"forms": forms, "what": what, "risk": risk, "trap": trap, "inputs": inputs}; d.update(kw); return d

COMP = {
 "air": (3, E([(("Ni on fine particles", "細顆粒上的鎳"), ("Oil combustion, smelting, incineration", "燃油、冶煉、焚化"))],
              ("Nickel travels on fine particles and returns with rain and dry deposition near its sources.", "鎳附著在細顆粒上傳輸，隨降雨和乾沉降回到污染源附近的地面。"),
              ("low", "Inhaled nickel compounds matter in workplaces; at background levels air is a minor route.", "吸入的鎳化合物主要在職業場所才重要；背景濃度下空氣是次要途徑。"),
              [("Filters at the stack", "煙囪加裝集塵設備")], [("emission rate", "排放量"), ("particle size", "粒徑"), ("rain intensity", "降雨強度")])),
 "glacier": (2, E([(("Ni on deposited dust", "沉降粉塵上的鎳"), ("Stored in snow and ice", "儲存在雪和冰中"))],
              ("Snow and ice store deposited nickel with dust and release it during melt. Taiwan has no glaciers; this compartment belongs to the original Alpine scene.", "雪和冰會連同粉塵儲存沉降的鎳，融化時釋出。台灣沒有冰河，這個介質屬於原本的阿爾卑斯山剖面。"),
              ("low", "No direct exposure.", "沒有直接暴露。"), [("Reservoirs trap glacial sediment", "水庫攔截冰河沉積物")], [("melt rate", "融化速率")])),
 "bedrock": (2, E([(("Ni in serpentine and ultramafic rock", "蛇紋岩和超基性岩中的鎳"), ("Natural, can be high", "天然，可能很高")), (("Ni in sulfide ores", "硫化礦中的鎳"), ("Geogenic", "地質成因"))],
              ("Serpentine and other ultramafic rocks are naturally rich in nickel and chromium; their soils and streams can carry high natural levels.", "蛇紋岩等超基性岩天然富含鎳和鉻，由它們形成的土壤和溪流可能有很高的天然濃度。"),
              ("low", "Natural background can exceed soil standards near serpentine; check before blaming a source.", "蛇紋岩附近的天然背景值可能超過土壤標準；判定污染源之前要先確認。"),
              [("Map the geology before setting background values", "設定背景值前先查地質")], [("rock type", "岩性"), ("weathering rate", "風化速率")])),
 "forest": (3, E([(("Ni²⁺ on oxides and humus", "氧化物和腐植質上的 Ni²⁺"), ("Natural and deposited", "天然和沉降")), (("Dissolved Ni in acidic soil water", "酸性土壤水中的溶解態鎳"), ("Mobile at low pH", "低 pH 時移動性高"))],
              ("In acidic forest soils nickel is partly mobile and leaches slowly to streams and groundwater.", "在酸性森林土壤中，鎳有一部分可移動，會慢慢淋溶到溪流和地下水。"),
              ("low", "Little direct exposure.", "直接暴露很少。"), [("Avoid further acidification", "避免土壤進一步酸化")], [("soil pH", "土壤 pH"), ("organic matter", "有機質")])),
 "farm": (2, E([(("Ni²⁺ on oxides, clay and humus", "氧化物、黏土和腐植質上的 Ni²⁺"), ("Main reservoir in topsoil", "表土中的主要儲存形式")), (("Dissolved Ni²⁺", "溶解態 Ni²⁺"), ("Taken up by crops at low pH", "低 pH 時被作物吸收"))],
              ("Nickel reaches farmland with polluted irrigation water, sludge and dust; crops take up more of it as soil pH falls.", "鎳隨受污染的灌溉水、污泥和粉塵進入農地；土壤 pH 越低，作物吸收越多。"),
              ("med", "Crops from polluted fields add to dietary intake.", "污染農田的作物會增加飲食攝入量。"),
              [("Lime acidic soils", "對酸性土壤施用石灰"), ("Keep polluted water out of irrigation channels", "不讓污染水進入灌溉渠道"), ("Remove or replace heavily polluted topsoil", "移除或更換嚴重污染的表土")],
              [("soil pH", "土壤 pH"), ("irrigation water quality", "灌溉水質"), ("crop type", "作物種類")], tw=TW_SOIL,
              sc={"acidic": (1, "Acidic soil: more Ni in solution and in crops.", "酸性土壤：溶液和作物中的鎳增加。")})),
 "town": (3, E([(("Ni in plating and metal-finishing waste", "電鍍和金屬表面處理廢棄物中的鎳"), ("Industrial", "工業"))],
              ("Plating and metal-finishing shops are the main local sources; wastewater carries nickel to sewers and channels.", "電鍍和金屬表面處理工廠是主要的在地污染源；廢水把鎳帶到下水道和渠道。"),
              ("med", "Local exposure near plating shops and along polluted channels.", "電鍍廠附近和受污染渠道沿線的局部暴露。"),
              [("Treat plating wastewater at the source", "在源頭處理電鍍廢水")], [("industrial discharges", "工業排放")])),
 "site": (3, E([(("Ni in plating sludge and residues", "電鍍污泥和殘渣中的鎳"), ("Industrial waste", "工業廢棄物")), (("Dissolved Ni in seepage", "入滲水中的溶解態鎳"), ("Mobile under acidic conditions", "酸性條件下移動性高"))],
              ("At plating sites nickel usually occurs with chromium, copper and zinc; acidic seepage carries it to groundwater.", "電鍍場址的鎳通常與鉻、銅、鋅一起出現；酸性入滲水會把它帶到地下水。"),
              ("high", "Groundwater below plating sites can exceed the standards.", "電鍍場址下方的地下水可能超過標準。"),
              [("Excavate or contain hot spots", "開挖或圍封熱點"), ("Monitor groundwater downgradient", "監測下游地下水")], [("source mass", "污染源質量"), ("soil pH", "土壤 pH")], tw=TW_SITE)),
 "people": (0, E([(("Dietary Ni", "飲食中的鎳"), ("Grains, legumes, nuts, cocoa", "穀物、豆類、堅果、可可")), (("Ni in drinking water", "飲用水中的鎳"), ("Taps, fittings, polluted wells", "水龍頭、管件、受污染的井"))],
              ("Food is the main source of nickel; drinking water adds to it near polluted wells.", "食物是鎳的主要來源；在受污染的井附近，飲用水會增加攝入量。"),
              ("med", "Skin allergy is the most common effect; long-term intake is compared with the EFSA tolerable daily intake.", "最常見的影響是皮膚過敏；長期攝入量以 EFSA 的每日容許攝入量比較。"),
              [("Test wells near plating sites", "檢測電鍍場址附近的井")], [("drinking water", "飲用水"), ("diet", "飲食"), ("body weight", "體重")], tw=TW_GW)),
 "wwtp": (2, E([(("Ni in sludge", "污泥中的鎳"), ("Part of the incoming Ni", "部分進流的鎳")), (("Dissolved Ni in effluent", "放流水中的溶解態鎳"), ("A large share passes", "相當比例會通過"))],
              ("Treatment plants remove only part of the nickel; much of the dissolved share passes to the river.", "污水廠只能去除部分的鎳；溶解態的鎳有很多會流到河川。"),
              ("low", "Mainly a question of industrial inputs.", "主要是工業排入的問題。"), [("Control industrial inputs to sewers", "管制工業排入下水道")], [("inflow load", "進流負荷")])),
 "river": (4, E([(("Dissolved Ni²⁺ and complexes", "溶解態 Ni²⁺ 和錯合物"), ("Main share", "主要部分")), (("Ni on suspended particles", "懸浮顆粒上的鎳"), ("Rises with suspended sediment", "隨懸浮泥砂增加"))],
              ("In rivers nickel is mostly dissolved; particle-bound nickel moves with floods.", "在河川中鎳大多為溶解態；顆粒態的鎳隨洪水移動。"),
              ("med", "Irrigation from polluted channels spreads nickel to fields.", "從受污染的渠道取水灌溉會把鎳帶到農田。"),
              [("Treat discharges upstream of irrigation intakes", "在灌溉取水口上游處理排放水")], [("discharge", "流量"), ("suspended sediment", "懸浮泥砂")])),
 "lake": (3, E([(("Dissolved Ni", "溶解態鎳"), ("Oxic water", "好氧水體")), (("Ni on settling particles", "沉降顆粒上的鎳"), ("Towards the sediment", "沉向底泥"))],
              ("In lakes and reservoirs part of the nickel settles with particles; anoxic bottom water fixes it as sulfide.", "在湖泊和水庫中，部分鎳隨顆粒沉降；缺氧的底層水會把它固定為硫化物。"),
              ("low", "Little direct exposure.", "直接暴露很少。"), [("Control inflow loads", "控制入流負荷")], [("residence time", "停留時間")])),
 "sediment": (1, E([(("NiS in anoxic sediment", "缺氧底泥中的 NiS"), ("Stable while reduced", "保持還原時穩定"))],
              ("Sediments store nickel as sulfide while they stay anoxic; oxidation or dredging releases it.", "底泥保持缺氧時以硫化物儲存鎳；氧化或清淤會讓它釋出。"),
              ("low", "A source again if disturbed or oxidised.", "受擾動或氧化時會再次成為污染源。"), [("Avoid resuspending polluted sediment", "避免讓受污染底泥再懸浮")], [("redox state", "氧化還原狀態")])),
 "gw": (2, E([(("Dissolved Ni²⁺", "溶解態 Ni²⁺"), ("Mobile in acidic aquifers", "在酸性含水層中容易移動")), (("Ni on aquifer sediment", "含水層沉積物上的鎳"), ("Retarded by sorption", "因吸附而遲滯"))],
              ("Nickel reaches groundwater mainly below plating sites and where soils are acidic; in neutral aquifers it is retarded by sorption.", "鎳主要在電鍍場址下方和土壤偏酸的地方到達地下水；在中性含水層中會因吸附而遲滯。"),
              ("med", "Wells near plating sites can exceed the drinking-water standard.", "電鍍場址附近的井可能超過飲用水標準。"),
              [("Monitor wells downgradient", "監測下游的井"), ("Contain the source", "圍封污染源")], [("aquifer pH", "含水層 pH"), ("Kd", "Kd")], tw=TW_GW)),
}

W_NI = ('{stack_air:[.5,"p"],air_glacier:[.4,"p"],air_forest:[.5,"p"],air_farm:[.5,"p"],air_lake:[.4,"p"],air_people:[.2,"p"],'
        'glacier_river:[.5,"p"],river_lake:[.7,"d"],bedrock_gw:[.2,"d"],bedrock_river:[.3,"p"],forest_gw:[.2,"d"],forest_river:[.4,"p"],'
        'farm_gw:[.2,"d"],farm_river:[.5,"p"],site_gw:[.4,"d"],site_river:[.5,"p"],town_wwtp:[.6,"p"],wwtp_river:[.3,"d"],town_river:[.5,"d"],'
        'gw_people:[.2,"d"],gw_lake:[.1,"d"],lake_sediment:[.7,"p"],sediment_lake:[.05,"d"],lake_people:[.05,"d"],soil_air:[0,"g"],'
        'farm_people:[.5,"d"],glacier_air:[0,"g"],lake_air:[0,"g"]}')
FORMS_NI = [("ni2", "Ni²⁺ salt or dissolved Ni", "Ni²⁺ 鹽類或溶解態鎳", 100), ("nio", "NiO and other Ni dust", "NiO 與其他含鎳粉塵", 60),
            ("niash", "Ni in fly ash", "飛灰中的鎳", 30), ("nis", "Nickel sulfide ore", "硫化鎳礦", 2)]
FORM_DEF_NI = [("orig", "Original form, not yet weathered", None), ("niSorb", "Ni on oxides, clay and organic matter", "氧化物、黏土和有機質上的鎳"),
               ("niS", "Nickel sulfide, formed", "生成的硫化鎳"), ("niD", "Dissolved Ni, free and with organic carbon", "溶解態鎳（游離或與有機碳錯合）"), ("dust", "Nickel on dust particles", "粉塵顆粒上的鎳")]
FORM_RULES_NI = '''  Ni:{   // indicative, following the Pb rules without carbonate and phosphate (assumption)
    soilSolid:(x, c) => { const ns = [0, 0.1, 0.3][c.r]; return {niS:x * ns, niSorb:x * (1 - ns)}; },
    soilWater:x => ({niD:x}),
    gwWater:x => ({niD:x}),
    gwSolid:(x, c) => c.a === 3 ? {niS:x * 0.5, niSorb:x * 0.5} : {niSorb:x},
    lakeWater:x => ({niD:x}),
    sed:(x, c) => { const ns = [0, 0.2, 0.5][c.lY] * c.s; return {niS:x * ns, niSorb:x * (1 - ns)}; },
    riverD:x => ({niD:x}), riverP:x => ({niSorb:x}),
    air:x => ({dust:x})
  }'''


def zh_pairs():
    p = {METAL["name"][0]: METAL["name"][1], METAL["site"][0]: METAL["site"][1], METAL["sig"][0]: METAL["sig"][1], METAL["lever"][0]: METAL["lever"][1],
         METAL["health"][1]: METAL["health"][2], TW_SOIL[0]: TW_SOIL[1], TW_GW[0]: TW_GW[1]}
    for a, b in METAL["forms"] + METAL["sources"]: p[a] = b
    for _, e in COMP.values():
        for f in e["forms"]: p[f[0][0]] = f[0][1]; p[f[1][0]] = f[1][1]
        p[e["what"][0]] = e["what"][1]; p[e["risk"][1]] = e["risk"][2]
        for a, b in e["trap"] + e["inputs"]: p[a] = b
        for v in e.get("sc", {}).values(): p[v[1]] = v[2]
    for _, en, zh, _ in FORMS_NI: p[en] = zh
    for _, en, zh in FORM_DEF_NI:
        if zh: p[en] = zh
    p["Nickel · Z 28"] = "鎳 Nickel · Z 28"
    p["Nickel TDI 13 µg/kg bw per day (EFSA 2020)"] = "鎳的每日容許攝入量 13 µg/kg 體重（EFSA 2020）"
    return p


METAL_JS = (',\n  Ni:{name:' + J(METAL["name"][0]) + ', site:' + J(METAL["site"][0]) + ',\n    sig:' + J(METAL["sig"][0]) +
            ',\n    forms:' + J([a for a, _ in METAL["forms"]]) + ',\n    sources:' + J([a for a, _ in METAL["sources"]]) +
            ',\n    health:' + J([METAL["health"][0], METAL["health"][1]]) + ',\n    lever:' + J(METAL["lever"][0]) + '}')

PATCHES = [
    (JS, ' remove or replace heavily polluted topsoil."}\n};', ' remove or replace heavily polluted topsoil."}' + METAL_JS + '\n};'),
    (JS, '   // indicative (assumption), see step_cd.py\n};', ',\n Ni:' + W_NI + '   // indicative (assumption), see step_cd.py and step_ni.py\n};'),
    (JS, '{id:"cds", label:"Cadmium sulfide CdS (pigment, ore)", fr:2}]\n};', '{id:"cds", label:"Cadmium sulfide CdS (pigment, ore)", fr:2}],\n  Ni:[   // reactive fractions follow the lead forms (assumption)\n'
     + ",\n".join(f'    {{id:"{i}", label:{J(en)}, fr:{fr}}}' for i, en, _, fr in FORMS_NI) + ']\n};'),
    (JS, 'Cd:Math.pow(10,5.0)};', 'Cd:Math.pow(10,5.0), Ni:Math.pow(10,4.3)};'),
    (JS, 'Cd:"0.44–192,000"};', 'Cd:"0.44–192,000", Ni:"8.9–256,842"};'),
    (JS, 'Hg:0.7, Cd:0.71}', 'Hg:0.7, Cd:0.71, Ni:0.70}'),
    (JS, '    lg = clamp(lg, Math.log10(0.44), Math.log10(192000));\n  } else {',
     '    lg = clamp(lg, Math.log10(0.44), Math.log10(192000));\n  } else if(m === "Ni"){\n    // Sauvé et al. (2000) Table 2: log Kd = 0.72 pH − 1.75 (SEE 0.70, n 138); Table 1 range 8.9–256,842 L/kg; sulfidic +0.5 (assumption)\n'
     '    lg = 0.72 * p.pH - 1.75;\n    if(p.redox === "sulfidic") lg += 0.5;\n    lg = clamp(lg, Math.log10(8.9), Math.log10(256842));\n  } else {'),
    (JS, "drink:{As:10, Hg:1, Pb:10, Cd:5},", "drink:{As:10, Hg:1, Pb:10, Cd:5, Ni:20},"),
    (JS, "1:{As:50, Hg:2, Pb:10, Cd:5}, 2:{As:500, Hg:20, Pb:100, Cd:50}},", "1:{As:50, Hg:2, Pb:10, Cd:5, Ni:100}, 2:{As:500, Hg:20, Pb:100, Cd:50, Ni:1000}},"),
    (JS, "1:{As:25, Hg:1, Pb:5, Cd:2.5}, 2:{As:250, Hg:10, Pb:50, Cd:25}},", "1:{As:25, Hg:1, Pb:5, Cd:2.5, Ni:50}, 2:{As:250, Hg:10, Pb:50, Cd:25, Ni:500}},"),
    (JS, "Pb:2000, Cd:20}, soilCtlFarm:{As:60, Hg:5, Pb:500, Cd:5},", "Pb:2000, Cd:20, Ni:200}, soilCtlFarm:{As:60, Hg:5, Pb:500, Cd:5, Ni:200},"),
    (JS, "Pb:1000, Cd:10}, soilMonFarm:{As:30, Hg:2, Pb:300, Cd:2.5},", "Pb:1000, Cd:10, Ni:130}, soilMonFarm:{As:30, Hg:2, Pb:300, Cd:2.5, Ni:130},"),
    (JS, 'Cd:{v:5, txt:"EU target value for Cd in PM10: 5 ng/m³ (Directive 2004/107/EC); the Taiwan value is not yet checked here"}};',
     'Cd:{v:5, txt:"EU target value for Cd in PM10: 5 ng/m³ (Directive 2004/107/EC); the Taiwan value is not yet checked here"}, '
     'Ni:{v:20, txt:"EU target value for Ni in PM10: 20 ng/m³ (Directive 2004/107/EC); the Taiwan value is not yet checked here"}};'),
    (JS, 'Pb:"", Cd:""}, bgAir:{As:"", Hg:"", Pb:"", Cd:""}', 'Pb:"", Cd:"", Ni:""}, bgAir:{As:"", Hg:"", Pb:"", Cd:"", Ni:""}', {"count": 2}),
    (JS, 'glConc:{As:0.1, Hg:0.01, Pb:2, Cd:0}', 'glConc:{As:0.1, Hg:0.01, Pb:2, Cd:0, Ni:0}'),
    (JS, 'ref = "Cadmium TWI 2.5 µg/kg bw per week (EFSA 2011)"; }',
     'ref = "Cadmium TWI 2.5 µg/kg bw per week (EFSA 2011)"; }\n'
     '      else if(m === "Ni"){ const tdi = 13, sh = o.dose / tdi; s = sh > 1 ? "crit" : sh > 0.1 ? "warn" : "ok"; tag = `${fmt(sh * 100)}% of TDI`; lim = tdi; ref = "Nickel TDI 13 µg/kg bw per day (EFSA 2020)"; }'),
    (JS, '{k:"dust", label:"Cadmium on dust particles"}]\n};', '{k:"dust", label:"Cadmium on dust particles"}],\n  Ni:[' + ", ".join(f'{{k:"{k}", label:{J(en)}}}' for k, en, _ in FORM_DEF_NI) + ']\n};'),
    (JS, "    air:x => ({dust:x})\n  }\n};", "    air:x => ({dust:x})\n  },\n" + FORM_RULES_NI + "\n};"),
    (JS, "Pb:207.2, Cd:112.41};", "Pb:207.2, Cd:112.41, Ni:58.69};"),
    (JS, 'Cd:["Otavite", "Cd(OH)2", "Greenockite"]};', 'Cd:["Otavite", "Cd(OH)2", "Greenockite"], Ni:["Ni(OH)2", "NiCO3", "NiS(alpha)"]};'),
    (JS, '      ok("Pb Kd follows log Kd = 1.99 + 0.42·pH",', '      ok("Ni Kd follows Sauvé et al. (2000): log Kd = 0.72·pH − 1.75", Math.abs(Math.log10(kdFn("Ni", {pH:6})) - (0.72 * 6 - 1.75)) < 1e-9, "pH 6");\n      ok("Pb Kd follows log Kd = 1.99 + 0.42·pH",'),
    (IDX, '<option value="Cd">Cadmium · Z 48</option>', '<option value="Cd">Cadmium · Z 48</option>\n          <option value="Ni">Nickel · Z 28</option>'),
    (CSS, '--cd:#2F7D6B;', '--cd:#2F7D6B; --ni:#6B7F2A;'),
    (CSS, ':root[data-metal="Cd"]{--metal:var(--cd)}', ':root[data-metal="Cd"]{--metal:var(--cd)}\n:root[data-metal="Ni"]{--metal:var(--ni)}'),
    (JS, 'Cd:`log Kd = 0.49·pH − 0.60 (Sauvé et al. 2000) = ${Math.log10(o.Kd).toFixed(2)}`})[m]', 'Cd:`log Kd = 0.49·pH − 0.60 (Sauvé et al. 2000) = ${Math.log10(o.Kd).toFixed(2)}`, Ni:`log Kd = 0.72·pH − 1.75 (Sauvé et al. 2000) = ${Math.log10(o.Kd).toFixed(2)}`})[m]'),
]


def build(F):
    s = F.get(JS)
    i, j = s.index("const C = {"), s.index("const ORDER = [")
    blk = s[i:j]
    for comp, (base, e) in COMP.items():
        a = blk.index(f"\n {comp}:{{name:")
        b, b2 = blk.find("\n },", a), blk.find("\n }\n};", a)
        end = b if b != -1 and (b2 == -1 or b < b2) else b2
        part, n = re.subn(r"(base:\{[^}]*Cd:\d)\}", lambda m: m.group(1) + f",Ni:{base}" + "}", blk[a:end], count=1)
        if n != 1:
            raise SystemExit(f"[step_ni] compartment {comp}: structure not as expected")
        blk = blk[:a] + part + ",\n  Ni:" + entry_js(e) + blk[end:]
    s = s[:i] + blk + s[j:]
    for k in ("bg", "bgGw", "bgRiv"):
        s, n = re.subn(r"(\b" + k + r":\{As:[^}]*,Cd:0)\}", r"\1,Ni:0}", s)
        if n < 5:
            raise SystemExit(f"[step_ni] {k}: expected 5 presets, found {n}")
    s = s.replace('Cd:"WRA 161086, layer 1: median of 54 wells 0 (most records below detection; limit not stated)"},',
                  'Cd:"WRA 161086, layer 1: median of 54 wells 0 (most records below detection; limit not stated)", Ni:"MOENV WQX_P_02, Chianan, 94 wells 2014–2025: 1,720 of 1,809 samples below 0.005 mg/L, so 0 used"},', 1)
    if 'Ni:"MOENV WQX_P_02' not in s:
        raise SystemExit("[step_ni] groundwater source not inserted")
    s = s.replace('Cd:"MOENV WQX_P_01, Chiayi and Tainan, 2021–2025: 682 of 719 samples below 0.001 mg/L, so 0 used"},',
                  'Cd:"MOENV WQX_P_01, Chiayi and Tainan, 2021–2025: 682 of 719 samples below 0.001 mg/L, so 0 used", Ni:"MOENV WQX_P_01, Chiayi and Tainan, 2021–2025: 467 of 719 samples below 0.005 mg/L, so 0 used"},', 1)
    s = s.replace('  Pb:{short:"shooting range", preset:"chianan",', '  Ni:{short:"plating-site seepage", preset:"chianan", v:{medium:"gw", form:"ni2", amount:0.1, horizon:100, gwWidth:50, gwThick:10, wellDist:200, land:"ind", drink:"yes", fish:"none"}},\n  Pb:{short:"shooting range", preset:"chianan",', 1)
    if 'Ni:{short:"plating-site seepage"' not in s:
        raise SystemExit("[step_ni] example not inserted")
    F.put(JS, s)
