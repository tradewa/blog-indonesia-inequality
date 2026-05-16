# Main Data Audit

This note has two sections:

1. The source and construction path for every CSV in `data/processed/`.
2. How the notebooks transform those CSVs into the chart series.

Generated files under `data/raw/` and `data/processed/` are local artifacts. Most can be rebuilt with:

```bash
.venv/bin/python scripts/download_all.py
```

Current primary source families:

- World Bank API: `https://api.worldbank.org/v2/`
- World Bank Poverty and Inequality Platform percentile file: `https://pip.worldbank.org/`
- BPS WebAPI: `https://webapi.bps.go.id/v1/api/`
- ILOSTAT bulk/API data: `https://rplumber.ilo.org/data/indicator/`

## 1. Processed CSV Source Audit

This section is organized by file in `data/processed/`.

### `comparative_inequality_growth.csv`

Script:

- `scripts/download_comparative_growth_inequality.py`

Raw sources:

- World Bank `SI.POV.GINI`: Gini index.
- World Bank `NY.GDP.PCAP.KD`: GDP per capita, constant 2015 US dollars.
- World Bank country metadata endpoint: country names, regions, and income levels.

Raw files:

- `data/raw/worldbank_comparative_SI.POV.GINI.json`
- `data/raw/worldbank_comparative_NY.GDP.PCAP.KD.json`
- `data/raw/worldbank_comparative_countries.json`

Construction:

1. Download Gini and constant-price GDP per capita for all non-aggregate countries.
2. Attach country metadata.
3. Keep country-year observations with valid Gini.
4. Join same-year real GDP per capita where available.
5. Calculate forward-looking annualized 5-year and 10-year real GDP-per-capita growth when the future GDP observation exists.

Core formula:

```python
future_growth = ((future_gdp / current_gdp) ** (1 / horizon) - 1) * 100
```

### `gdp_indonesia.csv`

Script:

- `scripts/download_gdp.py`

Raw sources:

- World Bank `NY.GDP.MKTP.KD.ZG`: real GDP growth.
- World Bank `NY.GDP.MKTP.CN`: nominal GDP, local currency.
- World Bank `NY.GDP.MKTP.KN`: real GDP, local currency.
- World Bank `NY.GDP.PCAP.CN`: nominal GDP per capita, local currency.
- World Bank `NY.GDP.PCAP.KN`: real GDP per capita, local currency.
- World Bank `NY.GDP.PCAP.KD`: real GDP per capita, constant 2015 US dollars.
- World Bank `NY.GDP.PCAP.CD`: nominal GDP per capita, current US dollars.
- World Bank `PA.NUS.PRVT.PP`: PPP conversion factor for private consumption.

Raw files:

- `data/raw/worldbank_gdp_*.json`

Construction:

1. Download each World Bank indicator for Indonesia.
2. Keep the project year range, currently 2000-2024.
3. Merge indicators by `year`.
4. Write one processed row per year.

Key chart column:

- `real_gdp_per_capita_lcu`, because it is already constant-price rupiah and is not distorted by exchange-rate changes.

### `inequality_indonesia.csv`

Script:

- `scripts/download_inequality.py`

Raw sources:

- World Bank `SI.POV.GINI`: Gini index.
- World Bank `SI.DST.FRST.10`: lowest 10% income or consumption share.
- World Bank `SI.DST.FRST.20`: lowest 20% share.
- World Bank `SI.DST.02ND.20`: second 20% share.
- World Bank `SI.DST.03RD.20`: third 20% share.
- World Bank `SI.DST.04TH.20`: fourth 20% share.
- World Bank `SI.DST.05TH.20`: highest 20% share.
- World Bank `SI.DST.10TH.10`: highest 10% share.

Raw files:

- `data/raw/worldbank_inequality_*.json`

Construction:

1. Download Indonesia-only World Bank inequality and distribution-share indicators.
2. Merge by `year`.
3. Derive broad grouped shares:
   - `expenditure_bottom40 = quintile_1_share + quintile_2_share`
   - `expenditure_middle40 = quintile_3_share + quintile_4_share`
   - `expenditure_top20 = quintile_5_share`

