# Machine Learning Specification — LastMile Delivery Intelligence

## Temporal Leakage Prevention Rules

To ensure real-world predictive validity, models strictly enforce:
`Information used at prediction time T <= T`

Forbidden inputs:
- Future stop actual arrival times
- Future route outcomes or completion durations
- Future driver behavior beyond prediction point

## Models

### 1. ETA / Delay Predictor (`ETAPredictionModel`)
- **Task**: Predict delivery delay in minutes (`delay_minutes`).
- **Algorithm**: `GradientBoostingRegressor` (compared against Historical Mean & Linear Regression baselines).
- **Features**:
  - `stop_count`, `planned_distance_km`, `planned_duration_min`
  - `avg_stop_distance_km`, `avg_stop_duration_min`
  - `driver_adherence_rate`, `driver_historical_delay_min`
  - `time_window_pressure`, `route_complexity_score`

### 2. Route Deviation Classifier (`RouteDeviationClassifier`)
- **Task**: Predict binary classification `is_material_deviation` (1 if sequence similarity < 0.85 or distance variance > 10%).
- **Algorithm**: `RandomForestClassifier`.
- **Features**: Route length, stop density, driver historical adherence rate, time-window pressure score.

## Composite Risk Scoring Formula

```text
Composite Risk Score (0..100) =
  (late_probability * 35) +
  (min(1.0, delay_min / 60) * 25) +
  (deviation_probability * 20) +
  (min(1.0, tw_pressure / 50) * 10) +
  (min(1.0, complexity / 50) * 10)
```

### Risk Level Thresholds
- **0–20**: LOW
- **21–50**: MEDIUM
- **51–75**: HIGH
- **76–100**: CRITICAL
