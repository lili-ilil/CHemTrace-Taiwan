"""Step 3 (part 1): cadmium (Cd). Plan and sources: 13_新增金屬計畫_Cd_Cr_Ni.md.

Sourced values
  soil Kd       log10 Kd = 0.49 pH - 0.60, SEE 0.71 log units, range 0.44-192,000 L/kg
                (Sauvé, Hendershot & Allen 2000, Environ. Sci. Technol. 34:1125, Tables 2 and 1, p. 1128)
  suspended Kd  log10 Kd 5.0 (median; Allison & Allison 2005, EPA/600/R-05/074, Table 5, p. 3-15)
  standards     drinking water 0.005 mg/L; groundwater control 0.0050 / 0.050 mg/L (class 1 / 2), monitoring half;
                soil control 20 mg/kg (food-crop farmland 5), monitoring 10 (2.5)   (05 file)
  air           EU target value for Cd in PM10: 5 ng/m³ (Directive 2004/107/EC); Taiwan value not checked
  health        tolerable weekly intake 2.5 µg/kg bw (EFSA 2011, EFSA Journal, doi 10.2903/j.efsa.2011.1975)
  molar mass    112.41 g/mol (minteq.v4.dat); PHREEQC minerals Otavite, Cd(OH)2, Greenockite (names in minteq.v4.dat)
  Chianan       groundwater Cd: WRA 161086 layer-1 median of 54 wells 0 (most records below detection) -> background 0;
                river Cd: MOENV WQX_P_01 2021-2025, 682 of 719 samples below 0.001 mg/L -> background 0
Assumptions (marked as such in the code comments and the 13 file)
  - sulfidic conditions raise log Kd by 0.5, as the site already assumes for Pb and Hg (CdS)
  - chemical forms, their reactive fractions and the form-split rules follow the lead entries (cation, same binding phases)
  - Explore flow weights are indicative like all others; Cd is set more mobile than Pb towards groundwater and crops,
    because its median soil Kd is about 260 times lower (Sauvé 2000 Table 1: 390 vs 102,410 L/kg)
  - soil background Cd unknown for Taiwan: 0 (ASSUMED) in every preset
  - the glacier release is not offered for Cd (Taiwan has no glaciers)
"""
import json
import re

JS, IDX, CSS = "assets/js/app.js", "index.html", "assets/css/styles.css"
J = lambda s: json.dumps(s, ensure_ascii=False)

# ---------------- texts: (English, Chinese) ----------------
METAL = {
    "name": ("Cadmium", "鎘"), "site": ("Plating waste", "電鍍廢棄物"),
    "sig": ("A soft, mobile metal. Cd²⁺ binds much less strongly to soil than lead, so more of it stays in solution, especially in acidic soils, and crops such as rice take it up readily.",
            "柔軟、移動性高的金屬。Cd²⁺ 與土壤的結合遠比鉛弱，較多留在溶液中，酸性土壤尤其明顯，稻米等作物很容易吸收。"),
    "forms": [("Cd²⁺ sorbed to humus, clay and oxides", "吸附在腐植質、黏土和氧化物上的 Cd²⁺"), ("Dissolved Cd²⁺ and Cd–chloride complexes", "溶解態 Cd²⁺ 和鎘氯錯合物"),
              ("Otavite CdCO₃ (calcareous soils)", "菱鎘礦 CdCO₃（石灰質土壤）"), ("Cadmium sulfide CdS (flooded, reduced soils)", "硫化鎘 CdS（淹水、還原的土壤）"),
              ("Cd in phosphate fertiliser and zinc ores", "磷肥和鋅礦中的鎘")],
    "sources": [("Industrial wastewater from plating, pigments and batteries, reaching farmland through irrigation water", "電鍍、顏料和電池業的工業廢水，經灌溉水進入農地"),
                ("Phosphate fertilisers and sewage sludge", "磷肥和污水污泥"), ("Zinc mining and smelting, where cadmium occurs with zinc", "鋅礦開採和冶煉（鎘與鋅共存）"),
                ("Waste incineration and fly ash", "廢棄物焚化和飛灰")],
    "health": ("high", "Accumulates in the kidneys over decades and damages them; also weakens bone. Food, especially rice and other grains, is the main route for non-smokers. Tolerable weekly intake 2.5 µg/kg body weight (EFSA 2011).",
               "在腎臟累積數十年並造成損傷，也會使骨骼變脆弱。對不吸菸者而言，食物（尤其稻米等穀物）是主要暴露途徑。每週容許攝入量 2.5 µg/kg 體重（EFSA 2011）。"),
    "lever": ("Keep soil pH near neutral, keep paddies flooded during grain filling where cadmium is the concern, keep polluted water out of irrigation channels, and remove or replace heavily polluted topsoil.",
              "讓土壤 pH 維持在接近中性；有鎘疑慮的稻田在穀粒充實期保持淹水；不讓污染水進入灌溉渠道；移除或更換嚴重污染的表土。"),
}

