import pandas as pd
import matplotlib.pyplot as plt


MIN_VALID_SALARY = 10_000
MAX_VALID_SALARY = 500_000


def clean_salary_dataframe(df: pd.DataFrame, salary_column: str = "avg_salary") -> pd.DataFrame:
    """Remove impossible salary values before visualisation.

    All salary charts are shown in cleaned USD/year. The 10K-500K filter is the
    same rule used in the Glue ETL, salary bucket analysis and ML notebook.
    This prevents mixed-period/currency records from creating fake multi-million
    salaries on the charts.
    """
    if salary_column not in df.columns:
        return df

    df = df.copy()
    df[salary_column] = pd.to_numeric(df[salary_column], errors="coerce")
    return df[df[salary_column].between(MIN_VALID_SALARY, MAX_VALID_SALARY)]


# ==============================
# Load CSV files
# ==============================

skills_df = pd.read_csv("data/results/top_skills_analysis.csv")
salary_df = pd.read_csv("data/results/salary_by_role.csv")
paying_skills_df = pd.read_csv("data/results/top_paying_skills.csv")


# ==============================
# Clean column names and salary ranges
# ==============================

skills_df.columns = skills_df.columns.str.strip()
salary_df.columns = salary_df.columns.str.strip()
paying_skills_df.columns = paying_skills_df.columns.str.strip()

salary_df = clean_salary_dataframe(salary_df, "avg_salary")
paying_skills_df = clean_salary_dataframe(paying_skills_df, "avg_salary")


# ==============================
# Top demanded skills
# ==============================

skills_df = skills_df.sort_values("demand", ascending=True).tail(10)

plt.figure(figsize=(10, 6))
plt.barh(skills_df["skill"], skills_df["demand"])

plt.title("Top 10 Most Demanded Skills")
plt.xlabel("Number of Mentions")
plt.ylabel("Skill")
plt.grid(axis="x", alpha=0.3)

for index, value in enumerate(skills_df["demand"]):
    plt.text(value + 0.5, index, str(int(value)), va="center")

plt.tight_layout()
plt.savefig("dashboards/top_skills_analysis.png", dpi=300)
plt.close()


# ==============================
# Average salary by role
# ==============================

role_column = "job_title_clean" if "job_title_clean" in salary_df.columns else "job_title"

salary_df = salary_df.sort_values("avg_salary", ascending=True).tail(10)

plt.figure(figsize=(11, 6))
plt.barh(salary_df[role_column], salary_df["avg_salary"])

plt.title("Top 10 Roles by Average Salary (Cleaned USD/year)")
plt.xlabel("Average Salary, USD per year")
plt.ylabel("Job Role")
plt.grid(axis="x", alpha=0.3)

for index, value in enumerate(salary_df["avg_salary"]):
    plt.text(value + 2000, index, f"${value:,.0f}", va="center")

plt.tight_layout()
plt.savefig("dashboards/salary_by_role.png", dpi=300)
plt.close()


# ==============================
# Top paying skills
# ==============================

paying_skills_df = paying_skills_df.sort_values("avg_salary", ascending=True).tail(10)

plt.figure(figsize=(10, 6))
plt.barh(paying_skills_df["skill"], paying_skills_df["avg_salary"])

plt.title("Top 10 Highest Paying Skills (Cleaned USD/year)")
plt.xlabel("Average Salary, USD per year")
plt.ylabel("Skill")
plt.grid(axis="x", alpha=0.3)

for index, value in enumerate(paying_skills_df["avg_salary"]):
    plt.text(value + 2000, index, f"${value:,.0f}", va="center")

plt.tight_layout()
plt.savefig("dashboards/top_paying_skills.png", dpi=300)
plt.close()


print("All charts generated successfully.")
