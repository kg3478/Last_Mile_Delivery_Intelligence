# System Architecture — LastMile Delivery Intelligence

## 1. Architectural Overview

LastMile Delivery Intelligence is architected as an **enterprise modular monolith** designed for high-throughput decision-making, explainable machine learning predictions, and deterministic vehicle routing optimization.

Rather than fragmenting operations across microservices with distributed transaction overhead, the platform integrates data ingestion, feature engineering, mathematical optimization, and operational analytics into a cohesive, high-performance service tier.

![System Architecture Diagram](./assets/system_architecture_diagram.jpg)

---

## 2. Core Architectural Principles

1. **Deterministic Optimization + Statistical Machine Learning**: Machine learning is employed exclusively for uncertain environmental factors (driver delay, likelihood of route deviation), whereas deterministic combinatorial algorithms (Google OR-Tools) solve routing constraints, traveling salesperson sequences, and vehicle assignments.
2. **Dual-Store Data Architecture (OLTP + OLAP)**: Application state, real-time dispatch decisions, and immutable audit logs are persisted in PostgreSQL / SQLite, while analytical fleet aggregations and historical query performance are powered by DuckDB with columnar Parquet storage.
3. **Dispatch-Time Temporal Leakage Prevention**: All predictive ML models are isolated from outcome telemetry. Only features available at route departure time $T_0$ are exposed to inference pipelines.
4. **Human-in-the-Loop Decision Governance**: Algorithmic recommendations generate structured evidence payloads. Final dispatch decisions require human authorization and are preserved in an append-only audit trail.

---

## 3. High-Level System Architecture

```mermaid
flowchart TB
    subgraph CLIENT["Frontend Client Tier (Next.js 14 App Router)"]
        UI_OVERVIEW["Operations Control Tower (/)"]
        UI_ROUTES["Route Explorer (/routes)"]
        UI_INVESTIGATE["Route Investigation Workspace (/routes/:id)"]
        UI_RISK["Delivery Risk Radar (/risk)"]
        UI_DEVIATION["Route Deviations & Adherence (/deviations)"]
        UI_OPT["VRP Optimization Workbench (/optimization)"]
        UI_SCENARIOS["What-If Scenario Simulator (/scenarios)"]
        UI_DRIVERS["Driver Performance Analytics (/drivers)"]
        UI_MODELS["ML Model Registry & Calibration (/models)"]
        UI_QUALITY["Data Quality & Provenance (/data-quality)"]
        UI_AUDIT["Decision Audit Trail (/audit)"]
    end

    subgraph API_GATEWAY["API & Routing Tier (FastAPI Async)"]
        ROUTER["FastAPI Router Gateway"]
        CORS["CORS & Origin Security"]
        LIFESPAN["Lifespan Startup Manager & Ingestion Check"]
    end

    subgraph DOMAIN_SERVICES["Domain Logic Tier"]
        INGEST["Data Ingestion & IngestionPipeline"]
        VAL["DataValidator (7-Point Checks)"]
        FEAT["FeatureEngineer (Dispatch-Time Features)"]
        ETA_MOD["ETAPredictionModel (GradientBoosting)"]
        DEV_MOD["RouteDeviationClassifier (RandomForest)"]
        RISK_ENG["DeliveryRiskScorer (Composite 0-100)"]
        OR_VRP["VRPOptimizer (Google OR-Tools pywrapcp)"]
        SIM_ENG["ScenarioSimulator (What-If Analysis)"]
        DEC_ENG["DispatchDecisionEngine (Rule-Based Matrix)"]
        DEV_ANA["RouteDeviationAnalyzer (Kendall Tau)"]
        FLEET_ANA["DeliveryAnalytics (Fleet KPI Engine)"]
    end

    subgraph DATA_TIER["Data Persistence Tier"]
        DB_SESS["Async SQLAlchemy Session Manager"]
        PG_DB[(PostgreSQL / SQLite State Store)]
        DUCK_DB[(DuckDB Columnar OLAP Engine)]
        RAW_FILES[("./data Raw Datasets: Amazon & Mendeley")]
    end

    CLIENT -->|REST / JSON| ROUTER
    ROUTER --> CORS
    ROUTER --> DOMAIN_SERVICES
    DOMAIN_SERVICES --> DB_SESS
    DB_SESS --> PG_DB
    INGEST --> VAL --> RAW_FILES
    INGEST --> DUCK_DB
    INGEST --> PG_DB
```

---

## 4. Layer Breakdown & Technology Stack

