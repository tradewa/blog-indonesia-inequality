from __future__ import annotations

import csv
import io
import urllib.request
from collections import defaultdict
from typing import Any

from common import PROCESSED_DIR, RAW_DIR, START_YEAR, END_YEAR, ensure_dirs, format_csv_value


PIP_PERCENTILES_URL = (
    "https://datacatalogfiles.worldbank.org/ddh-published/0063646/DR0090357/world_100bin.csv"
)

RAW_OUTPUT = RAW_DIR / "worldbank_pip_percentiles_indonesia.csv"
PROCESSED_OUTPUT = PROCESSED_DIR / "welfare_distribution_indonesia.csv"

GROUPS = {
    "Bottom 10%": range(1, 11),
    "Bottom 40%": range(1, 41),
    "Middle 40%": range(41, 81),
    "Top 20%": range(81, 101),
    "Top 10%": range(91, 101),
}

FIELDS = [
    "year",
    "group",
    "welfare_type",
    "avg_welfare_ppp_daily",
    "population_share",
    "welfare_share",
    "population",
    "source",
]


def clean_number(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def read_pip_indonesia_rows() -> list[dict[str, str]]:
    ensure_dirs()
    request = urllib.request.Request(
        PIP_PERCENTILES_URL,
        headers={"User-Agent": "indonesia-inequality-data-ingestion/0.1"},
    )

    rows: list[dict[str, str]] = []
    with urllib.request.urlopen(request, timeout=120) as response:
        text = io.TextIOWrapper(response, encoding="utf-8", newline="")
        reader = csv.DictReader(text)

        with RAW_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                if row.get("country_code") != "IDN":
                    continue
                if row.get("reporting_level") != "national":
                    continue

                year = int(row["year"])
                if START_YEAR <= year <= END_YEAR:
                    writer.writerow(row)
                    rows.append(row)

    return rows


def weighted_average(rows: list[dict[str, Any]], value_col: str, weight_col: str) -> float | None:
    numerator = 0.0
    denominator = 0.0

    for row in rows:
        value = clean_number(row.get(value_col))
        weight = clean_number(row.get(weight_col))
        if value is None or weight is None:
            continue

        numerator += value * weight
        denominator += weight

    if denominator == 0:
        return None
    return numerator / denominator


def aggregate_groups(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows_by_year: dict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (int(row["year"]), row["welfare_type"])
        rows_by_year[key].append(row)

    output_rows: list[dict[str, Any]] = []
    for (year, welfare_type), year_rows in sorted(rows_by_year.items()):
        for group, percentiles in GROUPS.items():
            percentile_set = set(percentiles)
            group_rows = [
                row for row in year_rows if int(float(row["percentile"])) in percentile_set
            ]
            if not group_rows:
                continue

            output_rows.append(
                {
                    "year": year,
                    "group": group,
                    "welfare_type": welfare_type,
                    "avg_welfare_ppp_daily": weighted_average(group_rows, "avg_welfare", "pop_share"),
                    "population_share": sum(
                        clean_number(row.get("pop_share")) or 0 for row in group_rows
                    ),
                    "welfare_share": sum(
                        clean_number(row.get("welfare_share")) or 0 for row in group_rows
                    ),
                    "population": sum(clean_number(row.get("pop")) or 0 for row in group_rows),
                    "source": "World Bank PIP percentiles, 2017 PPP USD per person per day",
                }
            )

    return output_rows


def write_processed(rows: list[dict[str, Any]]) -> None:
    PROCESSED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with PROCESSED_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_csv_value(row.get(field, "")) for field in FIELDS})


if __name__ == "__main__":
    indonesia_rows = read_pip_indonesia_rows()
    write_processed(aggregate_groups(indonesia_rows))
