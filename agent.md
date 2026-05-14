# Agent Handoff Notes

## Part 1: Data Downloading and Ingestion

Status: completed as a reproducible first pass.

The first part of the project is a data ingestion pipeline only. It identifies official/public sources, downloads raw API responses, minimally standardizes annual data, and writes local processed CSVs. It does not perform modeling, interpretation, dashboards, or essay generation.

## Current Source Strategy

World Bank API is the working source for the baseline pipeline because it provides stable country-level annual indicators for Indonesia (`IDN`) and does not require an API key.

BPS is the preferred source for more Indonesia-specific fields, especially category CPI, commodity prices, wages, informal employment, and SUSENAS expenditure distribution. However, the BPS Web API was returning a server-side failure during this setup, so BPS-backed fields are intentionally left blank instead of being fabricated or manually copied without a reproducible source.

## How to Rebuild the Downloaded Data

Run all current download scripts:

```bash
.venv/bin/python scripts/download_all.py
```

Run BPS source discovery separately:

```bash
.venv/bin/python scripts/discover_bps_sources.py
```

The scripts write raw responses to:

```text
data/raw/
```

The scripts write standardized CSVs to:

```text
data/processed/
```

## Generated Processed Files

- `data/processed/gdp_indonesia.csv`
- `data/processed/inflation_indonesia.csv`
- `data/processed/inequality_indonesia.csv`
- `data/processed/poverty_indonesia.csv`
- `data/processed/labor_indonesia.csv`
- `data/processed/cost_of_living_indonesia.csv`

Each processed file currently contains annual rows from 2000 through 2024. The project intentionally excludes 2025 for now to avoid treating not-yet-published values as missing data.

## World Bank Indicators Used

GDP:

- `NY.GDP.MKTP.KD.ZG`: GDP growth, annual %
- `NY.GDP.PCAP.KD`: GDP per capita, constant 2015 US$
- `NY.GDP.PCAP.CD`: GDP per capita, current US$

Inflation:

- `FP.CPI.TOTL`: consumer price index
- `FP.CPI.TOTL.ZG`: inflation, consumer prices, annual %

Inequality:

- `SI.POV.GINI`: Gini index
- `SI.DST.FRST.20`: income or consumption share, lowest 20%
- `SI.DST.02ND.20`: income or consumption share, second 20%
- `SI.DST.03RD.20`: income or consumption share, third 20%
- `SI.DST.04TH.20`: income or consumption share, fourth 20%
- `SI.DST.05TH.20`: income or consumption share, highest 20%

Poverty:

- `SI.POV.NAHC`: poverty headcount ratio at national poverty lines
- `SI.POV.DDAY`: poverty headcount ratio at $2.15/day, 2017 PPP

Labor:

- `SL.UEM.TOTL.ZS`: unemployment, total
- `SL.UEM.1524.ZS`: unemployment, youth total ages 15-24
- `SL.EMP.VULN.ZS`: vulnerable employment, total

Cost of living:

- `FP.CPI.TOTL`: current placeholder only for total CPI

## BPS API Status

The BPS Web API endpoint pattern used by the discovery script is:

```text
https://webapi.bps.go.id/v1/api/list/model/dynamictable/lang/ind/domain/0000/page/1/key/{BPS_API_KEY}
```

During the reproducible run, the BPS API did not return usable data. The exact error is saved at:

```text
data/raw/bps_dynamic_tables_page1_error.json
```

This means the current repository records the BPS problem as part of the data provenance. When BPS comes back online, rerun `scripts/discover_bps_sources.py` and use the returned table metadata to add BPS-specific download scripts.

## Known Gaps for Part 1

These fields still need BPS table IDs or another official API source:

- CPI by category: food, transport, housing, education, healthcare, restaurants
- rice and other food prices
- fuel, electricity, and LPG prices or indexes
- rent or housing cost index
- average wage
- real wage growth
- informal employment share
- expenditure distribution specifically from SUSENAS/BPS

## Part 2 Starting Point

The initial exploratory notebook is:

```text
notebooks/eda_indonesia_inequality.ipynb
```

It uses the processed CSVs currently available and explicitly visualizes missing fields caused by the BPS outage.
