# Documentation

Supporting docs, SQL queries, configuration references, and diagrams for the project.

## Contents

| File                                               | Purpose                                                                                        |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [`ARCHITECTURE.md`](ARCHITECTURE.md)               | End-to-end architecture explanation, design trade-offs, and the QuickSight failover story.     |
| [`athena_queries.sql`](athena_queries.sql)         | The full SQL inventory — nine queries from schema inspection to top-paying-skills aggregation. |
| [`glue_crawler_config.md`](glue_crawler_config.md) | AWS Glue Crawler configuration reference (name, data source, target database, IAM role).       |
| `diagrams/`                                        | Schema and pipeline visuals referenced from other docs.                                        |

## How to read these docs

Start with [`ARCHITECTURE.md`](ARCHITECTURE.md) — it explains _why_ every component sits where
it does. Then jump to [`athena_queries.sql`](athena_queries.sql) to see exactly what numbers were
produced and how. The Glue Crawler config is a quick reference for anyone rebuilding the catalog
from scratch.

## External documentation

These live outside the repo (in the project's GitHub releases):

- **Technical Documentation (Word, ~13 pages)** — formal report mapping the project to course
  criteria, with embedded charts and the full results tables.
- **Presentation Deck (PowerPoint, 13 slides)** — executive summary with native editable charts
  and a project retrospective.

## Conventions

- All SQL is written for **Amazon Athena (Presto)** — note the `CROSS JOIN UNNEST` syntax for
  array flattening, which is the main Presto-specific operator we rely on.
- Configuration files use Markdown tables for readability rather than YAML/JSON, since they
  describe AWS Console settings rather than parameters of any script.
