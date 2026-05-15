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

Raw sources:

- World Bank indicator `NY.GDP.PCAP.KN`: GDP per capita, constant local currency unit
- World Bank indicator `PA.NUS.PRVT.PP`: PPP conversion factor for households and NPISHs final consumption expenditure

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
- `ppp_private_consumption`: rupiah per international dollar for private consumption

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

## 6. Nominal Wages, Prices, And Purchasing Power

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

## 7. Household Price Pressure

Main chart:

- `How Prices Move From a Household Starting Point`

Processed files:

- `data/processed/inflation_indonesia.csv`
- `data/processed/labor_indonesia.csv`

Transformation concept:

1. Combine:
   - average monthly earnings
   - total CPI
   - selected BPS category CPI indexes
2. Rebase each series to its first available value from 2020 onward.
3. Plot the series in one shared chart, using solid lines for average monthly earnings and total CPI and dashed lines for category context.
4. Label each line on the right with its name and cumulative percentage increase, using fixed y-positions to avoid label overlap.

QMD aggregation:

```r
price_pressure <- bind_rows(
  avg_wage,
  total_cpi,
  category_cpi
) %>%
  filter(year >= 2020) %>%
  group_by(metric) %>%
  arrange(year, .by_group = TRUE) %>%
  mutate(index_start = value / first(value) * 100)
```

Interpretation caveat:

This chart compares movements, not household budget weights. Category CPI detail is source-backed only for 2020-2023 in the current BPS 2018=100 taxonomy, so it is used as a recent-period deep dive rather than a stitched long-run series.

## 8. Average Consumption By Decile

Main chart:

- `Average Consumption Growth by Decile`

Input files:

- `data/raw/worldbank_pip_percentiles_indonesia.csv`

Transformation concept:

1. Aggregate World Bank PIP 100-bin percentile rows into 10 decile bands: 0 - 10%, 11 - 20%, ..., 91 - 100%.
2. Use weighted average `avg_welfare` within each decile, weighted by `pop_share`.
3. Detect the latest available Indonesia national year in the raw PIP percentile file; the current local file runs through 2024.
4. Calculate cumulative growth from 2020 to the latest available year for each decile.
5. Plot a column chart with decile on the x-axis and consumption growth on the y-axis; label each bar with the latest daily consumption level converted to rupiah per day using the latest matching World Bank private-consumption PPP factor.

Interpretation caveat:

The decile series are average consumption/welfare in 2017 PPP dollars per person per day, not wage earnings. Because this is already a real purchasing-power welfare measure, it should not be directly compared with CPI as though it were nominal income. It is valid as a direct living-standard chart.

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
