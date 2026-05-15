# Agent Handoff Notes

## Purpose

This file is internal continuation context for future development. It should not duplicate the full README. The README is the replication guide and data dictionary; keep it self-sufficient for a human starting from a fresh clone.

## Current State

The project is now organized into three phases:

- Phase 1: data ingestion
- Phase 2: exploratory data analysis
- Phase 3: analysis report

Current phase status:

- Phase 1 is complete as a reproducible first pass.
- Phase 2 is complete as an initial EDA notebook.
- Phase 3 is currently skeleton-only. The full report will be written later.

Implemented:

- Download scripts for GDP, inflation, inequality, PIP welfare distribution, comparative inequality-growth, poverty, labor, and cost-of-living baseline data.
- ILOSTAT average monthly earnings download through `scripts/download_labor.py` using `EAR_EMTA_SEX_NB_A`, with real wage growth calculated from World Bank CPI.
- BPS WebAPI category CPI download through `scripts/download_inflation.py` using variables `1905`, `1907`, `1909`, `1910`, `1913`, and `1915`.
- BPS WebAPI rice-price download through `scripts/download_cost_of_living.py` using variable `295`.
- Raw API response persistence under `data/raw/`, ignored by git.
- Standardized annual processed CSVs under `data/processed/`, ignored by git.
- A BPS discovery script that scans working subject-variable endpoints and records raw metadata responses.
- Phase 2 EDA notebook at `notebooks/eda_indonesia_inequality.ipynb`.
- Phase 2 R/Quarto equivalent at `notebooks/eda_indonesia_inequality.qmd`.
- Phase 3 analysis skeleton at `reports/skeleton.md`.
- Project-local R package management through `renv`.

Not implemented:

- Final statistical modeling.
- Dashboarding or publication narrative.
- BPS-backed fills for administered prices, informal employment, or SUSENAS-specific validation fields.
- Longer CPI category history before 2020 and a documented bridge to the 2024 BPS 2022=100 CPI base.
- Retail commodity-price series beyond the currently mapped wholesale rice price.
- Output validation checks.

## Operating Rule

Do not fabricate or hand-copy blank BPS-backed fields into processed CSVs. If a field is filled, the raw source must be saved under `data/raw/` and the transformation into `data/processed/` must be reproducible from code.

Generated data files should stay out of git. The whole `data/` directory is ignored; users should rebuild raw JSON/CSV and processed CSV outputs locally.

## Replication

Use `README.md` for the authoritative fresh-clone instructions, source strategy, processed schemas, and known gaps.

The current rebuild entry points are:

```bash
.venv/bin/python scripts/download_all.py
.venv/bin/python scripts/discover_bps_sources.py
```

The scripts currently use Python standard-library modules only.

For R/Quarto work, restore the local R environment before rendering:

```bash
Rscript -e "renv::restore()"
quarto render notebooks/eda_indonesia_inequality.qmd
```

## Phase Boundaries

Phase 1 should stay focused on reproducible ingestion. Do not add interpretation or article text to the ingestion scripts.

Phase 2 should stay focused on EDA and QA: coverage checks, missingness, descriptive plots, and combined tables. Keep the `.ipynb` and `.qmd` conceptually aligned when changing analysis logic.

Phase 3 is where written analysis belongs. Keep the current skeleton as the source of narrative structure until the user is ready to write the full report.

## Key Caveats

- World Bank is the current baseline source because it provides stable annual Indonesia (`IDN`) indicators without an API key.
- World Bank PIP percentile data now provides grouped absolute consumption estimates for Indonesia in 2017 PPP USD per person per day.
- BPS remains the preferred future source for category CPI, commodity prices, administered prices, wages, informal employment, and validation of SUSENAS/BPS expenditure distribution.
- The old BPS `model=dynamictable` endpoint is not usable, but `model=var` subject discovery works. The current discovery script scans relevant subjects including consumer prices, consumption/expenditure, wages, wholesale prices, and poverty/inequality.
- Direct BPS data endpoints work when a stable variable ID is known. Current mapped examples are BPS CPI category variables `1905`, `1907`, `1909`, `1910`, `1913`, and `1915` for 2020-2023, plus wholesale rice price variable `295` for 2010-2024.
- `labor_indonesia.csv` includes ILOSTAT average monthly earnings for employees through 2023 and calculated real wage growth. This is employee wage evidence, not full household income and not informal/self-employed earnings.
- `inequality_indonesia.csv` now includes bottom/top decile shares plus grouped bottom 40%, middle 40%, and top 20% shares. `welfare_distribution_indonesia.csv` is preferred for group-level absolute welfare because it uses PIP percentile averages; current Indonesia rows use `consumption`.
- `comparative_inequality_growth.csv` provides cross-country Gini observations with future 5-year and 10-year real GDP-per-capita growth. Use it as comparative evidence only, not Indonesia-only causal proof.
- `vulnerable_employment_share` is related to informal employment but is not a direct substitute.

## Next Work

Highest-priority follow-ups:

- Add a lightweight `scripts/validate_outputs.py` that checks expected files, columns, years, and documented placeholder fields.
- Confirm stable BPS table or variable IDs for real-life cost indicators beyond CPI categories and wholesale rice.
- Add reproducible BPS download scripts once source IDs are known.
- Validate ILOSTAT wage series against BPS/Sakernas if a clean national BPS wage series is confirmed, and find an official informal employment source.
- Validate World Bank PIP percentile aggregates against BPS/SUSENAS expenditure distribution if a stable source is found.
