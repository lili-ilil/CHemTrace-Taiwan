"""Step 3 (part 3): chromium (Cr), with Cr(III) and Cr(VI). Same structure as step_cd.py; runs after step_ni.py.

Sourced values
  soil Kd       log10 Kd median Cr(III) 3.9 (range 1.0-4.7, SD 0.4, n 22) and Cr(VI) 1.1 (range -0.7-3.3, SD 0.8, n 24)
                (Allison & Allison 2005, EPA/600/R-05/074, Table 3, p. 3-8, soil/soil water; no pH regression for Cr)
  suspended Kd  log10 Kd Cr(III) 5.1 (median) and Cr(VI) 4.2 (mean, estimated by the report, CL 4) (Table 5, p. 3-15)
  valence       Cr(VI) is reduced to Cr(III) by ferrous iron, reduced sulfur and organic matter; most Cr(III) compounds are
                sparingly soluble at pH 5.5-8 and precipitate as hydroxide (Palmer & Puls 1994, EPA/540/5-94/505, as
                summarised by US EPA CLU-IN, Chromium VI, Chemistry and Behavior)
  standards     total Cr: drinking water 0.05 mg/L; groundwater control 0.050 / 0.50 mg/L (class 1 / 2), monitoring half;
                soil control 250 mg/kg, monitoring 175 mg/kg (no separate farmland value)   (05 file)
  health        Cr(III) tolerable daily intake 300 µg/kg bw (EFSA CONTAM 2014, EFSA Journal 3595, doi 10.2903/j.efsa.2014.3595);
                Cr(VI) tolerable daily intake 1.1 µg/kg bw (FSCJ 2019, Food Safety 7(2):56, doi 10.14252/foodsafetyfscj.D-1900002;
                BMDL10 0.11 mg/kg bw per day, duodenal hyperplasia in mice, uncertainty factor 100)
  air           no guideline value used; the Taiwan value is not checked
  molar mass    51.996 g/mol (minteq.v4.dat); PHREEQC minerals Cr(OH)3(am), Cr2O3, FeCr2O4 (names in minteq.v4.dat)
  Chianan       groundwater total Cr: MOENV WQX_P_02, 94 wells 2014-2025, 1,714 of 1,809 samples below 0.001 mg/L -> 0;
                river: total Cr not measured 2021-2025; Cr(VI) 668 of 703 samples below 0.002 mg/L -> 0;
                soil background unknown -> 0 (ASSUMED)
Assumptions
  - the valence switch: Cr(VI) counts as Cr(III) in permanently waterlogged soil and in anoxic or sulfidic aquifers,
    and stays Cr(VI) otherwise (rivers and lakes are treated as oxic); sediments hold Cr(III)
  - Kd uncertainty 0.8 log units for both valences (the larger of the two SDs)
  - chemical forms and reactive fractions follow the lead entries; Explore weights indicative, with Cr(VI) mobility
    towards groundwater cut under the 'reducing' scenario
  - child soil-ingestion dose: compared with the Cr(VI) TDI when the released form is Cr(VI) and the soil is not
    permanently waterlogged, otherwise with the Cr(III) TDI
"""
import re
from step_cd import J, entry_js

JS, IDX, CSS = "assets/js/app.js", "index.html", "assets/css/styles.css"

METAL = {
    "name": ("Chromium", "鉻"), "site": ("Plating or tannery site", "電鍍或製革場址"),
    "sig": ("Two forms with opposite behaviour: chromate Cr(VI) is mobile and toxic, Cr(III) binds strongly and is far less toxic. Iron(II), sulfide and organic matter turn Cr(VI) into Cr(III) where oxygen is absent.",
            "兩種價態的行為相反：鉻酸鹽 Cr(VI) 容易移動、毒性高；Cr(III) 吸附很強、毒性低很多。在缺氧的地方，二價鐵、硫化物和有機質會把 Cr(VI) 還原成 Cr(III)。"),
    "forms": [("Chromate CrO₄²⁻, Cr(VI), dissolved", "溶解態鉻酸鹽 CrO₄²⁻（Cr(VI)）"), ("Cr(III) sorbed and as Cr(OH)₃", "吸附態和 Cr(OH)₃ 形式的 Cr(III)"),
              ("Chromite and Cr in serpentine rock", "鉻鐵礦和蛇紋岩中的鉻"), ("Cr(III) in tannery waste", "製革廢棄物中的 Cr(III)")],
    "sources": [("Chrome plating and metal finishing", "鍍鉻和金屬表面處理"), ("Leather tanning", "皮革鞣製"),
                ("Chromate wood preservatives and pigments", "含鉻酸鹽的木材防腐劑和顏料"), ("Serpentine rock, which weathers to Cr-rich soils", "蛇紋岩風化形成富鉻土壤")],
    "health": ("high", "Cr(VI) is a human carcinogen when inhaled and harms the gut when swallowed; the tolerable daily intake is 1.1 µg/kg body weight (FSCJ 2019). Cr(III) is far less toxic (TDI 300 µg/kg body weight, EFSA 2014).",
               "吸入 Cr(VI) 會致癌，吞入會傷害腸道；每日容許攝入量 1.1 µg/kg 體重（日本食品安全委員會 2019）。Cr(III) 毒性低很多（每日容許攝入量 300 µg/kg 體重，EFSA 2014）。"),
    "lever": ("Treat plating wastewater at the source, reduce Cr(VI) to Cr(III) before discharge, and keep it out of irrigation channels.",
              "在源頭處理電鍍廢水，排放前把 Cr(VI) 還原成 Cr(III)，並不讓它進入灌溉渠道。"),
}
TW_SOIL = ("Taiwan soil pollution control standard for total Cr: 250 mg/kg (monitoring standard 175 mg/kg); no separate value for farmland.",
           "台灣土壤污染管制標準（總鉻）：250 mg/kg（監測標準 175 mg/kg）；農地沒有另訂數值。")
