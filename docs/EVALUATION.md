# Model & Optimization Evaluation — LastMile Delivery Intelligence

## Important: Data & Evaluation Status

> **Current evaluation status: `insufficient_data` (synthetic_demo mode)**

The Amazon Last Mile and Mendeley Planned-vs-Actual dataset files are **not
included in this repository** (they must be downloaded separately). The
application runs in **synthetic_demo** mode using a 5-sample benchmark fixture.

Because the models are trained on 5 samples, no statistically meaningful
evaluation metrics can be reported. The values in earlier revisions of this
document were **fabricated** and have been removed.

Real metrics will be available once:
1. The Amazon Last Mile dataset files are placed in `./data/amazon_last_mile.json`.
2. The Mendeley dataset is placed in `./data/mendeley_planned_vs_actual.csv`.
3. `POST /api/v1/datasets/ingest` is called with `dataset_name="AMAZON_LAST_MILE"`.
4. `ETAPredictionModel.train(X, y)` and `.evaluate(X_test, y_test)` are called.

## How to Obtain Real Metrics

```python
from app.ml.eta_model import ETAPredictionModel

model = ETAPredictionModel()
model.train(X_train, y_train, data_mode="real")
result = model.evaluate(X_test, y_test)
print(result)
# {
#   "evaluation_status": "evaluated",
#   "data_mode": "real",
#   "evaluation_sample_count": <n>,
#   "metrics": {"mae": ..., "rmse": ..., "median_ae": ..., "p90_error": ..., "bias": ...}
# }
```

The same pattern applies to `RouteDeviationClassifier.evaluate()`.

The `/api/v1/metrics` endpoint will automatically surface real metrics once
the models have been trained on sufficient real data.

## Route Optimization (OR-Tools VRP)

The OR-Tools solver is fully functional and runs in real-time. Optimization
results are computed by the actual Haversine distance matrix + the PATH_CHEAPEST_ARC
heuristic. Results will vary by route geometry.

The optimization savings percentages shown in the frontend are computed at
request time from the actual solver output — not from any pre-computed table.

## Evaluation Methodology (for Real-Data Mode)

When real data is available:

- **ETA**: Temporal train/test split (earlier dates train, later dates test)
- **Deviation**: Stratified split preserving class balance
- **No data from test split used during training**
- **Metrics reported**: MAE, RMSE, Median AE, P90 error, Bias (ETA);
  Precision, Recall, F1, PR-AUC via `sklearn.metrics.average_precision_score` (Deviation)