Interpretation caveat:

- World Bank distribution shares can refer to income or consumption depending on survey metadata. For the main charts, the PIP-based `welfare_distribution_indonesia.csv` is preferred for consumption-specific group shares.

### `prices_indonesia.csv`

Script:

- `scripts/build_prices.py`

Raw sources:

- World Bank `FP.CPI.TOTL`: total CPI.
- World Bank `FP.CPI.TOTL.ZG`: annual inflation.
- BPS WebAPI category CPI variables:
  - `1905`: food, beverages, tobacco.
  - `1907`: housing, water, electricity, fuel.
  - `1909`: health.
  - `1910`: transport.
  - `1913`: education.
  - `1915`: restaurants.
- BPS WebAPI variable `295`: Indonesia wholesale rice price.

Raw files:

- `data/raw/worldbank_prices_*.json`
- `data/raw/bps_cpi_category_*.json`
- `data/raw/bps_rice_price_grosir_*.json`

Construction:

1. Download World Bank annual total CPI and inflation for Indonesia.
2. Download BPS national category CPI values using the 2018=100 category taxonomy.
3. Prefer annual values from BPS when available, falling back to December values in the extractor.
4. Download BPS wholesale rice price through chunked annual BPS requests.
5. Merge all fields by `year` and write one row per year for 2000-2024.

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
- `rice_price`
- `fuel_price`
- `electricity_index`
- `rent_index`
- `education_index`
- `healthcare_index`
- `restaurant_index`
- `source`

Use in analysis:

- This is the only processed price file used by the notebooks.

Current limitations:

- Total CPI covers 2000-2024 through the World Bank.
- BPS category CPI coverage is source-backed only for 2020-2023 in the current taxonomy. It is intentionally not stitched to older BPS base years.
- `fuel_price`, `electricity_index`, `rent_index`, `education_index`, `healthcare_index`, and `restaurant_index` are schema placeholders until source-backed BPS series are mapped.

### `labor_indonesia.csv`

Script:

- `scripts/download_labor.py`

Raw sources:

- World Bank `FP.CPI.TOTL`: CPI deflator used to calculate real wage growth.
- ILOSTAT `EAR_EMTA_SEX_NB_A`: average monthly earnings of employees by sex, local currency, annual. The pipeline keeps Indonesia (`IDN`) and total sex (`SEX_T`).

Raw files:

- `data/raw/worldbank_labor_deflator_FP.CPI.TOTL.json`
- `data/raw/ilostat_average_monthly_earnings_EAR_EMTA_SEX_NB_A.csv.gz`

Construction:

1. Download ILOSTAT average monthly earnings.
2. Download World Bank total CPI for the deflator.
3. Keep Indonesia, total sex, annual observations.
4. Calculate real wage level as `avg_wage / cpi_total * 100`.
5. Calculate `real_wage_growth` as the year-over-year growth in that real wage level.
6. Merge wage fields by `year`.

Important caveat:

- `avg_wage` is national average monthly earnings of employees. It is not household income, not consumption, and not a middle-class-specific wage.

### `labour_income_deciles_indonesia.csv`

Script:

- `scripts/download_labour_income_deciles.py`

Raw source:

- ILOSTAT `LAP_2LID_QTL_RT`: labour income distribution by decile.
- ILOSTAT `EAR_EMTA_SEX_NB_A`: national average monthly earnings, used as the scale anchor already present in `labor_indonesia.csv`.

Raw file:

- `data/raw/ilostat_labour_income_distribution_LAP_2LID_QTL_RT.csv.gz`

Processed columns:

- `year`
- `decile`
- `labour_income_share_pct`
- `avg_wage`
- `estimated_avg_monthly_labour_income`
- `source`

Construction:

1. Download ILOSTAT labour-income shares by decile.
2. Keep Indonesia and decile classifications.
3. Read national average monthly earnings from `labor_indonesia.csv`.
4. Keep years where both the decile share and national average wage exist.
5. Estimate average monthly labour income by decile:

```python
estimated_avg_monthly_labour_income =
    avg_wage * labour_income_share_pct / 10
```

Conceptual caution:

- This is not directly observed wage-by-decile microdata. It is a decile-level estimate made from labour-income shares scaled by national average monthly earnings.
- It is useful as a sanity-check and distribution proxy, but chart titles and claims should say "estimated labour income", not "wage by decile".

### `welfare_distribution_indonesia.csv`

Script:

- `scripts/download_welfare_distribution.py`

Raw source:

- World Bank Poverty and Inequality Platform 100-bin percentile file: `world_100bin.csv`.

Raw file:

- `data/raw/worldbank_pip_percentiles_indonesia.csv`

Construction:

1. Download the global PIP 100-bin percentile file.
2. Keep Indonesia (`IDN`), national rows, and project years.
3. Aggregate percentile rows into:
   - Bottom 1%
   - Bottom 10%
   - Bottom 40%
   - Middle 40%
   - Top 20%
   - Top 10%
   - Top 1%
4. Calculate weighted average welfare for each group:

```python
avg_welfare_ppp_daily =
    sum(percentile_welfare * percentile_population) / sum(percentile_population)
```

5. Sum population share, welfare share, and population by group.

Important caveat:

- For Indonesia, the PIP welfare concept is `consumption`. The values should be described as consumption welfare in 2017 PPP US dollars per person per day, not income.

## 2. Chart Data Transformations

This section documents how the notebooks manipulate the processed CSVs into chart-ready series.

### `Real GDP per Capita`

Input:

- `gdp_indonesia.csv`

Transformation:

1. Keep rows with non-missing `real_gdp_per_capita_lcu`.
2. Sort by year.
3. Plot the raw constant-rupiah series.
4. Label the final point with cumulative first-to-last growth:

```r
real_gdp_per_capita_lcu / first(real_gdp_per_capita_lcu) - 1
```

Interpretation:

- This is an inflation-adjusted production-side living-standard proxy. It says the economy produced more per person in real terms; it does not by itself say gains were equally distributed.

### `Nominal Wages, Prices, and Purchasing Power`

Inputs:

- `labor_indonesia.csv`
- `prices_indonesia.csv`

Transformation:

1. Join `avg_wage` to `cpi_total` by year.
2. Keep non-missing wage and CPI observations.
3. Construct:

```r
real_wage = avg_wage / cpi_total * 100
nominal_wage_index = avg_wage / first(avg_wage) * 100
cpi_index = cpi_total / first(cpi_total) * 100
real_wage_index = real_wage / first(real_wage) * 100
```

4. Pivot the three indexes into a long table.
5. Plot them on the same 2000=100 basis.
6. Label final points with cumulative first-to-last increase.

Interpretation:

- Comparing wage growth with CPI is the cleaner purchasing-power comparison. If nominal wage grows faster than CPI, the national average employee wage has higher CPI-deflated purchasing power over that period.
- This is still national average employee earnings, not class-specific or informal-sector income.

### `Nominal Average Consumption by Decile Indexed to 2000`

Inputs:

- `worldbank_pip_percentiles_indonesia.csv` from `data/raw/`
- `prices_indonesia.csv`

Reason for using the raw PIP percentile file:

- The processed `welfare_distribution_indonesia.csv` has broad groups, but this chart needs 10 deciles. The QMD therefore aggregates the raw PIP percentiles directly into deciles.

Transformation:

1. Aggregate PIP percentiles into decile bands:
   - `0 - 10%`
   - `11 - 20%`
   - ...
   - `91 - 100%`
2. Compute weighted average `avg_consumption` within each decile using `pop_share`.
3. Convert each decile's real consumption welfare into a 2000=100 real index:

```r
real_consumption_index_2000 = avg_consumption / first(avg_consumption) * 100
```

4. Build a total CPI index:

```r
cpi_index_2000 = cpi_total / first(cpi_total) * 100
```

5. Convert the real consumption index into an implied nominal consumption index:

```r
nominal_consumption_index = real_consumption_index_2000 * cpi_index_2000 / 100
```