TW_SOIL = ("Taiwan soil pollution control standard for Cd: 20 mg/kg, or 5 mg/kg on food-crop farmland (monitoring standard 10 and 2.5 mg/kg).",
           "台灣土壤污染管制標準（鎘）：20 mg/kg，食用作物農地 5 mg/kg（監測標準 10 和 2.5 mg/kg）。")
TW_GW = ("Taiwan drinking-water standard for Cd: 0.005 mg/L. Groundwater control standard: 0.0050 mg/L (class 1), 0.050 mg/L (class 2).",
         "台灣飲用水水質標準（鎘）：0.005 mg/L。地下水污染管制標準：0.0050 mg/L（第一類）、0.050 mg/L（第二類）。")
TW_SITE = ("MOENV publishes the listed soil and groundwater pollution sites as open data (data.gov.tw 6351).",
           "環境部以開放資料公布列管的土壤及地下水污染場址（data.gov.tw 6351）。")

COMP = {   # compartment: (mobility base 0-5, entry)
 "air": (3, {"forms": [(("Cd and CdO on fine particles", "細顆粒上的 Cd 和 CdO"), ("Smelting, waste incineration, fuel combustion", "冶煉、廢棄物焚化、燃料燃燒")),
                       (("Cd on resuspended soil dust", "再揚起土壤粉塵上的鎘"), ("Polluted fields and roads", "受污染的農田和道路"))],
             "what": ("Cadmium travels on fine particles and returns with rain and dry deposition, mostly in the region around its sources.", "鎘附著在細顆粒上傳輸，隨降雨和乾沉降回到地面，大多落在污染源附近的區域。"),
             "risk": ("low", "Inhaled Cd particles harm the lungs and kidneys near smelters; at background levels air is a minor route compared with food.", "在冶煉廠附近吸入含鎘顆粒會傷害肺和腎；在背景濃度下，空氣相對於食物是次要途徑。"),
             "trap": [("Fabric filters or electrostatic precipitators at the stack", "煙囪加裝袋式集塵器或靜電集塵器"), ("Dust control on polluted land", "控制污染土地的揚塵")],
             "inputs": [("emission rate", "排放量"), ("particle size", "粒徑"), ("stack height", "煙囪高度"), ("rain intensity", "降雨強度")],
             "sc": {"storm": (0, "Rain washes Cd-bearing particles out: wet deposition peaks.", "降雨洗除含鎘顆粒：濕沉降達到高峰。")}}),
 "glacier": (2, {"forms": [(("Cd on deposited dust", "沉降粉塵上的鎘"), ("Stored in snow and ice", "儲存在雪和冰中"))],
             "what": ("Snow and ice store deposited cadmium with dust and release it during melt. Taiwan has no glaciers; this compartment belongs to the original Alpine scene.", "雪和冰會連同粉塵儲存沉降的鎘，融化時釋出。台灣沒有冰河，這個介質屬於原本的阿爾卑斯山剖面。"),
             "risk": ("low", "No direct exposure.", "沒有直接暴露。"),
             "trap": [("Reservoirs trap glacial sediment", "水庫攔截冰河沉積物")],
             "inputs": [("melt rate", "融化速率"), ("Cd in ice", "冰中的鎘")]}),
 "bedrock": (1, {"forms": [(("Cd in zinc sulfide ore (sphalerite)", "閃鋅礦（硫化鋅礦）中的鎘"), ("Natural", "天然")), (("Cd in black shale and phosphate rock", "黑色頁岩和磷礦岩中的鎘"), ("Geogenic", "地質成因"))],
             "what": ("Most rocks contain little cadmium; it is enriched in zinc ores, black shales and phosphate rock. Weathering of sulfide ores releases it together with zinc.", "大多數岩石含鎘很少；鎘富集在鋅礦、黑色頁岩和磷礦岩中。硫化礦風化時會和鋅一起釋出。"),
             "risk": ("low", "Geogenic cadmium matters mainly near zinc mines and phosphate deposits.", "地質成因的鎘主要在鋅礦和磷礦附近才重要。"),
             "trap": [("Contain mine waste and treat acidic drainage", "封存礦業廢棄物並處理酸性排水")],
             "inputs": [("rock type", "岩性"), ("ore occurrences", "礦床分布"), ("weathering rate", "風化速率")]}),
 "forest": (3, {"forms": [(("Cd²⁺ on humus", "腐植質上的 Cd²⁺"), ("Mainly from deposition", "主要來自沉降")), (("Dissolved Cd in acidic soil water", "酸性土壤水中的溶解態鎘"), ("Mobile at low pH", "低 pH 時移動性高"))],
             "what": ("In acidic forest soils cadmium binds weakly and part of it leaches to groundwater and streams; humus layers keep deposited cadmium for decades.", "在酸性森林土壤中，鎘結合較弱，部分會淋溶到地下水和溪流；腐植質層會把沉降的鎘保留數十年。"),
             "risk": ("low", "Exposure mainly through mushrooms and game near polluted areas.", "暴露主要來自污染區附近的菇類和野味。"),
             "trap": [("Avoid further acidification", "避免土壤進一步酸化"), ("Lime very acidic soils", "對強酸性土壤施用石灰")],
             "inputs": [("soil pH", "土壤 pH"), ("organic matter", "有機質"), ("deposition", "沉降量")]}),
 "farm": (2, {"forms": [(("Cd²⁺ on clay, humus and oxides", "黏土、腐植質和氧化物上的 Cd²⁺"), ("Main reservoir in topsoil", "表土中的主要儲存形式")),
                       (("Dissolved Cd²⁺", "溶解態 Cd²⁺"), ("Taken up by rice and leafy vegetables", "被稻米和葉菜類吸收")),
                       (("CdS in flooded paddy soil", "淹水稻田中的 CdS"), ("Forms under reducing conditions and dissolves again when the field is drained", "在還原條件下形成，田間排水後再溶出"))],
             "what": ("Cadmium enters farmland with polluted irrigation water, phosphate fertilisers and sludge. Its availability to crops rises as soil pH falls; in paddies it is held as CdS while the field is flooded and released when it is drained.", "鎘隨受污染的灌溉水、磷肥和污泥進入農地。土壤 pH 越低，作物越容易吸收；稻田淹水時鎘以 CdS 固定，排水後又會釋出。"),
             "risk": ("high", "Rice and vegetables from polluted fields are the main exposure route; long-term intake damages the kidneys.", "污染農田生產的稻米和蔬菜是主要暴露途徑；長期攝入會損害腎臟。"),
             "trap": [("Lime acidic soils to raise the pH", "對酸性土壤施用石灰以提高 pH"), ("Keep paddies flooded during grain filling", "穀粒充實期保持稻田淹水"),
                      ("Keep polluted water out of irrigation channels", "不讓污染水進入灌溉渠道"), ("Remove or replace heavily polluted topsoil", "移除或更換嚴重污染的表土")],
             "tw": TW_SOIL,
             "inputs": [("soil pH", "土壤 pH"), ("organic carbon", "有機碳"), ("irrigation water quality", "灌溉水質"), ("crop type", "作物種類"), ("water regime", "水分狀態")],
             "sc": {"acidic": (1, "Acidic soil: more Cd in solution and in crops.", "酸性土壤：溶液和作物中的鎘增加。"), "reducing": (-1, "Flooded, reducing soil: Cd is fixed as CdS until the field is drained.", "淹水還原的土壤：鎘以 CdS 固定，直到田間排水。")}}),
 "town": (3, {"forms": [(("Cd in plating and pigment waste", "電鍍和顏料廢棄物中的鎘"), ("Industrial", "工業")), (("Cd in dust and runoff", "灰塵和逕流中的鎘"), ("Urban surfaces", "都市地表"))],
             "what": ("Plating, pigments, batteries and plastic stabilisers are the main industrial uses; wastewater and dust carry cadmium to sewers, soils and rivers.", "電鍍、顏料、電池和塑膠安定劑是主要的工業用途；廢水和灰塵把鎘帶到下水道、土壤和河川。"),
             "risk": ("med", "Local exposure near factories and along polluted irrigation channels.", "工廠附近和受污染灌溉渠道沿線的局部暴露。"),
             "trap": [("Treat plating wastewater at the source", "在源頭處理電鍍廢水"), ("Separate industrial discharges from irrigation channels", "工業排水與灌溉渠道分流")],
             "inputs": [("industrial discharges", "工業排放"), ("runoff", "逕流")]}),
 "site": (3, {"forms": [(("Cd in sludge, slag and plating residues", "污泥、爐渣和電鍍殘渣中的鎘"), ("Industrial waste", "工業廢棄物")), (("Dissolved Cd in seepage", "入滲水中的溶解態鎘"), ("Mobile under acidic conditions", "酸性條件下移動性高"))],
             "what": ("At contaminated sites cadmium often occurs with zinc, nickel and chromium from plating or smelting waste; acidic seepage can carry it to groundwater.", "污染場址中的鎘常與電鍍或冶煉廢棄物中的鋅、鎳、鉻一起出現；酸性入滲水會把它帶到地下水。"),
             "risk": ("high", "Groundwater and nearby crops can be affected.", "可能影響地下水和附近的作物。"),
             "trap": [("Excavate or contain hot spots", "開挖或圍封熱點"), ("Raise the pH with lime to reduce mobility", "施用石灰提高 pH 以降低移動性"), ("Monitor groundwater downgradient", "監測下游地下水")],
             "tw": TW_SITE,
             "inputs": [("source mass", "污染源質量"), ("soil pH", "土壤 pH"), ("seepage rate", "入滲速率")]}),
 "people": (0, {"forms": [(("Dietary Cd", "飲食中的鎘"), ("Rice, grains, vegetables, shellfish", "稻米、穀物、蔬菜、貝類")), (("Inhaled Cd", "吸入的鎘"), ("Smoking, workplaces", "吸菸、職業場所"))],
             "what": ("Cadmium builds up in the kidneys over decades, so long-term intake matters more than single exposures.", "鎘在腎臟中累積數十年，所以長期攝入比單次暴露更重要。"),
             "risk": ("high", "Kidney damage and bone loss; itai-itai disease in Japan was caused by Cd-polluted rice.", "腎臟損傷和骨質流失；日本的痛痛病就是由受鎘污染的稻米引起。"),
             "trap": [("Monitor rice and vegetables from polluted fields", "監測污染農田的稻米和蔬菜"), ("Stop growing food crops on polluted land", "停止在污染土地種植食用作物")],
             "tw": TW_GW,
             "inputs": [("crop uptake", "作物吸收"), ("diet", "飲食"), ("body weight", "體重")]}),
 "wwtp": (2, {"forms": [(("Cd in sewage sludge", "污水污泥中的鎘"), ("Most of the incoming Cd", "大部分進流的鎘")), (("Dissolved Cd in effluent", "放流水中的溶解態鎘"), ("Smaller share", "較小部分"))],
             "what": ("Treatment plants move most cadmium from water into sludge; spreading that sludge on fields returns it to soil.", "污水廠把大部分的鎘從水中轉移到污泥；把污泥施用到農田又會讓鎘回到土壤。"),
             "risk": ("low", "Mainly a sludge disposal question.", "主要是污泥處置的問題。"),
             "trap": [("Control industrial inputs to sewers", "管制工業排入下水道"), ("Keep Cd-rich sludge off farmland", "含鎘污泥不施用於農地")],
             "inputs": [("inflow load", "進流負荷"), ("sludge use", "污泥用途")]}),
 "river": (4, {"forms": [(("Dissolved Cd²⁺ and complexes", "溶解態 Cd²⁺ 和錯合物"), ("Large share when suspended sediment is low", "懸浮泥砂少時占大部分")), (("Cd on suspended particles", "懸浮顆粒上的鎘"), ("Rises with suspended sediment", "隨懸浮泥砂增加"))],
             "what": ("In rivers cadmium is more often dissolved than lead; floods carry the particle-bound share downstream to estuaries and the sea.", "在河川中，鎘比鉛更常以溶解態存在；洪水把顆粒態的部分帶到下游的河口和海洋。"),
             "risk": ("med", "Irrigation from polluted rivers or channels spreads cadmium to fields.", "從受污染的河川或渠道取水灌溉會把鎘帶到農田。"),
             "trap": [("Treat discharges upstream of irrigation intakes", "在灌溉取水口上游處理排放水"), ("Dredge polluted channel sediment with care", "謹慎清淤受污染的渠道底泥")],
             "inputs": [("discharge", "流量"), ("suspended sediment", "懸浮泥砂"), ("Kd on suspended matter", "懸浮物的 Kd")]}),
 "lake": (3, {"forms": [(("Dissolved Cd", "溶解態鎘"), ("Oxic water", "好氧水體")), (("Cd on settling particles", "沉降顆粒上的鎘"), ("Towards the sediment", "沉向底泥"))],
             "what": ("In lakes and reservoirs cadmium settles with particles; under anoxic, sulfidic bottom water it is fixed as CdS.", "在湖泊和水庫中，鎘隨顆粒沉降；底層水缺氧且含硫化物時，鎘以 CdS 固定。"),
             "risk": ("low", "Fish and shellfish can accumulate cadmium.", "魚類和貝類可能累積鎘。"),
             "trap": [("Control inflow loads", "控制入流負荷")],
             "inputs": [("residence time", "停留時間"), ("trophic state", "營養狀態"), ("bottom-water oxygen", "底層水溶氧")]}),
 "sediment": (1, {"forms": [(("CdS in anoxic sediment", "缺氧底泥中的 CdS"), ("Stable while reduced", "保持還原時穩定")), (("Cd on organic matter and oxides", "有機質和氧化物上的鎘"), ("Oxic surface layer", "好氧的表層"))],
             "what": ("Sediments store cadmium as sulfide while they stay anoxic; dredging or oxidation releases it.", "底泥保持缺氧時以硫化物儲存鎘；清淤或氧化會讓它釋出。"),
             "risk": ("low", "A source again if disturbed or oxidised.", "受擾動或氧化時會再次成為污染源。"),
             "trap": [("Avoid resuspending polluted sediment", "避免讓受污染底泥再懸浮")],
             "inputs": [("redox state", "氧化還原狀態"), ("sulfide", "硫化物"), ("organic matter", "有機質")]}),
 "gw": (3, {"forms": [(("Dissolved Cd²⁺", "溶解態 Cd²⁺"), ("More mobile in acidic, low-carbonate aquifers", "在酸性、低碳酸鹽的含水層中移動性較高")), (("Cd on aquifer sediment", "含水層沉積物上的鎘"), ("Retarded by sorption", "因吸附而遲滯"))],
             "what": ("Cadmium reaches groundwater where soils are acidic or sandy and the input is large; in neutral, carbonate-rich aquifers it moves slowly.", "在土壤偏酸或砂質、輸入量大的地方，鎘會到達地下水；在中性、富含碳酸鹽的含水層中移動緩慢。"),
             "risk": ("med", "Wells near plating sites or under polluted farmland can exceed the drinking-water standard.", "電鍍場址附近或污染農地下方的井可能超過飲用水標準。"),
             "trap": [("Monitor wells downgradient", "監測下游的井"), ("Raise the pH or contain the source", "提高 pH 或圍封污染源")],
             "tw": TW_GW,
             "inputs": [("aquifer pH", "含水層 pH"), ("Kd", "Kd"), ("flow velocity", "流速")]}),
}

