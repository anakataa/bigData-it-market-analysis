import json
import os
import re
from datetime import datetime
from statistics import mean
from typing import Iterable

import pdfplumber
from dotenv import load_dotenv

from s3_uploader import upload_file_to_s3
from utils import SKILLS


load_dotenv()
PDF_INPUT_DIR = "data/pdf_reports"
OUTPUT_DIR = "data/raw_samples"
CURRENT_DATE_FILE = datetime.now().strftime("%Y_%m_%d")
CURRENT_DATE_RECORD = datetime.now().strftime("%Y-%m-%d")
OUTPUT_NDJSON_PATH = f"{OUTPUT_DIR}/pdf_reports_{CURRENT_DATE_FILE}.ndjson"
S3_KEY = f"raw/pdf/pdf_reports_{CURRENT_DATE_FILE}.ndjson"

# $120,000 / $120.000 / $120K / $120k / USD 120000 / USD 120,000
SALARY_PATTERNS = [
    re.compile(r"\$\s*(\d{2,3}(?:[,.]\d{3})+|\d{2,3})\s*([Kk])?"),
    re.compile(r"\bUSD\s*(\d{2,3}(?:[,.]\d{3})+|\d{5,7}|\d{2,3})\s*([Kk])?", re.IGNORECASE),
]

MIN_REASONABLE_SALARY = 20_000
MAX_REASONABLE_SALARY = 1_000_000

MIN_TEXT_LENGTH = 100
SNIPPET_LENGTH = 500


def normalize_text(text: str) -> str:
    """
    Collapse excessive whitespace from extracted PDF text.
    """

    # Replace multiple spaces/new lines/tabs with one normal space
    return re.sub(r"\s+", " ", text).strip()


def find_skills(text: str) -> list[str]:
    """
    Find technologies from utils.SKILLS inside a page of text.

    The regex uses lookarounds instead of only word boundaries, because
    technologies such as C++, C#, Node.js and CI/CD contain special symbols.
    """

    # If the page has no text, return empty skill list
    if not text:
        return []
    text_lower = text.lower()
    found_skills = []

    # Check every skill from the common project skill list
    for skill in SKILLS:
        skill_lower = skill.lower()

        # Escape special characters like +, #, ., / and use safe boundaries
        pattern = rf"(?<!\w){re.escape(skill_lower)}(?!\w)"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills


def _salary_to_int(number_text: str, suffix: str | None) -> int | None:
    """
    Convert a salary regex match into an integer USD amount.
    """
    if not number_text:
        return None

    # Remove thousand separators from salary text
    cleaned = number_text.replace(",", "").replace(".", "")

    try:
        amount = int(cleaned)
    except ValueError:
        return None

    # Convert 120K / 120k into 120000
    if suffix and suffix.lower() == "k":
        amount *= 1000

    return amount


def find_salary_mentions(text: str) -> list[int]:
    """
    Extract salary mentions and remove unreasonable values.
    """
    salaries = []

    # Try every supported salary regex pattern
    for pattern in SALARY_PATTERNS:
        for match in pattern.finditer(text):
            # Convert salary match into integer USD amount
            amount = _salary_to_int(match.group(1), match.group(2))

            # Skip broken salary matches
            if amount is None:
                continue

            # Keep only realistic annual salaries
            if MIN_REASONABLE_SALARY <= amount <= MAX_REASONABLE_SALARY:
                salaries.append(amount)

    # Keep original order but remove duplicates caused by overlapping formats
    unique_salaries = []
    seen = set()

    # Add each salary only once
    for salary in salaries:
        if salary not in seen:
            unique_salaries.append(salary)
            seen.add(salary)

    return unique_salaries


def iter_pdf_files(input_dir: str) -> Iterable[str]:
    """
    Yield PDF paths from the input directory in stable order.
    """

    # Stop with a error if the PDF folder does not exist
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(
            f"PDF input directory not found: {input_dir}. "
            "Create it and put at least 2 text-based PDF reports there."
        )

    # Go through all files in stable alphabetical order
    for filename in sorted(os.listdir(input_dir)):
        if filename.lower().endswith(".pdf"):
            yield os.path.join(input_dir, filename)


def parse_pdf_report(pdf_path: str) -> tuple[list[dict], int]:
    """
    Parse one PDF report and return useful page records.
    """
    records = []
    skipped_pages = 0

    # Save only file name, not full local path
    source_file = os.path.basename(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        # Process every page in the PDF, starting page numbering from 1
        for page_index, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() or ""

            text = normalize_text(raw_text)

            # Skip covers, separators, scanned pages, and almost empty pages
            if len(text) < MIN_TEXT_LENGTH:
                skipped_pages += 1
                continue

            skills = find_skills(text)
            salary_mentions = find_salary_mentions(text)

            # Skip pages without skills and without salary mentions
            if not skills and not salary_mentions:
                skipped_pages += 1
                continue

            avg_salary = round(mean(salary_mentions)) if salary_mentions else None

            records.append(
                {
                    "source_file": source_file,
                    "page": page_index,
                    "skills": skills,
                    "salary_mentions": salary_mentions,
                    "avg_salary_on_page": avg_salary,
                    "text_snippet": text[:SNIPPET_LENGTH],
                    "source": "PDF-Report",
                    "collected_at": CURRENT_DATE_RECORD,
                }
            )

    return records, skipped_pages


def save_to_ndjson(records: list[dict], output_path: str) -> None:
    """
    Save parsed PDF records to NDJSON.
    """

    # Create output directory if it does not exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write one valid JSON object per line
    with open(output_path, "w", encoding="utf-8") as output_file:
        for record in records:
            output_file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    """
    Run PDF report ingestion pipeline.
    """

    print("Starting PDF report ingestion...")

    pdf_paths = list(iter_pdf_files(PDF_INPUT_DIR))

    if len(pdf_paths) < 2:
        raise ValueError(
            f"Expected at least 2 PDF reports in {PDF_INPUT_DIR}, found {len(pdf_paths)}."
        )

    all_records = []
    total_skipped_pages = 0

    # Parse every PDF report
    for pdf_path in pdf_paths:
        print(f"Parsing PDF: {pdf_path}")
        records, skipped_pages = parse_pdf_report(pdf_path)

        # Add records from this PDF to the final list
        all_records.extend(records)
        total_skipped_pages += skipped_pages
        print(f"Useful records from {os.path.basename(pdf_path)}: {len(records)}")
        print(f"Skipped pages from {os.path.basename(pdf_path)}: {skipped_pages}")

    # Save all parsed records locally as NDJSON
    save_to_ndjson(all_records, OUTPUT_NDJSON_PATH)

    print(f"Saved records: {len(all_records)}")
    print(f"Skipped pages: {total_skipped_pages}")
    print(f"Local NDJSON: {OUTPUT_NDJSON_PATH}")
    upload_file_to_s3(OUTPUT_NDJSON_PATH, S3_KEY)
    print(f"Uploaded to S3: {S3_KEY}")
    print("PDF report ingestion finished successfully.")

if __name__ == "__main__":
    main()