TW_GW = ("Taiwan drinking-water standard for total Cr: 0.05 mg/L. Groundwater control standard: 0.050 mg/L (class 1), 0.50 mg/L (class 2).",
         "台灣飲用水水質標準（總鉻）：0.05 mg/L。地下水污染管制標準：0.050 mg/L（第一類）、0.50 mg/L（第二類）。")
TW_SITE = ("MOENV publishes the listed soil and groundwater pollution sites as open data (data.gov.tw 6351).",
           "環境部以開放資料公布列管的土壤及地下水污染場址（data.gov.tw 6351）。")

def E(forms, what, risk, trap, inputs, **kw):
    d = {"forms": forms, "what": what, "risk": risk, "trap": trap, "inputs": inputs}; d.update(kw); return d

COMP = {
 "air": (3, E([(("Cr on fine particles, part as Cr(VI)", "細顆粒上的鉻，部分為 Cr(VI)"), ("Plating mist, steel making, combustion", "電鍍霧氣、煉鋼、燃燒"))],
              ("Chromium travels on particles and returns with rain and dry deposition near its sources.", "鉻附著在顆粒上傳輸，隨降雨和乾沉降回到污染源附近的地面。"),
              ("med", "Inhaled Cr(VI) causes lung cancer; this matters most in and around plating works.", "吸入 Cr(VI) 會導致肺癌；在電鍍廠內和周邊最重要。"),
              [("Mist suppression and filters on plating baths", "電鍍槽加裝抑霧和過濾設備")], [("emission rate", "排放量"), ("particle size", "粒徑"), ("rain intensity", "降雨強度")])),
 "glacier": (2, E([(("Cr on deposited dust", "沉降粉塵上的鉻"), ("Stored in snow and ice", "儲存在雪和冰中"))],
              ("Snow and ice store deposited chromium with dust and release it during melt. Taiwan has no glaciers; this compartment belongs to the original Alpine scene.", "雪和冰會連同粉塵儲存沉降的鉻，融化時釋出。台灣沒有冰河，這個介質屬於原本的阿爾卑斯山剖面。"),
              ("low", "No direct exposure.", "沒有直接暴露。"), [("Reservoirs trap glacial sediment", "水庫攔截冰河沉積物")], [("melt rate", "融化速率")])),
 "bedrock": (2, E([(("Cr(III) in chromite and serpentine", "鉻鐵礦和蛇紋岩中的 Cr(III)"), ("Natural, can be high", "天然，可能很高")), (("Cr(VI) formed by oxidation", "氧化生成的 Cr(VI)"), ("Manganese oxides can oxidise Cr(III)", "錳氧化物可能把 Cr(III) 氧化"))],
              ("Serpentine and other ultramafic rocks are naturally rich in chromium and nickel; their soils and streams can carry high natural levels.", "蛇紋岩等超基性岩天然富含鉻和鎳，由它們形成的土壤和溪流可能有很高的天然濃度。"),
              ("low", "Natural background can exceed soil standards near serpentine; check before blaming a source.", "蛇紋岩附近的天然背景值可能超過土壤標準；判定污染源之前要先確認。"),
              [("Map the geology before setting background values", "設定背景值前先查地質")], [("rock type", "岩性"), ("weathering rate", "風化速率")])),
 "forest": (3, E([(("Cr(III) on oxides and humus", "氧化物和腐植質上的 Cr(III)"), ("Strongly bound", "結合很強")), (("Trace Cr(VI) in oxic soil water", "好氧土壤水中的微量 Cr(VI)"), ("Mobile", "容易移動"))],
              ("Forest soils hold Cr(III) firmly; organic matter reduces Cr(VI) that arrives with deposition.", "森林土壤把 Cr(III) 牢牢固定；有機質會把隨沉降進來的 Cr(VI) 還原。"),
              ("low", "Little direct exposure.", "直接暴露很少。"), [("Keep organic-rich topsoil", "保留富含有機質的表土")], [("organic matter", "有機質"), ("soil pH", "土壤 pH")])),
 "farm": (2, E([(("Cr(III) on oxides, clay and humus", "氧化物、黏土和腐植質上的 Cr(III)"), ("Main reservoir in topsoil", "表土中的主要儲存形式")), (("Cr(VI) from polluted irrigation water", "受污染灌溉水帶來的 Cr(VI)"), ("Leaches unless reduced", "沒有被還原就會淋溶"))],
              ("Chromium reaches farmland with polluted irrigation water and sludge. Cr(III) stays in the topsoil; Cr(VI) leaches to groundwater unless organic matter or flooding reduces it.", "鉻隨受污染的灌溉水和污泥進入農地。Cr(III) 留在表土；Cr(VI) 如果沒有被有機質或淹水還原，就會淋溶到地下水。"),
              ("med", "Polluted fields can exceed the soil standards; crops take up little chromium.", "受污染的農田可能超過土壤標準；作物吸收的鉻很少。"),
              [("Keep polluted water out of irrigation channels", "不讓污染水進入灌溉渠道"), ("Add organic matter to reduce Cr(VI)", "添加有機質還原 Cr(VI)"), ("Remove or replace heavily polluted topsoil", "移除或更換嚴重污染的表土")],
              [("irrigation water quality", "灌溉水質"), ("organic matter", "有機質"), ("waterlogging", "淹水狀況")], tw=TW_SOIL)),
 "town": (3, E([(("Cr(VI) in plating wastewater", "電鍍廢水中的 Cr(VI)"), ("Industrial", "工業")), (("Cr(III) in tannery effluent", "製革廢水中的 Cr(III)"), ("Industrial", "工業"))],
              ("Plating, metal-finishing and tanning works are the main local sources; wastewater carries chromium to sewers and channels.", "電鍍、金屬表面處理和製革工廠是主要的在地污染源；廢水把鉻帶到下水道和渠道。"),
              ("med", "Local exposure near plating works and along polluted channels.", "電鍍廠附近和受污染渠道沿線的局部暴露。"),
              [("Reduce Cr(VI) to Cr(III) before discharge", "排放前把 Cr(VI) 還原成 Cr(III)")], [("industrial discharges", "工業排放")])),
 "site": (3, E([(("Cr(VI) in soil below plating baths", "電鍍槽下方土壤中的 Cr(VI)"), ("Highly mobile", "移動性很高")), (("Cr(III) in sludge and residues", "污泥和殘渣中的 Cr(III)"), ("Stable while not oxidised", "沒有被氧化時穩定"))],
              ("At plating sites Cr(VI) seeps quickly to groundwater and forms long plumes in oxic aquifers; it is often found with nickel, copper and zinc.", "電鍍場址的 Cr(VI) 會很快滲入地下水，在好氧含水層中形成長的污染團；通常與鎳、銅、鋅一起出現。"),
              ("high", "Groundwater below plating sites can exceed the standards by far.", "電鍍場址下方的地下水可能遠超過標準。"),
              [("Excavate or contain hot spots", "開挖或圍封熱點"), ("Reduce Cr(VI) in place", "就地還原 Cr(VI)"), ("Monitor groundwater downgradient", "監測下游地下水")], [("source mass", "污染源質量"), ("valence", "價態"), ("aquifer redox", "含水層氧化還原狀態")], tw=TW_SITE)),
 "people": (0, E([(("Cr(VI) in drinking water", "飲用水中的 Cr(VI)"), ("Wells near plating sites", "電鍍場址附近的井")), (("Cr(III) in food", "食物中的 Cr(III)"), ("Low toxicity", "毒性低"))],
              ("Food carries mostly Cr(III); Cr(VI) exposure comes from polluted wells and workplace air.", "食物中的鉻大多是 Cr(III)；Cr(VI) 的暴露來自受污染的井和職業場所的空氣。"),
              ("high", "Cr(VI) in drinking water is compared with a tolerable daily intake of 1.1 µg/kg body weight.", "飲用水中的 Cr(VI) 以每日容許攝入量 1.1 µg/kg 體重比較。"),
              [("Test wells near plating sites for Cr(VI)", "檢測電鍍場址附近的井是否含 Cr(VI)")], [("drinking water", "飲用水"), ("valence", "價態"), ("body weight", "體重")], tw=TW_GW)),
 "wwtp": (2, E([(("Cr(III) in sludge", "污泥中的 Cr(III)"), ("Most of the incoming Cr", "大部分進流的鉻")), (("Cr(VI) in effluent", "放流水中的 Cr(VI)"), ("Passes if not reduced", "沒有被還原就會通過"))],
              ("Treatment plants remove Cr(III) with the sludge; Cr(VI) passes unless it is reduced first.", "污水廠會把 Cr(III) 隨污泥去除；Cr(VI) 除非先被還原，否則會通過。"),
              ("low", "Mainly a question of industrial inputs.", "主要是工業排入的問題。"), [("Pre-treat plating wastewater", "電鍍廢水先做前處理")], [("inflow load", "進流負荷")])),
 "river": (4, E([(("Dissolved chromate Cr(VI)", "溶解態鉻酸鹽 Cr(VI)"), ("Oxic water", "好氧水體")), (("Cr(III) on suspended particles", "懸浮顆粒上的 Cr(III)"), ("Moves with floods", "隨洪水移動"))],
              ("In rivers Cr(VI) stays dissolved; Cr(III) travels on particles and settles in slow reaches.", "在河川中 Cr(VI) 保持溶解；Cr(III) 附著在顆粒上移動，在流速慢的河段沉降。"),
              ("med", "Irrigation from polluted channels spreads chromium to fields.", "從受污染的渠道取水灌溉會把鉻帶到農田。"),
              [("Treat discharges upstream of irrigation intakes", "在灌溉取水口上游處理排放水")], [("discharge", "流量"), ("suspended sediment", "懸浮泥砂")])),
 "lake": (3, E([(("Cr(VI) in oxic water", "好氧水中的 Cr(VI)"), ("Dissolved", "溶解態")), (("Cr(III) on settling particles", "沉降顆粒上的 Cr(III)"), ("Towards the sediment", "沉向底泥"))],
              ("In lakes and reservoirs Cr(III) settles with particles; anoxic bottom water reduces Cr(VI).", "在湖泊和水庫中 Cr(III) 隨顆粒沉降；缺氧的底層水會把 Cr(VI) 還原。"),
              ("low", "Little direct exposure.", "直接暴露很少。"), [("Control inflow loads", "控制入流負荷")], [("residence time", "停留時間")])),
 "sediment": (1, E([(("Cr(III) in anoxic sediment", "缺氧底泥中的 Cr(III)"), ("Stable while reduced", "保持還原時穩定"))],
              ("Sediments store chromium as Cr(III); dredging or oxidation by manganese oxides can turn some back into Cr(VI).", "底泥以 Cr(III) 儲存鉻；清淤或錳氧化物的氧化作用可能讓一部分變回 Cr(VI)。"),
              ("low", "A source again if disturbed or oxidised.", "受擾動或氧化時會再次成為污染源。"), [("Avoid resuspending polluted sediment", "避免讓受污染底泥再懸浮")], [("redox state", "氧化還原狀態")])),
 "gw": (2, E([(("Dissolved chromate Cr(VI)", "溶解態鉻酸鹽 Cr(VI)"), ("Mobile in oxic aquifers", "在好氧含水層中容易移動")), (("Cr(III) on aquifer sediment", "含水層沉積物上的 Cr(III)"), ("Formed where Fe(II) or sulfide is present", "在有二價鐵或硫化物的地方生成"))],
              ("Cr(VI) moves almost with the groundwater in oxic aquifers; in anoxic aquifers iron(II) and sulfide reduce it to Cr(III), which stays on the sediment.", "在好氧含水層中 Cr(VI) 幾乎隨地下水移動；在缺氧含水層中，二價鐵和硫化物會把它還原成 Cr(III)，留在沉積物上。"),
              ("high", "Wells downgradient of plating sites can exceed the drinking-water standard.", "電鍍場址下游的井可能超過飲用水標準。"),
              [("Monitor wells downgradient", "監測下游的井"), ("Reduce Cr(VI) in place", "就地還原 Cr(VI)")], [("aquifer redox", "含水層氧化還原狀態"), ("Kd", "Kd")], tw=TW_GW)),
}