W_CD = ('{stack_air:[.5,"p"],air_glacier:[.4,"p"],air_forest:[.5,"p"],air_farm:[.5,"p"],air_lake:[.4,"p"],air_people:[.2,"p"],'
        'glacier_river:[.5,"p"],river_lake:[.7,"d"],bedrock_gw:[.2,"d"],bedrock_river:[.3,"d"],forest_gw:[.3,"d"],forest_river:[.4,"d"],'
        'farm_gw:[.3,"d"],farm_river:[.5,"p"],site_gw:[.5,"d"],site_river:[.5,"d"],town_wwtp:[.6,"p"],wwtp_river:[.2,"d"],town_river:[.5,"d"],'
        'gw_people:[.3,"d"],gw_lake:[.1,"d"],lake_sediment:[.7,"p"],sediment_lake:[.05,"d"],lake_people:[.1,"d"],soil_air:[0,"g"],'
        'farm_people:[.8,"d"],glacier_air:[0,"g"],lake_air:[0,"g"]}')

FORMS_CD = [("cd2", "Cd²⁺ salt or dissolved Cd", "Cd²⁺ 鹽類或溶解態鎘", 100), ("cdo", "CdO and other Cd dust", "CdO 與其他含鎘粉塵", 60),
            ("cdash", "Cd in fly ash", "飛灰中的鎘", 30), ("cds", "Cadmium sulfide CdS (pigment, ore)", "硫化鎘 CdS（顏料、礦石）", 2)]
