# Data Engineering, Provenance & Validation — LastMile Delivery Intelligence

## 1. Data Engineering Philosophy

LastMile Delivery Intelligence is engineered around **real-world logistics research datasets**. The data engineering pipeline is constructed to guarantee:

1. **Strict Provenance Tracking**: Every ingested dataset record maintains immutable metadata: source URL, DOI, licensing, download timestamp, and cryptographic SHA-256 file hashes.
2. **Canonical Data Normalization**: Raw heterogeneous formats (nested JSON from Amazon, multi-column CSV from Mendeley) are normalized into a unified relational schema (`Route`, `Stop`, `Delivery`, `Driver`).
3. **Data Quality Enforcements**: Automated 7-stage quality validator checks for spatial, temporal, and sequence anomalies before data enters the production database.
4. **Dual-Store Architecture (OLTP + OLAP)**: High-write relational records are stored in PostgreSQL/SQLite for transactional operations, while analytical route distributions are indexed in DuckDB using columnar Parquet.
5. **Absolute Data Honesty Policy**: Synthetic data fixtures are clearly tagged (`is_synthetic = True`, `data_mode = "synthetic_demo"`) and never used for reported model evaluation metrics.

---

## 2. Primary Public Datasets

### 2.1 Amazon Last Mile Routing Research Challenge
- **Source**: [AWS Open Data Registry](https://registry.opendata.aws/amazon-last-mile-challenges/)
- **Publication Year**: 2021
- **Domain**: Real-world e-commerce van delivery operations conducted across 5 metropolitan areas in the United States (Seattle, Chicago, Los Angeles, Austin, Boston).
- **Scope**: 9,184 historical delivery routes, over 1.2 million individual package deliveries.
- **Attributes Utilized**:
  - `route_id`, `station_code` (depot), `date_YYYY_MM_DD`, `departure_time`
  - `stops`: Stop IDs, latitude/longitude coordinates, stop type (`Dropoff`, `Station`), service time estimates.
  - `packages`: Dimensions ($L \times W \times H$), package weight (kg), volume ($m^3$), delivery time windows.
- **Role in Platform**: Primary benchmark for vehicle routing problem (VRP) optimization, spatial feature engineering, and stop-level service time analysis.
- **Setup Instruction**: Download `amazon_last_mile.json` from the official AWS Open Data Registry and place it in `./data/amazon_last_mile.json`.

### 2.2 Planned vs Actual Last-Mile Delivery Routes (Mendeley Data)
- **Source**: [Mendeley Data Repository](https://data.mendeley.com/datasets/kkwgfvmtxn)
- **DOI**: [`10.17632/kkwgfvmtxn.1`](https://doi.org/10.17632/kkwgfvmtxn.1)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Domain**: European urban courier and express parcel distribution network.
- **Scope**: Multi-stop commercial courier delivery routes with GPS telemetry.
- **Attributes Utilized**:
  - Planned route stop sequences vs actual executed driver stop sequences.
  - Planned travel distance (km) vs actual driven distance (km).
  - Planned route duration (min) vs actual route completion duration (min).
  - Stop arrival timestamps and delivery time-window compliance indicators.
- **Role in Platform**: Ground-truth benchmark for route deviation detection, Kendall Tau sequence rank similarity, and driver route adherence profiling.
- **Setup Instruction**: Download `mendeley_planned_vs_actual.csv` from Mendeley Data and place it in `./data/mendeley_planned_vs_actual.csv`.

### 2.3 Optional Third Dataset — LaDe (Last-mile Delivery Dataset)
- **Source**: Industry-scale benchmark from Cainiao / Alibaba Network.
- **Attributes**: Fine-grained courier trajectories with GPS point sequences.
- **Role in Platform**: Serves as a reference design for micro-telemetry expansion in Phase 4 roadmap.

---

## 3. Data Pipeline & Processing Flow

```mermaid
flowchart TD
    subgraph INGESTION["Raw File Ingestion"]
        RAW_JSON["Amazon JSON File<br/>data/amazon_last_mile.json"]
        RAW_CSV["Mendeley CSV File<br/>data/mendeley_planned_vs_actual.csv"]
    end

    subgraph VALIDATION["7-Stage Quality Validator (DataValidator)"]
        V1["1. Missing Value Detection"]
        V2["2. Duplicate Record Removal"]
        V3["3. Duration Validity Check (duration > 0)"]
        V4["4. Distance Validity Check (0 < dist < 500 km)"]
        V5["5. Geographic Bounds (-90<=lat<=90, -180<=lng<=180)"]
        V6["6. Stop Sequence Monotonicity Check"]
        V7["7. SHA-256 Checksum Verification"]
    end

    subgraph REPORT["Quality & Provenance Artifacts"]
        QREP["DataQualityReportSchema<br/>(status, issues, provenance_hash)"]
        IN_RUN["IngestionRun (SUCCESS / FAILED)"]
    end

    subgraph NORMALIZATION["Canonical Normalization Adapters"]
        ADAPT_AMAZON["AmazonAdapter"]
        ADAPT_MENDELEY["MendeleyAdapter"]
        CAN_MODELS["Canonical Models:<br/>Dataset, Driver, Route, Stop, Delivery"]
    end

    subgraph STORAGE["Dual-Store Persistence Layer"]
        PG_DB[("PostgreSQL / SQLite (OLTP)<br/>- routes, stops, deliveries<br/>- recommendations, audit_logs")]
        DUCK_OLAP[("DuckDB Parquet Store (OLAP)<br/>- routes_olap table<br/>- fast quantile analytics")]
    end

    RAW_JSON --> V1
    RAW_CSV --> V1
    V1 --> V2 --> V3 --> V4 --> V5 --> V6 --> V7
    V7 --> QREP
    QREP --> IN_RUN
    
    QREP -->|Validation Passed| ADAPT_AMAZON
    QREP -->|Validation Passed| ADAPT_MENDELEY
    ADAPT_AMAZON --> CAN_MODELS
    ADAPT_MENDELEY --> CAN_MODELS
    
    CAN_MODELS --> PG_DB
    CAN_MODELS --> DUCK_OLAP
```

---

## 4. Canonical Delivery Data Model (Entity Relationship)

All incoming datasets are mapped into a standardized relational data model:

```mermaid
erDiagram
    Dataset ||--o{ Route : contains
    Dataset ||--o{ Driver : tracks
    Dataset ||--o{ IngestionRun : logs
    Driver ||--o{ Route : operates
    Route ||--o{ Stop : includes
    Route ||--o| RouteMetric : computes
    Route ||--o| RouteDeviation : measures
    Route ||--o{ Prediction : evaluates
    Route ||--o{ OptimizationRun : solves
    Route ||--o{ ScenarioRun : simulates
    Route ||--o{ Recommendation : generates
    Stop ||--o{ Delivery : carries
    Stop ||--o{ Prediction : assesses

    Dataset {
        string id PK
        string name
        string source_url
        string doi
        string license
        string version
        timestamp download_timestamp
        string file_hash
        int row_count
        int route_count
        int stop_count
        int driver_count
        string validation_status
        boolean is_synthetic
    }

    Route {
        string id PK
        string dataset_id FK
        string external_route_id
        string driver_id FK
        string vehicle_id
        json depot_location
        string route_date
        float planned_distance_km
        float actual_distance_km
        float planned_duration_min
        float actual_duration_min
        int total_stops
        string status
        timestamp created_at
    }

    Stop {
        string id PK
        string route_id FK
        string external_stop_id
        int planned_sequence
        int actual_sequence
        float lat
        float lng
        string address
        timestamp planned_arrival
        timestamp actual_arrival
        float service_time_min
        timestamp time_window_start
        timestamp time_window_end
        string status
    }

    Delivery {
        string id PK
        string stop_id FK
        string package_id
        float weight_kg
        float volume_m3
        string priority
        boolean is_late
        float delay_minutes
    }

    RouteMetric {
        string id PK
        string route_id FK
        float distance_variance_km
        float duration_variance_min
        float on_time_delivery_rate
        int late_delivery_count
        float route_efficiency_score
    }

    RouteDeviation {
        string id PK
        string route_id FK
        float sequence_similarity_index
        int stop_reorder_count
        float additional_distance_km
        float additional_duration_min
        float deviation_percentage
        boolean is_material_deviation
        text explanation
    }
```

---

## 5. Automated Data Quality Enforcements

The `DataValidator` module implements 7 validation rules:

| # | Check Name | Validation Logic | Failure Classification |
| :--- | :--- | :--- | :--- |
| **1** | **Missing Values** | Checks critical keys (`route_id`, `stop_id`, coordinates). | Critical if primary identifiers null; Warning if metadata missing. |
| **2** | **Duplicate Detection**| Scans for duplicate stop identifiers within the same route. | Critical if duplicate stop sequences detected. |
| **3** | **Duration Bounds** | Verifies planned and actual duration are $> 0$ and $< 1,440\text{ min}$ (24h). | Critical if negative; Warning if duration $> 12\text{ hours}$. |
| **4** | **Distance Bounds** | Confirms route distances are $> 0.1\text{ km}$ and $< 600.0\text{ km}$. | Warning if distance exceeds single-shift bounds. |
| **5** | **Coordinate Bounds**| Validates $-90.0 \le \text{lat} \le 90.0$ and $-180.0 \le \text{lng} \le 180.0$. | Critical if out of physical bounds. |
| **6** | **Sequence Integrity**| Validates planned sequence starts at $1$ and increments monotonically. | Warning if non-consecutive stop sequences exist. |
| **7** | **Provenance Checksum**| Computes cryptographic SHA-256 hash of the input file. | Preserved permanently in `datasets.file_hash`. |

---

## 6. Synthetic Data Policy & Fallback Discipline

To support frictionless out-of-the-box local development, testing, and UI demonstrations without requiring users to download gigabytes of raw data:

1. **Explicit Tagging**: If neither Amazon nor Mendeley dataset files are located in `./data/`, the application bootstraps a lightweight benchmark fixture.
2. **Database Level**: The corresponding `Dataset` record is marked with `is_synthetic = True`.
3. **API Level**: Endpoints return `data_mode: "synthetic_demo"`.
4. **Machine Learning Integrity**: The ML subsystem reports:
   - `evaluation_status: "insufficient_data"`
   - `metrics: null`
5. **No Fake Claims**: The system **never** trains production models on synthetic fixtures or reports synthetic test metrics as genuine model performance.

---

## 7. Known Data Limitations

- **Urban Street Network vs Straight-Line Coordinates**: Datasets provide latitude/longitude waypoints rather than full GPS turn-by-turn vectors. Distance computations use the Haversine great-circle formula.
- **Static vs Dynamic Traffic**: Real historical datasets reflect observed transit times but do not include high-frequency live traffic sensor feeds.
- **Service Time Imputation**: When raw records omit stop unloading durations, a conservative domain-standard default ($5.0\text{ minutes}$) is applied.
