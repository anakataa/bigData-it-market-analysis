# IT Job Market & Salary Analysis (Big Data Project)

## Project Overview

This project is a cloud-based Big Data analytics platform designed to collect, process, analyze, and visualize IT job market data from multiple sources.

The system focuses on identifying salary trends, technology demand, remote work impact, and global hiring patterns in the technology industry.

Using AWS cloud technologies and modern data engineering practices, the platform processes large-scale datasets and transforms them into analytical dashboards and machine learning insights.

---

# Business Problem

The modern IT job market changes rapidly across countries, technologies, and work formats. Developers, analysts, and companies often struggle to understand:

- Which technologies are most valuable
- How remote work affects salaries
- Which countries offer the best opportunities
- Which skills are most demanded
- How experience impacts compensation

This project aims to solve these problems through scalable cloud analytics and machine learning.

---

# Project Goals

- Build an end-to-end cloud data pipeline
- Process large-scale job market datasets
- Analyze salary and demand trends
- Visualize insights through dashboards
- Develop machine learning salary prediction models
- Practice modern Big Data architecture using AWS

---

# Key Analytics Questions

This project aims to answer the following questions:

1. How does remote work affect salary levels in the IT industry?

2. Which technologies and programming languages are the most in-demand?

3. Which IT roles have the highest average salaries?

4. How does experience level impact compensation?

5. Which countries and regions offer the best salaries for tech specialists?

6. Which technical skills frequently appear together in job postings?

7. Can machine learning models predict salary ranges based on job features and skills?

---

# System Architecture (AWS Stack)

The platform follows a modern cloud-native data lake architecture.

```text
Data Sources (APIs, Kaggle, CSV, PDFs)
                    ↓
          Amazon S3 (Bronze Layer)
                    ↓
        AWS Glue ETL Jobs (PySpark)
                    ↓
       Data Cleaning & Transformation
                    ↓
       Parquet Storage (Silver/Gold)
                    ↓
             AWS Glue Catalog
                    ↓
              Amazon Athena
                    ↓
         Amazon QuickSight BI
                    ↓
      Dashboards & ML Predictions
