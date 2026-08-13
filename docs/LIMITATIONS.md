# System Limitations & Boundary Conditions — LastMile Delivery Intelligence

## Known Limitations

### 1. Real Dataset Files Not Included

The Amazon Last Mile Routing Challenge and Mendeley Planned-vs-Actual datasets
are **not committed to this repository**. Both must be downloaded separately
from their public sources and placed in `./data/`.

When the dataset files are absent, the application operates in **synthetic_demo**
mode using a hard-coded 5-route fixture. This mode is clearly labeled
(`is_synthetic=True` on Dataset records, `data_mode="synthetic_demo"` in the
ML model API).

### 2. ML Models: Insufficient Training Data in Demo Mode

Both ML models (ETA predictor, deviation classifier) are trained on 5 hard-coded
benchmark samples in synthetic_demo mode. No statistically meaningful evaluation
metrics are available until real data is provided. The `/api/v1/metrics` endpoint
returns `evaluation_status: "insufficient_data"` and `metrics: null` — not fake numbers.

### 3. Static Traffic Representation

The dataset does not include live GPS telemetry. Traffic factors are modeled
via service time variance and historical travel durations only.

### 4. Geographic Scope

Public datasets originate from U.S. metropolitan regions (Amazon) and specific
European urban courier networks (Mendeley). Model behavior in other geographies
is untested.

### 5. No Live Production Dispatch Integration

The platform is a decision-intelligence overlay with human-in-the-loop audit
logging. It does not directly control vehicle hardware or dispatch systems.

### 6. OR-Tools VRP Solver Assumptions

The optimization solver uses Haversine straight-line distance as a proxy for
actual road distance. Real road networks will produce different results. The
solver uses a 2-second time limit per route; complex routes may find only
heuristic (not globally optimal) solutions.

### 7. DuckDB OLAP Table is Append-Only on Re-Ingestion

`CREATE TABLE IF NOT EXISTS ... AS SELECT * FROM df` creates the DuckDB
`routes_olap` table only on first ingestion. User-triggered re-ingestion via
the API does not update the DuckDB table. This is a known limitation; a
full OLAP refresh on re-ingestion is a planned improvement.

### 8. Authentication Not Implemented

The current API has no authentication or authorization layer. All endpoints
are publicly accessible. This is acceptable for a local demonstration but must
be addressed before production deployment.

### 9. Default SECRET_KEY

The default development SECRET_KEY is insecure. It must be replaced with a
cryptographically strong random key before any production deployment. The
application logs a warning at startup when the default key is detected.