FORM_DEF_CD = [("orig", "Original form, not yet weathered", None), ("cdSorb", "Cd on organic matter, clay and oxides", "有機質、黏土和氧化物上的鎘"),
               ("cdCO3", "Cadmium carbonate (otavite)", "碳酸鎘（菱鎘礦）"), ("cdS", "Cadmium sulfide, formed", "生成的硫化鎘"),
               ("cdD", "Dissolved Cd, free and with chloride or organic carbon", "溶解態鎘（游離或與氯、有機碳錯合）"), ("dust", "Cadmium on dust particles", "粉塵顆粒上的鎘")]
FORM_RULES_CD = '''  Cd:{   // indicative, following the Pb rules without phosphate (assumption)
    soilSolid:(x, c) => { const cb = c.pH >= 7.5 ? 0.3 : c.pH >= 6.5 ? 0.1 : 0, cs = [0, 0.1, 0.3][c.r]; return {cdCO3:x * cb, cdS:x * cs, cdSorb:x * (1 - cb - cs)}; },
    soilWater:x => ({cdD:x}),
    gwWater:x => ({cdD:x}),
    gwSolid:(x, c) => c.a === 3 ? {cdS:x * 0.5, cdSorb:x * 0.5} : {cdSorb:x},
    lakeWater:x => ({cdD:x}),
    sed:(x, c) => { const cs = [0, 0.2, 0.5][c.lY] * c.s; return {cdS:x * cs, cdSorb:x * (1 - cs)}; },
    riverD:x => ({cdD:x}), riverP:x => ({cdSorb:x}),
    air:x => ({dust:x})
  }'''


