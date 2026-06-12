# 2. Transformation Layer

A reference PySpark / AWS Glue job that takes raw NDJSON from the S3 bronze zone, drops records
with missing salary, normalizes the job title, and writes the result back to S3 as Parquet.

## File

| File                           | Purpose                                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------------------- |
| `glue_spark_transformation.py` | AWS Glue ETL job — reads raw NDJSON, applies cleaning, writes Parquet to a "processed" zone. |

## What the job does

1. **Reads** all NDJSON files from `s3://$BUCKET/raw/`.
2. **Drops** rows where `salary` is `NULL` (so downstream `AVG()` is honest).
3. **Adds** a `job_title_clean` column = lower-cased `job_title` (used for `GROUP BY`).
4. **Writes** the result as **Parquet** to `s3://$BUCKET/processed/cleaned_data/`.
5. **Logs** the final row count and commits the Glue Job.

## Status: reference implementation

The production analytical path in this project queries the **raw NDJSON directly** via AWS Glue
Crawler + Athena — the Crawler does the schema inference, and Athena handles SQL-side cleansing
through `WHERE salary IS NOT NULL` and `HAVING COUNT(*) > 1` clauses.

This Spark job is kept as a reference for two reasons:

- It demonstrates the canonical Glue/Spark pattern for the project's transformation layer.
- It is the bridge to a future scaled-up pipeline where partitioned Parquet would replace ad-hoc
  NDJSON scans (10×+ faster queries, lower Athena scan costs).

## How to run on AWS

1. Upload `glue_spark_transformation.py` to an S3 location accessible by Glue.
2. Create a Glue Job (Spark, Python 3, Glue version 4.0+).
3. Attach the IAM role `Glue-S3-Project-Role` (S3 + CloudWatch permissions).
4. Set worker type `G.1X`, 2 workers — plenty for this dataset size.
5. Trigger the job. Output appears at `s3://$BUCKET/processed/cleaned_data/`.

## Why Parquet

Parquet is the columnar standard for analytical workloads on object storage:

- **Columnar** → Athena reads only the columns referenced by the query.
- **Compressed** → typically 5–10× smaller than the equivalent JSON.
- **Schema-aware** → no per-query schema inference, no surprises with type coercion.

Once the dataset grows beyond a few thousand records, switching the Crawler target from `raw/` to
`processed/cleaned_data/` is a one-line change with an outsized win on query latency and cost.
