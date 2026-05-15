# Main Data Audit

This note documents the data behind the main charts in `notebooks/eda_indonesia_inequality.qmd`: where the raw data comes from, what the raw records look like, and how the Python ingestion scripts transform them into the processed CSVs used by the QMD.

Generated files under `data/raw/` and `data/processed/` are intentionally ignored by git. Rebuild them locally with:

```bash
.venv/bin/python scripts/download_all.py
```

Primary source endpoints:

- World Bank API: `https://api.worldbank.org/v2/`
- World Bank Poverty and Inequality Platform percentile file: `https://pip.worldbank.org/`
- BPS WebAPI: `https://webapi.bps.go.id/v1/api/`
- ILOSTAT bulk/API data: `https://rplumber.ilo.org/data/indicator/`

## 1. Gini Comparison Across Countries

Main chart:

- `Latest Available Gini Index: Indonesia and Comparator Countries`

Processed file:

- `data/processed/comparative_inequality_growth.csv`

Script:

- `scripts/download_comparative_growth_inequality.py`

Raw sources:

- World Bank indicator `SI.POV.GINI`: Gini index
- World Bank indicator `NY.GDP.PCAP.KD`: GDP per capita, constant 2015 US dollars
- World Bank country metadata endpoint for country names, regions, and income groups

Important raw-file distinction:

There are two different World Bank Gini downloads in this project:

- `data/raw/worldbank_inequality_SI.POV.GINI.json` is Indonesia-only. It is created by `scripts/download_inequality.py`, which uses the shared country-specific helper for the main Indonesia inequality time series.
- `data/raw/worldbank_comparative_SI.POV.GINI.json` is cross-country. It is created by `scripts/download_comparative_growth_inequality.py` and is the raw file used for the comparator-country Gini chart.

So if you open `worldbank_inequality_SI.POV.GINI.json`, it is expected to contain only Indonesia. The other countries come from `worldbank_comparative_SI.POV.GINI.json`.

The comparative script uses this endpoint pattern:

```python
url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?{query}"
```

The Indonesia-only helper used by the other script uses this endpoint pattern:

```python
url = f"https://api.worldbank.org/v2/country/{COUNTRY}/indicator/{indicator}?{query}"
```

where `COUNTRY` is Indonesia.

Raw files created by the comparative script:

- `data/raw/worldbank_comparative_SI.POV.GINI.json`
- `data/raw/worldbank_comparative_NY.GDP.PCAP.KD.json`
- `data/raw/worldbank_comparative_countries.json`

Raw data shape:

World Bank indicator responses are JSON arrays. The second element is the observation list:

```json
[
  {"page": 1, "pages": 1, "...": "..."},
  [
    {
      "countryiso3code": "IDN",
      "date": "2023",
      "value": 36.1,
      "country": {"id": "ID", "value": "Indonesia"},
      "indicator": {"id": "SI.POV.GINI", "value": "Gini index"}
    }
  ]
]
```

Transformation concept:

1. Download Gini and real GDP per capita for all non-aggregate countries.
2. Keep country-year observations with valid Gini.
3. Attach same-year real GDP per capita.
4. Calculate future 5-year and 10-year annualized real GDP-per-capita growth when possible.
5. In the QMD, filter to selected comparator countries and keep the latest available Gini observation for each country.

Relevant logic:

```python
future_growth = ((future_gdp / current_gdp) ** (1 / horizon) - 1) * 100
```

QMD aggregation:

```r
latest_gini_comparison <- data$comparative_growth %>%
  inner_join(comparison_countries, by = "country_code") %>%
  drop_na(gini) %>%
  group_by(country_code) %>%
  slice_max(year, n = 1, with_ties = FALSE) %>%
  ungroup()
```

Interpretation caveat:

Comparator countries do not all have the same latest observation year. The chart labels show the year beside each Gini value.

## 2. Real GDP Per Capita

Main chart:

- `Real GDP per Capita`

Processed file:

- `data/processed/gdp_indonesia.csv`

