"""
Shared settings used by every script: the years compared, and the rule for
which industries count as remote-able or in-person.

THE CLASSIFICATION RULE
An industry's group is set by its SIC 2007 section, using the ONS Business
Insights and Conditions Survey (BICS), December 2023: the share of businesses
(weighted by employment) where staff were "using a hybrid model of working"
or "working from home".
    remote-able  : more than 50%
    in-person    : less than 25%
    in between   : left out, so the two groups are clearly different
BICS does not cover finance (section K). For finance I use the UK Household
Longitudinal Study figure that 84% of finance and insurance workers worked
from home in January 2021 (cited in POSTbrief 49, UK Parliament, 2022),
which puts it well above the 50% line.

Source of the BICS table: ONS, "Who are the hybrid workers?" (11 November 2024),
figure 6, chart data at https://www.ons.gov.uk/visualisations/dvc3086/fig06/index.html
"""

YEARS = list(range(2015, 2025))      # BRES years available
PRE = [2015, 2016, 2017, 2018, 2019]  # before remote work
POST = [2022, 2023, 2024]             # after; 2020-21 left out because lockdowns distort them

# ONS BICS, December 2023: % of businesses using hybrid working + % working from home
HOMEWORKING = {
    "J": ("Information and communication", 48.6 + 28.3),
    "M": ("Professional, scientific and technical", 42.3 + 18.1),
    "P": ("Education", 36.5 + 10.7),
    "L": ("Real estate", 28.7 + 11.3),
    "N": ("Administrative and support", 18.4 + 8.9),
    "R": ("Arts, entertainment and recreation", 14.9 + 4.4),
    "G": ("Wholesale and retail", 13.8 + 6.0),
    "Q": ("Health and social work", 13.7 + 6.3),
    "C": ("Manufacturing", 11.4 + 4.0),
    "F": ("Construction", 9.2 + 4.8),
    "H": ("Transport and storage", 8.8 + 2.4),
    "S": ("Other services", 4.8 + 5.0),
    "I": ("Accommodation and food", 3.7 + 2.4),
    "K": ("Finance and insurance (UKHLS, Jan 2021)", 84.0),   # not covered by BICS; see note above
}
REMOTE_MIN, INPERSON_MAX = 50, 25


def group_of_section(section):
    """'R' remote-able, 'P' in-person, or None (left out or no ONS figure)."""
    if section not in HOMEWORKING:
        return None
    rate = HOMEWORKING[section][1]
    return "R" if rate > REMOTE_MIN else "P" if rate < INPERSON_MAX else None


def section_of_division(d):
    """SIC 2007: map a two-digit division (e.g. 62) to its section letter (e.g. 'J')."""
    d = int(d)
    for lo, hi, s in [(1, 3, "A"), (5, 9, "B"), (10, 33, "C"), (35, 35, "D"), (36, 39, "E"), (41, 43, "F"),
                      (45, 47, "G"), (49, 53, "H"), (55, 56, "I"), (58, 63, "J"), (64, 66, "K"), (68, 68, "L"),
                      (69, 75, "M"), (77, 82, "N"), (84, 84, "O"), (85, 85, "P"), (86, 88, "Q"), (90, 93, "R"),
                      (94, 96, "S"), (97, 98, "T"), (99, 99, "U")]:
        if lo <= d <= hi:
            return s
    return None


def group_of_division(d):
    return group_of_section(section_of_division(d))
