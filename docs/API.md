# REST API Specification Reference — LastMile Delivery Intelligence

## 1. API Architecture Overview

The LastMile Delivery Intelligence API is built with **FastAPI**, featuring fully typed asynchronous request/response validation powered by **Pydantic V2**.

- **Base URL**: `http://localhost:8000` (Local) / `/api/v1` (API Root Prefix)
- **Interactive Documentation**: Swagger UI at `/docs`, OpenAPI JSON at `/api/v1/openapi.json`
- **Content-Type**: `application/json`
- **Date/Time Format**: ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SS.mmmmmmZ`)

---

## 2. API Endpoint Directory

```text
├── Health & Meta
│   └── GET  /health                                 # Service status & data mode
├── Fleet Overview Analytics
│   └── GET  /api/v1/overview                        # Fleet-wide delivery KPIs
├── Datasets & Ingestion
│   ├── GET  /api/v1/datasets                        # List registered datasets
│   ├── POST /api/v1/datasets/ingest                 # Trigger dataset ingestion
│   └── GET  /api/v1/datasets/quality                # Retrieve data quality validation reports
├── Routes
│   ├── GET  /api/v1/routes                          # List all delivery routes
│   ├── GET  /api/v1/routes/{id}                     # Get route detail with stops & packages
│   ├── GET  /api/v1/routes/{id}/performance         # Get route planned vs actual performance
│   └── GET  /api/v1/routes/{id}/deviation           # Get route Kendall Tau sequence deviation
├── Deliveries
│   ├── GET  /api/v1/deliveries                      # List deliveries (limit 100)
│   └── GET  /api/v1/deliveries/{id}                 # Get single delivery package detail
├── Risk Prediction
│   └── POST /api/v1/routes/predict-risk             # Predict ETA delay, deviation, & risk score
├── Optimization & Simulation
│   ├── POST /api/v1/routes/{id}/optimize            # Run Google OR-Tools VRP sequence solver
│   └── POST /api/v1/routes/{id}/simulate            # Run What-If dispatch scenario
├── Recommendations & Decisions
│   ├── GET  /api/v1/recommendations                 # List active recommendations
│   ├── GET  /api/v1/recommendations/{id}            # Get recommendation with evidence record
│   └── POST /api/v1/recommendations/decision        # Record ACCEPT / REJECT decision & audit
├── Drivers
│   ├── GET  /api/v1/drivers                         # List drivers with difficulty-adjusted KPIs
│   └── GET  /api/v1/drivers/{id}                    # Get single driver details
├── ML Models & Metrics
│   ├── GET  /api/v1/models                          # Model registry metadata & features
│   └── GET  /api/v1/metrics                         # Actual computed evaluation metrics
└── Audit Trail
    └── GET  /api/v1/audit                           # List immutable dispatch decision audit logs
