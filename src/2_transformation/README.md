# 2 Transformation

This folder contains the data cleaning and transformation logic.

## What it does

The transformation script reads raw data from Amazon S3, cleans it with PySpark, prepares useful columns, and saves the processed data back to S3 in Parquet format.

## Why this folder is needed

Raw data from APIs is usually messy and not ready for analysis. This step prepares the dataset so it can be queried in Athena, used in dashboards, and later used for machine learning.

## Main file

- `glue_spark_transformation.py` — AWS Glue / PySpark job for cleaning and saving processed data.
