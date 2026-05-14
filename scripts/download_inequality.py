from common import merge_indicator_rows


INDICATORS = {
    "gini_ratio": "SI.POV.GINI",
    "quintile_1_share": "SI.DST.FRST.20",
    "quintile_2_share": "SI.DST.02ND.20",
    "quintile_3_share": "SI.DST.03RD.20",
    "quintile_4_share": "SI.DST.04TH.20",
    "quintile_5_share": "SI.DST.05TH.20",
}

FIELDS = [
    "year",
    "gini_ratio",
    "expenditure_bottom40",
    "expenditure_middle40",
    "expenditure_top20",
    "source",
]

DERIVED = {
    "expenditure_bottom40": ("quintile_1_share", "quintile_2_share"),
    "expenditure_middle40": ("quintile_3_share", "quintile_4_share"),
    "expenditure_top20": ("quintile_5_share",),
}


if __name__ == "__main__":
    merge_indicator_rows(
        INDICATORS,
        "worldbank_inequality",
        "inequality_indonesia.csv",
        FIELDS,
        source="World Bank API: distribution shares are income or consumption shares depending on survey metadata",
        derived=DERIVED,
    )