Script:

- `scripts/download_gdp.py`

Raw source:

- World Bank indicator `NY.GDP.PCAP.KN`: GDP per capita, constant local currency unit

Raw data shape:

Same World Bank indicator JSON shape as above, with one observation per year.

Transformation concept:

1. Download annual Indonesia GDP indicators from World Bank.
2. Keep years 2000-2024.
3. Write one processed row per year.
4. Use `real_gdp_per_capita_lcu` for the main chart because it is already inflation-adjusted and not affected by USD exchange-rate movement.

Relevant processed columns:

- `real_gdp_per_capita_lcu`: constant-price GDP per person in Indonesian rupiah
- `gdp_growth`: annual constant-price GDP growth
- `nominal_gdp_per_capita`: current USD, kept only as a cautionary comparison field

## 3. Average Consumption By Population Group

Main chart:

- `Average Consumption by Population Group`

Processed file:

- `data/processed/welfare_distribution_indonesia.csv`

Script:

- `scripts/download_welfare_distribution.py`

Raw source:

- World Bank Poverty and Inequality Platform percentile file, `world_100bin.csv`

Raw data shape:

The raw PIP percentile file is long. Each row is a country-year-percentile observation. The exact raw columns can change slightly upstream, but the script standardizes the relevant fields:

```text
country_code, reporting_year, percentile, welfare, population, welfare_type, ...
IDN, 2023, 1, ..., ..., consumption, ...
IDN, 2023, 2, ..., ..., consumption, ...
...
IDN, 2023, 100, ..., ..., consumption, ...
```

Transformation concept:

1. Download the global 100-bin percentile file.
2. Filter to Indonesia (`IDN`) and national rows.
3. Keep percentile-level average welfare and population weights.
4. Aggregate percentiles into analysis groups:
   - Bottom 1%
   - Bottom 10%
   - Bottom 40%
   - Middle 40%
   - Top 20%
   - Top 10%
   - Top 1%
5. Calculate weighted average welfare for each group.

Core aggregation:

```python
avg_welfare_ppp_daily =
    sum(percentile_welfare * percentile_population) / sum(percentile_population)
```

Processed columns used:

- `group`
- `avg_welfare_ppp_daily`
- `population_share`
- `welfare_share`

QMD use:

```r
group_consumption <- data$welfare_distribution %>%
  filter(group %in% c("Bottom 40%", "Middle 40%", "Top 20%")) %>%
  drop_na(avg_welfare_ppp_daily)
```

Interpretation caveat:

For Indonesia, the PIP welfare concept is `consumption`, not income. The chart should be described as average consumption per person per day in 2017 PPP US dollars.

## 4. Distribution Shares By Population Group

Main charts:

- `Distribution Shares by Population Group`
- `Tail Distribution Shares`

Processed file:

- `data/processed/welfare_distribution_indonesia.csv`

Script:

- `scripts/download_welfare_distribution.py`

Transformation concept:

The distribution-share charts use the same grouped PIP percentile output as the average-consumption chart. Instead of average welfare level, they use the group's share of total welfare:

```python
welfare_share =
    sum(percentile_welfare * percentile_population for group)
    / sum(percentile_welfare * percentile_population for all percentiles)
```

For broad groups, the QMD keeps:

```r
group %in% c("Bottom 40%", "Middle 40%", "Top 20%")
```

For the tail view, the QMD keeps:

```r
group %in% c("Bottom 10%", "Top 10%")
```

Why this matters:

- `avg_welfare_ppp_daily` answers: did each group get better in absolute consumption terms?
- `welfare_share` answers: did each group receive a larger or smaller slice of total measured consumption?

These are different claims. The main narrative needs both.

## 5. Inflation And Total CPI

Main chart:

- `Inflation and CPI Coverage Available Now`

Processed file:

- `data/processed/inflation_indonesia.csv`

Script:

- `scripts/download_inflation.py`

Raw sources:

