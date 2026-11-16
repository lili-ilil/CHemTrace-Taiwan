"""Step 2b (part 2b): Chinese for texts the app builds at run time (tab notes, suggestions, summary, scenario label,
mass budget, sensitivity). Runs after step_2b, which adds tr().

trNodes(root) translates each text node under root with tr() (exact strings and the regex patterns in zh_strings);
on the English page it does nothing. Strings are in zh_dyn.py.
Also fixes three content gaps found on the way:
  - "All screened results are below Swiss limits." -> Taiwan standards and health reference points
  - the seepage and groundwater suggestion maps had entries only for As, Pb and Hg (Cd, Ni, Cr got nothing)
"""
JS = "assets/js/app.js"

TRNODES = '''
// translate every text node under root (dynamic panels); identifiers and numbers without a match stay as they are
function trNodes(root){
  if(!ZH || !root) return;
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n; const todo = [];
  while((n = w.nextNode())){ const t = n.nodeValue, s = t.trim(); if(s && /[A-Za-z]/.test(s)){ const z = tr(s); if(z !== s) todo.push([n, t.replace(s, z)]); } }
  todo.forEach(([n, v]) => { n.nodeValue = v; });
}
'''

PATCHES = [
    (JS, "// translate the strings of a data table in place;", TRNODES.lstrip("\n") + "// translate the strings of a data table in place;"),
    # tab note of the Site tab is refreshed without tr()
    (JS, 'if(n) n.textContent = TABNOTES.site(INP);', 'if(n) n.textContent = tr(TABNOTES.site(INP));'),
    # suggestions
    (JS, '$("#suggList").innerHTML = R.sugg.map(s => `<li>${esc(s)}</li>`).join("");', '$("#suggList").innerHTML = R.sugg.map(s => `<li>${esc(tr(s))}</li>`).join("");'),
    (JS, '${R.sugg.slice(0, 3).map(s => `<li>${esc(s)}</li>`).join("")}', '${R.sugg.slice(0, 3).map(s => `<li>${esc(tr(s))}</li>`).join("")}'),
    # summary and scenario label
    (JS, '<p class="risk">${esc(R.summary)}</p>', '<p class="risk">${esc(tr(R.summary))}</p>'),
    (JS, '  return p.join(" · ");\n}', '  return p.map(tr).join(" · ");\n}'),
    (JS, '"All screened results are below Swiss limits."', '"All screened results are below the Taiwan standards and health reference points."'),
    # derived conditions line
    (JS, '$("#derivedTxt").textContent = `${why.length ? "Reducing (" + why.join("; ") + ")" : "Oxic"} · ${S.ph === "acid" ? "Acidic" : "Near-neutral"} (soil pH ${fmt(I.pH)}, Soil tab)`;',
         '$("#derivedTxt").textContent = `${why.length ? tr("Reducing") + " (" + why.map(tr).join("; ") + ")" : tr("Oxic")} · ${tr(S.ph === "acid" ? "Acidic" : "Near-neutral")} (${tr("soil pH")} ${fmt(I.pH)}, ${tr("Soil tab")})`;'),
    # mass budget and sensitivity panels
    (JS, '  $("#budNote").innerHTML = N.map(t => `<li>${esc(t)}</li>`).join("");\n}',
         '  $("#budNote").innerHTML = N.map(t => `<li>${esc(t)}</li>`).join("");\n  trNodes($("#budTitle")); trNodes($("#budRows")); trNodes($("#budNote"));\n}'),
    (JS, 'note.textContent = "No uncertain result to analyse in this scenario."; return; }', 'note.textContent = tr("No uncertain result to analyse in this scenario."); return; }'),
    (JS, 'note.textContent = "This result does not vary across the runs (it is capped or fixed), so no input can be ranked."; return; }',
         'note.textContent = tr("This result does not vary across the runs (it is capped or fixed), so no input can be ranked."); return; }'),
    (JS, ': "No single input dominates this result; the spread comes from several inputs together.";\n}',
         ': "No single input dominates this result; the spread comes from several inputs together.";\n  trNodes(out); trNodes(note); trNodes(sel);\n}'),
    # suggestion maps: new metals (general remediation practice; mechanisms as cited)
    (JS, 'Hg:"Remove mercury hotspots or contain them with a sealing wall; keep the soil aerated to avoid methylation."}[m]);',
         'Hg:"Remove mercury hotspots or contain them with a sealing wall; keep the soil aerated to avoid methylation.", '
         'Cd:"Stop polluted irrigation water and lime acidic soil: cadmium binds more strongly at higher pH (Sauvé et al. 2000).", '
         'Ni:"Stop the seepage source and lime acidic soil: nickel binds more strongly at higher pH (Sauvé et al. 2000).", '
         'Cr:"Remove hot spots below plating baths, and reduce Cr(VI) in the soil with ferrous iron or organic amendments, which turns it into far less mobile Cr(III) (Palmer & Puls 1994)."}[m]);'),
    (JS, 'Hg:"Contain the plume with sealing walls; treat the water with activated carbon or thiol resins."}[m]);',
         'Hg:"Contain the plume with sealing walls; treat the water with activated carbon or thiol resins.", '
         'Cd:"Contain the plume hydraulically, or treat the water by coagulation-filtration or ion exchange.", '
         'Ni:"Contain the plume hydraulically, or treat the water by coagulation-filtration or ion exchange.", '
         'Cr:"Contain the plume, or reduce Cr(VI) in place (ferrous iron or a reactive barrier); treat pumped water by reduction and precipitation."}[m]);'),
    # overview panel: translate after it is built
    (JS, '    <p class="mini">Hover a compartment for its field guide · <a href="#results">all results and equations</a></p>`;\n}\nfunction advBlock(id){',
         '    <p class="mini">Hover a compartment for its field guide · <a href="#results">all results and equations</a></p>`;\n  trNodes(panel);\n}\nfunction advBlock(id){'),
    # "nothing has reached these yet": translate the labels in place
    (JS, '${hidden.map(b => b.label.charAt(0).toLowerCase() + b.label.slice(1)).join("; ")}', '${hidden.map(b => ZH ? tr(b.label) : b.label.charAt(0).toLowerCase() + b.label.slice(1)).join(ZH ? "；" : "; ")}'),
    # sensitivity note composed from translated parts
    (JS, '`<b>Measure first:</b> ${esc(top.f.meas)} ${esc(top.f.label)} explains the most spread in this result.`',
         '`<b>${tr("Measure first:")}</b> ${esc(tr(top.f.meas))} ${ZH ? esc(tr(top.f.label)) + "對這個結果的變異影響最大。" : esc(top.f.label) + " explains the most spread in this result."}`'),
    # report footer still pointed to the Swiss law portal
    (JS, '"Screening-level estimate from documented equations (see the page\'s methods). It does not replace a site investigation. Check limit values against the current text on fedlex.admin.ch."',
         '"Screening-level estimate from documented equations (see the page\'s methods). It does not replace a site investigation. Check standards against the current text on the Laws & Regulations Database (law.moj.gov.tw)."'),
    # panel header, units, flood menu, budget time buttons and the 100-year chart
    (JS, '<span class="p-zone">Screening run · ${esc(scenText())}</span>', '<span class="p-zone">${esc(tr("Screening run"))} · ${esc(scenText())}</span>'),
    (JS, '<b>${esc(r.vtxt)} ${esc(r.unit)}</b>', '<b>${esc(r.vtxt)} ${esc(tr(r.unit))}</b>'),
    (JS, '$("#floodSel").innerHTML = Object.entries(FLOODS).map(([k, f]) => `<option value="${k}">${esc(f.label)}</option>`).join("");',
         '$("#floodSel").innerHTML = Object.entries(FLOODS).map(([k, f]) => `<option value="${k}">${esc(tr(f.label))}</option>`).join("");'),
    (JS, 'trNodes($("#budTitle")); trNodes($("#budRows")); trNodes($("#budNote"));', 'trNodes($("#budTitle")); trNodes($("#budRows")); trNodes($("#budNote")); trNodes($("#budTSeg"));'),
    (JS, '  const svg = box.querySelector("svg"), hit = box.querySelector(".sc-hit"), cross = $("#scCross"), tip = $("#scTip");',
         '  trNodes(box);\n  const svg = box.querySelector("svg"), hit = box.querySelector(".sc-hit"), cross = $("#scCross"), tip = $("#scTip");'),
]
