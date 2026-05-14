from common import merge_indicator_rows


INDICATORS = {
    "cpi_total": "FP.CPI.TOTL",
    "inflation_yoy": "FP.CPI.TOTL.ZG",
}

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
    "source",
]


if __name__ == "__main__":
    merge_indicator_rows(INDICATORS, "worldbank_inflation", "inflation_indonesia.csv", FIELDS)
