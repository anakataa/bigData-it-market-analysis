"""
Salary bucket analysis for the IT Job Market Big Data project.

Input:  data/raw_samples/jobs_2026_05_18.ndjson
Output: dashboards/salary_buckets.png

The script creates three views:
1. Vacancy count by salary bucket
2. Percentage distribution by salary bucket
3. Remote vs Office split inside each bucket
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "raw_samples" / "jobs_2026_05_18.ndjson"
OUTPUT_FILE = PROJECT_ROOT / "dashboards" / "salary_buckets.png"

BUCKET_ORDER = ["Low", "Medium", "High"]
BUCKET_COLORS = {
    "Low": "#8E8E8E",
    "Medium": "#00BCD4",
    "High": "#7E57C2",
}


def load_and_prepare_data(input_file: Path) -> pd.DataFrame:
    """Load NDJSON data and create salary/work-mode bucket features."""
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    df = pd.read_json(input_file, lines=True)

    required_columns = {"salary_min", "salary_max", "remote"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    df["salary"] = df[["salary_min", "salary_max"]].mean(axis=1, skipna=True)
    df = df.dropna(subset=["salary"]).copy()

    # Remove unrealistic salaries and data-entry errors.
    df = df[(df["salary"] >= 10_000) & (df["salary"] <= 500_000)].copy()

    df["salary_bucket"] = pd.cut(
        df["salary"],
        bins=[0, 50_000, 150_000, float("inf")],
        labels=BUCKET_ORDER,
        right=False,
    )
    df["work_mode"] = df["remote"].fillna(False).astype(bool).map({True: "Remote", False: "Office"})

    return df


def create_salary_bucket_dashboard(df: pd.DataFrame, output_file: Path) -> None:
    """Create and save the 3-panel salary bucket dashboard."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    bucket_counts = df["salary_bucket"].value_counts().reindex(BUCKET_ORDER, fill_value=0)
    bucket_shares = bucket_counts / bucket_counts.sum() * 100

    remote_crosstab = pd.crosstab(df["salary_bucket"], df["work_mode"]).reindex(BUCKET_ORDER, fill_value=0)
    for column in ["Office", "Remote"]:
        if column not in remote_crosstab.columns:
            remote_crosstab[column] = 0
    remote_crosstab = remote_crosstab[["Office", "Remote"]]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Salary Bucket Analysis\nLow < $50K | Medium $50K-$150K | High ≥ $150K", fontsize=16)

    # 1. Bar chart: count by bucket
    axes[0].bar(
        bucket_counts.index.astype(str),
        bucket_counts.values,
        color=[BUCKET_COLORS[bucket] for bucket in BUCKET_ORDER],
    )
    axes[0].set_title("Vacancies by Salary Bucket")
    axes[0].set_xlabel("Salary bucket")
    axes[0].set_ylabel("Number of vacancies")
    for index, value in enumerate(bucket_counts.values):
        axes[0].text(index, value + 1, str(int(value)), ha="center", fontsize=10)

    # 2. Pie chart: percentage split
    axes[1].pie(
        bucket_shares.values,
        labels=[f"{bucket}\n{share:.1f}%" for bucket, share in bucket_shares.items()],
        colors=[BUCKET_COLORS[bucket] for bucket in BUCKET_ORDER],
        autopct="%1.1f%%",
        startangle=90,
    )
    axes[1].set_title("Salary Bucket Share")

    # 3. Stacked bar: remote vs office per bucket
    remote_crosstab.plot(kind="bar", stacked=True, ax=axes[2], color=["#BDBDBD", "#4DD0E1"])
    axes[2].set_title("Remote vs Office by Salary Bucket")
    axes[2].set_xlabel("Salary bucket")
    axes[2].set_ylabel("Number of vacancies")
    axes[2].tick_params(axis="x", rotation=0)
    axes[2].legend(title="Work mode")

    plt.tight_layout(rect=(0, 0, 1, 0.90))
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    summary = pd.DataFrame({
        "bucket": bucket_counts.index.astype(str),
        "count": bucket_counts.values,
        "share_percent": bucket_shares.round(2).values,
    })
    print("Salary bucket summary:")
    print(summary.to_string(index=False))
    print(f"Dashboard saved to: {output_file}")


def main() -> None:
    df = load_and_prepare_data(INPUT_FILE)
    create_salary_bucket_dashboard(df, OUTPUT_FILE)


if __name__ == "__main__":
    main()
