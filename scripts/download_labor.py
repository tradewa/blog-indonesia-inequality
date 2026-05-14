from common import merge_indicator_rows


INDICATORS = {
    "unemployment_rate": "SL.UEM.TOTL.ZS",
    "youth_unemployment": "SL.UEM.1524.ZS",
    "vulnerable_employment_share": "SL.EMP.VULN.ZS",
}

FIELDS = [
    "year",
    "unemployment_rate",
    "youth_unemployment",
    "avg_wage",
    "real_wage_growth",
    "informal_employment_share",
    "vulnerable_employment_share",
    "source",
]


if __name__ == "__main__":
    merge_indicator_rows(
        INDICATORS,
        "worldbank_labor",
        "labor_indonesia.csv",
        FIELDS,
        source="World Bank API; wage and informal employment columns require BPS/ILOSTAT follow-up",
    )
