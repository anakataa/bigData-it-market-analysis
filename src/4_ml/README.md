# 4. Machine Learning — Salary Prediction (Extension)

A planned extension that uses the cleaned vacancy corpus to train a salary-prediction model.

> **Status:** work in progress. The notebook scaffold is in place; the model itself is the next
> milestone after the core pipeline is delivered.

## File

| File                 | Purpose                                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------------- |
| `salary_model.ipynb` | Jupyter notebook scaffold — environment setup, data-loading stub, and a placeholder for training. |

## Intended approach

| Step                | Tooling                                                                              | Outcome                              |
| ------------------- | ------------------------------------------------------------------------------------ | ------------------------------------ |
| Load data           | `pandas` reading the Athena CSV outputs from `data/results/`                         | flat dataframe                       |
| Feature engineering | One-hot encode `country`, multi-hot encode `skills` (~80 columns), bucket experience | numeric feature matrix               |
| Train / test split  | `sklearn.model_selection.train_test_split` (80/20)                                   | reproducible split (random_state=42) |
| Model               | `LinearRegression` baseline → `RandomForestRegressor` → `XGBoost` if time permits    | trained estimator                    |
| Evaluation          | MAE, RMSE, R² + actual-vs-predicted scatter plot                                     | reported in notebook                 |

## How to run (once implemented)

```bash
pip install jupyter scikit-learn xgboost
jupyter notebook src/4_ml/salary_model.ipynb
```

## Open questions

- Sample size (~500 vacancies) is small for a high-cardinality model. Probably a regression with
  heavy regularization rather than a deep model.
- The `skills` column is the strongest signal but also the highest-dimensional. Worth experimenting
  with embedding the skill set rather than one-hot encoding it.