- World Bank indicator `FP.CPI.TOTL`: consumer price index
- World Bank indicator `FP.CPI.TOTL.ZG`: annual consumer price inflation

Transformation concept:

1. Download annual total CPI and inflation from World Bank.
2. Keep 2000-2024.
3. Write as `cpi_total` and `inflation_yoy`.

No aggregation is needed beyond year filtering. The QMD pivots these two columns into a long format for faceted plotting:

```r
inflation_long <- data$inflation %>%
  select(year, cpi_total, inflation_yoy) %>%
  pivot_longer(
    cols = c(cpi_total, inflation_yoy),
    names_to = "metric",
    values_to = "value"
  )
```

## 6. BPS Category CPI Indexes

Main chart:

- `BPS Category CPI Indexes`

Processed file:

- `data/processed/inflation_indonesia.csv`

Script:

- `scripts/download_inflation.py`

Raw source:

- BPS WebAPI `model=data`, national domain `0000`

Mapped BPS variables:

- `1905`: foods, beverages, and tobacco CPI, 2018=100
- `1907`: housing, water, electricity, and household fuel CPI, 2018=100
- `1909`: health CPI, 2018=100
- `1910`: transportation CPI, 2018=100
- `1913`: education CPI, 2018=100
- `1915`: provision of food and beverages / restaurant CPI, 2018=100

Raw BPS response shape:

The BPS data endpoint returns metadata plus a compact `datacontent` dictionary:

```json
{
  "status": "OK",
  "var": [{"val": 1905, "label": "Consumer Price Index of Foods, Beverages and Tobacco Group and Sub (2018=100)"}],
  "vervar": [{"val": 9999, "label": "INDONESIA"}],
  "turvar": [{"val": 1551, "label": "Foods, Beverages and Tobacco"}],
  "tahun": [{"val": 120, "label": "2020"}],
  "turtahun": [{"val": 12, "label": "December"}, {"val": 13, "label": "Annually"}],
  "datacontent": {
    "99991905155112012": 107.99
  }
}
```

BPS key construction:

The script builds a BPS `datacontent` lookup key by concatenating:

```python
key = f"{national_region}{variable_code}{group_code}{year_code}{december_subyear}"
```

For example:

- `9999`: Indonesia
- `1905`: food CPI variable
- `1551`: category group
- `120`: year code for 2020
- `12`: December

The script uses December national CPI as the year-end category index. It does not stitch 2024 because BPS switches to a 2022=100 base.

## 7. Real Wage Growth

Main chart:

- `Real Wage Growth`

Processed file:

- `data/processed/labor_indonesia.csv`

Script:

- `scripts/download_labor.py`

Raw sources:

- ILOSTAT `EAR_EMTA_SEX_NB_A`: average monthly earnings of employees by sex, local currency, annual
- World Bank `FP.CPI.TOTL`: total CPI, used as deflator

Raw ILOSTAT shape:

ILOSTAT bulk data is CSV.gz:

```text
ref_area,source,indicator,sex,time,obs_value,obs_status,note_indicator,note_source
IDN,BA:510,EAR_EMTA_SEX_NB,SEX_T,2023,2776803.875,,T30:122,R1:3513
IDN,BA:510,EAR_EMTA_SEX_NB,SEX_M,2023,3007410.446,,T30:122,R1:3513
IDN,BA:510,EAR_EMTA_SEX_NB,SEX_F,2023,2307995.085,,T30:122,R1:3513
```

Transformation concept:

1. Download the ILOSTAT earnings dataset.
2. Filter to:
   - `ref_area == "IDN"`
   - `sex == "SEX_T"` for total sex
   - years 2000-2024
3. Store nominal average monthly earnings as `avg_wage`.
4. Join World Bank total CPI by year.
5. Calculate real wage index internally:

```python
real_wage = avg_wage / cpi_total * 100
```

6. Calculate annual real wage growth:

```python
real_wage_growth =
    (real_wage[year] / real_wage[year - 1] - 1) * 100
```

Interpretation caveat:

