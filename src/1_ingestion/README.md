# 1 Ingestion

This folder contains scripts responsible for collecting raw job market data.

## What it does

The ingestion part downloads vacancies from the Adzuna API, extracts useful information, detects technical skills, checks whether a job is remote or hybrid, saves the results locally, and uploads the raw file to Amazon S3.

## Why this folder is needed

This is the first step of the Big Data pipeline. Without ingestion, the project would not have data to clean, analyze, visualize, or use for machine learning.

## Main files

- `adzuna_parser.py` — main script that collects vacancies from the API and saves them as NDJSON.
- `utils.py` — helper functions for skill extraction and remote work detection.
- `s3_uploader.py` — uploads collected files to an S3 bucket.
