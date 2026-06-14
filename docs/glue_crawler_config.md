# AWS Glue Crawler Configuration

This project uses two AWS Glue Crawlers: one for the raw NDJSON layer and one for the processed Parquet silver layer.

## Crawler 1 — Raw NDJSON Layer

| Field | Value |
|---|---|
| Crawler Name | `it-job-market-crawler` |
| Data source | `s3://it-job-market-analysis-project-kstaroshchuk/raw/jobs/` |
| IAM Role | `Glue-S3-Project-Role` |
| Target database | `it_job_market_db` |
| Generated table | `cleaned_data` |
| Data format | NDJSON / JSON |

### Purpose

The raw crawler scans job market data stored as newline-delimited JSON in Amazon S3 and creates metadata in the AWS Glue Data Catalog. Athena uses this table for SQL analytics over the raw lake layer.

## Crawler 2 — Processed Parquet Layer

| Field | Value |
|---|---|
| Crawler Name | `it-job-market-crawler-processed` |
| Data source | `s3://it-job-market-analysis-project-kstaroshchuk/processed/cleaned_data/` |
| IAM Role | `Glue-S3-Project-Role` |
| Target database | `it_job_market_db` |
| Table prefix | `processed_` |
| Generated table | `processed_cleaned_data` |
| Data format | Parquet |

### Purpose

The processed crawler scans the silver-zone Parquet output created by the Glue Spark ETL job. This allows Athena to query optimized columnar files instead of only the raw JSON data.

## Validation queries

```sql
SHOW TABLES IN it_job_market_db;
```

Expected tables:

```text
cleaned_data
processed_cleaned_data
```

```sql
SELECT skill, COUNT(*) AS demand
FROM it_job_market_db.processed_cleaned_data
CROSS JOIN UNNEST(skills) AS t(skill)
GROUP BY skill
ORDER BY demand DESC
LIMIT 10;
```

## Technologies Used

- AWS Glue Crawler
- AWS Glue Data Catalog
- AWS Glue Spark ETL
- Amazon S3
- Amazon Athena
- Parquet