This is employee earnings, not full household income. It does not fully capture informal workers or self-employed workers.

## 8. Nominal Wages, Prices, And Purchasing Power

Main chart:

- `Nominal Wages, Prices, and Purchasing Power`

Processed files:

- `data/processed/labor_indonesia.csv`
- `data/processed/inflation_indonesia.csv`

QMD transformation:

The chart indexes nominal wages, total CPI, and real wages to 2019 = 100:

```r
wage_price_index <- data$labor %>%
  select(year, avg_wage) %>%
  left_join(data$inflation %>% select(year, cpi_total), by = "year") %>%
  filter(year >= 2019) %>%
  drop_na(avg_wage, cpi_total) %>%
  mutate(real_wage = avg_wage / cpi_total * 100) %>%
  mutate(
    nominal_wage_index = avg_wage / first(avg_wage) * 100,
    cpi_index = cpi_total / first(cpi_total) * 100,
    real_wage_index = real_wage / first(real_wage) * 100
  )
```

Why 2019:

2019 is used as the pre-pandemic anchor for the wage-price comparison. The current data show that from 2019 to 2023 nominal average employee earnings increased, but CPI increased faster, so real wages remained below the 2019 index.

## 9. Household Price Pressure

Main chart:

- `How Prices Move From a Household Starting Point`

Processed files:

- `data/processed/inflation_indonesia.csv`
- `data/processed/cost_of_living_indonesia.csv`
- `data/processed/labor_indonesia.csv`

Raw source for rice:

- BPS WebAPI variable `295`: average wholesale rice price in Indonesia

Raw BPS rice response:

The rice endpoint has the same BPS `model=data` structure as category CPI:

```json
{
  "status": "OK",
  "var": [{"val": 295, "label": "The average rice price in Level Wholesale Indonesia"}],
  "tahun": [{"val": 124, "label": "2024"}],
  "turtahun": [{"val": 0, "label": "Annual"}],
  "datacontent": {"...": 13717}
}
```

Transformation concept:

1. Download BPS rice prices in three-year chunks because the BPS API rejects longer `th` ranges.
2. Extract annual national wholesale rice price.
3. Combine:
   - total CPI
   - selected BPS category CPI indexes
   - wholesale rice price
   - average monthly earnings
4. Rebase each series to 2020 = 100.

QMD aggregation:

```r
price_pressure <- bind_rows(
  total_cpi,
  category_cpi,
  rice_price,
  avg_wage
) %>%
  filter(year >= 2020) %>%
  group_by(metric) %>%
  arrange(year, .by_group = TRUE) %>%
  mutate(index_2020 = value / first(value) * 100)
```

Interpretation caveat:

This chart compares movements, not household budget weights. A full cost-of-living burden analysis would need expenditure weights by income group.

## Raw Data Files Produced Locally

Typical raw files created by the scripts:

```text
data/raw/worldbank_gdp_*.json
data/raw/worldbank_inflation_*.json
data/raw/worldbank_labor_*.json
data/raw/worldbank_labor_deflator_FP.CPI.TOTL.json
data/raw/ilostat_average_monthly_earnings_EAR_EMTA_SEX_NB_A.csv.gz
data/raw/bps_cpi_category_*.json
data/raw/bps_rice_price_grosir_*.json
```

These raw files are not committed. They are the audit trail on the local machine after running the ingestion scripts.

## Current Main Evidence

The core empirical chain now supported by the processed data is:

1. Indonesia is not the most unequal comparator country, but its Gini is high enough to make the public inequality concern plausible.
2. Real GDP per capita increased, so the economy became larger in inflation-adjusted terms.
3. Broad population groups saw absolute consumption gains.
4. Distribution shares show richer groups capturing a larger slice, especially visible in tail comparisons.
5. Since 2019, average employee earnings rose in nominal rupiah, but CPI rose faster by 2023, so real wages fell relative to 2019.

The weak point still requiring caution is that employee earnings are not the same as total household income or informal-sector earnings.