W_CR = ('{stack_air:[.5,"p"],air_glacier:[.4,"p"],air_forest:[.5,"p"],air_farm:[.5,"p"],air_lake:[.4,"p"],air_people:[.2,"p"],'
        'glacier_river:[.5,"p"],river_lake:[.7,"d"],bedrock_gw:[.2,"d"],bedrock_river:[.3,"p"],forest_gw:[.2,"d"],forest_river:[.4,"p"],'
        'farm_gw:[.4,"d"],farm_river:[.5,"p"],site_gw:[.6,"d"],site_river:[.5,"d"],town_wwtp:[.6,"p"],wwtp_river:[.3,"d"],town_river:[.5,"d"],'
        'gw_people:[.4,"d"],gw_lake:[.1,"d"],lake_sediment:[.7,"p"],sediment_lake:[.05,"d"],lake_people:[.05,"d"],soil_air:[0,"g"],'
        'farm_people:[.2,"d"],glacier_air:[0,"g"],lake_air:[0,"g"]}')
FORMS_CR = [("cr6", "Chromate Cr(VI), dissolved or salt (plating, wood preservative)", "鉻酸鹽 Cr(VI)，溶解態或鹽類（電鍍、木材防腐）", 100, "VI"),
            ("cr3", "Cr(III) salt or dissolved (tannery)", "Cr(III) 鹽類或溶解態（製革）", 100, "III"),
            ("cr2o3", "Cr₂O₃ pigment or refractory dust", "Cr₂O₃ 顏料或耐火材料粉塵", 60, "III"),
            ("crite", "Chromite ore, serpentine rock", "鉻鐵礦、蛇紋岩", 2, "III")]
