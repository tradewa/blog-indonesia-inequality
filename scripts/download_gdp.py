from common import merge_indicator_rows


INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "nominal_gdp_lcu": "NY.GDP.MKTP.CN",
    "real_gdp_lcu": "NY.GDP.MKTP.KN",
    "nominal_gdp_per_capita_lcu": "NY.GDP.PCAP.CN",
    "real_gdp_per_capita_lcu": "NY.GDP.PCAP.KN",
    "real_gdp_per_capita": "NY.GDP.PCAP.KD",
    "nominal_gdp_per_capita": "NY.GDP.PCAP.CD",
}

FIELDS = [
    "year",
    "gdp_growth",
    "nominal_gdp_lcu",
    "real_gdp_lcu",
    "nominal_gdp_per_capita_lcu",
    "real_gdp_per_capita_lcu",
    "real_gdp_per_capita",
    "nominal_gdp_per_capita",
    "source",
]


if __name__ == "__main__":
    merge_indicator_rows(INDICATORS, "worldbank_gdp", "gdp_indonesia.csv", FIELDS)
