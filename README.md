# Indonesia Inequality Project

This repository contains a phased Indonesia economic inequality project. It currently covers reproducible data ingestion, exploratory data analysis, and a first analysis skeleton.

The current repository does:

- identify usable official/public data sources
- download raw API responses
- standardize annual Indonesia-level records
- write processed CSVs for analysis
- provide an initial EDA notebook
- provide a markdown analysis skeleton for the future report

The current repository does not yet include final modeling, dashboarding, publication-ready narrative writing, or BPS-backed replacements for fields that still need stable BPS variable or table mappings.

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

Status: skeleton only.

Phase 3 currently defines the analysis structure before writing the full report. The skeleton lays out the intended narrative: real GDP growth, group-level consumption gains, distribution-share shifts, tail inequality, and the normative question of whether rising inequality is acceptable when the poorest also improve.

Primary outputs:

- `reports/skeleton.md`

The full Phase 3 report and chart images are intentionally not kept in the repository yet. They should be generated later after the skeleton narrative is reviewed.

## Repository Structure

```text
data/
  raw/                         Generated raw API responses, ignored by git
  processed/                   Generated standardized annual CSVs, ignored by git
notebooks/
  eda_indonesia_inequality.ipynb
  eda_indonesia_inequality.qmd
reports/
  skeleton.md                   Analysis structure for the future report
scripts/
  common.py                    Shared fetch, clean, and CSV helpers
  download_all.py              Runs all supported download scripts
  download_gdp.py
  download_inequality.py
  download_welfare_distribution.py
  download_comparative_growth_inequality.py
  download_labor.py
  download_labour_income_deciles.py
  build_prices.py              Builds the combined CPI and cost-of-living file
  discover_bps_sources.py      Scans BPS subject-variable metadata
README.md
agent.md                       Handoff notes for future work
requirements.txt
renv.lock                      Local R package lockfile, ignored by git
renv/                          Project-local R environment scaffold, ignored by git
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
.venv/bin/python scripts/download_inequality.py
.venv/bin/python scripts/download_welfare_distribution.py
.venv/bin/python scripts/download_comparative_growth_inequality.py
.venv/bin/python scripts/download_labor.py
.venv/bin/python scripts/download_labour_income_deciles.py
.venv/bin/python scripts/build_prices.py
```

Run BPS source discovery separately:

```bash
.venv/bin/python scripts/discover_bps_sources.py
```

Raw source extracts are saved locally in `data/raw/`. Standardized analysis CSVs are saved locally in `data/processed/`. These generated data files are ignored by git so the repository stays lightweight and reproducible.

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

The current outputs are reproducible from the scripts in this repository. Running `scripts/download_all.py` fetches raw World Bank API responses, filters World Bank PIP percentile data to Indonesia, downloads ILOSTAT wage data, downloads the currently mapped BPS rice-price series, and rebuilds the processed CSVs.

Current guarantees:

- Raw source responses are saved under `data/raw/`.
- Processed outputs are saved under `data/processed/`.
- Generated raw and processed data files are not committed to git.
- Processed outputs use annual Indonesia rows for 2000-2024.
- BPS-backed fields stay blank unless stable source IDs and reproducible download logic exist.
- Historical values may change if upstream providers revise their data.

This README and the source code are enough to reproduce the current pipeline from a fresh clone. `agent.md` is optional handoff context for future development, not required operating documentation.

## Source Strategy

World Bank API is the main working source for the baseline annual country-level pipeline because it provides stable Indonesia (`IDN`) indicators without an API key.

BPS is still the preferred source for Indonesia-specific fields such as detailed CPI categories, commodity prices, administered prices, and wages. The current working BPS route is subject-variable discovery through `model=var` plus direct data downloads through `model=data`. Total CPI uses the World Bank's continuous annual Indonesia CPI series for the full 2000-2024 horizon. The mapped BPS category CPI variables use the 2018=100 category taxonomy, which is source-backed from 2020 rather than stitched to older BPS base years and category groupings. The price builder uses BPS variable `295` for Indonesia wholesale rice prices.

## Processed Data

After running Phase 1, most processed files in `data/processed/` use one row per calendar year for Indonesia, currently covering 2000-2024. `welfare_distribution_indonesia.csv` is long by year and population group. Some indicators have missing values when the upstream source has no observation for a year.

For this small project, the processed data dictionary is kept in the main README because there are only a few processed files and the schemas are short. A separate `docs/data_dictionary.md` would be better once the documentation grows, the number of tables increases, or provenance notes become too detailed for the README.

Shared columns:

- `year`: calendar year of the observation.
- `source`: source note for the row. This also flags placeholder fields pending BPS, ILOSTAT, or another official source.

