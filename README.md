# Indonesia Inequality Data Ingestion

This repository contains a reproducible ingestion pipeline for official/public datasets that can support a later Indonesia economic inequality project.

Current scope is limited to:

- identify source datasets
- download/access raw data
- minimally clean annual records
- standardize schemas
- save local raw and processed files

No trend analysis, modeling, dashboarding, or narrative generation is included.

## Folder Structure

```text
data/
  raw/
  processed/
scripts/
README.md
```

## Run

Python 3.11+ is sufficient. The current scripts use the Python standard library only.

```bash
.venv/bin/python scripts/download_all.py
```

Run individual datasets independently:

```bash
.venv/bin/python scripts/download_gdp.py
.venv/bin/python scripts/download_inflation.py
.venv/bin/python scripts/download_inequality.py
.venv/bin/python scripts/download_poverty.py
.venv/bin/python scripts/download_labor.py
.venv/bin/python scripts/download_cost_of_living.py
```

Raw JSON responses are saved in `data/raw/`. Standardized yearly CSVs are saved in `data/processed/`.

## Source Summary

### GDP and Economic Growth

Output: `data/processed/gdp_indonesia.csv`

Source: World Bank API, country `IDN`

Indicators:

- `NY.GDP.MKTP.KD.ZG`: GDP growth, annual %
- `NY.GDP.PCAP.KD`: GDP per capita, constant 2015 US$
- `NY.GDP.PCAP.CD`: GDP per capita, current US$

Columns:

- `year`
- `gdp_growth`
- `real_gdp_per_capita`
- `nominal_gdp_per_capita`
- `source`

### Inflation / CPI

Output: `data/processed/inflation_indonesia.csv`

Source: World Bank API, country `IDN`

Indicators:

- `FP.CPI.TOTL`: Consumer price index
- `FP.CPI.TOTL.ZG`: Inflation, consumer prices, annual %

Columns:

- `year`
- `cpi_total`
- `inflation_yoy`
- `cpi_food`
- `cpi_transport`
- `cpi_housing`
- `cpi_education`
- `cpi_healthcare`
- `cpi_restaurant`
- `source`

Limitations:

- World Bank API covers total CPI and annual inflation, not the requested Indonesia CPI categories.
- Category CPI should be added from BPS once the relevant dynamic/static table IDs are confirmed.

### Inequality / Distribution

Output: `data/processed/inequality_indonesia.csv`

Source: World Bank API, country `IDN`

Indicators:

- `SI.POV.GINI`: Gini index
- `SI.DST.FRST.20`: income or consumption share, lowest 20%
- `SI.DST.02ND.20`: income or consumption share, second 20%
- `SI.DST.03RD.20`: income or consumption share, third 20%
- `SI.DST.04TH.20`: income or consumption share, fourth 20%
- `SI.DST.05TH.20`: income or consumption share, highest 20%

Derived fields:

- `expenditure_bottom40` = lowest 20% + second 20%
- `expenditure_middle40` = third 20% + fourth 20%
- `expenditure_top20` = highest 20%

Limitations:

- World Bank distribution indicators may be based on income or consumption depending on survey metadata. Treat these as distribution shares until BPS/SUSENAS expenditure-only tables are mapped.

### Poverty

Output: `data/processed/poverty_indonesia.csv`

Source: World Bank API, country `IDN`

Indicators:

- `SI.POV.NAHC`: poverty headcount ratio at national poverty lines
- `SI.POV.DDAY`: poverty headcount ratio at $2.15/day, 2017 PPP

Columns:

- `year`
- `poverty_rate`
- `extreme_poverty_rate`
- `source`

### Labor Market

Output: `data/processed/labor_indonesia.csv`

Source: World Bank API, country `IDN`

Indicators:

- `SL.UEM.TOTL.ZS`: unemployment, total
- `SL.UEM.1524.ZS`: unemployment, youth total ages 15-24
- `SL.EMP.VULN.ZS`: vulnerable employment, total

Columns:

- `year`
- `unemployment_rate`
- `youth_unemployment`
- `avg_wage`
- `real_wage_growth`
- `informal_employment_share`
- `vulnerable_employment_share`
- `source`

Limitations:

- Average wage, real wage growth, and informal employment share are not filled by the current World Bank script.
- These should be added from BPS labor force/wage tables or ILOSTAT after confirming stable annual series IDs.
- `vulnerable_employment_share` is included as a related labor-market indicator, not as a direct substitute for informal employment.

### Real-Life Cost Indicators

Output: `data/processed/cost_of_living_indonesia.csv`

Current source: World Bank API total CPI only.

Columns:

- `year`
- `rice_price`
- `fuel_price`
- `electricity_index`
- `rent_index`
- `education_index`
- `healthcare_index`
- `restaurant_index`
- `cpi_total`
- `source`

Limitations:

- Rice prices, fuel prices, electricity/LPG, rent, education, healthcare, and restaurant/eating-out price indexes require BPS table mapping or another official source.
- The current CSV preserves the standardized schema and fills `cpi_total` only.

## BPS API Notes

BPS Web API endpoints follow the pattern:

```text
https://webapi.bps.go.id/v1/api/list/model/{model}/lang/ind/domain/0000/.../key/{BPS_API_KEY}
```

The national domain is `0000`.

This repo includes:

```bash
.venv/bin/python scripts/discover_bps_sources.py
```

That script attempts to pull the first national dynamic-table page and saves either:

- `data/raw/bps_dynamic_tables_page1.json`, or
- `data/raw/bps_dynamic_tables_page1_error.json`

At the time this pipeline was created, the local BPS API request did not return usable table metadata with the configured key. The reproducible run writes the HTTP status to `data/raw/bps_dynamic_tables_page1_error.json`, so BPS-backed fields are documented as follow-up gaps rather than populated unreproducibly.

## Manual Follow-Up Checklist

Use official BPS portals to identify stable table IDs for:

- CPI by expenditure group: food, transport, housing/electricity/fuel, education, healthcare, restaurants
- retail rice price or food commodity prices
- administered fuel/electricity/LPG price series if available
- wage or average wage annual series
- informal employment share
- SUSENAS expenditure distribution by decile/quintile

After table IDs are confirmed, add BPS-specific download scripts that save raw JSON/CSV to `data/raw/` and write yearly outputs to the existing CSV schemas in `data/processed/`.
