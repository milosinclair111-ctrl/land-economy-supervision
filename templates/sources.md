# Sources

## Dataset 1: Business Register and Employment Survey (BRES)

- Provider and URL: ONS, via the Nomis API, dataset NM_189_1 (https://www.nomisweb.co.uk/)
- Version / dates: 2015–2024, downloaded November 2026
- Download steps: `fetch_data.py`
- Coverage and unit of observation: employee jobs by workplace, 2-digit SIC 2007 industry × region (GB regions)
- Variables and units: number of jobs
- Access / reuse terms: Open Government Licence

## Dataset 2: Annual Survey of Hours and Earnings (ASHE)

- Provider and URL: ONS, via Nomis, NM_99_1 (by workplace) and NM_30_1 (by residence)
- Version / dates: 2010–2025, downloaded November 2026
- Download steps: `fetch_data.py`
- Coverage and unit of observation: London, all employee jobs, annual
- Variables and units: number of jobs; mean and median gross annual pay (£)
- Access / reuse terms: Open Government Licence

## Dataset 3: classification of industries

- Provider and URL: ONS Business Insights and Conditions Survey, December 2023, share of businesses using hybrid working or working from home, by industry (https://www.ons.gov.uk/visualisations/dvc3086/fig06/index.html); finance from UKHLS January 2021 via POSTbrief 49
- Use: remote-able if above 50%, in-person if below 25%, in between left out (`common.py`)
