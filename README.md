# OrbitWatch: Orbital Traffic & Space Risk Intelligence Pipeline

An end-to-end data engineering project that integrates public orbital, launch and space-weather data into clean, analytics-ready tables, built layer by layer with Python, SQL, PySpark and AWS.

> **Status: in development.** This README describes the planned design. Sections are marked as complete only after the component is built and tested. See [Project Status](#project-status).

## Why this project

Orbits are getting more crowded, launches are accelerating, and solar activity affects satellites. The data to study this is public, but it is spread across sources with different formats, update schedules and access limits. OrbitWatch brings these sources together into one reliable, queryable system.

## Questions it answers

1. How crowded is each orbit band (low, medium, geostationary), and how fast is it growing?
2. Which countries and operators own the objects in orbit?
3. How do launch cadence, providers and success rates change over time?
4. How often do solar storms occur, and how strong are they?
5. *Stretch:* do changes in orbital data cluster around storm dates? (Correlation only; no causal claims.)

## Data sources

| Source | Content | Access |
|---|---|---|
| [CelesTrak](https://celestrak.org) | Orbital catalog (GP data) | Free, no key |
| [Launch Library 2](https://thespacedevs.com/llapi) | Launches, rockets, providers | Free, rate-limited |
| [NASA DONKI](https://api.nasa.gov) | Solar flares, CMEs, geomagnetic storms | Free NASA API key |

## Architecture

```
CelesTrak ─┐
Launch Lib ─┼─> Python ingestion ─> BRONZE (raw, untouched, timestamped)
NASA DONKI ─┘                            │
                                          v
                              SILVER (cleaned, validated, deduplicated)
                                          │
                                          v
                              GOLD (star schema, analytics-ready)
                                          │
                                          v
                              SQL queries ─> Power BI dashboard
```

*An architecture diagram will be added in `docs/` once the pipeline is running.*

The pipeline is built locally first (Parquet + DuckDB), then mirrored to AWS (S3, Glue Data Catalog, Athena) within free-tier limits.

## Tech stack

Python · pandas · SQL (DuckDB) · PySpark · Parquet · Amazon S3 · AWS Glue · Amazon Athena · Power BI · Git

## Engineering principles

- Bronze data is never modified, and every file is timestamped
- Ingestion is idempotent: re-running never creates duplicates
- Bad records are quarantined and reported, not silently dropped
- Automated data-quality checks run on every load
- Secrets live in `.env` and are never committed
- Major design decisions are recorded in a decision log

## Project structure (planned)

```
orbitwatch-data-pipeline/
├── data/
│   ├── bronze/        # raw data, untouched
│   ├── silver/        # cleaned and validated
│   └── gold/          # analytics-ready tables
├── src/               # ingestion, transformation, validation code
├── tests/
├── notebooks/
├── docs/              # architecture diagram, decision log
├── .env.example       # template for required keys (no real keys)
├── requirements.txt
└── PROJECT_CHARTER.md
```

## Getting started

*Setup instructions will be added once the ingestion phase is built and tested.*

You will need a free NASA API key from [api.nasa.gov](https://api.nasa.gov). Never commit your key; store it in a local `.env` file.

## Data usage notes

- CelesTrak throttles repeated requests, so the pipeline is designed to fetch each source no more often than needed.
- Raw data from licensed sources such as Space-Track is **not** included in this repository.

## Project status

| Phase | Status |
|---|---|
| 1. Ingestion | Not started |
| 2. Cleaning + SQL | Not started |
| 3. Data modeling | Not started |
| 4. PySpark | Not started |
| 5. Cloud (S3, Glue, Athena) | Not started |
| 6. Automation + tests | Not started |
| 7. Dashboard + docs | Not started |

## Documentation

- [Project Charter](PROJECT_CHARTER.md): objective, scope, roadmap and principles

## License

MIT
