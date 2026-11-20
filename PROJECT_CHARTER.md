# Orbital Traffic & Space Risk Intelligence Pipeline

*Working title. Project charter, v1.0*

## 1. Objective

Build an automated, end-to-end data engineering pipeline that collects public space data from three independent sources, cleans and models it, and serves analytics-ready tables that answer questions about orbital congestion, launch activity and space weather.

This is a data engineering project, not a dashboard project. The goal is to demonstrate ingestion, data quality, modeling, distributed processing, cloud storage and automation, and to explain every design decision.

## 2. Problem

Orbits are getting more crowded, launches are accelerating and solar activity affects satellites. The data to study this is public, but it is scattered across sources with different formats, update schedules and access limits. This project integrates those sources into one reliable, queryable system.

## 3. Questions the project answers

1. How crowded is each orbit band (low, medium, geostationary), and how fast is it growing?
2. Which countries and operators own the objects in orbit, and where does India stand?
3. How do launch cadence, providers and success rates change over time?
4. How often do solar storms occur, and how strong are they?
5. *Stretch:* do changes in orbital data cluster around storm dates? Correlation only; no causal claims.

## 4. Data sources

| Source | Content | Access | Notes |
|---|---|---|---|
| CelesTrak | Orbital catalog (GP data) | Free, no key | Use GP formats (JSON/CSV), not TLE. Respect throttling; do not poll repeatedly |
| Launch Library 2 (The Space Devs) | Launches, rockets, providers | Free, about 15 requests/hour unauthenticated | Backfill needs checkpoint and resume |
| NASA DONKI (api.nasa.gov) | Solar flares, CMEs, geomagnetic storms | Free NASA API key | Keep key in `.env`, never commit |

**Out of scope for v1:** Space-Track (requires an account and a data-use agreement that limits redistribution of raw data). It may be added later, and raw Space-Track data must never be committed to GitHub.

## 5. Architecture

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

Built locally first (Parquet files + DuckDB), then mirrored to AWS (S3, Glue Data Catalog, Athena) within free-tier limits.

## 6. Technology stack

- **Languages and processing:** Python, pandas, SQL (DuckDB), PySpark
- **Storage:** Parquet, local data lake, Amazon S3
- **Cloud:** AWS Glue Data Catalog, Amazon Athena
- **Visualization:** Power BI
- **Tooling:** VS Code, Git, GitHub, Jupyter

Tools are added only when the project needs them. Redshift, Airflow, Kafka and ML are deliberately out of scope.

## 7. Roadmap (about 12 weeks)

| Weeks | Phase | Outcome |
|---|---|---|
| 1-2 | Ingestion | Daily ingestion from all three sources into Bronze, with rate-limit handling and validation |
| 3-4 | Cleaning + SQL | Silver layer: cleaned, deduplicated, quality-checked |
| 5-6 | Data modeling | Orbit classification, launch-to-catalog join, Gold star schema |
| 7-8 | PySpark | Heavy transformations on accumulated daily snapshots |
| 9-10 | Cloud | Lake on S3, catalog in Glue, queries in Athena |
| 11 | Automation + tests | Incremental daily runs, automated tests |
| 12 | Dashboard + docs | Power BI, README, architecture diagram, decision log |

**Key principle:** ingestion starts in week 1 and runs daily, because CelesTrak provides only a current snapshot. History exists only if we collect it.

## 8. Engineering principles

- Bronze data is never modified; every file is timestamped
- Ingestion is idempotent: re-running it never creates duplicates
- Bad records are quarantined and reported, not silently dropped
- Automated data-quality checks run on every load
- Secrets live in `.env` and are excluded via `.gitignore`
- Every major design choice is recorded in a decision log
- A component is marked "done" only after it is built and tested

## 9. Deliverables

- Working daily pipeline with Bronze, Silver and Gold layers
- Data-quality checks and a rejected-records report
- SQL access to Gold tables
- Power BI dashboard answering the questions in section 3
- GitHub repository with README, architecture diagram, decision log and tests

## 10. Known challenges

- CelesTrak moved to 6-digit catalog numbers in July 2026; TLE format cannot represent new objects, so GP formats are required
- Finding a reliable join key between launch records and catalog objects
- Launch Library 2 rate limit makes historical backfill slow
- Accumulated history will be modest, so Spark is applied as a skill and its use is justified honestly in the documentation

## 11. Success criteria

- Pipeline runs daily without manual intervention
- Re-running any stage produces identical results
- All questions in section 3 are answerable from Gold tables
- Every component can be explained in a technical interview

## 12. Status

| Phase | Status |
|---|---|
| 1. Ingestion | Not started |
| 2. Cleaning + SQL | Not started |
| 3. Data modeling | Not started |
| 4. PySpark | Not started |
| 5. Cloud | Not started |
| 6. Automation + tests | Not started |
| 7. Dashboard + docs | Not started |