### `data/processed/gdp_indonesia.csv`

Annual GDP and GDP-per-capita indicators from the World Bank.

World Bank indicators:

- `NY.GDP.MKTP.KD.ZG`: GDP growth, annual %
- `NY.GDP.MKTP.CN`: GDP, current local currency unit
- `NY.GDP.MKTP.KN`: GDP, constant local currency unit
- `NY.GDP.PCAP.CN`: GDP per capita, current local currency unit
- `NY.GDP.PCAP.KN`: GDP per capita, constant local currency unit
- `NY.GDP.PCAP.KD`: GDP per capita, constant 2015 US$
- `NY.GDP.PCAP.CD`: GDP per capita, current US$
- `PA.NUS.PRVT.PP`: PPP conversion factor for households and NPISHs final consumption expenditure, LCU per international dollar

Columns:

- `year`: calendar year.
- `gdp_growth`: annual GDP growth rate, in percent. This is already based on constant-price GDP.
- `nominal_gdp_lcu`: GDP in current local currency units. Use this for the unadjusted domestic GDP level.
- `real_gdp_lcu`: GDP in constant local currency units. Use this as the preferred output measure when avoiding both inflation effects and US-dollar exchange-rate effects.
- `nominal_gdp_per_capita_lcu`: GDP per capita in current local currency units.
- `real_gdp_per_capita_lcu`: GDP per capita in constant local currency units. Use this as the preferred domestic living-standard proxy.
- `real_gdp_per_capita`: GDP per capita in constant 2015 US dollars. Useful for international comparison, but still expressed in US dollars.
- `nominal_gdp_per_capita`: GDP per capita in current US dollars. Use cautiously because exchange-rate movement can affect the series.
- `ppp_private_consumption`: rupiah per international dollar for private consumption, used to convert PIP PPP consumption labels into approximate current rupiah amounts.
- `source`: data source.

### `data/processed/prices_indonesia.csv`

Combined annual price table used by the notebooks. It contains total CPI, inflation, BPS category CPI fields, BPS wholesale rice price, and reserved cost-of-living fields in one file.

Built by:

- `scripts/build_prices.py`

World Bank indicators:

- `FP.CPI.TOTL`: consumer price index
- `FP.CPI.TOTL.ZG`: inflation, consumer prices, annual %

BPS variables:

- `1905`: foods, beverages, and tobacco CPI, 2018=100
- `1907`: housing, water, electricity, and household fuel CPI, 2018=100
- `1909`: health CPI, 2018=100
- `1910`: transportation CPI, 2018=100
- `1913`: education CPI, 2018=100
- `1915`: provision of food and beverages / restaurant CPI, 2018=100
- `295`: Indonesia wholesale rice price

Columns:

- `year`: calendar year.
- `cpi_total`: consumer price index, total.
- `inflation_yoy`: annual consumer price inflation, in percent.
- `cpi_food`: BPS national December CPI index for foods, beverages, and tobacco.
- `cpi_transport`: BPS national December CPI index for transportation.
- `cpi_housing`: BPS national December CPI index for housing, water, electricity, and household fuel.
- `cpi_education`: BPS national December CPI index for education.
- `cpi_healthcare`: BPS national December CPI index for health.
- `cpi_restaurant`: BPS national December CPI index for provision of food and beverages / restaurant.
- `rice_price`: wholesale rice price in rupiah per kilogram from BPS WebAPI variable `295`.
- `fuel_price`, `electricity_index`, `rent_index`, `education_index`, `healthcare_index`, `restaurant_index`: reserved cost-of-living fields pending source-backed mapping.
- `source`: data source and limitation notes.

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

### `data/processed/welfare_distribution_indonesia.csv`

Grouped welfare estimates derived from World Bank Poverty and Inequality Platform (PIP) percentile data. The script filters the global percentile file to Indonesia, keeps national rows, and aggregates percentiles into bottom 1%, bottom 10%, bottom 40%, middle 40%, top 20%, top 10%, and top 1% groups.

For the current Indonesia rows, `welfare_type` is `consumption`. The welfare level is average daily consumption per person in 2017 PPP US dollars.

Source file:

- World Bank PIP percentiles: `world_100bin.csv`

Columns:

- `year`: calendar year.
- `group`: population group.
- `welfare_type`: whether the PIP welfare concept is income or consumption. Current Indonesia rows use `consumption`.
- `avg_welfare_ppp_daily`: weighted average welfare for the group, in 2017 PPP US dollars per person per day.
- `population_share`: share of national population represented by the group, from 0 to 1.
- `welfare_share`: share of total measured welfare received by the group, from 0 to 1.
- `population`: estimated population represented by the group.
- `source`: data source and unit note.

