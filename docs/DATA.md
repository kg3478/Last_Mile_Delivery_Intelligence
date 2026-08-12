# Data Provenance & Ingestion Specification — LastMile Delivery Intelligence

## Primary Real-World Datasets

The platform is designed around two real public logistics research datasets:

### 1. Amazon Last Mile Routing Research Challenge
- **Source**: [AWS Open Data Registry](https://registry.opendata.aws/amazon-last-mile-challenges/)
- **Scope**: 9,184 historical driver routes performed in 2018 across five U.S. metropolitan areas.
- **Attributes Used**: Route sequences, stop locations, service times, package dimensions, depot coordinates.
- **Usage**: Benchmark for route intelligence, stop-level feature engineering, and VRP optimization.

### 2. Planned vs Actual Last-Mile Routes
- **Source**: [Mendeley Data](https://data.mendeley.com/datasets/kkwgfvmtxn)
- **DOI**: `https://doi.org/10.17632/kkwgfvmtxn.1`
- **License**: CC BY 4.0
- **Attributes Used**: Planned route sequences vs actual driver sequences, travel distance, duration, time-window data.
- **Usage**: Benchmark for sequence deviation prediction, driver adherence analytics, and Kendall Tau similarity index.

## Ingestion & Quality Validation Pipeline

```text
RAW DATA (CSV / Parquet / JSON)
        ↓
DataValidator (Null checks, duplicate checks, coordinate validation)
        ↓
DataQualityReport & SHA-256 Provenance Hash
        ↓
Canonical Delivery Model Normalization (Route, Stop, Package, Driver)
        ↓
PostgreSQL Persistence + DuckDB Parquet Analytics
```

## Data Quality Metrics
For every dataset ingested, the system computes:
- Total rows & missing value counts
- Duplicate record detection
- Negative distance & duration validation
- Cryptographic SHA-256 hash for provenance validation