```

---

## 3. Endpoint Specifications

### 3.1 Health Check
- **Endpoint**: `GET /health`
- **Description**: Returns system health status, active environment, and data mode (`real` vs `synthetic_demo`).
- **Response**:
```json
{
  "status": "healthy",
  "service": "LastMile Delivery Intelligence",
  "version": "1.0.0",
  "environment": "development",
  "data_mode": "synthetic_demo",
  "data_mode_note": "Real dataset files not found in ./data/. Running in synthetic_demo mode (SYNTHETIC TEST FIXTURE). See README Section 4 for dataset setup instructions."
}
```

---

### 3.2 Fleet Overview Analytics
- **Endpoint**: `GET /api/v1/overview`
- **Description**: Computes fleet-wide delivery KPIs including on-time rate, average delay, P90/P95 tail delays, route efficiency, and count of high-risk routes.
- **Response**:
```json
{
  "total_routes": 12,
  "total_deliveries": 96,
  "on_time_delivery_rate": 0.875,
  "late_delivery_rate": 0.125,
  "avg_delay_minutes": 8.4,
  "p90_delay_minutes": 18.2,
  "p95_delay_minutes": 24.5,
  "avg_route_efficiency_pct": 91.2,
  "route_deviation_rate": 0.167,
  "high_risk_routes_count": 2,
  "optimization_opportunities_count": 3
}
```

---

### 3.3 Route Risk Prediction
- **Endpoint**: `POST /api/v1/routes/predict-risk`
- **Description**: Extracts 9 dispatch-time features for the specified route, evaluates the `ETAPredictionModel` and `RouteDeviationClassifier`, calculates the composite risk score (0–100), and records an immutable `Prediction` record for auditability.
- **Request Body**:
```json
{
  "route_id": "RT_DEMO_02"
}
```
- **Response**:
```json
{
  "prediction_id": "4028a1c9-7d8b-4a5f-b52e-9d2a6a61b8f1",
  "route_id": "RT_DEMO_02",
  "external_route_id": "ROUTE_EXT_1002",
  "predicted_delay_min": 22.5,
  "late_probability": 0.818,
  "deviation_probability": 0.650,
  "composite_risk_score": 68.5,
  "risk_level": "HIGH",
  "data_mode": "synthetic_demo",
  "features": {
    "stop_count": 8.0,
    "planned_distance_km": 32.5,
    "planned_duration_min": 180.0,
    "avg_stop_distance_km": 4.06,
    "avg_stop_duration_min": 22.5,
    "driver_adherence_rate": 0.85,
    "driver_historical_delay_min": 8.0,
    "time_window_pressure": 15.0,
    "route_complexity_score": 18.25
  }
}
```

---

### 3.4 Route Optimization (Google OR-Tools VRP)
- **Endpoint**: `POST /api/v1/routes/{route_id}/optimize`
- **Description**: Solves the Traveling Salesperson / Vehicle Routing Problem for the route's stops using Google OR-Tools. Returns the baseline vs optimized sequence and distance/duration savings.
- **Request Body**:
```json
{
  "route_id": "RT_DEMO_02",
  "objective_weights": {
    "distance_weight": 1.0,
    "duration_weight": 1.5,
    "late_penalty_weight": 10.0,
    "time_window_penalty_weight": 20.0
  }
}
```
- **Response**:
```json
{
  "algorithm": "Google OR-Tools VRP Solver",
  "solver_time_ms": 14.52,
  "baseline_distance_km": 38.2,
  "optimized_distance_km": 31.5,
  "baseline_duration_min": 220.0,
  "optimized_duration_min": 189.2,
  "distance_savings_pct": 17.5,
  "duration_savings_pct": 14.0,
  "is_feasible": true,
  "optimized_sequence": [
    {
      "stop_id": "ST_01",
      "external_stop_id": "EXT_ST_01",
      "address": "124 Market St, San Francisco, CA",
      "original_sequence": 1,
      "optimized_sequence": 1
    },
    {
      "stop_id": "ST_04",
      "external_stop_id": "EXT_ST_04",
      "address": "550 Mission St, San Francisco, CA",
      "original_sequence": 4,
      "optimized_sequence": 2
    }
  ],
  "objective_value": 315.3,
  "weights_used": {
    "distance_weight": 1.0,
    "duration_weight": 1.5
  }
}
```

---

### 3.5 What-If Scenario Simulation
- **Endpoint**: `POST /api/v1/routes/{route_id}/simulate`
- **Description**: Simulates the operational impact of dispatcher interventions: stop removal, multi-vehicle split, or time optimization.
- **Request Body**:
```json
{
  "route_id": "RT_DEMO_02",
  "scenario_type": "MULTI_VEHICLE",
  "vehicle_count": 2
}
```
- **Response**:
```json
{
  "scenario_type": "MULTI_VEHICLE",
  "description": "Split route across 2 parallel delivery vehicles.",
  "baseline_distance_km": 38.2,
  "simulated_distance_km": 34.65,
  "distance_saved_km": 3.55,
  "baseline_duration_min": 220.0,
  "simulated_duration_min": 110.0,
  "duration_saved_min": 110.0,
  "baseline_late_stops": 0,
  "simulated_late_stops": 0,
  "efficiency_gain_pct": 50.0
}
```

---

### 3.6 Recommendation Decision & Audit Trail
- **Endpoint**: `POST /api/v1/recommendations/decision`
- **Description**: Records a dispatcher ACCEPT, REJECT, or DISMISS decision on an algorithmic recommendation and commits an immutable entry to `audit_logs`.
- **Request Body**:
```json
{
  "recommendation_id": "REC_98124_01",
  "action": "ACCEPT",
  "reason": "VRP resequencing yields 17.5% distance savings and eliminates predicted 22m delay.",
  "user_id": "dispatcher_01"
}
```
- **Response**:
```json
{
  "status": "SUCCESS",
  "recommendation_id": "REC_98124_01",
  "new_status": "ACCEPTED",
  "audit_recorded": true
}
```

---

### 3.7 ML Models & Honest Evaluation Metrics
- **Endpoint**: `GET /api/v1/metrics`
- **Description**: Returns verified evaluation metrics for each model. In `synthetic_demo` mode, metrics return `null` with a clear explanation rather than fabricated numbers.
- **Response**:
```json
{
  "eta_model": {
    "model_name": "ETA_DELAY_PREDICTOR",
    "algorithm": "GradientBoostingRegressor",
    "data_mode": "synthetic_demo",
    "training_sample_count": 5,
    "evaluation_sample_count": 0,
    "evaluation_status": "insufficient_data",
    "metrics": null,
    "limitations": "Model is trained on a 5-sample synthetic benchmark. Metrics are not available (insufficient_data). Supply real Amazon Last Mile data and call train()/evaluate() to obtain meaningful performance estimates."
  },
  "deviation_model": {
    "model_name": "ROUTE_DEVIATION_CLASSIFIER",
    "algorithm": "RandomForestClassifier",
    "data_mode": "synthetic_demo",
    "training_sample_count": 5,
    "evaluation_sample_count": 0,
    "evaluation_status": "insufficient_data",
    "metrics": null,
    "limitations": "Model is trained on a 5-sample synthetic benchmark. Metrics are not available (insufficient_data). Supply real Mendeley Planned-vs-Actual data and call train()/evaluate() to obtain meaningful performance estimates."
  }
}
```

---

### 3.8 Audit Trail Log
- **Endpoint**: `GET /api/v1/audit`
- **Description**: Fetches the 100 most recent immutable audit log entries, ordered chronologically descending.
- **Response**:
```json
[
  {
    "id": "18f273be-d5b1-4f74-8b65-68a8dc4e8c11",
    "user_id": "dispatcher_01",
    "action": "RECOMMENDATION_DECISION",
    "entity_type": "RECOMMENDATION",
    "entity_id": "REC_98124_01",
    "details": {
      "action": "ACCEPT",
      "reason": "VRP resequencing yields 17.5% distance savings and eliminates predicted 22m delay.",
      "route_id": "RT_DEMO_02",
      "risk_score": 68.5,
      "recommendation_action_type": "REROUTE",
      "recommendation_title": "Apply VRP-Optimized Stop Sequence",
      "evidence_snapshot": {
        "route_id": "RT_DEMO_02",
        "predicted_delay_min": 22.5,
        "deviation_probability": 0.65
      }
    },
    "timestamp": "2026-10-04T15:10:45.123456Z"
  }
]
```
