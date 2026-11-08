# Workflow

## Decisions

- Question: chosen because remote work is the biggest recent change to the cost of distance.
- Theory: Krugman (1991) with θ added; σ = 5, μ = 0.4. Check: the code reproduces the textbook break point (T = 1.6266) and sustain point (T = 1.8073).
- Data: BRES for jobs (finest industry detail by region), ASHE for pay by workplace and by residence.
- Groups: written rule from ONS BICS data (above 50% remote-able, below 25% in-person, in between left out).
- Years: 2015–19 against 2022–24, leaving out the lockdown years 2020–21.
- Test: difference-in-differences with industry and year effects, weighted by size, clustered by industry.
- Checks: year-by-year gaps, 2017 placebo, pre-2020 trends, unweighted, dropping finance, information and communication, and hospitality.
- Boundaries: London; London + South East + East; London within that wider region.
- A second, coarser dataset (ONS Workforce Jobs) was tried and left out of the final version.

## Checks

- Model reproduces published tipping points to seven significant figures.
- Every number on the website is filled in by `build_site.py` from the results files, not typed by hand.
- Deleting all results and rerunning the scripts reproduces `site/index.html` byte for byte.

## Tools

- Python (requests, pandas, numpy, statsmodels) for the data and analysis; the Nomis API for ONS data; HTML and JavaScript for the website.
