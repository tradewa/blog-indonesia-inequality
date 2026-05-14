from __future__ import annotations

import csv
import urllib.parse
from typing import Any

from common import PROCESSED_DIR, RAW_DIR, fetch_json, format_csv_value, save_json


START_YEAR = 2000
END_YEAR = 2024

INDICATORS = {
    "gini": "SI.POV.GINI",
    "gdp_per_capita_constant_2015_usd": "NY.GDP.PCAP.KD",
}

FIELDS = [
    "country_code",
    "country_name",
    "region",
    "income_level",
    "year",
    "gini",
    "gdp_per_capita_constant_2015_usd",
    "future_5y_growth_pct",
    "future_10y_growth_pct",
    "future_5y_end_year",
    "future_10y_end_year",
    "source",
]


def fetch_world_bank_pages(url: str) -> list[dict[str, Any]]:
    first_page = fetch_json(url)
    if not isinstance(first_page, list) or len(first_page) < 2:
        return []

    metadata = first_page[0]
    pages = int(metadata.get("pages", 1))
    rows = first_page[1] or []

    for page in range(2, pages + 1):
        page_url = f"{url}&page={page}"
        payload = fetch_json(page_url)
        if isinstance(payload, list) and len(payload) > 1 and payload[1]:
            rows.extend(payload[1])

    return rows


def fetch_countries() -> dict[str, dict[str, str]]:
    query = urllib.parse.urlencode({"format": "json", "per_page": 400})
    url = f"https://api.worldbank.org/v2/country?{query}"
    payload = fetch_json(url)
    save_json(payload, RAW_DIR / "worldbank_comparative_countries.json")

    countries: dict[str, dict[str, str]] = {}
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    for row in rows:
        code = row.get("id")
        region = (row.get("region") or {}).get("value")
        if not code or region == "Aggregates":
            continue

        countries[code] = {
            "country_name": row.get("name", ""),
            "region": region or "",
            "income_level": (row.get("incomeLevel") or {}).get("value", ""),
        }

    return countries


def fetch_indicator(indicator: str, raw_name: str) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "format": "json",
            "date": f"{START_YEAR}:{END_YEAR}",
            "per_page": 20000,
        }
    )
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?{query}"
    payload = fetch_json(url)
    save_json(payload, RAW_DIR / f"{raw_name}_{indicator}.json")
    return payload[1] if isinstance(payload, list) and len(payload) > 1 and payload[1] else []


def clean_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def annualized_growth(start_value: float | None, end_value: float | None, years: int) -> float | None:
    if start_value is None or end_value is None or start_value <= 0 or end_value <= 0:
        return None
    return ((end_value / start_value) ** (1 / years) - 1) * 100


def build_rows() -> list[dict[str, Any]]:
    countries = fetch_countries()
    values: dict[str, dict[str, dict[int, float]]] = {
        column: {} for column in INDICATORS
    }

    for column, indicator in INDICATORS.items():
        for row in fetch_indicator(indicator, "worldbank_comparative"):
            country_code = row.get("countryiso3code")
            if not country_code or country_code not in countries:
                continue

            year = int(row["date"])
            value = clean_number(row.get("value"))
            if value is None:
                continue

            values[column].setdefault(country_code, {})[year] = value

    rows: list[dict[str, Any]] = []
    for country_code, gini_by_year in sorted(values["gini"].items()):
        gdp_by_year = values["gdp_per_capita_constant_2015_usd"].get(country_code, {})
        country = countries[country_code]

        for year, gini in sorted(gini_by_year.items()):
            gdp = gdp_by_year.get(year)
            gdp_5y = gdp_by_year.get(year + 5)
            gdp_10y = gdp_by_year.get(year + 10)

            rows.append(
                {
                    "country_code": country_code,
                    "country_name": country["country_name"],
                    "region": country["region"],
                    "income_level": country["income_level"],
                    "year": year,
                    "gini": gini,
                    "gdp_per_capita_constant_2015_usd": gdp,
                    "future_5y_growth_pct": annualized_growth(gdp, gdp_5y, 5),
                    "future_10y_growth_pct": annualized_growth(gdp, gdp_10y, 10),
                    "future_5y_end_year": year + 5 if gdp_5y is not None else "",
                    "future_10y_end_year": year + 10 if gdp_10y is not None else "",
                    "source": "World Bank API: SI.POV.GINI and NY.GDP.PCAP.KD",
                }
            )

    return rows


def write_csv(path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_csv_value(row.get(field, "")) for field in FIELDS})


if __name__ == "__main__":
    write_csv(
        PROCESSED_DIR / "comparative_inequality_growth.csv",
        build_rows(),
    )
