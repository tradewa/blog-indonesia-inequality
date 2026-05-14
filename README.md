# Indonesia Inequality Project

This repository contains a phased Indonesia economic inequality project. It currently covers reproducible data ingestion, exploratory data analysis, and a first written analysis report.

The current repository does:

- identify usable official/public data sources
- download raw API responses
- standardize annual Indonesia-level records
- write processed CSVs for analysis
- provide an initial EDA notebook
- provide a markdown analysis report with generated charts

The current repository does not yet include final modeling, dashboarding, publication-ready narrative writing, or BPS-backed replacements for fields that still need stable BPS table mappings.

## Project Phases

### Phase 1: Data Ingestion

Status: completed as a reproducible first pass.

Phase 1 identifies official/public sources, downloads raw API responses, standardizes annual Indonesia-level records, and writes processed CSVs. Downloaded data is intentionally not committed to git; rebuild it locally with the scripts.

Primary outputs:

- `data/raw/`
- `data/processed/*.csv`
- `scripts/download_all.py`
- dataset-specific scripts in `scripts/`
- BPS discovery attempt through `scripts/discover_bps_sources.py`

### Phase 2: Exploratory Data Analysis

Status: completed as an initial EDA pass.

Phase 2 inspects processed data coverage, visualizes currently available fields, makes missing BPS-backed fields visible, and builds a combined annual table for future analysis work. It avoids causal claims and final narrative conclusions.

Primary outputs:

- `notebooks/eda_indonesia_inequality.ipynb`
- `notebooks/eda_indonesia_inequality.qmd`

The `.qmd` version is the R/Quarto equivalent of the notebook. It uses tidyverse-style data manipulation, `%>%` pipes, and `ggplot2`.

### Phase 3: Analysis Report

Status: completed as a first review draft.

Phase 3 turns the current EDA into a written markdown report with chart images. The report gives a provisional descriptive interpretation of the currently available data: strong GDP-per-capita growth and poverty reduction, alongside inequality indicators that remain above the early-2000s baseline.

Primary outputs:

- `reports/indonesia_inequality_eda_report.md`
- `reports/figures/*.png`

The Phase 3 report is review material, not a final publication. Its conclusions remain limited by missing BPS category CPI, cost-of-living, wage, informal-employment, and SUSENAS/BPS expenditure-distribution data.

## Repository Structure

```text
data/
  raw/                         Generated raw API responses, ignored by git
  processed/                   Generated standardized annual CSVs, ignored by git
notebooks/
  eda_indonesia_inequality.ipynb
  eda_indonesia_inequality.qmd
reports/
  indonesia_inequality_eda_report.md
  figures/                      Report chart images generated from notebook logic
scripts/
  common.py                    Shared fetch, clean, and CSV helpers
  download_all.py              Runs all World Bank-backed download scripts
  download_cost_of_living.py
  download_gdp.py
  download_inflation.py
  download_inequality.py
  download_labor.py
  download_poverty.py
  discover_bps_sources.py      Attempts BPS dynamic-table discovery
README.md
agent.md                       Handoff notes for future work
requirements.txt
renv.lock                      R package lockfile for Quarto/R analysis
renv/                          Project-local R environment scaffold
```

## Rebuild Data

Python 3.11+ is sufficient. The download scripts use the Python standard library only.

Fresh clone checklist:

```bash
python3 -m venv .venv
.venv/bin/python scripts/download_all.py
.venv/bin/python scripts/discover_bps_sources.py
```

Run all currently supported datasets:

```bash
.venv/bin/python scripts/download_all.py
```

Run individual datasets:

```bash
.venv/bin/python scripts/download_gdp.py
.venv/bin/python scripts/download_inflation.py
.venv/bin/python scripts/download_inequality.py
.venv/bin/python scripts/download_poverty.py
.venv/bin/python scripts/download_labor.py
.venv/bin/python scripts/download_cost_of_living.py
```

Run BPS source discovery separately:

```bash
.venv/bin/python scripts/discover_bps_sources.py
```

Raw JSON responses are saved locally in `data/raw/`. Standardized yearly CSVs are saved locally in `data/processed/`. These generated data files are ignored by git so the repository stays lightweight and reproducible.

## R / Quarto Environment

The R/Quarto notebook uses `renv` so R packages are restored into a project-local library instead of the global R library.

Restore the R environment:

```bash
Rscript -e "renv::restore()"
```

Render the Quarto EDA notebook:

```bash
quarto render notebooks/eda_indonesia_inequality.qmd
```

The `.qmd` expects Phase 1 data outputs to exist locally under `data/processed/`. Run `scripts/download_all.py` first if the processed CSVs are missing.

## Reproducibility Guarantees

