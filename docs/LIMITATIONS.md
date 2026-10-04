# System Limitations, Assumptions & Boundary Conditions — LastMile Delivery Intelligence

## 1. Overview of System Boundaries

LastMile Delivery Intelligence is engineered as a decision-intelligence overlay and tactical planning engine for last-mile logistics operations.

To ensure operational transparency and avoid misleading claims, this document enumerates all known architectural, algorithmic, statistical, and infrastructural boundary conditions.

---

## 2. Enumerated System Limitations

### 2.1 Public Research Dataset Availability (Demo Mode Boundary)
- **Constraint**: The Amazon Last Mile Routing Challenge (multi-gigabyte JSON) and Mendeley Planned-vs-Actual datasets are **not committed to the Git repository** due to size limits.
- **Operational Impact**: When raw dataset files are absent from `./data/`, the application operates in **`synthetic_demo`** mode with a 5-route benchmark fixture.
- **Mitigation / Remedy**: The system clearly tags records with `is_synthetic = True` and reports `data_mode: "synthetic_demo"`. Complete instructions to ingest genuine public datasets are documented in `docs/DATA.md`.

### 2.2 Statistical Validity of Demo Mode Machine Learning
- **Constraint**: Supervised ML models (`ETAPredictionModel`, `RouteDeviationClassifier`) trained on 5 bootstrap benchmark samples cannot yield statistically significant performance metrics.
- **Operational Impact**: The system reports `evaluation_status: "insufficient_data"` and `metrics: null`.
- **Policy Enforcement**: The platform strictly prohibits fabricating or hard-coding artificial accuracy numbers. Real evaluation metrics require downloading real datasets and running the evaluation pipeline.

### 2.3 Haversine Distance vs Real-World Road Topologies
- **Constraint**: The Google OR-Tools VRP solver computes all-pairs distance matrices using the **Haversine great-circle formula** (straight-line spherical geometry).
- **Operational Impact**: Haversine distance underestimates actual driving distance across urban road networks with one-way streets, cul-de-sacs, bridges, and traffic barricades.
- **Mitigation / Remedy**: The duration heuristic applies an urban circuity multiplier ($1.2 \dots 1.4\times$) and time-window pressure penalties to approximate real transit friction. Integration with real-road matrix engines (e.g., OpenStreetMap / OSRM) is planned for Phase 4.

### 2.4 OR-Tools Solver Heuristic Time Cutoff
- **Constraint**: To prevent blocking the asynchronous web server during dispatcher requests, the solver enforces a **2.0-second search cutoff**:
  ```python
  search_parameters.time_limit.seconds = 2
  ```
- **Operational Impact**: For complex routes exceeding 40 stops, the solver returns a high-quality local heuristic solution (`PATH_CHEAPEST_ARC`), which may not represent the global mathematical optimum.

### 2.5 Static Historical Traffic vs Live Real-Time Telemetry
- **Constraint**: The platform models delay risk using historical driver adherence, time-window tightness, and route complexity. It does not interface with live streaming GPS OBD-II transponders or dynamic traffic feeds (e.g. Google Maps Traffic API).
- **Operational Impact**: Sudden, unpredicted traffic anomalies occurring mid-shift (such as a multi-vehicle accident occurring 5 minutes ago) cannot be detected until reflected in stop arrival variance.

### 2.6 Geographic and Operational Scope
- **Constraint**: Datasets reflect U.S. metropolitan van deliveries (Amazon) and European urban courier networks (Mendeley).
- **Operational Impact**: Model behavior in different operating conditions (e.g. 2-wheeler hyper-local grocery delivery in Southeast Asia or long-haul rural freight) has not been benchmarked and requires local re-training.

### 2.7 DuckDB OLAP Table Re-Ingestion Behavior
- **Constraint**: In the current implementation, the DuckDB `routes_olap` analytical table is instantiated upon initial startup via:
  ```sql
  CREATE TABLE IF NOT EXISTS routes_olap AS SELECT * FROM df;
  ```
- **Operational Impact**: Triggering subsequent re-ingestion runs via the API updates the primary PostgreSQL/SQLite database but does not automatically drop and refresh the DuckDB OLAP table until the service is restarted.

### 2.8 Human-in-the-Loop Dispatch Overlay (No Direct Hardware Actuation)
- **Constraint**: The system functions as a **decision-support platform**, not an automated execution actuator.
- **Operational Impact**: Optimized sequences and recommendations are presented to dispatchers for explicit authorization (ACCEPT, REJECT, DISMISS). The platform does not directly flash turn-by-turn routes to third-party in-cab electronic logging devices (ELDs).

### 2.9 Authentication & Production Hardening
- **Constraint**: In the current release, authentication and authorization endpoints are stubbed; all API endpoints are publicly accessible across local networks.
- **Operational Impact**: Suitable for local evaluation, technical review, and staging environments, but requires OAuth2 / JWT authentication before exposing to public networks.

---

## 3. Production Deployment Readiness Checklist

Before deploying this software into a mission-critical commercial logistics environment, operators must execute the following hardening steps:

- [ ] **Configure Strong `SECRET_KEY`**: Set a high-entropy 256-bit secret key in `.env` to replace the default development key.
- [ ] **Deploy OSRM / Mapbox Road Matrix Engine**: Replace Haversine straight-line distances with true road-network driving distances and turn restrictions.
- [ ] **Ingest Real Dataset Volume**: Ingest $\ge 1,000$ historical routes to transition ML models from `synthetic_demo` to `real` evaluated mode.
- [ ] **Enforce Authentication & RBAC**: Activate role-based access control (`ADMIN`, `DISPATCHER`, `OPERATIONS_MANAGER`, `ANALYST`, `VIEWER`).
- [ ] **Configure Redis Caching**: Cache computed Haversine distance matrices for frequently repeated depot/cluster locations.
- [ ] **Set Production CORS Origins**: Restrict `ALLOWED_ORIGINS` to the exact production domain (e.g., `https://lastmile.enterprise.com`).
