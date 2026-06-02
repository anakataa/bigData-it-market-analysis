import pandas as pd
import matplotlib.pyplot as plt


# ==============================
# Load CSV files
# ==============================

skills_df = pd.read_csv("data/results/top_skills_analysis.csv")
salary_df = pd.read_csv("data/results/salary_by_role.csv")
paying_skills_df = pd.read_csv("data/results/top_paying_skills.csv")


# ==============================
# Clean column names
# ==============================

skills_df.columns = skills_df.columns.str.strip()
salary_df.columns = salary_df.columns.str.strip()
paying_skills_df.columns = paying_skills_df.columns.str.strip()


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
    plt.text(value, index, str(value), va="center")

plt.tight_layout()
plt.savefig("dashboards/top_skills_analysis.png")
plt.close()


# ==============================
# Average salary by role
# ==============================

role_column = "job_title_clean" if "job_title_clean" in salary_df.columns else "job_title"

salary_df = salary_df.sort_values("avg_salary", ascending=True).tail(10)

plt.figure(figsize=(10, 6))
plt.barh(salary_df[role_column], salary_df["avg_salary"])

plt.title("Top 10 Roles by Average Salary")
plt.xlabel("Average Salary")
plt.ylabel("Job Role")
plt.grid(axis="x", alpha=0.3)

for index, value in enumerate(salary_df["avg_salary"]):
    plt.text(value, index, f"{value:,.0f}", va="center")

plt.tight_layout()
plt.savefig("dashboards/salary_by_role.png")
plt.close()


# ==============================
# Top paying skills
# ==============================

paying_skills_df = paying_skills_df.sort_values("avg_salary", ascending=True).tail(10)

plt.figure(figsize=(10, 6))
plt.barh(paying_skills_df["skill"], paying_skills_df["avg_salary"])

plt.title("Top 10 Highest Paying Skills")
plt.xlabel("Average Salary")
plt.ylabel("Skill")
plt.grid(axis="x", alpha=0.3)

for index, value in enumerate(paying_skills_df["avg_salary"]):
    plt.text(value, index, f"{value:,.0f}", va="center")

plt.tight_layout()
plt.savefig("dashboards/top_paying_skills.png")
plt.close()


print("All charts generated successfully.")
