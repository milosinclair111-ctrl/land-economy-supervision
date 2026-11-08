"""STEP 0: download every dataset from the Nomis API (ONS). Run this first; it writes the CSVs in data/.
BRES NM_189_1: employment by workplace, 2-digit SIC 2007, GB regions, 2015-2024 (values in hundreds of jobs).
ASHE NM_99_1 (workplace) and NM_30_1 (residence): London number of jobs and mean/median annual gross pay."""
import io, re, requests, pandas as pd
from common import group_of_division
API = "https://www.nomisweb.co.uk/api/v01/dataset"
REGIONS = ",".join(str(2013265921 + i) for i in range(11))      # 11 GB regions (London = 2013265927)

codes = requests.get(f"{API}/NM_189_1/industry.def.sdmx.json").json()["structure"]["codelists"]["codelist"][0]["code"]
divs = [c["value"] for c in codes if re.match(r"^\d\d : ", c["description"]["value"])]
url = (f"{API}/NM_189_1.data.csv?geography={REGIONS}&industry={','.join(map(str, divs))}"
       "&employment_status=4&measure=1&measures=20100&time=2015-2024&select=geography_code,industry_name,date_name,obs_value")
b = pd.read_csv(io.StringIO(requests.get(url).text))
b["div"] = b.INDUSTRY_NAME.str[:2]
gb = b.groupby(["div", "DATE_NAME"]).OBS_VALUE.sum().unstack()
lon = b[b.GEOGRAPHY_CODE == "E12000007"].groupby(["div", "DATE_NAME"]).OBS_VALUE.sum().unstack()
out = pd.concat([lon.add_prefix("L"), gb.add_prefix("G")], axis=1).div(100).round().astype(int)
out = out[(out.filter(like="G").sum(1) > 0)]
out.index.name = "div"; out.to_csv("data/bres_london_gb_by_division.csv")

# Greater South East (London + South East + East) by division, for the boundary test
gse = b[b.GEOGRAPHY_CODE.isin(["E12000006", "E12000007", "E12000008"])].groupby(["div", "DATE_NAME"]).OBS_VALUE.sum().unstack()
gse = gse.loc[out.index].div(100).round().astype(int).add_prefix("S"); gse.index.name = "div"
gse.to_csv("data/bres_greater_south_east_by_division.csv")

# Each region's share of GB jobs in the remote-able (R) and in-person (P) groups
d = b.copy()
d["group"] = d["div"].map(group_of_division)          # same rule as everything else (common.py)
d = d.dropna(subset=["group"])
reg = d.groupby(["GEOGRAPHY_CODE", "group", "DATE_NAME"]).OBS_VALUE.sum()
tot = d.groupby(["group", "DATE_NAME"]).OBS_VALUE.sum()
sh = (100 * reg / tot.reindex(reg.index.droplevel(0)).values).round(2).unstack()
names = {"E12000001":"North East","E12000002":"North West","E12000003":"Yorkshire and The Humber","E12000004":"East Midlands","E12000005":"West Midlands","E12000006":"East","E12000007":"London","E12000008":"South East","E12000009":"South West","W92000004":"Wales","S92000003":"Scotland"}
sh = sh.reset_index(); sh.insert(0, "region", sh.GEOGRAPHY_CODE.map(names)); sh.drop(columns="GEOGRAPHY_CODE").to_csv("data/bres_region_group_shares.csv", index=False)

def ashe(ds, geo):
    u = f"{API}/{ds}.data.csv?geography={geo}&sex=7&item=1,2,4&pay=7&measures=20100&time=2010-latest&select=item_name,date_name,obs_value"
    d = pd.read_csv(io.StringIO(requests.get(u).text)).pivot(index="DATE_NAME", columns="ITEM_NAME", values="OBS_VALUE")
    return d.rename(columns={"Number of jobs": "jobs", "Mean": "mean", "Median": "median"})
wp, res, g = ashe("NM_99_1", 2013265927), ashe("NM_30_1", 2013265927), ashe("NM_99_1", 2092957698)
a = pd.DataFrame({"wp_jobs": wp.jobs, "wp_mean": wp["mean"], "wp_median": wp["median"],
                  "res_jobs": res.jobs, "res_mean": res["mean"], "res_median": res["median"], "gb_mean": g["mean"]})
a.index.name = "year"; a.to_csv("data/ashe_london_workplace_vs_residence.csv")
print("saved data/")
