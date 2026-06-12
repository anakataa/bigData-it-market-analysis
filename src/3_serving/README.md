# 3. Serving Layer

Reserved for the data-serving / business-intelligence layer.

## Current state

The serving layer in this project is **decoupled from AWS QuickSight** (which was the original plan
— see the architecture note in the root [`README`](../../README.md#-architecture)).

The serving path is:

```text
Athena SQL  ──►  CSV exports  ──►  visualization.py  ──►  PNG dashboards
                                          │
                                          ▼
                                   dashboards/*.png
```

- The CSVs are produced from `docs/athena_queries.sql` via the **Athena → Download results** UI.
- They land in [`data/results/`](../../data/results/).
- The chart generator [`src/visualization.py`](../visualization.py) reads them and writes PNGs to
  [`dashboards/`](../../dashboards/).

## Future work

- Re-introduce Amazon QuickSight as a hosted BI front-end once the regional rollout stabilizes.
- Wrap `visualization.py` in an AWS Lambda function triggered on new CSV uploads.
- Serve the dashboards through a static-site bucket (S3 + CloudFront).