def entry_js(e):
    out = {"forms": [[f[0][0], f[1][0]] for f in e["forms"]], "what": e["what"][0], "risk": [e["risk"][0], e["risk"][1]],
           "trap": [t[0] for t in e["trap"]], "inputs": [i[0] for i in e["inputs"]]}
    if "tw" in e: out["tw"] = e["tw"][0]
    if "sc" in e: out["sc"] = {k: [v[0], v[1]] for k, v in e["sc"].items()}
    return json.dumps(out, ensure_ascii=False)


def zh_pairs():
    """English -> Chinese pairs for zh_strings (imported there)."""
    p = {METAL["name"][0]: METAL["name"][1], METAL["site"][0]: METAL["site"][1], METAL["sig"][0]: METAL["sig"][1], METAL["lever"][0]: METAL["lever"][1],
         METAL["health"][1]: METAL["health"][2], TW_SOIL[0]: TW_SOIL[1], TW_GW[0]: TW_GW[1]}
    for a, b in METAL["forms"] + METAL["sources"]: p[a] = b
    for _, e in COMP.values():
        for f in e["forms"]: p[f[0][0]] = f[0][1]; p[f[1][0]] = f[1][1]
        p[e["what"][0]] = e["what"][1]; p[e["risk"][1]] = e["risk"][2]
        for a, b in e["trap"] + e["inputs"]: p[a] = b
        for v in e.get("sc", {}).values(): p[v[1]] = v[2]
    for _, en, zh, _ in FORMS_CD: p[en] = zh
    for _, en, zh in FORM_DEF_CD:
        if zh: p[en] = zh
    p["Cadmium · Z 48"] = "鎘 Cadmium · Z 48"
    p["Cadmium TWI 2.5 µg/kg bw per week (EFSA 2011)"] = "鎘的每週容許攝入量 2.5 µg/kg 體重（EFSA 2011）"
    return p


