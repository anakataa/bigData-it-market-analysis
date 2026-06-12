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

# Currency conversion rates to USD
CURRENCY_TO_USD = {
    "USD": 1.0,
    "GBP": 1.27,
    "PLN": 0.25
}

# Default currency by country
COUNTRY_DEFAULT_CURRENCY = {
    "us": "USD",
    "gb": "GBP",
    "pl": "PLN"
}

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


def get_detection_text(job: dict) -> str:
    """
    Combine title and description for salary analysis.
    """
# Get title text
    title = job.get("title", "") or ""
# Get description text
    description = job.get("description", "") or ""
# Return combined lowercase text
    return f"{title} {description}".lower()


def detect_currency(job: dict, country: str) -> str:
    """
    Detect salary currency.
    """
# Prepare text for currency detection
    text = get_detection_text(job)

# Detect USD from text
    if "$" in text or " usd" in text or "dollar" in text or "dollars" in text:
        return "USD"

# Detect GBP from text
    if "£" in text or " gbp" in text or "pound" in text or "pounds" in text:
        return "GBP"

# Detect PLN from text
    if "zł" in text or " pln" in text or " zl" in text or "zloty" in text or "złotych" in text:
        return "PLN"

# Use default currency based on country
    return COUNTRY_DEFAULT_CURRENCY.get(country, "USD")


def get_average_salary(job: dict):
    """
    Calculate average salary value for period detection.
    """
# Get minimum salary
    salary_min = job.get("salary_min")
# Get maximum salary
    salary_max = job.get("salary_max")

# Store existing salary values
    values = []

# Add minimum salary if it exists
    if salary_min is not None:
        values.append(float(salary_min))

# Add maximum salary if it exists
    if salary_max is not None:
        values.append(float(salary_max))

# Return None if salary does not exist
    if not values:
        return None

# Return average salary value
    return sum(values) / len(values)


def detect_salary_period(job: dict, currency: str):
    """
    Detect salary period: hour, day, month, or year.
    """
# Prepare text for period detection
    text = get_detection_text(job)

# Detect hourly salary
    if (
        "per hour" in text
        or "hourly" in text
        or "/hour" in text
        or "/hr" in text
        or " an hour" in text
        or "/h" in text
        or "godzinę" in text
    ):
        return "hour"

# Detect daily salary
    if (
        "per day" in text
        or "daily rate" in text
        or "/day" in text
        or " a day" in text
        or "/d" in text
        or "dziennie" in text
    ):
        return "day"

# Detect monthly salary
    if (
        "per month" in text
        or "monthly" in text
        or "/month" in text
        or "/mo" in text
        or " a month" in text
        or "miesięcznie" in text
        or "/mies" in text
        or "/msc" in text
    ):
        return "month"

# Detect yearly salary
    if (
        "per year" in text
        or "yearly" in text
        or "annually" in text
        or "annual salary" in text
        or "/year" in text
        or "/yr" in text
        or "per annum" in text
        or "rocznie" in text
    ):
        return "year"

# Get average salary for fallback detection
    salary_value = get_average_salary(job)

# Return None if there is no salary
    if salary_value is None:
        return None

# Fallback rules for PLN salaries
    if currency == "PLN":
        if salary_value < 150:
            return "hour"
        if salary_value < 3000:
            return "day"
        if salary_value < 45000:
            return "month"
        return "year"

# Fallback rules for USD and GBP salaries
    if currency in ["USD", "GBP"]:
        if salary_value < 150:
            return "hour"
        if salary_value < 1000:
            return "day"
        if salary_value < 15000:
            return "month"
        return "year"

# Default fallback
    return "year"


def convert_salary_to_usd_year(amount, currency: str, period: str):
    """
    Convert salary to USD per year.
    """
# Return None if salary does not exist
    if amount is None:
        return None

# Return None if period cannot be detected
    if period is None:
        return None

# Convert amount to float
    amount = float(amount)

# Convert hourly salary to yearly salary
    if period == "hour":
        amount = amount * 2080

# Convert daily salary to yearly salary
    elif period == "day":
        amount = amount * 260

# Convert monthly salary to yearly salary
    elif period == "month":
        amount = amount * 12

# Convert salary currency to USD
    amount = amount * CURRENCY_TO_USD.get(currency, 1.0)

# Round salary value
    return round(amount, 2)


def normalize_job(job: dict, country: str) -> dict:
    """
    Normalize raw API vacancy into a clean structure.
    """
# Vacancy description is used for skill extraction
    description = job.get("description", "")

# Detect original salary currency
    currency = detect_currency(job, country)

# Detect salary period
    salary_period = detect_salary_period(job, currency)

# Convert minimum salary to USD per year
    salary_min = convert_salary_to_usd_year(
        job.get("salary_min"),
        currency,
        salary_period
    )

# Convert maximum salary to USD per year
    salary_max = convert_salary_to_usd_year(
        job.get("salary_max"),
        currency,
        salary_period
    )

# Standardized structure
    normalized_job = {
        "job_title": job.get("title"),
        "company": job.get("company", {}).get("display_name"),
        "location": job.get("location", {}).get("display_name"),
        "salary_min": salary_min,
        "salary_max": salary_max,
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

                normalized_job = normalize_job(job, country)

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