# User Flow & Operational Workflows — LastMile Delivery Intelligence

## 1. The Core Operational Decision Loop

The operational lifecycle in LastMile Delivery Intelligence follows a structured 7-stage loop:

```mermaid
graph TD
    A["1. OBSERVE<br/>Fleet KPIs, active routes, and initial delay indicators"] --> B["2. PREDICT<br/>ML forecasts delay (min), late probability, & deviation likelihood"]
    B --> C["3. DIAGNOSE<br/>Identify root cause: stop reordering, time window pressure, or traffic"]
    C --> D["4. OPTIMIZE<br/>Google OR-Tools VRP recalculates mathematically optimal sequence"]
    D --> E["5. SIMULATE<br/>Run What-If scenarios: vehicle splits, stop removal, or priority tuning"]
    E --> F["6. DECIDE<br/>Human dispatcher accepts, rejects, or modifies recommendation"]
    F --> G["7. LEARN<br/>Decisions logged to immutable audit trail for continuous feedback"]
    G -.-> A
```

---

## 2. User Personas

| Persona | Primary Goal | Core Workflows |
| :--- | :--- | :--- |
| **Lead Logistics Dispatcher** | Mitigate in-flight delivery delays, prevent SLA breaches, and resequence active routes. | Monitor Control Tower $\rightarrow$ Filter High-Risk Routes $\rightarrow$ Run VRP Optimization $\rightarrow$ Accept Dispatch Action. |
| **Operations Fleet Manager** | Identify recurring bottlenecks, manage driver adherence, and optimize delivery territory constraints. | Driver Analytics $\rightarrow$ Route Deviations $\rightarrow$ What-If Vehicle Split Simulations $\rightarrow$ SLA Compliance Reviews. |
| **Logistics Data Analyst** | Validate data integrity, inspect ML model calibration, and evaluate optimization savings. | Data Quality Reports $\rightarrow$ Model Registry & Drift Metrics $\rightarrow$ Dataset Ingestion Runs $\rightarrow$ Audit Log Inspection. |

---

## 3. Global Navigation & Workspace Map

```mermaid
graph LR
    NAV["Global Sidebar Navigation"]
    
    NAV --> P1["Overview Control Tower (/)"]
    NAV --> P2["Route Explorer (/routes)"]
    NAV --> P3["Delivery Risk Radar (/risk)"]
    NAV --> P4["Route Deviations (/deviations)"]
    NAV --> P5["VRP Optimization (/optimization)"]
    NAV --> P6["Scenario Simulator (/scenarios)"]
    NAV --> P7["Driver Analytics (/drivers)"]
    NAV --> P8["Model Registry (/models)"]
    NAV --> P9["Data Quality & Ingestion (/data-quality)"]
    NAV --> P10["Audit Trail (/audit)"]
    NAV --> P11["System Settings (/settings)"]

    P1 -.->|Investigate Route| P_DETAIL["Route Detail Workspace (/routes/:id)"]
    P2 -.->|Select Route| P_DETAIL
    P3 -.->|Inspect Risk| P_DETAIL
```

---

## 4. End-to-End Dispatcher User Journey

The diagram below details how a dispatcher navigates through the application during an active delivery shift to detect, analyze, and resolve an at-risk route:

```mermaid
sequenceDiagram
    autonumber
    actor D as Dispatcher
    participant CT as Control Tower (Overview)
    participant RW as Route Workspace (/routes/:id)
    participant ML as ML Prediction Engine
    participant VRP as OR-Tools VRP Solver
    participant SIM as Scenario Simulator
    participant AUD as Audit Trail (/audit)

    Note over D,CT: Phase 1: OBSERVE & TRIAGE
    D->>CT: Load Overview Dashboard
    CT-->>D: Display Fleet KPIs (On-Time: 87.5%, Avg Delay: 8.4m, P90: 18.2m)
    CT-->>D: Display Priority Routes Requiring Action
    D->>CT: Click "Investigate" on High-Risk Route (RT_DEMO_02)

    Note over D,RW: Phase 2: PREDICT & DIAGNOSE
    CT->>RW: Navigate to /routes/RT_DEMO_02
    RW->>ML: POST /routes/predict-risk
    ML-->>RW: Risk Score: 68.5 (HIGH), Predicted Delay: +24.0m, Late Prob: 86.5%
    RW-->>D: Display Stop Sequence, Kendall Tau Index (0.71), Reorder Alert
    D->>RW: Review Root Cause: Driver reordered stops 3 & 4 under tight time windows

    Note over D,VRP: Phase 3: OPTIMIZE & COMPARE
    D->>RW: Adjust Weights (Distance: 1.0, Duration: 1.5, Late Penalty: 10.0)
    D->>RW: Click "Run VRP Optimization"
    RW->>VRP: POST /routes/RT_DEMO_02/optimize
    VRP-->>RW: Feasible Solution Found: Distance -17.5% (32.5 vs 38.2 km), Duration -14.0%
    RW-->>D: Render Side-by-Side Sequence Comparison Table

    Note over D,SIM: Phase 4: SIMULATE WHAT-IF SCENARIOS
    D->>RW: Test Scenario: "Split across 2 vehicles"
    RW->>SIM: POST /routes/RT_DEMO_02/simulate (MULTI_VEHICLE, count=2)
    SIM-->>RW: Simulated Duration per Vehicle: 110 min (50% reduction)
    D->>RW: Test Scenario: "Prioritize strict time windows"
    RW->>SIM: POST /routes/RT_DEMO_02/simulate (TIME_WINDOW_PRIORITY)
    SIM-->>RW: Zero time window violations predicted

    Note over D,AUD: Phase 5: DECIDE & AUDIT
    D->>RW: Select Recommended Action: "Apply VRP-Optimized Sequence"
    D->>RW: Click "ACCEPT RECOMMENDATION"
    RW->>AUD: POST /recommendations/decision (action=ACCEPT, reason="VRP saves 17.5% distance")
    AUD-->>RW: Stored Immutable Audit Record (ID: AUD_9921)
    RW-->>D: Status Updated to ACCEPTED with green badge
    D->>AUD: View Audit Log confirming timestamp, dispatcher ID, and evidence snapshot
```

---

## 5. Detailed Screen Workflows

### 5.1 Route Investigation Workspace (`/routes/[id]`)

```mermaid
flowchart TD
    START([Dispatcher Arrives at Route Detail]) --> LOAD_DATA[Load Route Info, Stops, & Deliveries]
    LOAD_DATA --> FETCH_RISK[Fetch ML Risk & ETA Prediction]
    
    FETCH_RISK --> DISPLAY_PANELS[Display 4 Core Panels]
    
    subgraph PANELS["Workspace Panels"]
        P_METRICS["1. Route Metrics & Variance<br/>Planned vs Actual Distance & Time"]
        P_RISK["2. ML Risk Assessment<br/>Score: 0-100, Delay min, Late %"]
        P_VRP["3. VRP Optimization<br/>OR-Tools Sequence Solver"]
        P_SIM["4. What-If Simulator<br/>Resequence / Split / Remove Stop"]
    end
    
    DISPLAY_PANELS --> PANELS
    PANELS --> DECISION_BOX{"Dispatcher Decision Box"}
    
    DECISION_BOX -->|Accept| ACT_ACCEPT[Apply Optimized Sequence<br/>Log to Audit Trail]
    DECISION_BOX -->|Reject| ACT_REJECT[Maintain Current Plan<br/>Log Rationale to Audit Trail]
    DECISION_BOX -->|Dismiss| ACT_DISMISS[Acknowledge Risk<br/>No Routing Change]
    
    ACT_ACCEPT --> COMPLETED([Route Updated & Audited])
    ACT_REJECT --> COMPLETED
    ACT_DISMISS --> COMPLETED
```

---

### 5.2 What-If Scenario Exploration (`/scenarios`)

```mermaid
flowchart LR
    SELECT_ROUTE[Select Active Route] --> CHOOSE_SCENARIO{Choose Scenario Type}
    
    CHOOSE_SCENARIO -->|RESEQUENCE| SCEN_1[Optimal Spatial TSP Resequencing]
    CHOOSE_SCENARIO -->|REMOVE_STOP| SCEN_2[Remove Problematic Stop / Reassign]
    CHOOSE_SCENARIO -->|MULTI_VEHICLE| SCEN_3[Split Route Across 2+ Vehicles]
    CHOOSE_SCENARIO -->|TIME_OPTIMIZED| SCEN_4[Prioritize Duration over Distance]
    CHOOSE_SCENARIO -->|TIME_WINDOW| SCEN_5[Strict SLA Time-Window Penalties]
    
    SCEN_1 --> RUN_SIM[Execute Simulation Engine]
    SCEN_2 --> RUN_SIM
    SCEN_3 --> RUN_SIM
    SCEN_4 --> RUN_SIM
    SCEN_5 --> RUN_SIM
    
    RUN_SIM --> EVAL_OUTCOME[Evaluate Delta Metrics:<br/>- Distance Saved (km)<br/>- Duration Saved (min)<br/>- Late Stops Avoided<br/>- Efficiency Gain %]
    
    EVAL_OUTCOME --> DISPATCH_ACTION[Export Solution to Dispatcher Console]
```