METAL_JS = (',\n  Cd:{name:' + J(METAL["name"][0]) + ', site:' + J(METAL["site"][0]) + ',\n    sig:' + J(METAL["sig"][0]) +
            ',\n    forms:' + J([a for a, _ in METAL["forms"]]) + ',\n    sources:' + J([a for a, _ in METAL["sources"]]) +
            ',\n    health:' + J([METAL["health"][0], METAL["health"][1]]) + ',\n    lever:' + J(METAL["lever"][0]) + '}')

PATCHES = [
    (JS, 'particle retention in runoff and rivers."}\n};', 'particle retention in runoff and rivers."}' + METAL_JS + '\n};'),
    (JS, 'farm_people:[.7,"p"],glacier_air:[0,"g"],lake_air:[0,"g"]}\n};', 'farm_people:[.7,"p"],glacier_air:[0,"g"],lake_air:[0,"g"]},\n Cd:' + W_CD + '   // indicative (assumption), see step_cd.py\n};'),
    (JS, '{id:"pbs", label:"Galena PbS", fr:2}]\n};', '{id:"pbs", label:"Galena PbS", fr:2}],\n  Cd:[   // reactive fractions follow the lead forms (assumption)\n'
     + ",\n".join(f'    {{id:"{i}", label:{J(en)}, fr:{fr}}}' for i, en, _, fr in FORMS_CD) + ']\n};'),
    (JS, 'const KDSS = {As:Math.pow(10,4.0), Pb:Math.pow(10,5.7), Hg:Math.pow(10,5.3)};', 'const KDSS = {As:Math.pow(10,4.0), Pb:Math.pow(10,5.7), Hg:Math.pow(10,5.3), Cd:Math.pow(10,5.0)};   // Allison & Allison 2005, Table 5 medians'),
    (JS, 'const KDRANGE = {As:"2–20,000", Pb:"10–100,000", Hg:"160–630,000"};', 'const KDRANGE = {As:"2–20,000", Pb:"10–100,000", Hg:"160–630,000", Cd:"0.44–192,000"};'),
    (JS, 'const KD_SIG = {As:0.8, Pb:0.7, Hg:0.7}', 'const KD_SIG = {As:0.8, Pb:0.7, Hg:0.7, Cd:0.71}'),
    (JS, '  } else {\n    // Hg(II) bound to organic matter',
     '  } else if(m === "Cd"){\n    // Sauvé et al. (2000) Table 2: log Kd = 0.49 pH − 0.60 (SEE 0.71, n 830); kept within their Table 1 range 0.44–192,000 L/kg;\n'
     '    // sulfidic +0.5 as assumed for Pb and Hg (CdS)\n    lg = 0.49 * p.pH - 0.60;\n    if(p.redox === "sulfidic") lg += 0.5;\n    lg = clamp(lg, Math.log10(0.44), Math.log10(192000));\n  } else {\n    // Hg(II) bound to organic matter'),
    # Taiwan standards
    (JS, "  drink:{As:10, Hg:1, Pb:10},", "  drink:{As:10, Hg:1, Pb:10, Cd:5},"),
    (JS, "  gwCtl:{1:{As:50, Hg:2, Pb:10}, 2:{As:500, Hg:20, Pb:100}},", "  gwCtl:{1:{As:50, Hg:2, Pb:10, Cd:5}, 2:{As:500, Hg:20, Pb:100, Cd:50}},"),
    (JS, "  gwMon:{1:{As:25, Hg:1, Pb:5}, 2:{As:250, Hg:10, Pb:50}},", "  gwMon:{1:{As:25, Hg:1, Pb:5, Cd:2.5}, 2:{As:250, Hg:10, Pb:50, Cd:25}},"),
    (JS, "  soilCtl:{As:60, Hg:20, Pb:2000}, soilCtlFarm:{As:60, Hg:5, Pb:500},", "  soilCtl:{As:60, Hg:20, Pb:2000, Cd:20}, soilCtlFarm:{As:60, Hg:5, Pb:500, Cd:5},"),
    (JS, "  soilMon:{As:30, Hg:10, Pb:1000}, soilMonFarm:{As:30, Hg:2, Pb:300},", "  soilMon:{As:30, Hg:10, Pb:1000, Cd:10}, soilMonFarm:{As:30, Hg:2, Pb:300, Cd:2.5},"),
    (JS, 'Hg:{v:1000, txt:"WHO guideline for inorganic Hg vapour: 1 µg/m³, annual mean; the Taiwan value is not yet checked here"}};',
     'Hg:{v:1000, txt:"WHO guideline for inorganic Hg vapour: 1 µg/m³, annual mean; the Taiwan value is not yet checked here"}, '
     'Cd:{v:5, txt:"EU target value for Cd in PM10: 5 ng/m³ (Directive 2004/107/EC); the Taiwan value is not yet checked here"}};'),
    # inputs per metal
    (JS, 'bgDep:{As:"", Hg:"", Pb:""}, bgAir:{As:"", Hg:"", Pb:""},', 'bgDep:{As:"", Hg:"", Pb:"", Cd:""}, bgAir:{As:"", Hg:"", Pb:"", Cd:""},'),
    (JS, 'glConc:{As:0.1, Hg:0.01, Pb:2}', 'glConc:{As:0.1, Hg:0.01, Pb:2, Cd:0}'),
    (JS, 'bgDep:{As:"", Hg:"", Pb:""}, bgAir:{As:"", Hg:"", Pb:""}}), m)', 'bgDep:{As:"", Hg:"", Pb:"", Cd:""}, bgAir:{As:"", Hg:"", Pb:"", Cd:""}}), m)'),
    # glacier release only for the original metals
    (JS, '[["gw","Groundwater, directly"],["river","River"],["glacier","Glacier melt (old deposition)"]]', '[["gw","Groundwater, directly"],["river","River"]].concat(["As","Hg","Pb"].includes(m) ? [["glacier","Glacier melt (old deposition)"]] : [])'),
    (JS, '  if(INP.medium === "road" && S.metal !== "Pb") INP.medium = "soil";', '  if(INP.medium === "road" && S.metal !== "Pb") INP.medium = "soil";\n  if(INP.medium === "glacier" && !["As","Hg","Pb"].includes(S.metal)) INP.medium = "soil";'),
    # child soil-ingestion dose against the cadmium TWI
    (JS, 'ref = "Inorganic Hg TWI 4 µg/kg bw per week (EFSA 2012). The Swiss Hg value allots 10% of it to soil."; }',
     'ref = "Inorganic Hg TWI 4 µg/kg bw per week (EFSA 2012). The Swiss Hg value allots 10% of it to soil."; }\n'
     '      else if(m === "Cd"){ const tdi = 2.5 / 7, sh = o.dose / tdi; s = sh > 1 ? "crit" : sh > 0.1 ? "warn" : "ok"; tag = `${fmt(sh * 100)}% of TWI`; lim = tdi; ref = "Cadmium TWI 2.5 µg/kg bw per week (EFSA 2011)"; }'),
    # forms by phase
    (JS, '{k:"dust", label:"Lead in dust particles"}]\n};', '{k:"dust", label:"Lead in dust particles"}],\n  Cd:[' + ", ".join(f'{{k:"{k}", label:{J(en)}}}' for k, en, _ in FORM_DEF_CD) + ']\n};'),
    (JS, "    air:x => ({dust:x})\n  }\n};", "    air:x => ({dust:x})\n  },\n" + FORM_RULES_CD + "\n};"),
    # exports
    (JS, "const MWT = {As:74.92, Hg:200.59, Pb:207.2};", "const MWT = {As:74.92, Hg:200.59, Pb:207.2, Cd:112.41};"),
    (JS, 'As:["Arsenolite", "Orpiment", "Realgar"]};', 'As:["Arsenolite", "Orpiment", "Realgar"], Cd:["Otavite", "Cd(OH)2", "Greenockite"]};'),
    # self-test
    (JS, 'ok("Pb Kd follows log Kd = 1.99 + 0.42·pH",', 'ok("Cd Kd follows Sauvé et al. (2000): log Kd = 0.49·pH − 0.60", Math.abs(Math.log10(kdFn("Cd", {pH:6})) - (0.49 * 6 - 0.60)) < 1e-9, "pH 6");\n      ok("Pb Kd follows log Kd = 1.99 + 0.42·pH",'),
    # page: metal menu and colour
    (IDX, '<option value="Pb">Lead · Z 82</option>', '<option value="Pb">Lead · Z 82</option>\n          <option value="Cd">Cadmium · Z 48</option>'),
    (CSS, '--pb:#4A5A86;', '--pb:#4A5A86; --cd:#2F7D6B;'),
    (CSS, ':root[data-metal="Pb"]{--metal:var(--pb)}', ':root[data-metal="Pb"]{--metal:var(--pb)}\n:root[data-metal="Cd"]{--metal:var(--cd)}'),
    # Kd card: explanation and tag (the map had only As, Hg and Pb, so new metals showed "undefined")
    (JS, '(m === "Pb" ? "Published fit" : "Estimated")', '(["Pb", "Cd", "Ni"].includes(m) ? "Published fit" : "Estimated")'),
    (JS, 'US EPA advises site-measured Kd for As`})[m]', 'US EPA advises site-measured Kd for As`, Cd:`log Kd = 0.49·pH − 0.60 (Sauvé et al. 2000) = ${Math.log10(o.Kd).toFixed(2)}`})[m]'),
]


