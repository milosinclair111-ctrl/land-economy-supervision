# Analysis

- Software / dependencies: Python 3 with requests, pandas, numpy, statsmodels
- Input files and locations: `supervision-3-remote-work-london/data/` (written by `fetch_data.py`)
- Steps or commands, in order (run inside `supervision-3-remote-work-london/`):
  1. `python fetch_data.py`: download BRES and ASHE from Nomis
  2. `python analysis.py`: London shares, main difference-in-differences, year-by-year gaps, placebo, pay leak
  3. `python robustness.py`: pre-2020 trends, unweighted, dropping sectors
  4. `python region_test.py`: three boundary definitions of London
  5. `python model_results.py`: Krugman model with θ (uses `model.py`)
  6. `python build_site.py`: builds `site/index.html` from the results
- Output files: `supervision-3-remote-work-london/results/*.json` and `supervision-3-remote-work-london/site/index.html`

Rebuilding from scratch reproduces `site/index.html` exactly.
