"""Chinese strings for the field help texts and source notes (2b part 2). English as patched by step_help_tw.py.
Terms follow 11_術語對照表.md. Imported by zh_strings.py.
"""
HELP = {
    # release
    "Where the metal first enters the environment. Road traffic and glacier melt calculate the release from their own inputs.":
        "金屬最先進入環境的地方。道路交通和冰河融化會由各自的輸入值計算釋放量。",
    "Sets the default reactive fraction and, for air, the particle sizes.": "決定預設的可反應比例；空氣排放時也決定粒徑分布。",
    "Average daily traffic, from road traffic counts.": "平均每日交通量，取自道路交通量調查。",
    "Each heavy vehicle counts as four cars (assumption).": "每輛重型車輛以四輛小客車計（假設）。",
    "Taiwan phased out leaded petrol from 1983 and stopped supplying it in 2000 (Yao et al. 2015); roadside soils can still hold its lead.":
        "台灣自 1983 年起逐步淘汰含鉛汽油，2000 年停止供應（Yao et al. 2015）；路旁土壤可能仍殘留當時的鉛。",
    "Empty: 0.076 mg Pb per car-km today (EMEP/EEA Guidebook 2023, brake and tyre wear) or 10 mg in the leaded-petrol era (assumption).":
        "空白：目前每車公里 0.076 mg Pb（EMEP/EEA Guidebook 2023，煞車和輪胎磨耗），含鉛汽油時期 10 mg（假設）。",
    "Draws the roadside strip on the spread map.": "在擴散地圖上畫出路旁帶狀範圍。",
    "Swiss glaciers covered 861 km² in 2023 (GLAMOS). Taiwan has no glaciers; this release type is kept from the Swiss version.":
        "瑞士冰河在 2023 年的面積為 861 km²（GLAMOS）。台灣沒有冰河；這種釋放類型是沿用瑞士版。",
    "Average thinning in metres of water. Swiss glaciers lost 1.1–1.7 m a year in 2017–2025 (GLAMOS).":
        "平均變薄量，以水當量公尺計。瑞士冰河在 2017–2025 年每年減少 1.1–1.7 m（GLAMOS）。",
    "The ice of 1950–1990 is only part of what melts each year. Assumption: 20%.": "每年融化的冰只有一部分是 1950–1990 年形成的。假設：20%。",
    "Share that can dissolve and sorb: salts 100%, metallic Pb about 10%, sulfides 1–5%.": "可以溶解和吸附的比例：鹽類 100%，金屬鉛約 10%，硫化物 1–5%。",
    "The area around the stack you assess: a circle of this size.": "評估煙囪周圍的範圍：以這個面積的圓形計。",
    "Empty: calculated from particle size, release height, wind and rain (Air & surface tab). Enter a measured or modelled value (e.g. AERMOD) to replace it.":
        "空白：由粒徑、排放高度、風和雨計算（空氣與地表分頁）。可填入實測或模式（例如 AERMOD）的數值取代。",
    "Capped at the aquifer thickness.": "不超過含水層厚度。",
    "2–5% in Swiss ammunition (FOEN).": "瑞士彈藥中為 2–5%（瑞士聯邦環境署 FOEN）。",
    "8–15% measured (FOEN).": "實測 8–15%（FOEN）。",
    "About 20 L/kg below pH 8 (FOEN).": "pH 8 以下約 20 L/kg（FOEN）。",
    # site and climate
    "Use the 1991–2020 normal of the nearest Central Weather Administration station.": "使用最近的中央氣象署測站 1991–2020 年氣候平均值。",
    "Share of precipitation that recharges groundwater.": "降雨中補注地下水的比例。",
    "Sets how long snow covers the ground.": "決定積雪覆蓋地面的時間。",
    "Background air quality at the site.": "場址的背景空氣品質。",
    # air
    "Stack height, or about 1 m for dust from the ground. Plume rise is ignored, which is cautious near the source.":
        "煙囪高度；地面揚塵約 1 m。不考慮煙流抬升，在污染源附近偏保守。",
    "Annual mean wind speed at the nearest Central Weather Administration station.": "最近的中央氣象署測站的年平均風速。",
    "Shapes the deposition footprint on the spread map. Use the prevailing wind direction at the nearest Central Weather Administration station.":
        "決定擴散地圖上沉降範圍的形狀。使用最近的中央氣象署測站的盛行風向。",
    "Within ±45° of it; the rest of the time the wind is spread evenly.": "指在此風向 ±45° 內的時間比例；其餘時間的風向平均分布。",
    "Waste incineration: about 20% Hg⁰, 60% Hg(II) gas, 20% on particles; coal plants about 50/40/10 (US EPA speciation factors).":
        "廢棄物焚化：約 20% Hg⁰、60% 氣態 Hg(II)、20% 在顆粒上；燃煤電廠約 50/40/10（US EPA 物種分配係數）。",
    "Empty fields use the split for the chemical form. Fine particles travel tens of kilometres; filtered stacks emit mostly fine particles.":
        "空白時使用化學型態對應的分配。細顆粒可傳輸數十公里；有過濾設備的煙囪主要排放細顆粒。",
    "Dust from heaps, tailings and handling lands within a few hundred metres.": "堆置場、尾礦和裝卸產生的粉塵落在數百公尺內。",
    "Forest canopies catch about three times more fine dust than fields, and leaves take up Hg⁰. Empty: 100% if the land use is forest, otherwise 30% (Swiss average, not checked for Taiwan).":
        "森林樹冠攔截的細粉塵約為農田的三倍，葉片也會吸收 Hg⁰。空白：土地利用為森林時 100%，其他 30%（瑞士平均，未查核台灣）。",
    "Roofs, roads and squares: rain washes what lands there into drains. Empty: from the land use.": "屋頂、道路和廣場：落在上面的物質會被雨水沖進排水系統。空白：依土地利用。",
    "Where runoff goes: straight to a stream, onto road shoulders, to an oil separator, a road-runoff treatment plant (SABA) or a sewage works (Steiner & Hermann 2023 for FOEN).":
        "逕流的去處：直接進入溪流、路肩、油水分離器、道路逕流處理設施（瑞士稱 SABA）或污水處理廠（Steiner & Hermann 2023，FOEN 委託）。",
    "Wind lifting dust from bare ground. Empty: 0.05% on industrial ground, 0.01% on fields, 0.005% in gardens, 0 in forest (assumption). About 30% of it leaves the area; the rest lands close by.":
        "風從裸露地面揚起粉塵。空白：工業用地 0.05%、農田 0.01%、庭園 0.005%、森林 0（假設）。約 30% 離開範圍，其餘落在附近。",
    "Empty: from elevation, with the Swiss relation (Hydrological Atlas of Switzerland, shortened for today's climate); in Taiwan snow is limited to the high mountains. Above about 3200 m the Swiss relation keeps snow all year and stores the metal in firn.":
        "空白：依海拔，用瑞士的關係式（瑞士水文圖集，依目前氣候縮短）；台灣只有高山會積雪。依瑞士關係式，約 3200 m 以上全年積雪，金屬儲存在粒雪中。",
    "Sunlight turns Hg in snow back into Hg⁰ gas before melt: about 50–60% at Swiss latitudes (model, Durnford et al. 2012).":
        "融雪前，陽光會把雪中的汞轉回 Hg⁰ 氣體：在瑞士的緯度約 50–60%（模式，Durnford et al. 2012）。",
    "Share of what was stored in the snowpack that leaves with surface runoff at melt; the rest enters the soil. Assumption: 30%.":
        "融雪時，積雪中儲存的量隨地表逕流離開的比例；其餘進入土壤。假設：30%。",
    # soil
    "Background soils emit 1–2 ng/(m²·h); contaminated soils 20–800 (Zhu et al. 2016; Floreani et al. 2023). Default 10 per mg/kg; ×10 for elemental Hg, ×0.1 for cinnabar.":
        "背景土壤排放 1–2 ng/(m²·h)；受污染土壤 20–800（Zhu et al. 2016；Floreani et al. 2023）。預設每 mg/kg 為 10；元素汞 ×10，辰砂 ×0.1。",
    "Main sink for arsenic.": "砷的主要吸附相。",
    "20 cm for arable or garden topsoil; 50 cm or more for berms.": "農地或庭園表土 20 cm；土堤 50 cm 以上。",
    "For example crop offtake or mixing into deeper soil. Erosion, Hg⁰ emission and blown dust are set separately.": "例如作物移出或混入較深土層。沖蝕、Hg⁰ 排放和風揚粉塵另外設定。",
    "Will be filled from terrain once the Taiwan elevation grid exists; type it in until then. Scales the default erosion with the RUSLE slope factor relative to a 5% slope (assumption).":
        "台灣的高程網格完成後會由地形自動填入；在那之前請自行輸入。以 RUSLE 坡度因子相對於 5% 坡度調整預設沖蝕量（假設）。",
    "Empty uses the default for the land use: 0.7 t/ha/yr on arable land (measured at Frienisberg, Switzerland; no Taiwan value found yet).":
        "空白時使用土地利用的預設值：農地 0.7 t/ha/yr（瑞士 Frienisberg 實測；還沒找到台灣的數值）。",
    "Share of eroded soil that reaches a stream. Assumed 10%.": "沖蝕的土壤到達溪流的比例。假設 10%。",
    "Fine particles carry more metal. Assumed 1.5.": "細顆粒帶有較多金屬。假設 1.5。",
    "Leave empty to use the screening relation.": "空白時使用篩選用的關係式。",
    # groundwater
    "Gravel 1e-3 to 1e-2; fractured rock 1e-7 to 1e-5.": "礫石 1e-3 到 1e-2；裂隙岩 1e-7 到 1e-5。",
    "Recommended: read it from groundwater-level contours of nearby WRA observation wells or from your own wells, or click Set direction on the spread map.":
        "建議：由附近水利署觀測井或自己的井的地下水位等值線判讀，或在擴散地圖上按「設定方向」。",
    # river and lake
    "Default: median from Allison & Allison (2005).": "預設：Allison & Allison (2005) 的中位數。",
    "More nutrients mean more algae; their decay uses up oxygen at the lake bottom and feeds methylating bacteria.": "營養鹽越多，藻類越多；藻類分解會耗盡湖底的氧，並供應進行甲基化的細菌。",
    "Which moment the lake results describe: methylation and the forms in lake water. Summer: stratified, seasonal anoxia at the bottom, strong sunlight at the surface. Winter: mixed and oxic. The multi-year budget always runs the seasonal cycle.":
        "湖泊結果描述的時間點：甲基化和湖水中的化學型態。夏季：分層，底層季節性缺氧，表層日照強。冬季：混合且好氧。多年質量收支一律跑季節循環。",
    "Sunlight reduces dissolved Hg(II) to Hg⁰ gas, which escapes to air. Year average; the budget runs it twice as fast from May to September and slower in winter. Assumption: 10% of the lake-water Hg per year for deep lakes. Shallow lakes can lose much more.":
        "陽光把溶解態 Hg(II) 還原成 Hg⁰ 氣體並逸散到空氣。這是年平均；質量收支在 5 到 9 月以兩倍速度計算，冬季較慢。假設：深湖每年湖水中汞的 10%。淺湖可能損失更多。",
    "TM2 121° (EPSG:3826). Set it on the spread map with Move source, or pick a site on the map above. Empty: the default place.":
        "TM2 121°（EPSG:3826）。可在擴散地圖上按「移動污染源」設定，或在上方地圖選點。空白：預設地點。",
    "How far groundwater flows from the source before it seeps into surface water.": "地下水從污染源流到滲入地面水體之前的距離。",
    "Cracks, root channels and fine particles can carry seepage straight to the water table. 0 = slow matrix flow only. Karst and fractured rock are always treated as fast.":
        "裂縫、根孔和細顆粒可能把入滲水直接帶到地下水位。0 = 只考慮緩慢的基質流。喀斯特和裂隙岩一律當作快速流。",
    "Water residence time of the lake or reservoir downstream. Enter 0 if no lake lies downstream.": "下游湖泊或水庫的水力停留時間。下游沒有湖泊時填 0。",
    "Bulk sediment retention measured at 97–98% in Lake Geneva and Lake Brienz. Metals ride on the finest particles, which settle least, so 90% is a cautious default.":
        "日內瓦湖和布里恩茨湖實測的整體沉積物截留率為 97–98%。金屬附著在最細、最不易沉降的顆粒上，所以預設 90% 偏保守。",
    # budget and floods
    "Assumption: 10 t/ha in one event, about 14 years of average arable erosion.": "假設：一次事件 10 t/ha，約為農地平均沖蝕 14 年的量。",
    "Assumption: 30%. Heavy runoff connects fields to streams.": "假設：30%。大量逕流會把農田和溪流連接起來。",
    "Assumption: 10% of the flood's particle load settles on flooded land.": "假設：洪水顆粒負荷的 10% 沉積在淹水的土地上。",
    # redox and water analysis
    "For users with water-chemistry data. Microbes oxidise organic matter with oxygen first, then nitrate, manganese and iron oxides, then sulfate. From an electron balance the ladder finds the predominant terminal electron-accepting process below the source. It shows the dominant process only; it does not calculate species. Oxygen, nitrate and sulfate come from the Water analysis tab.":
        "給有水質資料的使用者。微生物氧化有機質時先用氧，再用硝酸鹽、錳和鐵氧化物，最後用硫酸鹽。氧化還原階梯以電子平衡找出污染源下方主要的終端電子接受反應。只顯示主要反應，不計算物種。氧、硝酸鹽和硫酸鹽取自水質分析分頁。",
    "Empty keeps the water regime on the Soil tab. Fewer than 14 days: well drained; up to 180: periodically waterlogged; more: permanently. Low organic carbon (under 1%) moves it one step towards oxic.":
        "空白時沿用土壤分頁的水分狀態。少於 14 天：排水良好；180 天以內：間歇淹水；更多：長期淹水。有機碳低（低於 1%）時往好氧方向調一級。",
    "Usually 0.5–2 mg/L under fields and forests; more under wetlands or peat.": "農田和森林下方通常 0.5–2 mg/L；濕地或泥炭下方較高。",
    "Organic contaminants enter only as electron donors: they use up oxygen, nitrate and the oxides and push the aquifer towards reducing conditions. Their own fate and transformation products are not calculated.":
        "有機污染物只當作電子供體：它們消耗氧、硝酸鹽和氧化物，使含水層趨向還原。不計算它們本身的宿命和轉化產物。",
    "From site wells (TPH or BTEX analysis). Fully oxidised, 1 mg gives about 0.42 mmol of electrons (benzene 0.38, toluene 0.39, alkanes 0.44).":
        "取自場址的井（TPH 或 BTEX 分析）。完全氧化時 1 mg 約提供 0.42 mmol 電子（苯 0.38、甲苯 0.39、烷類 0.44）。",
    "Biodegradable organic carbon, counted like natural organic carbon (4 electrons per C).": "可生物分解的有機碳，和天然有機碳一樣計算（每個 C 4 個電子）。",
    "Reactive iron oxides come from the Groundwater tab.": "可反應的鐵氧化物取自地下水分頁。",
    "Used in the PHREEQC file and to convert a measured Eh to pe.": "用在 PHREEQC 檔，以及把實測 Eh 換算成 pe。",
    "Also used by the redox ladder. The default 8 mg/L is a placeholder.": "氧化還原階梯也會用到。預設 8 mg/L 只是暫定值。",
    "Also used by the redox ladder. Default 15 mg/L.": "氧化還原階梯也會用到。預設 15 mg/L。",
    "Also used by the redox ladder. Default 30 mg/L.": "氧化還原階梯也會用到。預設 30 mg/L。",
    "Empty: the PHREEQC file sets dissolved carbonate from an assumed CO₂ pressure instead.": "空白：PHREEQC 檔改用假設的 CO₂ 分壓設定溶解碳酸鹽。",
    "Filtered and acidified in the field.": "在現場過濾並酸化。",
    "If given, the PHREEQC file holds pe at this value instead of the redox class. Electrode Eh is often not at equilibrium; measured O₂, Fe²⁺ and sulfide are more reliable.":
        "有填時，PHREEQC 檔把 pe 固定在這個值，而不用氧化還原分級。電極測得的 Eh 常常不在平衡狀態；實測的 O₂、Fe²⁺ 和硫化物比較可靠。",
    # exposure
    "0.25 g/d is the 95th percentile used for the Swiss Hg value.": "0.25 g/d 是瑞士汞限值使用的第 95 百分位數。",
}

