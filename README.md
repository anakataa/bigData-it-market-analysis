# IT Job Market & Salary Analysis

> A cloud-native, fully serverless Big Data pipeline on AWS — ingesting, cataloging, and analyzing **519 live IT vacancies** to surface salary trends and demanded technologies.

![AWS](https://img.shields.io/badge/AWS-Serverless-FF9900?logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Athena](https://img.shields.io/badge/Amazon-Athena-7B42BC?logo=amazon-aws&logoColor=white)
![Glue](https://img.shields.io/badge/AWS-Glue-FF9900?logo=amazon-aws&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-delivered-success)

---

## Table of Contents

- [Overview](#-overview)
- [Team](#-team)
- [Architecture](#-architecture)
- [Key Findings](#-key-findings)
- [Repository Structure](#-repository-structure)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Course Criteria Mapping](#-course-criteria-mapping)
- [License](#-license)

---

## Overview

The global IT job market shifts faster than any quarterly report can keep up with. This project answers the
question every developer, recruiter, and hiring manager actually cares about — **which technologies are
in demand right now, and which ones actually pay** — by building a real, end-to-end Big Data analytics
pipeline on AWS.

We ingest live job listings from the [Adzuna API](https://developer.adzuna.com/) (US, UK, Poland),
land them in Amazon S3 as NDJSON, let AWS Glue Crawler infer the schema, and run serverless SQL
analytics over the result in Amazon Athena. The final aggregates are exported to CSV and rendered as
charts via a lightweight matplotlib script.

### Why this matters

Most "tech trend" reports rely on surveys. We rely on the actual hiring market — which is louder,
faster, and a lot more honest about what companies will pay for.

---

## Team

| Member                 | Role                             | Owned Layer                                          |
| ---------------------- | -------------------------------- | ---------------------------------------------------- |
| **Kirill Staroshchuk** | Project Lead & Cloud Architect   | AWS infrastructure, IAM, coordination, documentation |
| **Mykhailo Bitiukov**  | Data Acquisition Engineer        | Python scraper, ingestion, S3 upload                 |
| **Dmytro Buran**       | Cloud Data Engineer & BI Analyst | Glue Crawler, Athena SQL, visualizations             |

---

## 🏗 Architecture

The pipeline is fully serverless — no managed clusters, no idle compute, no EC2 to babysit.

```text
┌─────────────────────┐
│  Adzuna Live API    │   (US, UK, Poland)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Python Scraper     │   adzuna_parser.py
│  • normalization    │   → salary → USD/year
│  • skill extraction │   → regex tagging
│  • remote detection │   → keyword scan
└──────────┬──────────┘
           │ NDJSON
           ▼
┌─────────────────────┐
│  Amazon S3          │   it-job-market-analysis-project-kstaroshchuk
│  (Bronze / raw)     │   region: eu-north-1
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AWS Glue Crawler   │   schema inference
│  it-job-market-     │   → it_job_market_db
│  crawler            │   → table: cleaned_data
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Amazon Athena      │   Presto SQL
│  CROSS JOIN UNNEST  │   → flatten skills array
└──────────┬──────────┘
           │ CSV exports
           ▼
┌─────────────────────┐
│  Local BI Layer     │   matplotlib (visualization.py)
│  (decoupled)        │   → 3 final dashboards
└─────────────────────┘
```

> **Note on the architecture diagram:** The original plan called for Amazon QuickSight as the
> BI front-end and a PySpark/Glue transformation layer producing Parquet output. The QuickSight
> registration looped repeatedly in `eu-north-1`, so we pivoted to a decoupled local BI layer
> driven by Athena CSV exports. The Glue Spark transformation script is preserved in
> `src/2_transformation/` for completeness — the production path queries the raw NDJSON directly.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full architectural rationale and
trade-offs.

---

## Key Findings

Across **519 normalized vacancies** collected in May 2026:

### Top 3 Most Demanded Skills

| Rank | Skill  | Mentions | Share of corpus |
| ---- | ------ | -------- | --------------- |
| 1    | SQL    | 99       | 19.1%           |
| 2    | Python | 72       | 13.9%           |
| 3    | Java   | 56       | 10.8%           |

**Insight:** Cloud & DevOps skills (CI/CD, Azure, Kubernetes, AWS) form a strong second tier —
they are no longer a specialization, they are baseline expectations.

### Top 3 Highest Paying Skills

| Rank | Skill   | Avg. Salary (USD/yr) | Sample size |
| ---- | ------- | -------------------- | ----------- |
| 1    | GraphQL | 971,748              | 5           |
| 2    | Django  | 948,555              | 4           |
| 3    | Node.js | 427,546              | 11          |

**Insight:** Top compensation is concentrated in niche / senior-contract roles. The truer
"mid-premium" tier sits at 350K–430K USD (Kafka, Rust, MongoDB) — distributed-systems work.

### Top-Paying Role

> **Senior AWS Developer (Contracting):** **4.3M USD/year**, ~3× the senior baseline.

A clear premium on cloud-native seniority. Full results in [`data/results/`](data/results/) and
visualized in [`dashboards/`](dashboards/).

---

## 📁 Repository Structure

```text
bigData-it-market-analysis/
│
├── dashboards/                       # Final charts (PNG) + Athena query screenshots
│   ├── salary_by_role.png
│   ├── top_paying_skills.png
│   └── top_skills_analysis.png
│
├── data/
│   ├── raw_samples/                  # NDJSON samples of scraped vacancies
│   │   └── jobs_2026_05_18.ndjson
│   └── results/                      # CSV aggregates exported from Athena
│       ├── salary_by_role.csv
│       ├── top_paying_skills.csv
│       └── top_skills_analysis.csv
│
├── docs/
│   ├── ARCHITECTURE.md               # Detailed architecture + trade-offs
│   ├── athena_queries.sql            # 9 production SQL queries
│   └── glue_crawler_config.md        # Crawler configuration reference
│
├── src/
│   ├── 1_ingestion/                  # Python scraper (Adzuna → S3)
│   │   ├── adzuna_parser.py          #   main pipeline entry
│   │   ├── utils.py                  #   skill extraction + remote detection
│   │   └── s3_uploader.py            #   boto3 upload helper
│   ├── 2_transformation/             # PySpark/Glue cleaning job (reference)
│   │   └── glue_spark_transformation.py
│   ├── 3_serving/                    # Reserved for BI / serving layer
│   ├── 4_ml/                         # ML extension (work in progress)
│   │   └── salary_model.ipynb
│   └── visualization.py              # Local matplotlib chart generator
│
├── README.md                         # ← you are here
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Excludes .env, venv, __pycache__
└── LICENSE                           # MIT
```

---

## 🛠 Technology Stack

| Layer              | Tools                                                               |
| ------------------ | ------------------------------------------------------------------- |
| **Ingestion**      | Python 3.10+, `requests`, `boto3`, `python-dotenv`, Adzuna REST API |
| **Storage**        | Amazon S3 (bronze raw zone, NDJSON)                                 |
| **Cataloging**     | AWS Glue Crawler, AWS Glue Data Catalog                             |
| **Query Engine**   | Amazon Athena (Presto SQL, `CROSS JOIN UNNEST`)                     |
| **Visualization**  | pandas, matplotlib (decoupled local BI)                             |
| **ML (extension)** | scikit-learn, Jupyter                                               |
| **Security**       | AWS IAM (least-privilege per-user keys, service roles)              |
| **VCS**            | Git + GitHub feature-branch workflow with pull requests             |

---

## Quick Start

### Prerequisites

- Python 3.10+
- An AWS account with permissions to create S3 buckets, IAM users, and Glue resources
- Adzuna API credentials ([free tier sign-up](https://developer.adzuna.com/))

### 1. Clone & install

```bash
git clone https://github.com/anakataa/bigData-it-market-analysis.git
cd bigData-it-market-analysis

python -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the repo root (already git-ignored):

```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=eu-north-1
S3_BUCKET_NAME=your-bucket-name
```

### 3. Run the pipeline end-to-end

```bash
# 1. Ingest: scrape vacancies → NDJSON → S3
python src/1_ingestion/adzuna_parser.py

# 2. Catalog: run Glue Crawler (one click in the AWS Console,
#    or via aws glue start-crawler --name it-job-market-crawler)

# 3. Analyze: execute queries from docs/athena_queries.sql in Athena,
#    download the CSV results into data/results/

# 4. Visualize: regenerate the dashboards locally
python src/visualization.py
```

---

## Documentation

- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture and design decisions
- 📄 [`docs/athena_queries.sql`](docs/athena_queries.sql) — full SQL inventory
- 📄 [`docs/glue_crawler_config.md`](docs/glue_crawler_config.md) — crawler configuration
- **Technical Documentation (Word)** — full 13-section report
- **Presentation Deck (PowerPoint)** — 13 slides, executive summary

---
