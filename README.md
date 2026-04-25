# IT Job Market & Salary Analysis (Big Data Project)

## Project Overview
This project is a comprehensive end-to-end data engineering and analytics system designed to collect, process, and visualize IT job market data. [cite_start]The primary goal is to provide insights into salary trends and demand for technical skills across different regions and employment types[cite: 4].

## Key Objectives
* [cite_start]**Salary Correlation**: Analyze the relationship between technology stacks and compensation levels[cite: 5].
* [cite_start]**Demand Analysis**: Identify the most sought-after skills based on geographical location and work mode (Remote/Office)[cite: 6].
* [cite_start]**Predictive Modeling**: Develop a regression model to estimate potential salaries based on job features[cite: 33].

## System Architecture (AWS Stack)
[cite_start]The project is built using Amazon Web Services (AWS) and follows a 4-layer architecture[cite: 7, 8]:

1.  **Layer 1: Data Ingestion**
    * [cite_start]Python scripts (Boto3) to collect data from APIs (JSON), Kaggle (CSV), and PDF reports[cite: 9, 10].
    * [cite_start]Raw data storage in **Amazon S3 (Bronze Zone)**[cite: 9].
2.  **Layer 2: Transformation**
    * [cite_start]**AWS Glue (PySpark)** for data cleaning, currency normalization, and duplicate removal[cite: 11].
    * [cite_start]Data conversion to **Parquet** (columnar format) and storage in **Amazon S3 (Silver/Gold Zones)**[cite: 11, 12, 37].
3.  **Layer 3: Data Serving**
    * [cite_start]**Amazon Athena** for SQL-based analysis[cite: 13, 31].
    * [cite_start]Interactive dashboards created with **Amazon QuickSight** or **Tableau**[cite: 13, 32].
4.  **Layer 4: Machine Learning**
    * [cite_start]Regression model developed using **Scikit-learn** to predict salary ranges[cite: 14, 33, 64].

## Project Structure
```text
BigData-IT-Market-Analysis/
[cite_start]├── data/                 # Sample data for local testing [cite: 46]
[cite_start]│   ├── raw_samples/      # Sample JSON/CSV files [cite: 47, 54]
[cite_start]│   └── pdf_reports/      # Sample PDF files [cite: 48, 55]
[cite_start]├── src/                  # Source code [cite: 49]
[cite_start]│   ├── 1_ingestion/      # Data collection scripts [cite: 50, 57]
[cite_start]│   ├── 2_transformation/ # Spark ETL scripts [cite: 60]
[cite_start]│   ├── 3_serving/        # SQL queries for Athena [cite: 61, 62]
[cite_start]│   └── 4_ml/             # ML models and notebooks [cite: 63, 64]
[cite_start]├── dashboards/           # Visualization files or screenshots [cite: 65]
[cite_start]├── docs/                 # Project documentation and reports [cite: 65, 66]
[cite_start]├── .gitignore            # AWS credential and data exclusion [cite: 37, 46, 53]
[cite_start]├── requirements.txt      # Project dependencies [cite: 46, 54]
[cite_start]└── README.md             # Project roadmap and description [cite: 45]
Team Roles

Student 1 (Cloud Engineer): Infrastructure, IAM roles, and AWS Glue ETL pipelines.


Student 2 (Data Ingestion): Data sourcing, API scrapers, and PDF parsers.


Student 3 (ML Engineer): SQL analytics, ML modeling, and full project documentation.