| Layer | Technology | Primary Functionality |
| :--- | :--- | :--- |
| **Frontend UI** | Next.js 14, React 18, TypeScript | High-performance Operations Control Tower, server-side rendering, responsive dark-theme glassmorphism UI. |
| **Styling & Visualization** | Tailwind CSS, Lucide Icons, Recharts | Real-time distance variance bar charts, risk gauges, sequence progression diagrams, interactive metric cards. |
| **API Web Server** | FastAPI, Uvicorn, Starlette | Asynchronous HTTP REST endpoints, automatic OpenAPI / Swagger generation, dependency injection, CORS handling. |
| **Validation & Serialization** | Pydantic V2 | Type-safe schema validation, request payload parsing, response model contract enforcement. |
| **Relational Storage (OLTP)** | SQLAlchemy 2.0 (Async), PostgreSQL / SQLite | Acid-compliant entity storage (`routes`, `stops`, `deliveries`, `drivers`, `recommendations`, `audit_logs`). |
| **Analytical Storage (OLAP)**| DuckDB, Apache Parquet | Fast in-process analytical SQL queries on route historical distributions (`routes_olap`). |
| **Optimization Engine** | Google OR-Tools (`ortools.constraint_solver.pywrapcp`) | Traveling Salesperson Problem (TSP) & Vehicle Routing Problem (VRP) solver with penalty terms and capacity constraints. |
| **Predictive ML** | scikit-learn (`GradientBoostingRegressor`, `RandomForestClassifier`), NumPy, Pandas | Supervised ETA delay regression, binary deviation classification, Kendall Tau sequence rank correlation. |
| **Containerization & Deployment** | Docker, Docker Compose, Render PaaS | Multi-stage container builds for frontend and backend with environment configuration. |

---

## 5. Subsystem Deep-Dives

### 5.1 Backend Modular Services

The backend source structure (`backend/app`) is segregated into discrete operational domains:

```text
backend/app/
├── analytics/         # Analytical computation engines
│   ├── delivery.py    # Fleet-wide KPI calculations (OTD rate, P90/P95 delay)
│   └── deviation.py   # Normalized Kendall Tau distance & stop reorder detection
├── api/               # API route controllers
│   ├── audit.py       # GET /audit (immutable decision logs)
│   ├── datasets.py    # GET /datasets, POST /datasets/ingest, GET /datasets/quality
│   ├── deliveries.py  # GET /deliveries, GET /deliveries/{id}, POST /routes/predict-risk
│   ├── drivers.py     # GET /drivers (route difficulty-adjusted performance)
│   ├── health.py      # GET /health (service & data mode status)
│   ├── models.py      # GET /models, GET /metrics (model registry and evaluation)
│   ├── optimization.py# POST /routes/{id}/optimize, POST /routes/{id}/simulate
│   ├── recommendations.py # GET /recommendations, POST /recommendations/decision
│   └── routes.py      # GET /routes, GET /routes/{id}, GET /routes/{id}/deviation
├── core/              # Infrastructure and configuration
│   ├── config.py      # Environment variables via Pydantic BaseSettings
│   └── database.py    # Async engine, session factories, init_db()
├── decisions/         # Human-in-the-loop decision intelligence
│   └── engine.py      # Rule-based decision matrix generating recommendations
├── ingestion/         # Ingestion, validation, and normalization
│   ├── amazon_adapter.py    # Amazon Last Mile Challenge JSON parser
│   ├── mendeley_adapter.py  # Mendeley Planned vs Actual CSV parser
│   ├── canonical.py         # Canonical schema mapping
│   ├── pipeline.py          # Dual-write pipeline (PostgreSQL + DuckDB)
│   └── validation.py        # 7-stage quality validator & SHA-256 provenance
├── ml/                # Predictive machine learning
│   ├── deviation_model.py   # RandomForestClassifier for route deviation
│   ├── eta_model.py         # GradientBoostingRegressor for ETA delay
│   └── features.py          # Strict dispatch-time 9-feature extractor
├── models/            # SQLAlchemy database entities
│   └── models.py      # 14 relational tables mapping the logistics domain
├── optimization/      # Constraint programming
│   └── vrp.py         # OR-Tools VRP and TSP solver
├── risk/              # Risk evaluation
│   └── scorer.py      # Composite multi-factor 0-100 risk scoring
├── schemas/           # Pydantic V2 contract schemas
│   └── schemas.py     # Request/response schemas
└── simulation/        # Operational scenario testing
    └── simulator.py   # What-If dispatcher simulator
```

---

### 5.2 Data Ingestion & Dual-Store Architecture

The platform separates fast transactional writes from analytical batch queries:

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Operator / Startup Event
    participant Pipe as IngestionPipeline
    participant Val as DataValidator
    participant Adapt as Amazon / Mendeley Adapter
    participant PG as PostgreSQL (OLTP)
    participant Duck as DuckDB (OLAP)

    Admin->>Pipe: run_ingestion(dataset_name)
    Pipe->>Val: validate_file(file_path)
    Val-->>Pipe: DataQualityReport (missing values, coordinates, bounds)
    Pipe->>Adapt: parse_raw_records()
    Adapt-->>Pipe: Canonical Records (Route, Stop, Delivery, Driver)
    par Concurrent Persistence
        Pipe->>PG: Batch Insert Canonical ORM Entities
        Pipe->>Duck: CREATE TABLE IF NOT EXISTS routes_olap AS SELECT *
    end
    Pipe-->>Admin: IngestionRun (SUCCESS, counts, provenance hash)
