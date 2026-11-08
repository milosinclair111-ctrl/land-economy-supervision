"""
BOUNDARY TEST: where did London's extra remote-able jobs come from?

The same test as analysis.py, run with three definitions of "London":
  1. London (the 32 boroughs + City) vs Great Britain
  2. Greater South East (London + South East + East of England) vs Great Britain
  3. London vs the Greater South East (i.e. London within its own wider region)
Also each region's change in its share of Britain's remote-able jobs.
Results go to results/regions.json.
"""
import json, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from common import YEARS, PRE, POST, group_of_division

b = pd.read_csv("data/bres_london_gb_by_division.csv", dtype={"div": str})
s = pd.read_csv("data/bres_greater_south_east_by_division.csv", dtype={"div": str})
b = b.merge(s, on="div"); b = b[b.filter(regex="^G").sum(axis=1) > 0]
L = b[[f"L{y}" for y in YEARS]].to_numpy(float); G = b[[f"G{y}" for y in YEARS]].to_numpy(float); S = b[[f"S{y}" for y in YEARS]].to_numpy(float)
div = b["div"].astype(int).to_numpy(); grp = np.array([group_of_division(d) for d in div], dtype=object)
keep = np.isin(grp, ["R", "P"]) & (L.min(1) > 0) & (G.min(1) >= 100)

def did(num, den):
    rows = [dict(d=div[i], y=y, ls=np.log(num[i, t] / den[i, t]), w=den[i].mean(), r=int(grp[i] == "R"), post=int(y >= 2022))
            for i in np.where(keep)[0] for t, y in enumerate(YEARS) if y not in (2020, 2021)]
    d = pd.DataFrame(rows)
    m = smf.wls("ls ~ r:post + C(d) + C(y)", d, weights=d.w).fit(cov_type="cluster", cov_kwds={"groups": d.d})
    return dict(effect=100 * (np.exp(m.params["r:post"]) - 1), se=100 * m.bse["r:post"], p=float(m.pvalues["r:post"]))

out = dict(london_vs_gb=did(L, G), gse_vs_gb=did(S, G), london_within_gse=did(L, S))
r = pd.read_csv("data/bres_region_group_shares.csv")
r = r[r.group == "R"].copy()
r["change"] = r[[str(y) for y in POST]].mean(axis=1) - r[[str(y) for y in PRE]].mean(axis=1)
out["regions"] = {row.region: round(row.change, 2) for row in r.itertuples()}
out["gse_change"] = round(sum(out["regions"][k] for k in ["London", "South East", "East"]), 2)
json.dump(out, open("results/regions.json", "w"), indent=1)
for k in ["london_vs_gb", "gse_vs_gb", "london_within_gse"]: print(f"{k:20s} {out[k]['effect']:+.1f}% (se {out[k]['se']:.1f}, p {out[k]['p']:.3f})")
print(out["regions"], "GSE total", out["gse_change"])
