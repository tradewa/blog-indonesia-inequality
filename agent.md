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
- Phase 3 is complete as a first markdown report draft for user review.

Implemented:

- World Bank-backed download scripts for GDP, inflation, inequality, poverty, labor, and cost-of-living baseline data.
- Raw API response persistence under `data/raw/`, ignored by git.
- Standardized annual processed CSVs under `data/processed/`, ignored by git.
- A BPS dynamic-table discovery script that records failure output when the BPS API does not return usable metadata.
- Phase 2 EDA notebook at `notebooks/eda_indonesia_inequality.ipynb`.
- Phase 2 R/Quarto equivalent at `notebooks/eda_indonesia_inequality.qmd`.
- Phase 3 analysis report at `reports/indonesia_inequality_eda_report.md` with chart images under `reports/figures/`.
- Project-local R package management through `renv`.

Not implemented:

- Final statistical modeling.
- Dashboarding or publication narrative.
- BPS-backed fills for category CPI, commodity/administered prices, wages, informal employment, or SUSENAS-specific distribution fields.
- Output validation checks.

## Operating Rule

Do not fabricate or hand-copy blank BPS-backed fields into processed CSVs. If a field is filled, the raw source must be saved under `data/raw/` and the transformation into `data/processed/` must be reproducible from code.

Generated data files should stay out of git. Keep `data/raw/.gitkeep` and `data/processed/.gitkeep` only; users should rebuild raw JSON and processed CSV outputs locally.

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

Phase 3 is where written analysis belongs. Keep the report clearly provisional until missing BPS/SUSENAS, wage, and cost-of-living sources are filled.

## Key Caveats

- World Bank is the current baseline source because it provides stable annual Indonesia (`IDN`) indicators without an API key.
- BPS remains the preferred future source for category CPI, commodity prices, administered prices, wages, informal employment, and SUSENAS/BPS expenditure distribution.
- The current BPS discovery failure is recorded at `data/raw/bps_dynamic_tables_page1_error.json`.
- `inequality_indonesia.csv` now includes bottom/top decile shares plus grouped bottom 40%, middle 40%, and top 20% shares. All distribution shares may be based on income or consumption depending on survey metadata.
- `vulnerable_employment_share` is related to informal employment but is not a direct substitute.

## Next Work

Highest-priority follow-ups:

- Add a lightweight `scripts/validate_outputs.py` that checks expected files, columns, years, and documented placeholder fields.
- Confirm stable BPS table IDs for CPI categories and real-life cost indicators.
- Add reproducible BPS download scripts once table IDs are known.
- Confirm an official source for wages, real wage growth, and informal employment.
- Replace World Bank distribution-share proxies with BPS/SUSENAS expenditure distribution if available.
