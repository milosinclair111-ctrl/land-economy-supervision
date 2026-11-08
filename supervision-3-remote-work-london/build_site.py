"""
BUILD THE WEBSITE from the analysis results, so no number on the page is typed by hand.

Reads: results/main.json, results/robustness.json, results/regions.json, results/model.json
Uses:  site/template_body.html (the text, with {{placeholders}}), site/style.css and the chart code in site/js_*.js
Writes: site/index.html (one self-contained file; opens in any browser)
Run after analysis.py, robustness.py, region_test.py and model_results.py.
"""
import json, re
from common import HOMEWORKING, REMOTE_MIN, INPERSON_MAX, group_of_section

M = json.load(open("results/main.json")); Rb = json.load(open("results/robustness.json"))
Rg = json.load(open("results/regions.json")); Md = json.load(open("results/model.json"))

NAMES = {1:"Farming",2:"Forestry",3:"Fishing",5:"Coal mining",6:"Oil & gas extraction",8:"Quarrying",9:"Mining support",10:"Food manufacturing",11:"Drinks manufacturing",12:"Tobacco",13:"Textiles",14:"Clothing manufacturing",15:"Leather goods",16:"Wood products",17:"Paper products",18:"Printing",19:"Oil refining",20:"Chemicals",21:"Pharmaceuticals",22:"Rubber & plastics",23:"Glass, cement & ceramics",24:"Basic metals",25:"Metal products",26:"Computers & electronics",27:"Electrical equipment",28:"Machinery",29:"Motor vehicles",30:"Other transport equipment",31:"Furniture",32:"Other manufacturing",33:"Machinery repair",35:"Electricity & gas",36:"Water supply",37:"Sewerage",38:"Waste",39:"Remediation",41:"Building construction",42:"Civil engineering",43:"Specialist construction",45:"Motor trade",46:"Wholesale",47:"Retail",49:"Land transport",50:"Water transport",51:"Air transport",52:"Warehousing",53:"Post & couriers",55:"Hotels",56:"Restaurants & bars",58:"Publishing",59:"Film & TV production",60:"Broadcasting",61:"Telecoms",62:"Software & IT",63:"Information services",64:"Banking",65:"Insurance",66:"Other finance",68:"Real estate",69:"Legal & accounting",70:"Head offices & consultancy",71:"Architecture & engineering",72:"Research & development",73:"Advertising",74:"Other professional",75:"Vets",77:"Rental & leasing",78:"Recruitment",79:"Travel agencies",80:"Security",81:"Cleaning & building services",82:"Office support",84:"Public administration",85:"Education",86:"Health",87:"Residential care",88:"Social work",90:"Arts",91:"Museums & libraries",92:"Gambling",93:"Sport & recreation",94:"Membership organisations",95:"Repairs",96:"Personal services"}

f1 = lambda v: f"{v:.1f}"
sg = lambda v: ("+" if v > 0 else "−" if v < 0 else "") + f"{abs(v):.1f}"
p3 = lambda v: f"{v:.2f}" if v >= 0.01 else "<0.01"
reg = Rg["regions"]
V = dict(
    sigma=Md["sigma"], mu=Md["mu"], break0=f"{Md['break_numeric']:.2f}", sustain0=f"{Md['sustain_numeric']:.2f}",
    sustain10=f"{Md['sustain_by_theta']['0.10']:.2f}", sustain20=f"{Md['sustain_by_theta']['0.20']:.2f}",
    fall10a=f"{max(Md['fall_per_10pts']):.0f}", fall10b=f"{min(Md['fall_per_10pts']):.0f}", fall3=f"{Md['fall_for_3pts']:.1f}",
    remote_min=REMOTE_MIN, inperson_max=INPERSON_MAX,
    remote_pre=f1(M["remote_pre"]), remote_post=f1(M["remote_post"]), inperson_pre=f1(M["inperson_pre"]), inperson_post=f1(M["inperson_post"]),
    remote_rel=sg(M["remote_rel"]), inperson_rel=sg(M["inperson_rel"]), n_ind=M["main"]["n_industries"],
    main_effect=sg(M["main"]["effect"]), main_effect_abs=f"{abs(M['main']['effect']):.0f}", main_se=f1(M["main"]["se"]),
    main_p=p3(M["main"]["p"]), main_p_pct=f"{100 * M['main']['p']:.0f}",
    placebo_effect=sg(M["placebo"]["effect"]), placebo_p=p3(M["placebo"]["p"]),
    gt_effect=sg(Rb["group_trend"]["effect"]), gt_p=p3(Rb["group_trend"]["p"]),
    nofin=sg(Rb["no_finance"]["effect"]), noinfo=sg(Rb["no_infocomms"]["effect"]), nohosp=sg(Rb["no_hospitality"]["effect"]),
    london_chg=f"{reg['London']:.1f}", belt_loss=f"{-(reg['South East'] + reg['East']):.1f}", gse_chg=sg(Rg["gse_change"]) + " points",
    leak_pre=f1(M["leak"]["pre"]), leak_post=f1(M["leak"]["post"]), leak_jump=f"{M['leak']['post'] - M['leak']['pre']:.0f}",
)
rows = "".join(f'<tr><td>{n}</td><td class="n">{v:.0f}%</td><td>{ {"R": "Remote-able", "P": "In-person", None: "Left out"}[group_of_section(s)] }</td></tr>'
               for s, (n, v) in sorted(HOMEWORKING.items(), key=lambda kv: -kv[1][1]))
V["homeworking_table"] = f'<table><tr><th>Industry (SIC section)</th><th class="n">Hybrid or home</th><th>Group</th></tr>{rows}</table>'

body = open("site/template_body.html").read()
body = re.sub(r"\{\{(\w+)\}\}", lambda m: str(V[m.group(1)]), body)
assert "{{" not in body, "unfilled placeholder"

data = dict(industries=[dict(i, name=NAMES[i["div"]]) for i in M["industries"]], event=M["event"], leak=M["leak"],
            regions=Rg["regions"], boundary={k: Rg[k] for k in ["london_vs_gb", "gse_vs_gb", "london_within_gse"]})
js = ("const DATA = " + json.dumps(data, separators=(",", ":")) + ";\n" + open("site/js_head.js").read()
      + open("site/js_model_dots_map.js").read() + open("site/js_data_charts.js").read() + open("site/js_pipeline.js").read() + "})();\n")
page = ('<!DOCTYPE html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Has remote work made London more dominant?</title>\n<style>\n' + open("site/style.css").read() + '</style>\n</head>\n<body>\n'
        + body + "\n<script>\n" + js + "</script>\n</body>\n</html>\n")
open("site/index.html", "w").write(page)
print("built site/index.html", len(page), "bytes")
