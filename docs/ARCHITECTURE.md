# Architecture

This document describes the **actual** architecture of the IT Job Market & Salary Analysis
pipeline as delivered — not the original planning diagram.

## TL;DR

A fully serverless AWS pipeline. Python scraper writes NDJSON to S3 → Glue Crawler builds a
catalog → Athena runs SQL → results exported as CSV → matplotlib renders the final charts. No
managed compute, no idle servers, no operational overhead.

## Component diagram

```text
                         ┌─────────────────────────┐
                         │   Adzuna REST API       │
                         │   (US, UK, Poland)      │
                         └────────────┬────────────┘
                                      │
                                      │ HTTP/JSON
                                      ▼
              ┌────────────────────────────────────────────┐
              │  Python Scraper  (src/1_ingestion/)        │
              │  ───────────────────────────────────────── │
              │  • adzuna_parser.py  — main loop           │
              │  • utils.py          — skill extraction    │
              │  • s3_uploader.py    — boto3 PUT           │
              │                                            │
              │  Normalization:                            │
              │    • salary → USD/year                     │
              │    • skills → regex over 80-tech list      │
              │    • remote → keyword scan (EN + PL)       │
              └────────────────────────┬───────────────────┘
                                       │
                                       │ NDJSON (1 JSON / line)
                                       ▼
              ┌────────────────────────────────────────────┐
              │  Amazon S3 — Bronze Zone                   │
              │  s3://it-job-market-analysis-project-      │
              │       kstaroshchuk/raw/jobs/               │
              │  Region: eu-north-1 (Stockholm)            │
              └────────────────────────┬───────────────────┘
                                       │
                                       │ on-demand scan
                                       ▼
              ┌────────────────────────────────────────────┐
              │  AWS Glue Crawler                          │
              │  it-job-market-crawler                     │
              │  ───────────────────────────────────────── │
              │  Infers schema from NDJSON                 │
              │  Publishes table:                          │
              │    it_job_market_db.cleaned_data           │
              │  Columns: job_title, job_title_clean,      │
              │           salary, currency, skills         │
              └────────────────────────┬───────────────────┘
                                       │
                                       │ schema lookup
                                       ▼
              ┌────────────────────────────────────────────┐
              │  Amazon Athena                             │
              │  ───────────────────────────────────────── │
              │  Distributed Presto SQL over S3            │
              │  Key pattern:                              │
              │    CROSS JOIN UNNEST(skills) AS t(skill)   │
              │  9 queries → 3 analytical outputs          │
              └────────────────────────┬───────────────────┘
                                       │
                                       │ "Download results CSV"
                                       ▼
              ┌────────────────────────────────────────────┐
              │  data/results/*.csv                        │
              │  (versioned in Git)                        │
              └────────────────────────┬───────────────────┘
                                       │
                                       │ pandas read
                                       ▼
              ┌────────────────────────────────────────────┐
              │  src/visualization.py — matplotlib         │
              │  → dashboards/*.png                        │
              └────────────────────────────────────────────┘
```

## Component reference

### 1. Adzuna scraper

- Iterates over 3 countries × 120 pages × 50 results per page.
- Filters out non-technical vacancies (must mention ≥ 2 known skills).
- Converts every salary to USD/year regardless of original currency or period.
- Emits NDJSON line-by-line (so streaming ingestion is trivial later).

### 2. S3 bronze zone

A single regional bucket, three logical prefixes:

| Prefix | Purpose |
|---|---|
| `raw/jobs/` | Bronze — raw NDJSON files as captured. |
| `processed/` | Silver — reserved for the future Parquet output of the Glue Spark job. |
| `athena-results/` | Athena query result manifests and output files. |

Files are named `jobs_YYYY_MM_DD.ndjson` for easy date-based partitioning later.

### 3. AWS Glue Crawler

| Setting | Value |
|---|---|
| Name | `it-job-market-crawler` |
| Source | `s3://it-job-market-analysis-project-kstaroshchuk/raw/jobs/` |
| IAM role | `Glue-S3-Project-Role` (policies: `AWSGlueServiceRole`, `AmazonS3FullAccess`) |
| Target DB | `it_job_market_db` |
| Output table | `cleaned_data` |

### 4. Amazon Athena

Athena is the analytical workhorse — no infrastructure, just SQL. The defining feature of our
queries is the `CROSS JOIN UNNEST(skills) AS t(skill)` pattern, which flattens the nested
`array<string>` skills column into one row per (vacancy, skill) pair. Without this, every
skill-level metric would require pre-processing.

Full SQL inventory: [`athena_queries.sql`](athena_queries.sql).

### 5. Decoupled local BI

A 90-line matplotlib script ([`src/visualization.py`](../src/visualization.py)) that reads the
three CSV exports from `data/results/` and writes the three PNGs in `dashboards/`. Idempotent,
reproducible, version-controlled.

## Design decisions & trade-offs

### Why NDJSON over a single JSON array

Each NDJSON line is an independent record. The file can be:

- Appended to without re-parsing.
- Read in parallel.
- Tail-truncated at any line boundary without corrupting the rest.

JSON arrays don't allow any of that.

### Why query raw NDJSON instead of Parquet

The Glue Spark transformation job (`src/2_transformation/glue_spark_transformation.py`) exists
and works, but for a 519-record dataset the upfront ETL pass costs more than it saves. Athena
scans NDJSON happily for this volume.

The threshold to switch is somewhere around **tens of thousands of records** — once the per-query
scan size makes Athena cost or latency noticeable, moving to partitioned Parquet (Athena scans
only the relevant partition, and the columnar format compresses ~5–10×) becomes a one-day change.

### Why we abandoned Amazon QuickSight

QuickSight registration looped silently in `eu-north-1` during the project window — the signup
form would seemingly succeed but the account never materialized in the console. We tried other
regions; the same loop appeared with our IAM user.

Rather than wait for AWS support, we decoupled the BI layer. Athena exports CSV, matplotlib
renders charts, and the chart code lives in version control alongside the rest of the pipeline.
The analytical outputs are identical; reproducibility actually improved.

### Why IAM users per team member

We avoided sharing the root account. Each contributor got a scoped IAM user with the minimum
policies needed for their layer:

| User | Policies |
|---|---|
| Ingestion (Misha) | `AmazonS3FullAccess` (write-only to bronze zone) |
| Analytics (Dima) | `AmazonAthenaFullAccess`, `AWSGlueConsoleFullAccess`, `IAMReadOnlyAccess` |
| Lead (Kirill) | Admin |

The Glue Crawler runs under its own service role (`Glue-S3-Project-Role`) — service-to-service
identity, not user-to-service.

## Failure modes & mitigations

| Failure mode | Mitigation |
|---|---|
| Adzuna rate-limits or returns 5xx | Scraper logs and skips the page; the run continues. |
| Network drop mid-upload | S3 multipart upload retries automatically via `boto3`. |
| Crawler infers wrong types | Schema changes are non-destructive — re-running creates a new table version. |
| Athena query times out | Queries are cheap; just re-run. For larger data, partition by `collected_at`. |
| Secrets accidentally committed | `.env` is in `.gitignore`; pre-commit review during PRs. |

## What's next

- **Partition by date** in S3 (`raw/jobs/year=2026/month=05/day=18/`). Smaller Athena scans.
- **Convert to Parquet** in the silver zone. Columnar compression + projection pushdown.
- **Lambda + EventBridge** to make the scraper fully autonomous.
- **SageMaker** to train the salary-prediction model in the cloud rather than locally.
- **Re-enable QuickSight** once the regional rollout stabilizes, for a hosted dashboard.
