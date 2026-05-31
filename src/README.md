# Source Code

This folder contains the main source code of the project.

## What it does

It stores scripts and notebooks used for data ingestion, transformation, serving/analysis, and machine learning.

## Why this folder is needed

The `src` folder separates executable project logic from data, documentation, and dashboard files. This makes the project structure cleaner and easier to navigate.

## Folder structure

- `1_ingestion/` — collects raw job data and uploads it to AWS S3.
- `2_transformation/` — cleans and transforms raw data using AWS Glue and PySpark.
- `3_serving/` — reserved for serving or final analytical layer files.
- `4_ml/` — contains machine learning work, including salary prediction notebooks.
