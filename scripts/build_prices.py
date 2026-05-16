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
    "inflation_yoy": "FP.CPI.TOTL.ZG",
}

BPS_CATEGORY_CPI = {
    "cpi_food": "1905",
    "cpi_housing": "1907",
    "cpi_healthcare": "1909",
    "cpi_transport": "1910",
    "cpi_education": "1913",
    "cpi_restaurant": "1915",
}

BPS_CPI_YEAR_CODES = [120, 121, 122, 123]
BPS_CPI_CHUNK_SIZE = 3


FIELDS = [
    "year",
    "cpi_total",
    "inflation_yoy",
    "cpi_food",
    "cpi_transport",
    "cpi_housing",
    "cpi_education",
    "cpi_healthcare",
    "cpi_restaurant",
    "rice_price",
    "fuel_price",
    "electricity_index",
    "rent_index",
    "education_index",
    "healthcare_index",
    "restaurant_index",
    "source",
]


def extract_bps_category_cpi(payload: dict[str, Any] | None) -> dict[int, float]:
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
    national_region = next(
        (str(item["val"]) for item in regions if "INDONESIA" in str(item.get("label", "")).upper()),
        None,
    )
    annual_subyear = next(
        (
            str(item["val"])
            for item in subyears
            if str(item.get("label", "")).lower() in {"annual", "annually", "tahunan"}
        ),
        None,
    )
    december_subyear = next(
        (str(item["val"]) for item in subyears if str(item.get("label", "")).lower() in {"december", "desember"}),
        None,
    )
    if national_region is None or annual_subyear is None or december_subyear is None:
        return {}

    group_code = str(turvars[0]["val"])
    result: dict[int, float] = {}
    for item in years:
        year = int(item["label"])
        year_code = str(item["val"])
        annual_key = f"{national_region}{variable_code}{group_code}{year_code}{annual_subyear}"
        december_key = f"{national_region}{variable_code}{group_code}{year_code}{december_subyear}"
        value = values.get(annual_key, values.get(december_key))
        if value is not None:
            result[year] = float(value)

    return result


def fetch_bps_category_cpi() -> dict[str, dict[int, float]]:
    result: dict[str, dict[int, float]] = {column: {} for column in BPS_CATEGORY_CPI}
    chunks = [
        BPS_CPI_YEAR_CODES[index : index + BPS_CPI_CHUNK_SIZE]
        for index in range(0, len(BPS_CPI_YEAR_CODES), BPS_CPI_CHUNK_SIZE)
    ]

    for column, variable_id in BPS_CATEGORY_CPI.items():
        for chunk in chunks:
            th_value = f"{chunk[0]}:{chunk[-1]}" if len(chunk) > 1 else str(chunk[0])
            payload = fetch_bps_json(
                [
                    "list",
                    "model",
                    "data",
                    "lang",
                    "eng",
                    "domain",
                    "0000",
                    "var",
                    variable_id,
                    "th",
                    th_value,
                ],
                f"bps_cpi_category_{column}_{th_value.replace(':', '_')}",
            )
            result[column].update(extract_bps_category_cpi(payload))

    return result


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
    rows_by_year = year_rows()

    for column, values in fetch_world_bank_indicators(INDICATORS, "worldbank_prices").items():
        for year, value in values.items():
            rows_by_year[year][column] = value

    for column, values in fetch_bps_category_cpi().items():
        for year, value in values.items():
            rows_by_year[year][column] = value

    for year, value in fetch_bps_rice_prices().items():
        rows_by_year[year]["rice_price"] = value

    for row in rows_by_year.values():
        row["source"] = (
            "World Bank API for total CPI and inflation; BPS WebAPI December national CPI category "
            "indexes from variables 1905, 1907, 1909, 1910, 1913, and 1915 for 2020-2023 where available "
            "(2018=100 base; not stitched to older BPS CPI bases/category taxonomies); "
            "BPS WebAPI var 295 for wholesale rice price; remaining item/category indicators require BPS table mapping"
        )

    rows = [rows_by_year[year] for year in sorted(rows_by_year)]
    write_csv(PROCESSED_DIR / "prices_indonesia.csv", rows, FIELDS)