6. Bind the nominal decile series with total CPI for visual comparison.
7. Label lines at the right edge.

Interpretation caveat:

- PIP consumption is already real PPP welfare. The nominal conversion is an implied nominal index, not directly observed rupiah spending by decile.

### `Distribution Shares by Population Group`

Input:

- `welfare_distribution_indonesia.csv`

Transformation:

1. Keep broad groups:
   - Bottom 40%
   - Middle 40%
   - Top 20%
2. Use `welfare_share * 100` as the plotted share.
3. Label the final point with percentage-point change from the first observation:

```r
share - first(share)
```

Interpretation:

- This chart answers distribution, not absolute welfare. A group can have rising real consumption while its share of total consumption falls.

### `Average Consumption Growth by Decile`

Inputs:

- `worldbank_pip_percentiles_indonesia.csv` from `data/raw/`
- `gdp_indonesia.csv`
- `prices_indonesia.csv`

Transformation:

1. Aggregate raw PIP percentiles into decile bands.
2. Keep the recent-period window, currently 2020-2024.
3. Calculate cumulative real consumption growth by decile:

```r
growth = latest_consumption / first(avg_consumption) - 1
```

4. Convert the latest PIP 2017 PPP daily consumption level to rupiah per day for labels:

```r
latest_consumption_rupiah =
    latest_consumption
    * ppp_private_consumption_2017
    * latest_cpi_total / cpi_total_2017
```

Interpretation:

- The bar height is real consumption-welfare growth. Labels are approximate rupiah/day levels in the latest CPI price basis.
- This chart is about observed consumption welfare, not purchasing power from wages.

### `How Prices Move From a Household Starting Point`

Inputs:

- `welfare_distribution_indonesia.csv`
- `prices_indonesia.csv`

Transformation:

1. Build the Middle 40% consumption series from `avg_welfare_ppp_daily`.
2. Join to `cpi_total`.
3. Convert Middle 40% real consumption into an implied nominal index:

```r
real_consumption_index = avg_welfare_ppp_daily / first(avg_welfare_ppp_daily) * 100
cpi_index = cpi_total / first(cpi_total) * 100
middle_consumption_nominal_index = real_consumption_index * cpi_index / 100
```

4. Combine that Middle 40% implied nominal consumption index with BPS category CPI indexes:
   - food, beverages, tobacco
   - transport
   - housing, water, electricity, fuel
   - education
   - health
   - restaurants
5. Rebase every line to 2020=100.
6. Label each line with cumulative growth from first to last point.

Interpretation caveat:

- This is not a strict purchasing-power chart. For purchasing power, wages or income should be compared with prices.
- Comparing consumption with category prices is a welfare-pressure comparison: it shows whether observed consumption growth kept up with the prices of major spending categories.

### `Estimated Labour Income by Decile vs National Average Wage`

Inputs:

- `labour_income_deciles_indonesia.csv`
- `labor_indonesia.csv`

Transformation:

1. Plot `estimated_avg_monthly_labour_income` by decile.
2. Join the national `avg_wage` series over the shared years.
3. Overlay national average wage as a black reference line.
4. Use a log y-axis so bottom and top deciles are readable on the same chart.

Interpretation caveat:

- This chart is a sanity check for the decile labour-income file. It should not be overinterpreted until the file's ingestion path is formalized and the estimated decile levels are validated.

### Appendix-only charts

The appendix notebook also includes supporting charts built from the same processed CSVs:

- Gini comparator chart from `comparative_inequality_growth.csv`.
- GDP growth from `gdp_indonesia.csv`.
- Average consumption by broad population group from `welfare_distribution_indonesia.csv`.
- Tail consumption and tail distribution shares from `welfare_distribution_indonesia.csv`.
- Inflation and total CPI coverage from `prices_indonesia.csv`.
- Gini index from `inequality_indonesia.csv`.
- Inequality and future growth scatter from `comparative_inequality_growth.csv`.
- Rice price and missingness checks from `prices_indonesia.csv`.
- Long-run decile consumption growth and YoY decile consumption growth from raw PIP percentile data plus CPI.
