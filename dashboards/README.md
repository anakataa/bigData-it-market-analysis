    # Dashboards

Final visual outputs of the analytical pipeline — three matplotlib charts and three Athena query
screenshots that prove the pipeline actually ran.

## Final charts

These three PNGs are regenerated from `data/results/*.csv` by running
[`src/visualization.py`](../src/visualization.py).

### `top_skills_analysis.png` — Most Demanded Skills

Horizontal bar chart of the **top 10 most-mentioned skills** across the 519-vacancy corpus.

> **Insight:** SQL leads with 99 mentions (≈ 1 in 5 vacancies), followed by Python (72) and Java
> (56). Cloud / DevOps skills — CI/CD (51), Azure (49), Kubernetes (41), AWS (41) — form a strong
> second tier, confirming that infrastructure competencies are no longer optional.

Source query: §2 of [`docs/athena_queries.sql`](../docs/athena_queries.sql).

### `top_paying_skills.png` — Highest Paying Skills

Horizontal bar chart of the **top 10 skills by average salary** (USD per year). Filtered for skills
appearing in **more than one vacancy** to avoid outliers.

> **Insight:** Niche frameworks (GraphQL ~971K, Django ~948K) top the table but on small samples
> (4–5 vacancies). The truer "mid-premium" band is Node.js, MongoDB, Kafka, Rust — all in the
> 350K–430K range — distributed-systems and streaming work.

Source query: §8 of [`docs/athena_queries.sql`](../docs/athena_queries.sql).

### `salary_by_role.png` — Top Roles by Average Salary

Horizontal bar chart of the **top 10 roles** by average salary, using the normalized job-title
column.

> **Insight:** The top 3 roles are senior contracting positions, led by a **Senior AWS Developer
> (Contracting)** at ~4.3M USD/year — roughly 3× the next-tier senior baseline. Concrete evidence
> of the cloud-native seniority premium.

Source query: §1 of [`docs/athena_queries.sql`](../docs/athena_queries.sql).

## Athena query screenshots

Captured directly from the AWS Console — they serve as the "ground-truth" proof that the SQL ran
on real data and the results match what we report.

| File                                 | Shows                                                           |
| ------------------------------------ | --------------------------------------------------------------- |
| `athena_top_skills_query.png`        | Query 2 — count of skill mentions, sorted DESC                  |
| `athena_top_paying_skills_query.png` | Query 8 — average salary per skill, filtered for `COUNT(*) > 1` |
| `athena_salary_by_role_query.png`    | Query 1 — average salary per `job_title_clean`, sorted DESC     |

## Why local matplotlib instead of QuickSight

Amazon QuickSight signup looped silently in `eu-north-1` during the project window. To preserve
the timeline we decoupled the BI layer — pulling clean CSV from Athena and rendering charts with
matplotlib. The analytical outputs are identical; reproducibility actually improved because the
visual pipeline is now a single script in version control.

See [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) for the full failover discussion.

## Regenerating the charts

```bash
python src/visualization.py
```

This overwrites the PNG files in this folder using the latest CSV exports under
`data/results/`.
