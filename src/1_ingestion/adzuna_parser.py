import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
# Import helper functions for text analysis
from utils import extract_skills, detect_remote
# Import AWS upload function
from s3_uploader import upload_file_to_s3

# Load environment variables from .env
load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Countries to collect vacancies from
COUNTRIES = ["us", "gb", "pl"]

# Number of pages to fetch per country
PAGES_PER_COUNTRY = 120

# Create output directory if it does not exist
os.makedirs("data/raw_samples", exist_ok=True)

# Generate output filename using current date
current_date = datetime.now().strftime("%Y_%m_%d")
local_output_path = f"data/raw_samples/jobs_{current_date}.ndjson"


def fetch_jobs(country: str, page: int) -> list:
    """
    Fetch vacancies from Adzuna API.
    """

    url = (
        f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
        f"?app_id={ADZUNA_APP_ID}"
        f"&app_key={ADZUNA_APP_KEY}"
        f"&results_per_page=50"
    )
 # Send GET request to Adzuna API
    response = requests.get(url)
# Handle API errors
    if response.status_code != 200:
        print(f"API error for {country} page {page}: {response.status_code}")
        return []
# Convert API response into Python dictionary
    data = response.json()
# Return only vacancy list from response
    return data.get("results", [])


def normalize_job(job: dict) -> dict:
    """
    Normalize raw API vacancy into a clean structure.
    """
# Vacancy description is used for skill extraction
    description = job.get("description", "")
# Standardized structure
    normalized_job = {
        "job_title": job.get("title"),
        "company": job.get("company", {}).get("display_name"),
        "location": job.get("location", {}).get("display_name"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "currency": "USD",
        "remote": detect_remote(description),
        "skills": extract_skills(description),
        "description": description,
        "source": "Adzuna",
        "collected_at": datetime.now().strftime("%Y-%m-%d")
    }

    return normalized_job


def save_jobs_to_ndjson(jobs: list, file_path: str):
    """
    Save jobs into NDJSON format.
    One JSON object per line.
    """
# This allows writing new data without deleting old content
    with open(file_path, "a", encoding="utf-8") as file:
        # Write one vacancy per line
        for job in jobs:
            file.write(json.dumps(job) + "\n")


def main():
    """
    Main ingestion pipeline.
    """
# Store all collected vacancies in memory
    all_jobs = []

    # Fetch vacancies from multiple countries
    for country in COUNTRIES:

        for page in range(1, PAGES_PER_COUNTRY + 1):

            print(f"Fetching {country} page {page}")
            # Download raw vacancies from API
            jobs = fetch_jobs(country, page)
            # Store cleaned vacancies for current page
            normalized_jobs = []

            for job in jobs:

                normalized_job = normalize_job(job)

                # Keep only technical vacancies
                if len(normalized_job["skills"]) >= 2:
                    normalized_jobs.append(normalized_job)

            all_jobs.extend(normalized_jobs)

    # Save locally
    save_jobs_to_ndjson(all_jobs, local_output_path)

    # Upload file to S3
    s3_key = f"raw/jobs/jobs_{current_date}.ndjson"

    upload_file_to_s3(local_output_path, s3_key)

    print(f"Collected {len(all_jobs)} technical vacancies")

# Runs only if file executed directly
if __name__ == "__main__":
    main()