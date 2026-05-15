from __future__ import annotations

from typing import Any

from common import (
    START_YEAR,
    END_YEAR,
    PROCESSED_DIR,
    fetch_bps_json,
    fetch_world_bank_indicators,
    write_csv,
    year_rows,
)


INDICATORS = {
    "cpi_total": "FP.CPI.TOTL",
}

FIELDS = [
    "year",
    "rice_price",
    "fuel_price",
    "electricity_index",
    "rent_index",
    "education_index",
    "healthcare_index",
    "restaurant_index",
    "cpi_total",
    "source",
]


def extract_bps_rice_prices(payload: dict[str, Any] | None) -> dict[int, float]:
    if not payload or payload.get("status") != "OK":
        return {}

    variables = payload.get("var") or []
    regions = payload.get("vervar") or []
    turvars = payload.get("turvar") or []
    years = payload.get("tahun") or []
    subyears = payload.get("turtahun") or []
    values = payload.get("datacontent") or {}

    if not variables or not regions or not turvars:
        return {}

    variable_code = str(variables[0]["val"])
    region_code = str(regions[0]["val"])
    turvar_code = str(turvars[0]["val"])
    annual_subyear = next(
        (str(item["val"]) for item in subyears if str(item.get("label", "")).lower() == "tahunan"),
        None,
    )
    if annual_subyear is None:
        return {}

    rice_prices: dict[int, float] = {}
    for item in years:
        year = int(item["label"])
        if not START_YEAR <= year <= END_YEAR:
            continue

        year_code = str(item["val"])
        key = f"{region_code}{variable_code}{turvar_code}{year_code}{annual_subyear}"
        value = values.get(key)
        if value is not None:
            rice_prices[year] = float(value)

    return rice_prices


def fetch_bps_rice_prices() -> dict[int, float]:
    rice_prices: dict[int, float] = {}
    bps_year_codes = list(range(START_YEAR - 1900, END_YEAR - 1900 + 1))

    for index in range(0, len(bps_year_codes), 3):
        chunk = bps_year_codes[index : index + 3]
        th_value = f"{chunk[0]}:{chunk[-1]}" if len(chunk) > 1 else str(chunk[0])
        payload = fetch_bps_json(
            [
                "list",
                "model",
                "data",
                "lang",
                "ind",
                "domain",
                "0000",
                "var",
                "295",
                "th",
                th_value,
            ],
            f"bps_rice_price_grosir_{th_value.replace(':', '_')}",
        )
        rice_prices.update(extract_bps_rice_prices(payload))

    return rice_prices


if __name__ == "__main__":
    world_bank_data = fetch_world_bank_indicators(INDICATORS, "worldbank_cost_of_living")
    rows_by_year = year_rows()

    for column, values in world_bank_data.items():
        for year, value in values.items():
            rows_by_year[year][column] = value

    for year, value in fetch_bps_rice_prices().items():
        rows_by_year[year]["rice_price"] = value

    for row in rows_by_year.values():
        row["source"] = (
            "World Bank API CPI total; BPS WebAPI var 295 for wholesale rice price; "
            "remaining item/category indicators require BPS table mapping"
        )

    rows = [rows_by_year[year] for year in sorted(rows_by_year)]
    write_csv(
        PROCESSED_DIR / "cost_of_living_indonesia.csv",
        rows,
        FIELDS,
    )
