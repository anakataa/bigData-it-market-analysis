# IT Job Market & Salary Analysis (Big Data Project)

## Project Overview

This project is focused on building a cloud-based Big Data analytics platform for analyzing the modern IT job market. The platform collects, processes, analyzes, and visualizes job-related data from multiple sources in order to identify salary trends, technology demand, and hiring patterns across the technology industry.

Using AWS cloud technologies and modern data engineering tools, the project transforms raw datasets into analytical dashboards and machine learning insights.

---

## Business Problem

The global IT job market changes rapidly depending on technologies, work formats, and regional demand. Developers, analysts, and companies often struggle to understand:

* which technologies are currently the most valuable,
* how remote work impacts salaries,
* which skills are most in demand,
* which job roles offer the highest compensation,
* and how salary trends change across different datasets.

This project aims to solve these problems through scalable cloud analytics and machine learning techniques.

---

## Project Goals

* Build an end-to-end cloud data pipeline
* Process and clean large-scale job market datasets
* Analyze salary and technology demand trends
* Create analytical dashboards and visual reports
* Develop salary prediction models using machine learning
* Practice real-world Big Data architecture using AWS services

---

## Key Analytics Questions

The project is designed to answer the following questions:

1. How does remote work affect salary levels in the IT industry?
2. Which technologies and programming languages are the most in-demand?
3. Which IT roles have the highest average salaries?
4. How does experience level impact compensation?
5. Which countries and regions offer the best salaries for tech specialists?
6. Which technical skills frequently appear together in job postings?
7. Can machine learning models predict salary ranges based on job features and technical skills?

---

## System Architecture (AWS Stack)

The platform follows a modern cloud-native data lake architecture:

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
```

---

## Technologies Used

### Cloud & Data Engineering

* Amazon S3
* AWS Glue
* AWS Athena
* Amazon QuickSight

### Data Processing

* PySpark
* Pandas
* Apache Parquet

### Machine Learning

* Scikit-learn
* Jupyter Notebook

### Programming & Query Languages

* Python
* SQL (Athena / Presto SQL)

---

## Project Structure

```text
bigData-it-market-analysis/
│
├── dashboards/           # Dashboard screenshots and BI visuals
├── data/                 # Raw and processed datasets
├── docs/                 # Documentation and Athena SQL queries
├── src/
│   ├── ingestion/        # Data ingestion scripts
│   ├── transformation/   # PySpark ETL jobs
│   ├── analysis/         # Athena SQL analytics
│   └── ml/               # Machine learning notebooks
│
├── README.md
├── requirements.txt
└── LICENSE
```

---


## License

This project is licensed under the Apache-2.0 License.
