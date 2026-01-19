# Netherlands COVID-19 Dashboard and Analysis Project

## Portfolio Narrative
This repository is a portfolio-ready data analytics project that demonstrates how I ingest public health data, clean and model it, and publish analysis-ready datasets and visuals. The project focuses on COVID-19 trends in the Netherlands and highlights the end-to-end workflow I would use in a data analytics role: reproducible data extraction, transparent data cleaning, and storytelling through visual exploration.

## Project Goals
- **Build a reusable data pipeline** that fetches authoritative COVID-19 data from the Dutch RIVM.
- **Produce standardized, analysis-ready datasets** for national and provincial trend analysis.
- **Enable exploratory analysis and visualization** via notebooks and Dash prototypes.

## End-to-End Workflow
1. **Data ingestion**: Pull raw datasets from RIVM’s public endpoints (cumulative cases, daily cases, case demographics, reproduction rate, and contagiousness estimates).
2. **Data cleaning**: Normalize column names, parse dates, remove redundant fields, and aggregate to national and provincial levels.
3. **Dataset publishing**: Export raw datasets to `raw-data/` and curated datasets to `clean-data/` for repeatable analysis.
4. **Exploratory analysis & visualization**: Use notebooks under `plot-scripts/` for charting and geospatial exploration, plus Dash prototypes for dashboard interactions.

## Analyses Included
- **National time series trends**: Daily and cumulative cases, hospital admissions, and deaths over time.
- **Provincial comparisons**: Daily and cumulative metrics aggregated by province.
- **Descriptive case analysis**: Demographics and case metadata (age group, sex, province, statistics type).
- **Reproduction rate (R)**: Low/average/high estimates of COVID-19 reproduction rate.
- **Contagiousness estimates**: Low/average/high prevalence estimates derived from RIVM data.

## Repository Map
- `workflows/rivm.py` — ETL pipeline that downloads raw data and produces cleaned datasets.
- `raw-data/` — Unmodified source exports from RIVM.
- `clean-data/` — Curated, analysis-ready CSV files.
- `plot-scripts/` — Jupyter notebooks for plotting and geospatial analysis.
- `dash_test.py`, `report.py` — Dash prototypes for interactive dashboards.
- `assets/` and `plots/` — Styling and generated visual assets.

## How to Run the Data Pipeline
```bash
python workflows/rivm.py
```
This regenerates `raw-data/` and `clean-data/` from the latest RIVM endpoints.

## Example Visualizations
The notebooks in `plot-scripts/` include national, provincial, and descriptive analysis views, as well as geospatial mapping using the Netherlands GeoJSON files stored under `plot-scripts/` and `external/`.

## Data Sources
- RIVM COVID-19 datasets: https://data.rivm.nl/covid-19/

## Licenses & Acknowledgements
- Data provided by the Dutch National Institute for Public Health and the Environment (RIVM).
- Third-party geo data sources are included under `external/` with their original attribution.