The World Bank-backed outputs are reproducible from the scripts in this repository. Running `scripts/download_all.py` fetches the raw World Bank API responses and rebuilds the processed CSVs.

Current guarantees:

- Raw source responses are saved under `data/raw/`.
- Processed outputs are saved under `data/processed/`.
- Generated raw and processed data files are not committed to git.
- Processed outputs use annual Indonesia rows for 2000-2024.
- BPS-backed fields are intentionally blank until stable source IDs and reproducible download logic exist.
- Historical values may change if upstream providers revise their data.

This README and the source code are enough to reproduce the current pipeline from a fresh clone. `agent.md` is optional handoff context for future development, not required operating documentation.

## Source Strategy

World Bank API is the current working source for the baseline annual country-level pipeline because it provides stable Indonesia (`IDN`) indicators without an API key.

BPS is still the preferred source for Indonesia-specific fields such as detailed CPI categories, commodity prices, administered prices, wages, informal employment, and SUSENAS expenditure distributions. The current BPS discovery attempt did not return usable table metadata, so those fields are intentionally left blank rather than filled manually without a reproducible source.

## Processed Data

After running Phase 1, the processed files in `data/processed/` use one row per calendar year for Indonesia, currently covering 2000-2024. Some indicators have missing values when the upstream source has no observation for a year.

For this small project, the processed data dictionary is kept in the main README because there are only six processed files and the schemas are short. A separate `docs/data_dictionary.md` would be better once the documentation grows, the number of tables increases, or provenance notes become too detailed for the README.

Shared columns:

- `year`: calendar year of the observation.
- `source`: source note for the row. This also flags placeholder fields pending BPS, ILOSTAT, or another official source.

### `data/processed/gdp_indonesia.csv`

Annual GDP and GDP-per-capita indicators from the World Bank.

World Bank indicators:

- `NY.GDP.MKTP.KD.ZG`: GDP growth, annual %
- `NY.GDP.PCAP.KD`: GDP per capita, constant 2015 US$
- `NY.GDP.PCAP.CD`: GDP per capita, current US$

Columns:

- `year`: calendar year.
- `gdp_growth`: annual GDP growth rate, in percent.
- `real_gdp_per_capita`: GDP per capita in constant 2015 US dollars.
- `nominal_gdp_per_capita`: GDP per capita in current US dollars.
- `source`: data source.

### `data/processed/inflation_indonesia.csv`

Annual CPI and inflation indicators. Total CPI and annual inflation are populated from the World Bank; category CPI columns are reserved for future BPS-backed data.

World Bank indicators:

- `FP.CPI.TOTL`: consumer price index
- `FP.CPI.TOTL.ZG`: inflation, consumer prices, annual %

Columns:

- `year`: calendar year.
- `cpi_total`: consumer price index, total.
- `inflation_yoy`: annual consumer price inflation, in percent.
- `cpi_food`: food CPI category. Currently blank until a BPS source is mapped.
- `cpi_transport`: transport CPI category. Currently blank until a BPS source is mapped.
- `cpi_housing`: housing, utilities, electricity, gas, or fuel CPI category. Currently blank until a BPS source is mapped.
- `cpi_education`: education CPI category. Currently blank until a BPS source is mapped.
- `cpi_healthcare`: healthcare CPI category. Currently blank until a BPS source is mapped.
- `cpi_restaurant`: restaurant or eating-out CPI category. Currently blank until a BPS source is mapped.
- `source`: data source.

### `data/processed/inequality_indonesia.csv`

Annual inequality and distribution indicators from the World Bank. Distribution indicators may refer to income or consumption depending on survey metadata, so treat them as distribution shares until BPS/SUSENAS expenditure-only tables are mapped.

World Bank indicators:

- `SI.POV.GINI`: Gini index
- `SI.DST.FRST.10`: income or consumption share, lowest 10%
- `SI.DST.FRST.20`: income or consumption share, lowest 20%
- `SI.DST.02ND.20`: income or consumption share, second 20%
- `SI.DST.03RD.20`: income or consumption share, third 20%
- `SI.DST.04TH.20`: income or consumption share, fourth 20%
- `SI.DST.05TH.20`: income or consumption share, highest 20%
- `SI.DST.10TH.10`: income or consumption share, highest 10%

Derived fields:

- `expenditure_bottom40`: lowest 20% + second 20%
- `expenditure_middle40`: third 20% + fourth 20%
- `expenditure_top20`: highest 20%

Columns:

