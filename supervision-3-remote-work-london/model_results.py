"""
MODEL NUMBERS used on the website.

Uses model.py (Krugman 1991 plus theta, the share of wages spent in the other region),
with sigma = 5 and mu = 0.4 throughout.
  - break and sustain points with theta = 0 (checked against the textbook formulas)
  - the sustain point (highest trade cost at which a cluster survives) for several theta
  - how much trade costs must fall to cancel a given rise in theta
Results go to results/model.json.
"""
import json
from model import wage_gap, break_point_phi, T_of, sustain_lhs, bisect

def sustain(theta):
    """Highest trade cost T at which a full cluster still pays more than the other region."""
    return bisect(lambda T: wage_gap(1.0, T, theta=theta), 1.01, 3.0)

def breakpt(theta):
    slope = lambda T: wage_gap(0.5 + 1e-4, T, theta=theta) - wage_gap(0.5 - 1e-4, T, theta=theta)
    return bisect(slope, 1.01, 3.0)

out = dict(sigma=5, mu=0.4,
           break_numeric=breakpt(0), break_formula=T_of(break_point_phi(5, 0.4), 5),
           sustain_numeric=sustain(0), sustain_formula=T_of(bisect(lambda p: sustain_lhs(p, 5, 0.4) - 1, 0.05, 0.999), 5),
           sustain_by_theta={f"{t:.2f}": sustain(t) for t in [0, 0.03, 0.1, 0.2, 0.3]})
s = out["sustain_by_theta"]
out["fall_per_10pts"] = [100 * (1 - s["0.10"] / s["0.00"]), 100 * (1 - s["0.20"] / s["0.10"])]
out["fall_for_3pts"] = 100 * (1 - s["0.03"] / s["0.00"])
json.dump(out, open("results/model.json", "w"), indent=1)
print(json.dumps(out, indent=1))
