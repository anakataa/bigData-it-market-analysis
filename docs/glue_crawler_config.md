# AWS Glue Crawler Configuration

## Crawler Information

Crawler Name:
it-job-market-crawler

## Source Data

S3 Bucket:
s3://it-job-market-analysis-project-kstaroshchuk/raw/jobs/

## Target Database

Database:
it_job_market_db

Generated Table:
cleaned_data

## Purpose

The AWS Glue Crawler scans raw JSON job market data stored in Amazon S3 and automatically updates the schema in AWS Glue Data Catalog.

The generated metadata table is later used in Amazon Athena for SQL analytics and reporting.

## Technologies Used

- AWS Glue Crawler
- Amazon S3
- AWS Glue Data Catalog
- Amazon Athena