```

1. **Transactional Store (PostgreSQL / SQLite)**:
   - Stores granular relationships (`Route` $\rightarrow$ `Stop` $\rightarrow$ `Delivery`).
   - Maintains transactional integrity for dispatcher actions (`Recommendation` $\rightarrow$ `AuditLog`).
   - Uses SQLAlchemy `selectinload` to prevent N+1 query overhead.
2. **Analytical Store (DuckDB)**:
   - Houses the `routes_olap` table backed by columnar storage.
   - Computes quantile aggregations (P90 and P95 delivery delay distributions) in milliseconds without placing load on the primary transactional database.

---

### 5.3 Request Lifecycle: Route Investigation & Optimization

When a dispatcher navigates to the Route Investigation Workspace (`/routes/[id]`):

```mermaid
sequenceDiagram
    autonumber
    actor Dispatcher as Logistics Dispatcher
    participant FE as Next.js Control Tower
    participant API as FastAPI Backend
    participant ML as ML & Risk Engine
    participant VRP as Google OR-Tools Solver
    participant DB as PostgreSQL DB

    Dispatcher->>FE: Open Route RT_DEMO_02
    FE->>API: GET /api/v1/routes/RT_DEMO_02
    API->>DB: Query Route + Stops + Metrics
    DB-->>API: Entity Graph
    API-->>FE: Route Details & Historical Variance

    FE->>API: POST /api/v1/routes/predict-risk
    API->>ML: Extract Dispatch-Time Features
    ML->>ML: GradientBoosting ETA Delay + RandomForest Deviation Prob
    ML->>ML: DeliveryRiskScorer.calculate_risk()
    ML->>DB: Persist Prediction Record (Audit Traceability)
    API-->>FE: Risk Score, Level (HIGH), & Delay Estimate

    Dispatcher->>FE: Trigger Optimization (W_dist=1.0, W_dur=1.5)
    FE->>API: POST /api/v1/routes/RT_DEMO_02/optimize
    API->>VRP: VRPOptimizer.optimize_route(route, stops)
    VRP->>VRP: Build Haversine Distance Matrix
    VRP->>VRP: Solve via RoutingModel & PATH_CHEAPEST_ARC
    VRP-->>API: Optimized Sequence, Distance (-17.5%), Duration (-14.0%)
    API-->>FE: Comparison Payload

    Dispatcher->>FE: Click "ACCEPT RECOMMENDATION"
    FE->>API: POST /api/v1/recommendations/decision
    API->>DB: Update Recommendation Status to ACCEPTED
    API->>DB: Append Immutable AuditLog Entry
    API-->>FE: Confirmation & Audit ID
```

---

## 6. Containerization & Deployment Architecture

The system is deployed using isolated Docker containers orchestrated via `docker-compose.yml`:

```mermaid
graph TD
    subgraph DOCKER["Docker Environment"]
        subgraph FRONTEND_CONTAINER["Frontend Service (Port 3000)"]
            NEXT["Next.js Production Server<br/>Node.js 18 Alpine"]
        end

        subgraph BACKEND_CONTAINER["Backend Service (Port 8000)"]
            UVICORN["FastAPI Application<br/>Uvicorn ASGI Server<br/>Python 3.11 Slim"]
            LOCAL_DB["SQLite / PostgreSQL<br/>lastmile.db"]
            LOCAL_DUCK["DuckDB Analytics<br/>analytics.duckdb"]
        end
    end

    BROWSER[Dispatcher Browser] -->|HTTP / 3000| FRONTEND_CONTAINER
    FRONTEND_CONTAINER -->|API Calls / 8000| BACKEND_CONTAINER
    BROWSER -->|Direct API / Swagger| BACKEND_CONTAINER
```

### Docker Multi-Stage Strategy
- **Frontend Dockerfile**: Multi-stage build leveraging Node.js 18 Alpine. Installs dependencies with `npm ci`, compiles Next.js standalone output, and runs in a lightweight runtime container.
- **Backend Dockerfile**: Python 3.11-slim base image. Installs C build dependencies required for `numpy`, `scikit-learn`, and `ortools`, followed by dependency installation and non-root execution.
- **Render Deployment (`render.yaml`)**: Preconfigured for Render PaaS deployment with automatic environment variable injection and persistent disk mounts for SQLite and DuckDB files.

---

## 7. Security, Concurrency & Reliability

1. **CORS Security**:
   - Explicitly configured via `CORSMiddleware`.
   - In production, allowed origins are restricted via `ALLOWED_ORIGINS` environment variable.
   - `allow_credentials` is set to `False` to prevent wildcard origin credential leaks.
2. **Database Concurrency**:
   - Asynchronous SQLAlchemy (`async_engine` + `AsyncSessionLocal`) guarantees non-blocking I/O.
   - Relationships utilize `lazy="raise"` on sensitive foreign keys (e.g. `driver`) to prevent implicit synchronous blocking queries.
3. **Graceful Startup Handling**:
   - `lifespan` context manager handles initial schema migrations with `init_db()`.
   - Validates existence of default benchmark records to prevent redundant re-ingestion loops.
   - Warns operators if the default development `SECRET_KEY` is active.