def build(F):
    s = F.get(JS)
    i, j = s.index("const C = {"), s.index("const ORDER = [")
    blk = s[i:j]
    for comp, (base, e) in COMP.items():
        a = blk.index(f"\n {comp}:{{name:")
        b = blk.find("\n },", a)
        b2 = blk.find("\n }\n};", a)
        end = b if b != -1 and (b2 == -1 or b < b2) else b2
        part = blk[a:end]
        part2, n = re.subn(r"base:\{([^}]*Pb:\d)\}", lambda m: "base:{" + m.group(1) + f",Cd:{base}" + "}", part, count=1)
        if n != 1 or not part2.rstrip().endswith("}"):
            raise SystemExit(f"[step_cd] compartment {comp}: structure not as expected")
        part2 = part2 + ",\n  Cd:" + entry_js(e)
        blk = blk[:a] + part2 + blk[end:]
    s = s[:i] + blk + s[j:]
    # every preset: per-metal backgrounds get Cd (0 = unknown or below detection)
    for k in ("bg", "bgGw", "bgRiv"):
        s, n = re.subn(r"(\b" + k + r":\{As:[^,}]+,Hg:[^,}]+,Pb:[^,}]+)\}", r"\1,Cd:0}", s)
        if n < 5:
            raise SystemExit(f"[step_cd] {k}: expected 5 presets, found {n}")
    s = s.replace('bgGw:{As:"WRA 161086, layer 1: median of 54 wells 0.05 mg/L (the deeper layers 0.10–0.12 mg/L)"},',
                  'bgGw:{As:"WRA 161086, layer 1: median of 54 wells 0.05 mg/L (the deeper layers 0.10–0.12 mg/L)", Cd:"WRA 161086, layer 1: median of 54 wells 0 (most records below detection; limit not stated)"},', 1)
    s = s.replace('bgRiv:{As:"MOENV WQX_P_01, Chiayi and Tainan, 2021–2025: median total As of 45 stations (total, so an upper bound for dissolved; one record per station, time and item)"},',
                  'bgRiv:{As:"MOENV WQX_P_01, Chiayi and Tainan, 2021–2025: median total As of 45 stations (total, so an upper bound for dissolved; one record per station, time and item)", Cd:"MOENV WQX_P_01, Chiayi and Tainan, 2021–2025: 682 of 719 samples below 0.001 mg/L, so 0 used"},', 1)
    # example for the Load example button
    s = s.replace('  Pb:{short:"shooting range", preset:"chianan",', '  Cd:{short:"plating wastewater in irrigation", preset:"chianan", v:{medium:"soil", form:"cd2", pattern:"continuous", amount:1, duration:20, horizon:100, area:10000, depthMix:20, land:"agri", drink:"yes", fish:"none", reactive:100}},\n  Pb:{short:"shooting range", preset:"chianan",', 1)
    if 'Cd:{short:"plating wastewater in irrigation"' not in s:
        raise SystemExit("[step_cd] example not inserted")
    F.put(JS, s)
