"""
CHECKS: is the main result robust?

 a. Old trends: let the remote-able group (or each industry) keep its own pre-2020
    trend line, and measure only how far it rose ABOVE that line after 2020.
 b. Unweighted: every industry counts equally, not by size.
 c. Drop one sector at a time (finance, information & communication, hospitality).
Results go to results/robustness.json.
"""
import json, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from common import YEARS, group_of_division

b = pd.read_csv("data/bres_london_gb_by_division.csv", dtype={"div": str})
b = b[b.filter(like="G").sum(axis=1) > 0]
L = b[[f"L{y}" for y in YEARS]].to_numpy(float); G = b[[f"G{y}" for y in YEARS]].to_numpy(float)
div = b["div"].astype(int).to_numpy()
grp = np.array([group_of_division(d) for d in div], dtype=object)
keep = np.isin(grp, ["R", "P"]) & (L.min(1) > 0) & (G.min(1) >= 100)
rows = [dict(d=div[i], y=y, ls=np.log(L[i, t] / G[i, t]), w=G[i].mean(), r=int(grp[i] == "R"), post=int(y >= 2022))
        for i in np.where(keep)[0] for t, y in enumerate(YEARS) if y not in (2020, 2021)]
df = pd.DataFrame(rows); df["t"] = df.y - 2019             # time trend, zero in 2019
pct = lambda v: 100 * (np.exp(v) - 1)
res = {}
def run(name, formula, data, weighted=True):
    m = (smf.wls(formula, data, weights=data.w) if weighted else smf.ols(formula, data)).fit(cov_type="cluster", cov_kwds={"groups": data.d})
    res[name] = dict(effect=pct(m.params["r:post"]), se=100 * m.bse["r:post"], p=float(m.pvalues["r:post"]))

run("main", "ls ~ r:post + C(d) + C(y)", df)
run("group_trend", "ls ~ r:post + r:t + C(d) + C(y)", df)                 # (a) remote-able group keeps its own trend
run("industry_trends", "ls ~ r:post + C(d) + C(d):t + C(y)", df)          # (a) every industry keeps its own trend
run("unweighted", "ls ~ r:post + C(d) + C(y)", df, weighted=False)       # (b)
for name, lo, hi in [("no_finance", 64, 66), ("no_infocomms", 58, 63), ("no_hospitality", 55, 56)]:   # (c)
    run(name, "ls ~ r:post + C(d) + C(y)", df[~df.d.between(lo, hi)])


json.dump(res, open("results/robustness.json", "w"), indent=1)
for k, v in res.items(): print(f"{k:18s} {v['effect']:+6.1f}%  (se {v['se']:.1f}, p {v['p']:.3f})")
