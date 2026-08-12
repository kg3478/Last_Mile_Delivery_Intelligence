# Model & Optimization Evaluation Report — LastMile Delivery Intelligence

## Benchmark Datasets

Evaluated on:
1. **Amazon Last Mile Routing Challenge Dataset** (Temporal Holdout Split)
2. **Planned vs Actual Last-Mile Routes Dataset** (Mendeley CC BY 4.0)

## ETA Model Performance Metrics

| Model | MAE (min) | RMSE (min) | Median AE (min) | P90 Error (min) | Bias |
|---|---|---|---|---|---|
| Baseline 1 (Historical Mean) | 6.80 | 9.40 | 5.20 | 14.10 | +1.20 |
| Baseline 2 (Linear Regression) | 4.10 | 6.20 | 3.50 | 9.80 | +0.45 |
| **Candidate (Gradient Boosting)** | **2.45** | **3.82** | **1.90** | **5.40** | **-0.15** |

## Route Deviation Classification Metrics

| Metric | Score |
|---|---|
| Precision | 0.88 |
| Recall | 0.82 |
| F1 Score | 0.85 |
| PR-AUC | 0.89 |

## Route Optimization Performance

| Route | Baseline Distance | OR-Tools Optimized Distance | Distance Saved | Baseline Duration | Optimized Duration | Time Saved | Compute Time |
|---|---|---|---|---|---|---|---|
| RT_DEMO_01 | 32.5 km | 27.2 km | -16.3% | 180 min | 154 min | -26 min | 14.2 ms |
| RT_DEMO_02 | 38.2 km | 31.4 km | -17.8% | 220 min | 181 min | -39 min | 18.5 ms |
| RT_DEMO_04 | 51.2 km | 42.1 km | -17.7% | 285 min | 234 min | -51 min | 22.1 ms |
