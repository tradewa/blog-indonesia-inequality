from __future__ import annotations

import csv
import gzip
import io
import urllib.request
from typing import Any

from common import (
    START_YEAR,
    END_YEAR,
    PROCESSED_DIR,
    RAW_DIR,
    fetch_world_bank_indicators,
    write_csv,
    year_rows,
)


INDICATORS = {
    "unemployment_rate": "SL.UEM.TOTL.ZS",
    "youth_unemployment": "SL.UEM.1524.ZS",
    "vulnerable_employment_share": "SL.EMP.VULN.ZS",
}

DEFLATOR_INDICATORS = {
    "cpi_total": "FP.CPI.TOTL",
}

ILOSTAT_WAGE_URL = (
    "https://rplumber.ilo.org/data/indicator/"
    "?channel=ilostat&format=.csv.gz&id=EAR_EMTA_SEX_NB_A&type=code"
)

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


def fetch_ilostat_average_monthly_earnings() -> dict[int, float]:
    request = urllib.request.Request(
        ILOSTAT_WAGE_URL,
        headers={"User-Agent": "indonesia-inequality-data-ingestion/0.1"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "ilostat_average_monthly_earnings_EAR_EMTA_SEX_NB_A.csv.gz").write_bytes(payload)

    text = gzip.decompress(payload).decode("utf-8-sig")
    rows = csv.DictReader(io.StringIO(text))

    values: dict[int, float] = {}
    for row in rows:
        if row.get("ref_area") != "IDN" or row.get("sex") != "SEX_T":
            continue

        year = int(row["time"])
        if START_YEAR <= year <= END_YEAR and row.get("obs_value"):
            values[year] = round(float(row["obs_value"]))

    return values


def calculate_real_wage_growth(
    avg_wage: dict[int, float],
    cpi_total: dict[int, float | None],
) -> dict[int, float]:
    real_wage = {
        year: wage / float(cpi_total[year]) * 100
        for year, wage in avg_wage.items()
        if cpi_total.get(year) not in (None, "")
    }

    growth: dict[int, float] = {}
    for year in sorted(real_wage):
        previous_year = year - 1
        if previous_year not in real_wage:
            continue
        growth[year] = (real_wage[year] / real_wage[previous_year] - 1) * 100

    return growth


if __name__ == "__main__":
    labor_data = fetch_world_bank_indicators(INDICATORS, "worldbank_labor")
    deflator_data = fetch_world_bank_indicators(DEFLATOR_INDICATORS, "worldbank_labor_deflator")
    avg_wage = fetch_ilostat_average_monthly_earnings()
    real_wage_growth = calculate_real_wage_growth(avg_wage, deflator_data["cpi_total"])
    rows_by_year = year_rows()

    for column, values in labor_data.items():
        for year, value in values.items():
            rows_by_year[year][column] = value

    for year, value in avg_wage.items():
        rows_by_year[year]["avg_wage"] = value

    for year, value in real_wage_growth.items():
        rows_by_year[year]["real_wage_growth"] = value

    for row in rows_by_year.values():
        row["source"] = (
            "World Bank API for unemployment and vulnerable employment; "
            "ILOSTAT EAR_EMTA_SEX_NB_A for average monthly earnings of employees; "
            "World Bank CPI total used to calculate real wage growth"
        )

    rows = [rows_by_year[year] for year in sorted(rows_by_year)]
    write_csv(PROCESSED_DIR / "labor_indonesia.csv", rows, FIELDS)