FORM_DEF_CR = [("orig", "Original form, not yet weathered", None), ("crSorb", "Cr(III) sorbed and as Cr(OH)₃", "吸附態和 Cr(OH)₃ 形式的 Cr(III)"),
               ("cr6S", "Cr(VI) sorbed on oxides", "氧化物上吸附的 Cr(VI)"), ("crD", "Dissolved Cr(III)", "溶解態 Cr(III)"),
               ("cr6D", "Dissolved chromate Cr(VI)", "溶解態鉻酸鹽 Cr(VI)"), ("dust", "Chromium on dust particles", "粉塵顆粒上的鉻")]
FORM_RULES_CR = '''  Cr:{   // Cr(VI) stays Cr(VI) unless the soil is permanently waterlogged or the aquifer anoxic or sulfidic (assumption, see step_cr.py)
    soilSolid:(x, c) => c.form === "cr6" && c.r < 2 ? {cr6S:x} : {crSorb:x},
    soilWater:(x, c) => c.form === "cr6" && c.r < 2 ? {cr6D:x} : {crD:x},
    gwWater:(x, c) => c.form === "cr6" && c.a < 2 ? {cr6D:x} : {crD:x},
    gwSolid:(x, c) => c.form === "cr6" && c.a < 2 ? {cr6S:x} : {crSorb:x},
    lakeWater:(x, c) => c.form === "cr6" ? {cr6D:x} : {crD:x},
    sed:x => ({crSorb:x}),
    riverD:(x, c) => c.form === "cr6" ? {cr6D:x} : {crD:x}, riverP:x => ({crSorb:x}),
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
    for _, en, zh, _, _ in FORMS_CR: p[en] = zh
    for _, en, zh in FORM_DEF_CR:
        if zh: p[en] = zh
    p["Chromium · Z 24"] = "鉻 Chromium · Z 24"
    p["No guideline"] = "沒有指引值"
    p["No guideline value for chromium in air is used here; the Taiwan value is not yet checked here"] = "這裡沒有使用空氣中鉻的指引值；台灣的數值還沒查核"
    p["Cr(VI) TDI 1.1 µg/kg bw per day (FSCJ 2019)"] = "Cr(VI) 每日容許攝入量 1.1 µg/kg 體重（日本食品安全委員會 2019）"
    p["Cr(III) TDI 300 µg/kg bw per day (EFSA 2014)"] = "Cr(III) 每日容許攝入量 300 µg/kg 體重（EFSA 2014）"
    p["Reduce Cr(VI) to Cr(III) at the source (ferrous iron, sulfide or organic matter) before it reaches oxic groundwater (Palmer & Puls 1994)."] = "在源頭把 Cr(VI) 還原成 Cr(III)（用二價鐵、硫化物或有機質），不讓它進入好氧的地下水（Palmer & Puls 1994）。"
    p["Empty: no background is added; Taiwan deposition data are not yet included. Enter a measured value if you have one."] = "空白：不加背景值；還沒有納入台灣的沉降資料。有實測值請填入。"
    p["Empty: no background is added; Taiwan metal-in-PM10 data are not yet included. Enter a measured value if you have one."] = "空白：不加背景值；還沒有納入台灣 PM10 中金屬的資料。有實測值請填入。"
    return p


def zh_patterns():
    return [[r"^(Cr\((?:III|VI)\)): median of soil data, log Kd (-?[\d.]+) \(Allison & Allison 2005, Table 3\)$", r"$1：土壤資料中位數，log Kd $2（Allison & Allison 2005，表 3）"]]


METAL_JS = (',\n  Cr:{name:' + J(METAL["name"][0]) + ', site:' + J(METAL["site"][0]) + ',\n    sig:' + J(METAL["sig"][0]) +
            ',\n    forms:' + J([a for a, _ in METAL["forms"]]) + ',\n    sources:' + J([a for a, _ in METAL["sources"]]) +
            ',\n    health:' + J([METAL["health"][0], METAL["health"][1]]) + ',\n    lever:' + J(METAL["lever"][0]) + '}')
NI_LEVER = J("Treat plating wastewater at the source, keep it out of irrigation channels, and keep soil pH near neutral.")
NI_FORM_END = '{id:"nis", label:"Nickel sulfide ore", fr:2}]\n};'

PATCHES = [
    (JS, 'lever:' + NI_LEVER + '}\n};', 'lever:' + NI_LEVER + '}' + METAL_JS + '\n};'),
    (JS, '   // indicative (assumption), see step_cd.py and step_ni.py\n};', ',\n Cr:' + W_CR + '   // indicative (assumption), see step_cd.py, step_ni.py and step_cr.py\n};'),
    (JS, '           Pb:{sediment_lake:.5}},', '           Pb:{sediment_lake:.5},\n           Cr:{farm_gw:.3,site_gw:.3,forest_gw:.3,bedrock_gw:.5,gw_people:.5}},   // Cr(VI) reduced to Cr(III) (indicative)'),
    (JS, NI_FORM_END, NI_FORM_END[:-3] + ',\n  Cr:[   // reactive fractions follow the lead forms (assumption); sp = valence\n'
     + ",\n".join(f'    {{id:"{i}", label:{J(en)}, fr:{fr}, sp:"{sp}"}}' for i, en, _, fr, sp in FORMS_CR) + ']\n};'),
    (JS, 'Ni:Math.pow(10,4.3)};', 'Ni:Math.pow(10,4.3), Cr:Math.pow(10,5.1), CrVI:Math.pow(10,4.2)};'),
    (JS, 'Ni:"8.9–256,842"};', 'Ni:"8.9–256,842", Cr:"0.2–50,000"};'),
    (JS, 'Cd:0.71, Ni:0.70}', 'Cd:0.71, Ni:0.70, Cr:0.8}'),
    (JS, '    lg = clamp(lg, Math.log10(8.9), Math.log10(256842));\n  } else {',
     '    lg = clamp(lg, Math.log10(8.9), Math.log10(256842));\n  } else if(m === "Cr"){\n'
     '    // Allison & Allison (2005) Table 3, p. 3-8 (soil): median log Kd Cr(III) 3.9 (range 1.0–4.7), Cr(VI) 1.1 (range −0.7–3.3); no pH regression.\n'
     '    // Cr(VI) is reduced to Cr(III) by Fe(II), sulfide and organic matter (Palmer & Puls 1994); taken to happen in permanently\n'
     '    // waterlogged soil and in anoxic or sulfidic aquifers (assumption)\n'
     '    const iii = p.sp !== "VI" || p.drain === "perm" || p.redox === "anoxic" || p.redox === "sulfidic";\n'
     '    lg = iii ? clamp(3.9, 1.0, 4.7) : clamp(1.1, -0.7, 3.3);\n  } else {'),
    (JS, '  const kdSS = (num(I.kdSS) || KDSS[m]) * u.kdSS;', '  const kdSS = (num(I.kdSS) || (m === "Cr" && sp === "VI" ? KDSS.CrVI : KDSS[m])) * u.kdSS;'),
    (JS, 'kdSSdef:KDSS[m]};', 'kdSSdef:(m === "Cr" && form.sp === "VI" ? KDSS.CrVI : KDSS[m])};'),
    (JS, "drink:{As:10, Hg:1, Pb:10, Cd:5, Ni:20},", "drink:{As:10, Hg:1, Pb:10, Cd:5, Ni:20, Cr:50},"),
    (JS, "Cd:5, Ni:100}, 2:{As:500, Hg:20, Pb:100, Cd:50, Ni:1000}},", "Cd:5, Ni:100, Cr:50}, 2:{As:500, Hg:20, Pb:100, Cd:50, Ni:1000, Cr:500}},"),
    (JS, "Cd:2.5, Ni:50}, 2:{As:250, Hg:10, Pb:50, Cd:25, Ni:500}},", "Cd:2.5, Ni:50, Cr:25}, 2:{As:250, Hg:10, Pb:50, Cd:25, Ni:500, Cr:250}},"),
    (JS, "Cd:20, Ni:200}, soilCtlFarm:{As:60, Hg:5, Pb:500, Cd:5, Ni:200},", "Cd:20, Ni:200, Cr:250}, soilCtlFarm:{As:60, Hg:5, Pb:500, Cd:5, Ni:200, Cr:250},"),
    (JS, "Cd:10, Ni:130}, soilMonFarm:{As:30, Hg:2, Pb:300, Cd:2.5, Ni:130},", "Cd:10, Ni:130, Cr:175}, soilMonFarm:{As:30, Hg:2, Pb:300, Cd:2.5, Ni:130, Cr:175},"),
    (JS, 'Ni:{v:20, txt:"EU target value for Ni in PM10: 20 ng/m³ (Directive 2004/107/EC); the Taiwan value is not yet checked here"}};',
     'Ni:{v:20, txt:"EU target value for Ni in PM10: 20 ng/m³ (Directive 2004/107/EC); the Taiwan value is not yet checked here"}, '
     'Cr:{v:null, txt:"No guideline value for chromium in air is used here; the Taiwan value is not yet checked here"}};'),
    (JS, 'mc:st(x => (x.airPM + x.airGasC) * I.amount + bgc, al.v),\n          status: ctot > al.v ? "crit" : "ok", tag: ctot > al.v ? "Above guideline" : "Below guideline",',
     'mc:st(x => (x.airPM + x.airGasC) * I.amount + bgc, al.v || null),\n          status: al.v == null ? "info" : ctot > al.v ? "crit" : "ok", tag: al.v == null ? "No guideline" : ctot > al.v ? "Above guideline" : "Below guideline",'),
    (JS, 'Cd:"", Ni:""}, bgAir:{As:"", Hg:"", Pb:"", Cd:"", Ni:""}', 'Cd:"", Ni:"", Cr:""}, bgAir:{As:"", Hg:"", Pb:"", Cd:"", Ni:"", Cr:""}', {"count": 2}),
    (JS, 'glConc:{As:0.1, Hg:0.01, Pb:2, Cd:0, Ni:0}', 'glConc:{As:0.1, Hg:0.01, Pb:2, Cd:0, Ni:0, Cr:0}'),
    (JS, 'ref = "Nickel TDI 13 µg/kg bw per day (EFSA 2020)"; }',
     'ref = "Nickel TDI 13 µg/kg bw per day (EFSA 2020)"; }\n'
     '      else if(m === "Cr"){ const six = formOf().sp === "VI" && I.drain !== "perm", tdi = six ? 1.1 : 300, sh = o.dose / tdi; s = sh > 1 ? "crit" : sh > 0.1 ? "warn" : "ok"; tag = `${fmt(sh * 100)}% of TDI`; lim = tdi; ref = six ? "Cr(VI) TDI 1.1 µg/kg bw per day (FSCJ 2019)" : "Cr(III) TDI 300 µg/kg bw per day (EFSA 2014)"; }'),
    (JS, '{k:"dust", label:"Nickel on dust particles"}]\n};', '{k:"dust", label:"Nickel on dust particles"}],\n  Cr:[' + ", ".join(f'{{k:"{k}", label:{J(en)}}}' for k, en, _ in FORM_DEF_CR) + ']\n};'),
    (JS, "    air:x => ({dust:x})\n  }\n};", "    air:x => ({dust:x})\n  },\n" + FORM_RULES_CR + "\n};"),
    (JS, "Cd:112.41, Ni:58.69};", "Cd:112.41, Ni:58.69, Cr:51.996};"),
    (JS, 'Ni:["Ni(OH)2", "NiCO3", "NiS(alpha)"]};', 'Ni:["Ni(OH)2", "NiCO3", "NiS(alpha)"], Cr:["Cr(OH)3(am)", "Cr2O3", "FeCr2O4"]};'),
    (JS, '      ok("Pb Kd follows log Kd = 1.99 + 0.42·pH",',
     '      ok("Cr Kd: Cr(VI) log 1.1, reduced to Cr(III) log 3.9 in an anoxic aquifer (Allison & Allison 2005)", Math.abs(Math.log10(kdFn("Cr", {sp:"VI", pH:7})) - 1.1) < 1e-9 && Math.abs(Math.log10(kdFn("Cr", {sp:"VI", pH:7, redox:"anoxic"})) - 3.9) < 1e-9, "oxic and anoxic");\n'
     '      ok("Pb Kd follows log Kd = 1.99 + 0.42·pH",'),
    (IDX, '<option value="Ni">Nickel · Z 28</option>', '<option value="Ni">Nickel · Z 28</option>\n          <option value="Cr">Chromium · Z 24</option>'),
    (CSS, '--ni:#6B7F2A;', '--ni:#6B7F2A; --cr:#9A4F7A;'),
    (CSS, ':root[data-metal="Ni"]{--metal:var(--ni)}', ':root[data-metal="Ni"]{--metal:var(--ni)}\n:root[data-metal="Cr"]{--metal:var(--cr)}'),
    (JS, 'Ni:`log Kd = 0.72·pH − 1.75 (Sauvé et al. 2000) = ${Math.log10(o.Kd).toFixed(2)}`})[m]', 'Ni:`log Kd = 0.72·pH − 1.75 (Sauvé et al. 2000) = ${Math.log10(o.Kd).toFixed(2)}`, Cr:`${formOf().sp === "VI" && I.drain !== "perm" ? "Cr(VI)" : "Cr(III)"}: median of soil data, log Kd ${Math.log10(o.Kd).toFixed(2)} (Allison & Allison 2005, Table 3)`})[m]'),
    (JS, '  if(m === "Pb" && I.pH < 5.5) sugg.push("Lime the soil: lead mobility rises sharply below pH 5 to 5.5.");',
         '  if(m === "Pb" && I.pH < 5.5) sugg.push("Lime the soil: lead mobility rises sharply below pH 5 to 5.5.");\n'
         '  if(m === "Cr" && formOf().sp === "VI") sugg.push("Reduce Cr(VI) to Cr(III) at the source (ferrous iron, sulfide or organic matter) before it reaches oxic groundwater (Palmer & Puls 1994).");'),
    # PHREEQC export: chromate on the Hfo surface model (tested 2026-11-15: Kd about 3,200 L/kg at pH 7, oxic soil, vs 13 here)
    (JS, '  if(m === "Hg") L.push(`# For Hg the website Kd comes from organic matter (Koc), so expect a much lower Kd here until humic binding is added.`);',
         '  if(m === "Hg") L.push(`# For Hg the website Kd comes from organic matter (Koc), so expect a much lower Kd here until humic binding is added.`);\n'
         '  if(m === "Cr") L.push(`# For Cr the website Kd is the soil median of Allison & Allison (2005): Cr(VI) log 1.1, Cr(III) log 3.9. The Hfo surface model here can bind chromate much more strongly (a test at pH 7 in oxic soil gave Kd about 3,200 L/kg); compare both.`);'),
]


def build(F):
    s = F.get(JS)
    i, j = s.index("const C = {"), s.index("const ORDER = [")
    blk = s[i:j]
    for comp, (base, e) in COMP.items():
        a = blk.index(f"\n {comp}:{{name:")
        b, b2 = blk.find("\n },", a), blk.find("\n }\n};", a)
        end = b if b != -1 and (b2 == -1 or b < b2) else b2
        part, n = re.subn(r"(base:\{[^}]*Ni:\d)\}", lambda m: m.group(1) + f",Cr:{base}" + "}", blk[a:end], count=1)
        if n != 1:
            raise SystemExit(f"[step_cr] compartment {comp}: structure not as expected")
        blk = blk[:a] + part + ",\n  Cr:" + entry_js(e) + blk[end:]
    s = s[:i] + blk + s[j:]
    for k in ("bg", "bgGw", "bgRiv"):
        s, n = re.subn(r"(\b" + k + r":\{As:[^}]*,Ni:0)\}", r"\1,Cr:0}", s)
        if n < 5:
            raise SystemExit(f"[step_cr] {k}: expected 5 presets, found {n}")
    a1 = 'Ni:"MOENV WQX_P_02, Chianan, 94 wells 2014–2025: 1,720 of 1,809 samples below 0.005 mg/L, so 0 used"},'
    a2 = 'Ni:"MOENV WQX_P_01, Chiayi and Tainan, 2021–2025: 467 of 719 samples below 0.005 mg/L, so 0 used"},'
    for a, add in ((a1, 'Cr:"MOENV WQX_P_02, Chianan, 94 wells 2014–2025: total Cr 1,714 of 1,809 samples below 0.001 mg/L, so 0 used"'),
                   (a2, 'Cr:"MOENV WQX_P_01, Chiayi and Tainan, 2021–2025: total Cr not measured; Cr(VI) 668 of 703 samples below 0.002 mg/L, so 0 used"')):
        if a not in s:
            raise SystemExit("[step_cr] preset source anchor missing: " + a[:40])
        s = s.replace(a, a[:-2] + ", " + add + "},", 1)
    s = s.replace('  Pb:{short:"shooting range", preset:"chianan",', '  Cr:{short:"chromate in irrigation water", preset:"chianan", v:{medium:"soil", form:"cr6", pattern:"continuous", amount:1, duration:20, horizon:100, area:10000, depthMix:20, land:"agri", drink:"yes", fish:"none", reactive:100}},\n  Pb:{short:"shooting range", preset:"chianan",', 1)
    if 'Cr:{short:"chromate in irrigation water"' not in s:
        raise SystemExit("[step_cr] example not inserted")
    F.put(JS, s)
