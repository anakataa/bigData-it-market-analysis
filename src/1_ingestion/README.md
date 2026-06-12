# 1. Ingestion Layer

The first stage of the pipeline: pull live IT vacancies from the [Adzuna REST API](https://developer.adzuna.com/),
normalize them, and upload them as NDJSON to the project's S3 raw zone.

## Files

| File               | Purpose                                                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------------------------- |
| `adzuna_parser.py` | Main entry point. Iterates over countries/pages, normalizes each vacancy, writes NDJSON, and triggers the S3 upload. |
| `utils.py`         | Pure helpers: skill extraction (regex over a curated tech list) and remote/hybrid detection (keyword scan).          |
| `s3_uploader.py`   | Thin `boto3` wrapper that uploads a local file to the configured S3 bucket.                                          |

## What gets collected

The scraper queries Adzuna for **three countries** by default:

| Country code | Region         | Default currency       |
| ------------ | -------------- | ---------------------- |
| `us`         | United States  | USD                    |
| `gb`         | United Kingdom | GBP → converted to USD |
| `pl`         | Poland         | PLN → converted to USD |

Up to **120 pages × 50 results** per country (= ~18,000 raw listings per run). After normalization
and the "must mention ≥ 2 known skills" filter, the typical batch settles around 500 technical vacancies.

## Normalization

Each raw API record becomes a clean object with the following shape:

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
  "collected_at": "2026-05-18"
}
```

Key normalization rules:

- **Salary** → converted to **USD per year** regardless of original currency or period (hour/day/month/year).
- **Skills** → extracted via word-boundary regex against a curated list of ~80 technologies (see `utils.py`).
  Special tokens like `C++`, `C#`, `Node.js`, `CI/CD` are matched with non-word lookarounds to avoid
  false positives.
- **Remote** → boolean. Detects English ("remote", "hybrid", "work from home") and Polish
  ("zdalnie", "praca zdalna", "praca hybrydowa") keywords.

## Environment variables

Create a `.env` file at the repo root with the following keys:

```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=eu-north-1
S3_BUCKET_NAME=your-bucket-name
```

Get your Adzuna credentials from <https://developer.adzuna.com/> (the free tier is sufficient).

## How to run

From the **repo root** (not from inside this folder):

```bash
python src/1_ingestion/adzuna_parser.py
```

Output:

- Local: `data/raw_samples/jobs_YYYY_MM_DD.ndjson`
- Remote: `s3://$S3_BUCKET_NAME/raw/jobs/jobs_YYYY_MM_DD.ndjson`

The script appends to the local file (does not overwrite), so a partial run can resume safely.

## Troubleshooting

- `401 Unauthorized` → check your Adzuna `app_id` / `app_key`.
- `AccessDenied` on upload → the IAM user must have `s3:PutObject` on the target bucket.
- Empty file → the "≥ 2 skills" filter is strict; widen the `SKILLS` list in `utils.py` if you
  need more coverage.