### `data/processed/comparative_inequality_growth.csv`

Cross-country comparison dataset for the question: does higher inequality today tend to precede weaker future growth? This is supporting comparative evidence, not Indonesia-only causal proof.

The script combines World Bank Gini observations with real GDP per capita in constant 2015 US dollars, then computes annualized 5-year and 10-year future growth after each inequality observation.

World Bank indicators:

- `SI.POV.GINI`: Gini index
- `NY.GDP.PCAP.KD`: GDP per capita, constant 2015 US dollars

Columns:

- `country_code`: ISO 3-letter country code.
- `country_name`: country name.
- `region`: World Bank region.
- `income_level`: World Bank income group.
- `year`: inequality observation year.
- `gini`: Gini index in that year.
- `gdp_per_capita_constant_2015_usd`: real GDP per capita in the same year.
- `future_5y_growth_pct`: annualized real GDP-per-capita growth from `year` to `year + 5`, in percent.
- `future_10y_growth_pct`: annualized real GDP-per-capita growth from `year` to `year + 10`, in percent.
- `future_5y_end_year`: end year used for the 5-year growth calculation.
- `future_10y_end_year`: end year used for the 10-year growth calculation.
- `source`: data source note.

### `data/processed/labor_indonesia.csv`

Annual wage file. Average monthly earnings are populated from ILOSTAT. Real wage growth is retained as a derived field for table checks, calculated by deflating those earnings with World Bank total CPI.

ILOSTAT indicator:

- `EAR_EMTA_SEX_NB_A`: average monthly earnings of employees by sex, local currency, annual. The pipeline uses Indonesia and total sex (`SEX_T`).

Columns:

- `year`: calendar year.
- `avg_wage`: average monthly earnings of employees, in nominal rupiah, from ILOSTAT. Available through 2023 in the current processed output.
- `real_wage_growth`: annual real wage growth, in percent, calculated from `avg_wage / cpi_total`.
- `source`: data source.

### `data/processed/labour_income_deciles_indonesia.csv`

Estimated monthly labour income by decile. The script downloads ILOSTAT labour-income shares by decile and scales each decile share by the national average monthly earnings already stored in `labor_indonesia.csv`.

Built by:

- `scripts/download_labour_income_deciles.py`

ILOSTAT indicator:

- `LAP_2LID_QTL_RT`: labour income distribution by decile

Columns:

- `year`: calendar year.
- `decile`: population decile.
- `labour_income_share_pct`: decile share of total labour income, in percent.
- `avg_wage`: national average monthly earnings of employees, in nominal rupiah.
- `estimated_avg_monthly_labour_income`: estimated monthly labour income for the decile, calculated as `avg_wage * labour_income_share_pct / 10`.
- `source`: data source and scaling note.

## BPS API Status

BPS Web API endpoints follow this pattern:

```text
https://webapi.bps.go.id/v1/api/list/model/{model}/lang/ind/domain/0000/.../key/{BPS_API_KEY}
```

The national domain is `0000`. The current discovery script scans working `model=var` subject endpoints for relevant variables:

```bash
.venv/bin/python scripts/discover_bps_sources.py
```

It saves raw variable-list responses such as:

- `data/raw/bps_var_subject_3_page1.json`
- `data/raw/bps_var_subject_20_page1.json`
- `data/raw/bps_var_subject_23_page1.json`

The older `model=dynamictable` endpoint currently returns `Model dynamictable is not recognized`, so the repo no longer relies on it. Direct BPS data endpoints work when a variable ID is known. For example, `scripts/build_prices.py` downloads BPS CPI category variables in chunks and BPS variable `295` in three-year chunks.

## Notebook

The initial exploratory notebook is:

```text
notebooks/eda_indonesia_inequality.ipynb
```

The R/Quarto equivalent is:

```text
notebooks/eda_indonesia_inequality.qmd
```

The appendix-only Quarto companion is:

```text
notebooks/eda_indonesia_inequality_appendix.qmd
```

These notebooks use the processed CSVs and make missing fields visible instead of hiding or imputing them.

## Known Gaps

Use official BPS portals, BPS API metadata, ILOSTAT, or another official reproducible source to fill:

- longer CPI category history before 2020 and a carefully documented bridge to the 2024 BPS 2022=100 CPI base
- retail rice price or other food commodity prices beyond the currently mapped BPS wholesale rice series
- administered fuel, electricity, or LPG price series
- rent or housing cost index
- BPS/SUSENAS expenditure distribution validation against World Bank PIP percentile aggregates

After stable source IDs are confirmed, add source-specific download scripts that save raw data to `data/raw/` and write yearly outputs to the existing CSV schemas in `data/processed/`.
