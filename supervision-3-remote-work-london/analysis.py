"""
MAIN ANALYSIS: did remote-able jobs move towards London after 2020?

Data: ONS Business Register and Employment Survey (BRES), jobs counted at the
workplace, every two-digit industry, 2015-2024 (data/bres_london_gb_by_division.csv,
in hundreds of jobs). Also ONS ASHE pay data for the "pay leak".

Steps:
 1. London's share of Britain's jobs, each year, for remote-able and in-person industries.
 2. The main test (difference-in-differences): did London's share rise more for
    remote-able industries than for in-person ones, 2015-19 vs 2022-24?
 3. Year-by-year version of the test (to see whether a gap existed before 2020).
 4. Placebo: pretend remote work arrived in 2017; a sound test should find nothing.
 5. Each industry's change, for the charts.
 6. The pay leak: share of London's workplace pay that goes to people living outside London.
Results are written to results/main.json, which build_site.py puts into the website.
"""
import json, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from common import YEARS, PRE, POST, group_of_division, section_of_division

b = pd.read_csv("data/bres_london_gb_by_division.csv", dtype={"div": str})
b = b[b.filter(like="G").sum(axis=1) > 0]                      # drop industries with no jobs at all
L = b[[f"L{y}" for y in YEARS]].to_numpy(float)                 # London jobs, by industry and year
G = b[[f"G{y}" for y in YEARS]].to_numpy(float)                 # Great Britain jobs
div = b["div"].astype(int).to_numpy()
grp = np.array([group_of_division(d) for d in div], dtype=object)
R, P = grp == "R", grp == "P"
iy = {y: i for i, y in enumerate(YEARS)}
pre, post = [iy[y] for y in PRE], [iy[y] for y in POST]

# 1. London's share of Britain's jobs in each group, each year
share = lambda m: L[m].sum(0) / G[m].sum(0) * 100
sR, sP = share(R), share(P)
avg = lambda s, idx: float(np.mean(s[idx]))

# 2. Main test. One row per industry per year; outcome = log of London's share.
#    Industry fixed effects absorb each industry's normal level; year fixed effects absorb
#    anything that moved all industries together. The remote-able x after-2020 term is the
#    extra change for remote-able industries: the effect we are looking for.
keep = (R | P) & (L.min(1) > 0) & (G.min(1) >= 100)                # drop tiny industries (<10,000 jobs) with noisy shares
rows = [dict(d=div[i], y=y, ls=np.log(L[i, t] / G[i, t]), w=G[i].mean(), r=int(R[i]), post=int(y >= 2022))
        for i in np.where(keep)[0] for t, y in enumerate(YEARS) if y not in (2020, 2021)]
df = pd.DataFrame(rows)
fit = lambda f, d, w=True: (smf.wls(f, d, weights=d.w) if w else smf.ols(f, d)).fit(cov_type="cluster", cov_kwds={"groups": d.d})
m = fit("ls ~ r:post + C(d) + C(y)", df)
pct = lambda b_: 100 * (np.exp(b_) - 1)                            # log points -> per cent
main = dict(effect=pct(m.params["r:post"]), se=100 * m.bse["r:post"], p=float(m.pvalues["r:post"]),
            n_industries=int(df.d.nunique()), n_remote=int(df[df.r == 1].d.nunique()))

# 3. Year-by-year gap, relative to 2019
ev = df.copy()
evy = [2015, 2016, 2017, 2018, 2022, 2023, 2024]
for y in evy: ev[f"e{y}"] = ((ev.y == y) & (ev.r == 1)).astype(int)
me = fit("ls ~ " + " + ".join(f"e{y}" for y in evy) + " + C(d) + C(y)", ev)
event = [[y, 100 * me.params[f"e{y}"], 100 * me.bse[f"e{y}"]] for y in evy[:4]] + [[2019, 0, 0]] + [[y, 100 * me.params[f"e{y}"], 100 * me.bse[f"e{y}"]] for y in evy[4:]]

# 4. Placebo: 2015-19 only, pretend the change came in 2017
pl = df[df.y <= 2019].copy(); pl["post"] = (pl.y >= 2017).astype(int)
mp = fit("ls ~ r:post + C(d) + C(y)", pl)
placebo = dict(effect=pct(mp.params["r:post"]), se=100 * mp.bse["r:post"], p=float(mp.pvalues["r:post"]))

# 5. Each industry's change in London's share (points), 2015-19 vs 2022-24
inds = []
for i in range(len(div)):
    if G[i].mean() < 100: continue
    a = L[i, pre].sum() / G[i, pre].sum() * 100; c = L[i, post].sum() / G[i, post].sum() * 100
    inds.append(dict(div=int(div[i]), section=section_of_division(div[i]), group=grp[i], pre=a, post=c, size=float(G[i].mean())))

# 6. Pay leak (ASHE): 1 - (London residents' pay bill / London workplace pay bill)
a = pd.read_csv("data/ashe_london_workplace_vs_residence.csv")
a["bill_bn"] = a.wp_jobs * a.wp_mean / 1e9
a["leak"] = 100 * (1 - a.res_jobs * a.res_mean / (a.wp_jobs * a.wp_mean))
a["nonres_bn"] = a.bill_bn * a.leak / 100
leak = dict(years=a.year.tolist(), share=a.leak.round(2).tolist(), bill_bn=a.bill_bn.round(1).tolist(), nonres_bn=a.nonres_bn.round(1).tolist(),
            pre=float(a.loc[a.year.between(2015, 2019), "leak"].mean()), post=float(a.loc[a.year.between(2022, 2025), "leak"].mean()),
            pay_gap_pre=float((a.wp_mean / a.res_mean - 1).loc[a.year.between(2015, 2019)].mean() * 100),
            pay_gap_post=float((a.wp_mean / a.res_mean - 1).loc[a.year.between(2022, 2025)].mean() * 100))

out = dict(years=YEARS, share_remote=sR.round(2).tolist(), share_inperson=sP.round(2).tolist(),
           remote_pre=avg(sR, pre), remote_post=avg(sR, post), inperson_pre=avg(sP, pre), inperson_post=avg(sP, post),
           remote_rel=100 * (avg(sR, post) / avg(sR, pre) - 1), inperson_rel=100 * (avg(sP, post) / avg(sP, pre) - 1),
           main=main, event=event, placebo=placebo, industries=inds, leak=leak)
json.dump(out, open("results/main.json", "w"), indent=1, default=float)
print(f"Remote-able: London share {out['remote_pre']:.1f}% -> {out['remote_post']:.1f}%   In-person: {out['inperson_pre']:.1f}% -> {out['inperson_post']:.1f}%")
print(f"Main test: {main['effect']:+.1f}% (se {main['se']:.1f}, p {main['p']:.3f}), {main['n_industries']} industries")
print(f"Placebo: {placebo['effect']:+.1f}% (p {placebo['p']:.2f})   Leak: {leak['pre']:.1f}% -> {leak['post']:.1f}%")
print("Event:", [(y, round(b_, 1)) for y, b_, _ in event])
