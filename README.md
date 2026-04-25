# IT Job Market & Salary Analysis (Big Data Project)

##  Project Overview
This project is a comprehensive end-to-end data engineering and analytics system designed to collect, process, and visualize IT job market data. The primary goal is to provide insights into salary trends and demand for technical skills across different regions and employment types.

##  Key Objectives
* **Salary Correlation**: Analyze the relationship between technology stacks and compensation levels.
* **Demand Analysis**: Identify the most sought-after skills based on geographical location and work mode (Remote/Office).
* **Predictive Modeling**: Develop a regression model to estimate potential salaries based on job features.

##  System Architecture (AWS Stack)
The project is built using Amazon Web Services (AWS) and follows a 4-layer architecture:

### 1. Layer 1: Data Ingestion
* Python scripts (**Boto3**) to collect data from APIs (JSON), Kaggle (CSV), and PDF reports.
* Raw data storage in **Amazon S3 (Bronze Zone)**.

### 2. Layer 2: Transformation
* **AWS Glue (PySpark)** for data cleaning, currency normalization, and duplicate removal.
* Data conversion to **Parquet** (columnar format) and storage in **Amazon S3 (Silver/Gold Zones)**.

### 3. Layer 3: Data Serving
* **Amazon Athena** for SQL-based analysis.
* Interactive dashboards created with **Amazon QuickSight** or **Tableau**.

### 4. Layer 4: Machine Learning
* Regression model developed using **Scikit-learn** to predict salary ranges.

##  Project Structure
```text
BigData-IT-Market-Analysis/
├── data/                 # Sample data for local testing
│   ├── raw_samples/      # Sample JSON/CSV files
│   └── pdf_reports/      # Sample PDF files
├── src/                  # Source code
│   ├── 1_ingestion/      # Student 2: Data collection scripts
│   ├── 2_transformation/ # Student 1: Spark ETL scripts
│   ├── 3_serving/        # Student 3: SQL queries for Athena
│   └── 4_ml/             # Student 3: ML models and notebooks
├── dashboards/           # Visualization files or screenshots
├── docs/                 # Project documentation and reports
├── .gitignore            # AWS credential and data exclusion
├── requirements.txt      # Project dependencies
└── README.md             # Project roadmap and description
