    # Source Code

All executable project logic — Python scripts, the Glue job, and the analytics notebook — lives
under `src/`. The folders are numbered to make the data flow obvious at a glance.

## Pipeline layers

| #   | Folder                                   | What it does                                                                    | Main file                      |
| --- | ---------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------ |
| 1   | [`1_ingestion/`](1_ingestion/)           | Scrapes Adzuna API, normalizes vacancies, uploads to S3                         | `adzuna_parser.py`             |
| 2   | [`2_transformation/`](2_transformation/) | PySpark / AWS Glue job — cleans data, writes Parquet (reference implementation) | `glue_spark_transformation.py` |
| 3   | [`3_serving/`](3_serving/)               | Reserved for serving layer                                                      | —                              |
| 4   | [`4_ml/`](4_ml/)                         | Machine-learning extension — salary prediction (work in progress)               | `salary_model.ipynb`           |

Plus one helper at the root:

- **`visualization.py`** — reads the CSV exports from `data/results/` and renders the three final
  charts saved under `dashboards/`. Run after Athena queries have been exported.

## Data flow

```text
1_ingestion ──► S3 (raw NDJSON) ──► Glue Crawler ──► Athena ──► CSV exports ──► visualization.py
                                                                                    │
                                                                                    ▼
                                                                                dashboards/
```

## Why the numbered folders

Pipeline-shaped layouts read top-to-bottom like the actual data flow. New contributors don't have to
guess which step depends on which.

## Conventions

- All secrets live in `.env` at the repo root (git-ignored — see [`.gitignore`](../.gitignore)).
- All file paths are written with forward slashes (Linux-style) — works on Windows too.
- All scripts assume the **working directory is the repo root**, not the script's own folder.
