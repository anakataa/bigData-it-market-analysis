import csv
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Import AWS upload function
from s3_uploader import upload_file_to_s3


# Load environment variables from .env
load_dotenv()
INPUT_CSV_PATH = "data/raw_samples/data_science_salaries.csv"
OUTPUT_DIR = "data/raw_samples"
CURRENT_DATE_FILE = datetime.now().strftime("%Y_%m_%d")
CURRENT_DATE_RECORD = datetime.now().strftime("%Y-%m-%d")
OUTPUT_NDJSON_PATH = f"{OUTPUT_DIR}/kaggle_salaries_{CURRENT_DATE_FILE}.ndjson"
S3_KEY = f"raw/jobs/kaggle_salaries_{CURRENT_DATE_FILE}.ndjson"


# Columns required in the Kaggle CSV file
REQUIRED_COLUMNS = {
    "job_title",
    "experience_level",
    "employment_type",
    "work_models",
    "work_year",
    "employee_residence",
    "salary",
    "salary_currency",
    "salary_in_usd",
    "company_location",
    "company_size",
}


def validate_csv_header(fieldnames: list) -> None:
    """
    Validate that CSV file contains all required columns.
    """

    # Stop script if CSV file has no header
    if fieldnames is None:
        raise ValueError("CSV file has no header row.")

    # Convert actual CSV columns to set
    actual_columns = set(fieldnames)

    # Find missing required columns
    missing_columns = REQUIRED_COLUMNS - actual_columns

    # Stop script if some required columns are missing
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV file is missing required columns: {missing_text}")


def safe_float(value):
    """
    Convert value to float safely.
    """

    try:
        # Return None for empty values
        if value is None or value == "":
            return None

        # Convert value to float
        return float(value)

    # Return None if conversion fails
    except ValueError:
        return None


def safe_int(value):
    """
    Convert value to integer safely.
    """

    try:
        # Return None for empty values
        if value is None or value == "":
            return None

        # Convert value to integer
        return int(float(value))

    # Return None if conversion fails
    except ValueError:
        return None


def normalize_row(row: dict) -> dict:
    """
    Normalize one Kaggle CSV row into common project schema.
    """

    salary_usd = safe_float(row.get("salary_in_usd"))
    work_year = safe_int(row.get("work_year"))

    # Skip row if salary is missing or invalid
    if salary_usd is None:
        raise ValueError("Missing or invalid salary_in_usd")

    work_model = row.get("work_models")

    normalized_record = {
        "job_title": row.get("job_title"),
        "company": None,
        "location": row.get("company_location"),
        "salary_min": salary_usd,
        "salary_max": salary_usd,
        "currency": "USD",
        "remote": work_model in ["Remote", "Hybrid"],
        "skills": [],
        "description": None,
        "experience_level": row.get("experience_level"),
        "employment_type": row.get("employment_type"),
        "company_size": row.get("company_size"),
        "work_year": work_year,
        "source": "Kaggle-DS-Salaries",
        "collected_at": CURRENT_DATE_RECORD,
    }
    return normalized_record


def load_and_normalize_csv(input_path: str) -> tuple[list, int]:
    """
    Load Kaggle CSV file and normalize all valid rows.
    """
    normalized_records = []
    skipped_rows = 0

    # Open CSV file
    with open(input_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        validate_csv_header(reader.fieldnames)
        # Process each CSV row
        for row_number, row in enumerate(reader, start=2):

            try:
                # Normalize current row
                normalized_record = normalize_row(row)
                normalized_records.append(normalized_record)

            except Exception as error:
                # Skip broken row and continue processing
                skipped_rows += 1
                print(f"Skipped row {row_number}: {error}")

    # Return normalized data and skipped rows count
    return normalized_records, skipped_rows


def save_to_ndjson(records: list, output_path: str) -> None:
    """
    Save normalized records to NDJSON file.
    """

    # Create output directory if it does not exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Open output NDJSON file
    with open(output_path, "w", encoding="utf-8") as output_file:

        # Write each record as separate JSON line
        for record in records:
            output_file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    """
    Run Kaggle CSV ingestion pipeline.
    """

    print("Starting Kaggle CSV ingestion...")

    # Check that input CSV file exists
    if not os.path.exists(INPUT_CSV_PATH):
        raise FileNotFoundError(
            f"Input CSV file not found: {INPUT_CSV_PATH}. "
            f"Put your Kaggle file into data/raw_samples/data_science_salaries.csv"
        )

    # Load and normalize Kaggle CSV data
    records, skipped_rows = load_and_normalize_csv(INPUT_CSV_PATH)

    # Save normalized records to local NDJSON file
    save_to_ndjson(records, OUTPUT_NDJSON_PATH)

    # Print local processing result
    print(f"Saved records: {len(records)}")
    print(f"Skipped rows: {skipped_rows}")
    print(f"Local NDJSON: {OUTPUT_NDJSON_PATH}")
    upload_file_to_s3(OUTPUT_NDJSON_PATH, S3_KEY)
    print(f"Uploaded to S3: {S3_KEY}")
    print("Kaggle CSV ingestion finished successfully.")


if __name__ == "__main__":
    main()