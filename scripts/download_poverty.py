from common import merge_indicator_rows


INDICATORS = {
    "poverty_rate": "SI.POV.NAHC",
    "extreme_poverty_rate": "SI.POV.DDAY",
}

FIELDS = [
    "year",
    "poverty_rate",
    "extreme_poverty_rate",
    "source",
]


if __name__ == "__main__":
    merge_indicator_rows(INDICATORS, "worldbank_poverty", "poverty_indonesia.csv", FIELDS)
