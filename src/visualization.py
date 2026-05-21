import pandas as pd
import matplotlib.pyplot as plt


# ==============================
# Load CSV files
# ==============================

skills_df = pd.read_csv("data/results/top_skills_analysis.csv.csv")
salary_df = pd.read_csv("data/results/salary_by_role.csv.csv")
paying_skills_df = pd.read_csv("data/results/top_paying_skills.csv.csv")


# ==============================
# Top demanded skills
# ==============================

plt.figure(figsize=(8, 5))

plt.bar(skills_df["skill"], skills_df["demand"])

plt.title("Top Demanded Skills")
plt.xlabel("Skill")
plt.ylabel("Demand")

plt.tight_layout()

plt.savefig("dashboards/top_skills_analysis.png")

plt.close()


# ==============================
# Average salary by role
# ==============================

plt.figure(figsize=(8, 5))

plt.bar(salary_df["job_title"], salary_df["avg_salary"])

plt.title("Average Salary by Role")
plt.xlabel("Job Title")
plt.ylabel("Average Salary")

plt.tight_layout()

plt.savefig("dashboards/salary_by_role.png")

plt.close()


# ==============================
# Top paying skills
# ==============================

plt.figure(figsize=(8, 5))

plt.bar(
    paying_skills_df["skill"],
    paying_skills_df["avg_salary"]
)

plt.title("Top Paying Skills")
plt.xlabel("Skill")
plt.ylabel("Average Salary")

plt.tight_layout()

plt.savefig("dashboards/top_paying_skills.png")

plt.close()


print("All charts generated successfully.")
