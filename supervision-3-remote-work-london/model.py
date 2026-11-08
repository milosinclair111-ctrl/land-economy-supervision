"""
Two-region core-periphery model (Krugman 1991), in the normalisation of
Fujita, Krugman and Venables (1999, ch. 5), with two optional extensions:

  delta : a congestion / housing cost. Real wages are divided by N_r**delta,
          where N_r is the region's population. This is a reduced-form way of
          saying that crowding into one place pushes up the cost of living
          (the mechanism behind Helpman 1998 and the bell-shaped curve in
          Puga 1999 / Puga 2002).

  theta : remote work. A share theta of the workers employed by firms in one
          region live (and spend their wages) in the other region. This splits
          'where you earn' from 'where you spend', which is the link Krugman's
          backward linkage relies on.

With delta = 0 and theta = 0 this is exactly Krugman (1991).

Notation
  sigma  elasticity of substitution between varieties (sigma > 1)
  mu     share of spending on manufactures / tradeable services, and the
         share of the workforce that is mobile (skilled)
  T      iceberg trade cost (T = 1 is free trade)
  phi    freeness of trade, T**(1 - sigma), between 0 and 1
  lam    share of mobile workers employed in region 1
"""
import numpy as np


def short_run(lam, T, sigma=5.0, mu=0.4, delta=0.0, theta=0.0, tol=1e-12, max_iter=20000):
    """Solve the short-run equilibrium for a given split lam.

    Returns a dict with nominal wages w, price indices G, incomes Y,
    populations N and the real return to working in each region omega.
    """
    lam_v = np.array([lam, 1.0 - lam])
    farm = (1.0 - mu) / 2.0                    # immobile workers, half in each region
    tau = np.array([[1.0, T], [T, 1.0]])       # trade cost matrix
    w = np.ones(2)
    for _ in range(max_iter):
        # incomes: residents' wages are spent where they live
        stay = mu * (1.0 - theta) * lam_v * w          # work and live in r
        move = mu * theta * lam_v[::-1] * w[::-1]       # work in s, live in r
        Y = stay + move + farm
        # price index of the composite good in each region
        G = (lam_v[None, :] * (w[None, :] * tau) ** (1.0 - sigma)).sum(axis=1) ** (1.0 / (1.0 - sigma))
        # wage equation: zero-profit wage given market access
        w_new = ((Y[None, :] * G[None, :] ** (sigma - 1.0)) * tau ** (1.0 - sigma)).sum(axis=1) ** (1.0 / sigma)
        if np.max(np.abs(w_new - w)) < tol:
            w = w_new
            break
        w = 0.5 * w + 0.5 * w_new
    N = mu * ((1.0 - theta) * lam_v + theta * lam_v[::-1]) + farm   # residents
    col = G ** (-mu) * N ** (-delta)          # real value of one unit of income where you live
    # real return to a job in r: (1-theta) of the time you live in r, theta in s
    omega = w * ((1.0 - theta) * col + theta * col[::-1])
    return dict(w=w, G=G, Y=Y, N=N, omega=omega)


def wage_gap(lam, T, **kw):
    """omega_1 - omega_2: the incentive to move into region 1."""
    o = short_run(lam, T, **kw)["omega"]
    return o[0] - o[1]


def T_of(phi, sigma):
    return phi ** (1.0 / (1.0 - sigma))


def sustain_lhs(phi, sigma, mu):
    """omega_2 / omega_1 at full agglomeration in region 1 (closed form).
    The core-periphery outcome is sustainable when this is below one."""
    w2 = ((1 + mu) / 2 * phi + (1 - mu) / 2 / phi) ** (1.0 / sigma)
    return w2 * phi ** (mu / (sigma - 1.0))


def break_point_phi(sigma, mu):
    """Closed-form break point (Baldwin et al. 2003, Economic Geography and
    Public Policy, ch. 2, in FKV's normalisation)."""
    return ((1 - mu) * (sigma - 1 - sigma * mu)) / ((1 + mu) * (sigma - 1 + sigma * mu))


def bisect(f, a, b, it=200):
    fa = f(a)
    for _ in range(it):
        m = 0.5 * (a + b)
        fm = f(m)
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return 0.5 * (a + b)


if __name__ == "__main__":
    sigma, mu = 5.0, 0.4
    # numerical break point: where the slope of the gap at 1/2 changes sign
    slope = lambda T: (wage_gap(0.5 + 1e-4, T, sigma=sigma, mu=mu) - wage_gap(0.5 - 1e-4, T, sigma=sigma, mu=mu)) / 2e-4
    T_B_num = bisect(slope, 1.01, 3.0)
    print("break point T: numeric", T_B_num, " closed form", T_of(break_point_phi(sigma, mu), sigma))
    # numerical sustain point: where omega_2/omega_1 at lam=1 equals one
    ratio = lambda T: short_run(1.0, T, sigma=sigma, mu=mu)["omega"][1] / short_run(1.0, T, sigma=sigma, mu=mu)["omega"][0] - 1
    T_S_num = bisect(ratio, 1.01, 3.0)
    T_S_cf = T_of(bisect(lambda p: sustain_lhs(p, sigma, mu) - 1, 0.05, 0.999), sigma)
    print("sustain point T: numeric", T_S_num, " closed form", T_S_cf)
