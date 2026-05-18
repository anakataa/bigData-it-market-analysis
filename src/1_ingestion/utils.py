# Regular expressions are used for exact skill matching
# This prevents false positives from partial word matches
import re
# List of technologies used for skill extraction
# Vacancy descriptions are scanned for these keywords
SKILLS = [
    "Python",
    "Java",
    "Scala",
    "JavaScript",
    "TypeScript",
    "Go",
    "Rust",
    "C++",
    "C#",
    "PHP",
    "Ruby",
    "Kotlin",
    "Swift",
    "MATLAB",
    "Bash",
    "Shell",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
    "Cassandra",
    "Elasticsearch",
    "AWS",
    "Azure",
    "GCP",
    "Docker",
    "Kubernetes",
    "Terraform",
    "Jenkins",
    "CI/CD",
    "Linux",
    "Git",
    "Ansible",
    "Helm",
    "Prometheus",
    "Grafana",
    "Airflow",
    "Kafka",
    "Spark",
    "PySpark",
    "Hadoop",
    "Hive",
    "dbt",
    "Snowflake",
    "Databricks",
    "BigQuery",
    "Redshift",
    "ETL",
    "Data Lake",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn",
    "Keras",
    "XGBoost",
    "OpenCV",
    "Machine Learning",
    "Deep Learning",
    "MLOps",
    "NLP",
    "LLM",
    "FastAPI",
    "Flask",
    "Django",
    "Spring",
    "Node.js",
    "REST API",
    "GraphQL",
    "Microservices",
    "Tableau",
    "Power BI",
    "Excel",
    "Looker"
]

REMOTE_KEYWORDS = [
    "remote",
    "work from home",
    "hybrid"
]


def extract_skills(text: str) -> list:
     """
    Extract technologies from vacancy description.

    Uses regex-based exact matching to avoid
    detecting technologies inside unrelated words.
    """
# Return empty result if description missing
    if not text:
        return []
# Normalize text for case-insensitive matching
    text = text.lower()
    found_skills = []
 # Check every known technology against vacancy text
    for skill in SKILLS:

        skill_lower = skill.lower()

        # Handle technologies with special symbols
        # Examples: C++, C#, Node.js, CI/CD
        if any(char in skill_lower for char in ["+", "#", ".", "/"]):
            # Match exact technology without allowing
            # letters or numbers around it
            pattern = rf"(?<!\w){re.escape(skill_lower)}(?!\w)"

        else:
            # Use word boundaries for exact matching
            pattern = rf"\b{re.escape(skill_lower)}\b"
# Add technology if regex match found
        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


def detect_remote(text: str) -> bool:
    """
    Detect whether vacancy is remote/hybrid.
    """
# Handle empty descriptions safely
    if not text:
        return False

    text = text.lower()

    return any(keyword in text for keyword in REMOTE_KEYWORDS)