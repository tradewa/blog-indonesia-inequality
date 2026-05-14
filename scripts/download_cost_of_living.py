from common import merge_indicator_rows


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


if __name__ == "__main__":
    merge_indicator_rows(
        INDICATORS,
        "worldbank_cost_of_living",
        "cost_of_living_indonesia.csv",
        FIELDS,
        source="World Bank API CPI total only; item/category indicators require BPS manual/API table mapping",
    )
