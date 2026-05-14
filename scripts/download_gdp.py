from common import merge_indicator_rows


INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "real_gdp_per_capita": "NY.GDP.PCAP.KD",
    "nominal_gdp_per_capita": "NY.GDP.PCAP.CD",
}

FIELDS = [
    "year",
    "gdp_growth",
    "real_gdp_per_capita",
    "nominal_gdp_per_capita",
    "source",
]


if __name__ == "__main__":
    merge_indicator_rows(INDICATORS, "worldbank_gdp", "gdp_indonesia.csv", FIELDS)