---

### 5.3 Driver Performance & Difficulty-Adjusted Scoring (`/drivers`)

Traditional dispatch platforms unfairly penalize drivers assigned to congested urban centers or high-density apartment complexes with short delivery windows. LastMile Delivery Intelligence introduces **Difficulty-Adjusted Driver Evaluation**:

```mermaid
flowchart TD
    FETCH_DRIVERS[Fetch Drivers & Historical Routes] --> CALC_DIFF[Calculate Route Difficulty Index]
    
    subgraph FORMULA["Difficulty Formula"]
        F1["Difficulty Score = (Avg Stops * 0.4) + (Avg Distance km * 0.6)"]
    end
    
    CALC_DIFF --> FORMULA
    FORMULA --> CORRELATE[Correlate Difficulty with Adherence Rate & Mean Delay]
    
    CORRELATE --> SEGMENT{Driver Evaluation Context}
    
    SEGMENT -->|High Difficulty + High Adherence| STAR[Top Performer: Handles Dense / Complex Routes]
    SEGMENT -->|Low Difficulty + Low Adherence| COACH[Training Opportunity: Deviation on Simple Routes]
    SEGMENT -->|High Difficulty + Moderate Delay| EXPECTED[Expected Variance: Urban Density Impact]
    
    STAR --> DRIVER_TABLE[Render Context-Aware Driver Table]
    COACH --> DRIVER_TABLE
    EXPECTED --> DRIVER_TABLE
```

---

### 5.4 Data Quality & Provenance Pipeline (`/data-quality`)

```mermaid
flowchart TD
    DATA_INPUT[Raw Dataset Selection:<br/>Amazon Last Mile / Mendeley] --> TRIGGER_INGEST[Trigger Ingestion Pipeline]
    
    TRIGGER_INGEST --> VALIDATION_SUITE[7-Stage Data Quality Validator]
    
    subgraph CHECKS["Validation Suite"]
        C1["1. Missing Value Detection"]
        C2["2. Duplicate Record Checks"]
        C3["3. Negative / Zero Duration Checks"]
        C4["4. Negative / Extreme Distance Checks"]
        C5["5. Geographic Coordinate Bounds Check"]
        C6["6. Sequence Integrity & Monotonicity"]
        C7["7. SHA-256 Checksum Calculation"]
    end
    
    VALIDATION_SUITE --> CHECKS
    CHECKS --> REPORT_GEN[Generate DataQualityReport]
    
    REPORT_GEN --> STATUS_CHECK{Validation Status?}
    STATUS_CHECK -->|PASS / WARNING| PERSIST[Persist to PostgreSQL & DuckDB]
    STATUS_CHECK -->|CRITICAL| REJECT_DATA[Halt Ingestion & Log Errors]
    
    PERSIST --> UI_REPORT[Render Interactive Quality Report in UI]
```

---

### 5.5 Decision Audit Trail & Governance (`/audit`)

```mermaid
flowchart LR
    ACTION_TRIGGERED[Dispatcher Takes Decision] --> ENRICH_RECORD[Enrich Payload with Context]
    
    subgraph AUDIT_PAYLOAD["Audit Payload Attributes"]
        A1["Timestamp UTC"]
        A2["User / Dispatcher ID"]
        A3["Route ID & External Route ID"]
        A4["Action Taken: ACCEPT / REJECT / DISMISS"]
        A5["Pre-Action Risk Score & Level"]
        A6["Predicted Delay & Deviation Probability"]
        A7["VRP Objective Weights Used"]
        A8["Written Dispatcher Justification"]
    end
    
    ENRICH_RECORD --> AUDIT_PAYLOAD
    AUDIT_PAYLOAD --> APPEND_LOG[(Append to Immutable AuditLog Table)]
    APPEND_LOG --> LIVE_AUDIT_VIEW[Surfaced in Real-time Audit Viewer (/audit)]
```