SRC = {
    "Road traffic counts": "道路交通量調查",
    "GLAMOS glacier inventory": "GLAMOS 瑞士冰河資料",
    "Central Weather Administration climate statistics": "中央氣象署氣候統計",
    "MOENV air quality monitoring stations": "環境部空氣品質監測站",
    "Central Weather Administration station climatology": "中央氣象署測站氣候資料",
    "Central Weather Administration wind records": "中央氣象署風向紀錄",
    "Soil surveys (no national Taiwan dataset found yet)": "土壤調查（還沒找到台灣全國資料）",
    "No national soil background data found for Taiwan; sample reference soil": "沒有找到台灣全國的土壤背景資料；請採集對照土壤",
    "MOENV and WRA groundwater monitoring": "環境部和水利署地下水監測",
    "O₂, NO₃⁻, Fe²⁺, H₂S from MOENV or WRA monitoring wells, or site wells": "O₂、NO₃⁻、Fe²⁺、H₂S，取自環境部或水利署監測井，或場址的井",
    "WRA groundwater observation wells and water levels (data.gov.tw 32718, 32717)": "水利署地下水觀測井和水位（data.gov.tw 32718、32717）",
    "WRA hydrological yearbook and discharge stations": "水利署水文年報和流量站",
    "MOENV river water quality monitoring": "環境部河川水質監測",
    "MOENV reservoir water quality (WQX_P_03): total phosphorus, chlorophyll a, Carlson index": "環境部水庫水質（WQX_P_03）：總磷、葉綠素 a、卡爾森指數",
    "MOENV reservoir water quality (WQX_P_03): dissolved oxygen by sampling depth": "環境部水庫水質（WQX_P_03）：各採樣深度的溶氧",
    "Reservoir storage and inflow records": "水庫蓄水量和入流量紀錄",
    "Site observation; MOA detailed soil map (drainage class)": "場址觀察；農業部詳細土壤圖（排水等級）",
    "Site wells: TPH or BTEX": "場址的井：TPH 或 BTEX",
    "Leachate or effluent analysis (COD, BOD)": "滲出水或放流水分析（COD、BOD）",
    "Recharge or upstream groundwater (MOENV or WRA wells, site wells)": "補注水或上游地下水（環境部或水利署的井、場址的井）",
    "Groundwater Pollution Control Standards": "地下水污染管制標準",
}


def pairs():
    d = dict(HELP); d.update(SRC); return d