- `year`: calendar year.
- `gini_ratio`: Gini index. Higher values indicate greater inequality.
- `distribution_bottom10`: income or consumption share of the lowest decile, in percent.
- `expenditure_bottom40`: combined income or consumption share of the lowest two quintiles, in percent.
- `expenditure_middle40`: combined income or consumption share of the third and fourth quintiles, in percent.
- `expenditure_top20`: income or consumption share of the highest quintile, in percent.
- `distribution_top10`: income or consumption share of the highest decile, in percent.
- `source`: data source and survey-basis caveat.

### `data/processed/poverty_indonesia.csv`

Annual poverty indicators from the World Bank.

World Bank indicators:

- `SI.POV.NAHC`: poverty headcount ratio at national poverty lines
- `SI.POV.DDAY`: poverty headcount ratio at $2.15/day, 2017 PPP

Columns:

- `year`: calendar year.
- `poverty_rate`: poverty headcount ratio at national poverty lines, in percent of the population.
- `extreme_poverty_rate`: poverty headcount ratio at $2.15/day, 2017 PPP, in percent of the population.
- `source`: data source.

### `data/processed/labor_indonesia.csv`

Annual labor-market indicators. Unemployment and vulnerable employment are populated from the World Bank; wage and informal-employment fields are reserved for future BPS or ILOSTAT-backed data.

World Bank indicators:

- `SL.UEM.TOTL.ZS`: unemployment, total
- `SL.UEM.1524.ZS`: unemployment, youth total ages 15-24
- `SL.EMP.VULN.ZS`: vulnerable employment, total

Columns:

- `year`: calendar year.
- `unemployment_rate`: total unemployment rate, in percent of the labor force.
- `youth_unemployment`: unemployment rate for ages 15-24, in percent of the youth labor force.
- `avg_wage`: average wage. Currently blank until a BPS or ILOSTAT source is mapped.
- `real_wage_growth`: annual real wage growth. Currently blank until a BPS or ILOSTAT source is mapped.
- `informal_employment_share`: informal employment share. Currently blank until a BPS or ILOSTAT source is mapped.
- `vulnerable_employment_share`: vulnerable employment share, in percent of total employment. This is related to informal work but is not a direct substitute for informal employment.
- `source`: data source and follow-up note for blank fields.

### `data/processed/cost_of_living_indonesia.csv`

Annual real-life cost indicator schema. Only total CPI is currently populated from the World Bank; item and category fields are reserved for future BPS-backed data.

World Bank indicator:

- `FP.CPI.TOTL`: consumer price index

Columns:

- `year`: calendar year.
- `rice_price`: retail rice price. Currently blank until a BPS or official commodity-price source is mapped.
- `fuel_price`: fuel price. Currently blank until an official source is mapped.
- `electricity_index`: electricity, gas, or utilities price index. Currently blank until a BPS source is mapped.
- `rent_index`: rent or housing cost index. Currently blank until a BPS source is mapped.
- `education_index`: education cost index. Currently blank until a BPS source is mapped.
- `healthcare_index`: healthcare cost index. Currently blank until a BPS source is mapped.
- `restaurant_index`: restaurant or eating-out cost index. Currently blank until a BPS source is mapped.
- `cpi_total`: consumer price index, total.
- `source`: data source and follow-up note for blank fields.

## BPS API Status

BPS Web API endpoints follow this pattern:

```text
https://webapi.bps.go.id/v1/api/list/model/{model}/lang/ind/domain/0000/.../key/{BPS_API_KEY}
```

The national domain is `0000`. The current discovery script attempts to read the first national dynamic-table page:

```bash
.venv/bin/python scripts/discover_bps_sources.py
```

It saves one of these files:

- `data/raw/bps_dynamic_tables_page1.json`
- `data/raw/bps_dynamic_tables_page1_error.json`

The current repository contains `data/raw/bps_dynamic_tables_page1_error.json`, which records the failed discovery attempt. BPS-backed fields remain documented as follow-up gaps until stable table IDs and reproducible download logic are added.

## Notebook

The initial exploratory notebook is:

```text
notebooks/eda_indonesia_inequality.ipynb
```

The R/Quarto equivalent is:

```text
notebooks/eda_indonesia_inequality.qmd
```

Both versions use the processed CSVs and make missing BPS-backed fields visible instead of hiding or imputing them.

## Known Gaps

Use official BPS portals, BPS API metadata, ILOSTAT, or another official reproducible source to fill:

- CPI by expenditure group: food, transport, housing/electricity/fuel, education, healthcare, restaurants
- retail rice price or other food commodity prices
- administered fuel, electricity, or LPG price series
- rent or housing cost index
- wage or average wage annual series
- real wage growth
- informal employment share
- SUSENAS/BPS expenditure distribution by decile or quintile

After stable source IDs are confirmed, add source-specific download scripts that save raw data to `data/raw/` and write yearly outputs to the existing CSV schemas in `data/processed/`.
