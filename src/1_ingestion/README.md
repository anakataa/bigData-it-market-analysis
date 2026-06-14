# 1. Ingestion Layer

The first stage of the pipeline collects raw IT job market data from multiple sources, normalizes it into a common schema, saves it locally as NDJSON, and uploads it to the project's S3 raw zone.

Currently implemented sources:

1. Adzuna REST API
2. Kaggle Data Science Salaries CSV

---

## Files

| File               | Purpose                                                                                                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `adzuna_parser.py` | Main entry point for Adzuna ingestion. It collects IT vacancies from the Adzuna API, normalizes salaries, extracts skills, detects remote jobs, writes NDJSON, and uploads the file to S3. |
| `kaggle_loader.py` | Loads the Kaggle Data Science Salaries CSV file, normalizes salary records to the common project schema, writes NDJSON, and uploads the file to S3.                                        |
| `utils.py`         | Helper functions for text analysis, mainly skill extraction and remote/hybrid job detection.                                                                                               |
| `s3_uploader.py`   | Reusable `boto3` helper that uploads a local file to the configured S3 bucket.                                                                                                             |

---

## Data sources

### Adzuna REST API

The Adzuna ingestion script collects live IT vacancies from selected countries.

Default countries:

| Country code | Region         | Default currency |
| ------------ | -------------- | ---------------- |
| `us`         | United States  | USD              |
| `gb`         | United Kingdom | GBP              |
| `pl`         | Poland         | PLN              |

The script fetches multiple pages of vacancies, normalizes each job offer, filters records by known technical skills, and saves the result as NDJSON.

### Kaggle Data Science Salaries CSV

The Kaggle ingestion script loads a local CSV file with salary records for data and IT-related roles.

Expected local input file:

```text
data/raw_samples/data_science_salaries.csv
```

The dataset contains columns such as:

```text
job_title, experience_level, employment_type, work_models, work_year,
employee_residence, salary, salary_currency, salary_in_usd,
company_location, company_size
```

The script uses `salary_in_usd` as the normalized salary value and stores the result in the same raw S3 area as Adzuna job data.

---

## Common output schema

Both ingestion scripts produce records that follow a common job-market schema.

Example Adzuna record:

```json
{
  "job_title": "Senior Data Engineer",
  "company": "Example Corp",
  "location": "London, UK",
  "salary_min": 120000.0,
  "salary_max": 145000.0,
  "currency": "USD",
  "remote": true,
  "skills": ["Python", "AWS", "Spark"],
  "description": "...",
  "source": "Adzuna",
  "collected_at": "2026-06-14"
}
```

Example Kaggle record:

```json
{
  "job_title": "Data Engineer",
  "company": null,
  "location": "United States",
  "salary_min": 95000.0,
  "salary_max": 95000.0,
  "currency": "USD",
  "remote": true,
  "skills": [],
  "description": null,
  "experience_level": "Senior-level",
  "employment_type": "Full-time",
  "company_size": "Large",
  "work_year": 2024,
  "source": "Kaggle-DS-Salaries",
  "collected_at": "2026-06-14"
}
```

---

## Normalization rules

### Adzuna normalization

| Field                       | Rule                                                                                |
| --------------------------- | ----------------------------------------------------------------------------------- |
| `job_title`                 | Taken from the Adzuna vacancy title.                                                |
| `company`                   | Taken from Adzuna company data.                                                     |
| `location`                  | Taken from Adzuna location data.                                                    |
| `salary_min` / `salary_max` | Extracted from Adzuna salary fields and converted to yearly USD values.             |
| `currency`                  | Normalized to `USD`.                                                                |
| `remote`                    | Detected from title and description keywords.                                       |
| `skills`                    | Extracted from title and description using the curated `SKILLS` list in `utils.py`. |
| `description`               | Taken from the Adzuna vacancy description.                                          |
| `source`                    | Always `Adzuna`.                                                                    |
| `collected_at`              | Current run date in `YYYY-MM-DD` format.                                            |

### Kaggle normalization

| Field              | Rule                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| `job_title`        | Taken from the CSV `job_title` column.                                                                  |
| `company`          | Set to `null`, because the dataset does not contain company names.                                      |
| `location`         | Taken from `company_location`.                                                                          |
| `salary_min`       | Taken from `salary_in_usd`.                                                                             |
| `salary_max`       | Same value as `salary_min`, because the dataset contains point salary values, not salary ranges.        |
| `currency`         | Always `USD`.                                                                                           |
| `remote`           | `true` if `work_models` is `Remote` or `Hybrid`; otherwise `false`.                                     |
| `skills`           | Empty list `[]`, because the dataset does not contain skills.                                           |
| `description`      | Set to `null`, because the dataset does not contain job descriptions.                                   |
| `experience_level` | Taken directly from the CSV, for example `Entry-level`, `Mid-level`, `Senior-level`, `Executive-level`. |
| `employment_type`  | Taken directly from the CSV, for example `Full-time`, `Part-time`, `Contract`, `Freelance`.             |
| `company_size`     | Taken directly from the CSV, for example `Small`, `Medium`, `Large`.                                    |
| `work_year`        | Taken from the CSV `work_year` column.                                                                  |
| `source`           | Always `Kaggle-DS-Salaries`.                                                                            |
| `collected_at`     | Current run date in `YYYY-MM-DD` format.                                                                |

---


## How to run

Run all commands from the project root, not from inside `src/1_ingestion/`.

### Run Adzuna ingestion

```bash
python src/1_ingestion/adzuna_parser.py
```

Output:

```text
data/raw_samples/jobs_YYYY_MM_DD.ndjson
s3://$S3_BUCKET_NAME/raw/jobs/jobs_YYYY_MM_DD.ndjson
```

### Run Kaggle CSV ingestion

First, place the Kaggle CSV file here:

```text
data/raw_samples/data_science_salaries.csv
```

Then run:

```bash
python src/1_ingestion/kaggle_loader.py
```

Output:

```text
data/raw_samples/kaggle_salaries_YYYY_MM_DD.ndjson
s3://$S3_BUCKET_NAME/raw/jobs/kaggle_salaries_YYYY_MM_DD.ndjson
```

---


