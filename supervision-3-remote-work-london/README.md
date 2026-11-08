# Has remote work made London more dominant?

Paper 7 (Regional Economics and Policy), Supervision 3, Part A. Milo Sinclair, November 2026.

**The website (`site/index.html`) is the write-up.** This repository holds the data, the code that produced every number on it, and the script that builds it.

## Objective and approach

Krugman's (1991) core–periphery model says remote work should pull London two ways: cheaper trade in services concentrates activity in the biggest market, while people earning in London but living and spending elsewhere (θ, which I add to the model) weakens the spending that holds a cluster together. Since the trade cost cannot be measured directly, I measure the net result (did remote-able jobs move towards London?) and the leak (did more London pay go to non-residents?) using ONS data from 2015–2025.

## Results

| | Result |
|---|---|
| London's share of GB remote-able jobs | 30.9% (2015–19) → 33.2% (2022–24); in-person 13.5% → 13.9% |
| Main test (difference-in-differences, BRES) | +6.0% (p = 0.056) |
| Allowing pre-2020 trends, BRES | +11.1% (p = 0.062) |
| Placebo (pretend remote work began in 2017, 2015–19 data only) | −4.6%: no false London gain |
| Greater South East vs GB | -1.0% (p = 0.424) |
| London within the Greater South East | +6.7% (p = 0.005) |
| Share of London workplace pay going to non-residents (ASHE) | 26.8% (2015–19) → 29.8% (2022–25) |

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Question | Has remote work made London more dominant? | Remote work is the biggest recent change to the cost of distance, so a direct test of Krugman's model |
| Theory | Krugman (1991) in the Fujita–Krugman–Venables form, plus θ | θ (wages spent in the other region) captures earning in one place and spending in another; θ = 0 is Krugman |
| Model settings | σ = 5, μ = 0.4 | Standard textbook values; the code reproduces the textbook break (T = 1.6266) and sustain (T = 1.8073) points |
| What to measure | The net jobs outcome and the pay leak | The trade cost of services cannot be measured directly |
| Jobs data | ONS BRES, jobs by workplace, 2-digit industries, 2015–2024 | Finest industry detail by region |
| Remote-able vs in-person | ONS BICS Dec 2023: hybrid + home share > 50% remote-able, < 25% in-person, in between left out (finance: UKHLS 84%) | A written rule from official data, applied by SIC section (`common.py`) |
| Years | 2015–19 vs 2022–24; 2020–21 left out | Lockdowns distort 2020–21 |
| Test | Difference-in-differences: log London share on industry and year effects + remote-able × post-2020, weighted by size, clustered by industry | Compares remote-able with in-person industries, so changes common to both cancel out  |
| Checks | Year-by-year gaps, 2017 placebo, pre-2020 trends, unweighted, drop finance / info & comms / hospitality | To test whether the result is an old trend, one sector, or an artefact of the method |
| Boundaries | London; London + South East + East; London within that wider region | A region should be a functional (commuting) area |
| Pay leak | 1 − (London residents' pay bill ÷ London workplace pay bill), ASHE | Measures pay earned in London by people living outside it |

## Files and how to run

| Order | File | What it does |
|---|---|---|
| 0 | `fetch_data.py` | Downloads BRES (NM_189_1), ASHE (NM_99_1, NM_30_1) from the Nomis API into `data/` |
| – | `common.py` | Shared settings: years compared and the remote-able / in-person rule with its ONS source |
| 1 | `analysis.py` | Shares, main test, year-by-year gaps, placebo, per-industry changes, pay leak → `results/main.json` |
| 2 | `robustness.py` | Pre-2020 trends, unweighted, dropping sectors → `results/robustness.json` |
| 3 | `region_test.py` | The three boundary definitions and each region's change → `results/regions.json` |
| 4 | `model.py`, `model_results.py` | Krugman's model with θ; tipping points and the trade-off numbers → `results/model.json` |
| 5 | `build_site.py` | Builds `site/index.html` from the results and `site/template_body.html`, so no number on the page is typed by hand |

```
pip install requests pandas numpy statsmodels
python fetch_data.py
python analysis.py && python robustness.py && python region_test.py && python model_results.py
python build_site.py
```

The data in `data/` is the snapshot downloaded in November 2026 that the website uses.
