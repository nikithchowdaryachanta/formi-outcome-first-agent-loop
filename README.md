# Formi – Outcome-First Agent Loop

**An autonomous workflow monitoring and decision system built with Python and SQLite.**

Formi collects workflow events, monitors operational performance, identifies anomalies, evaluates configuration changes, and maintains an auditable record of system activity.

The system follows an outcome-first approach: decisions are evaluated using measurable workflow performance rather than activity alone.

---

## Overview

Formi is designed to monitor and analyze automated workflows by connecting event processing, performance measurement, operational monitoring, and evidence-based decision evaluation.

It focuses on three key performance indicators:

| Metric | Description |
|---|---|
| **Pickup Rate** | Percentage of dial attempts that successfully connect. |
| **Engagement Rate** | Percentage of connected people who remain engaged until the interaction concludes. |
| **Outcome Rate** | Percentage of uploaded leads that reach a concluded outcome. |

Keeping these metrics separate helps identify whether a workflow is experiencing connection problems, engagement problems, or issues with its overall outcomes.

## System Architecture

The application uses modular components that work together to collect, process, analyze, and record workflow activity.

```text
                  Workflow Simulator
                          |
                       HTTP API
                          |
                          v
                      Controller
                          |
                          v
                    Event Ingestion
                          |
                          v
                      SQLite DB
                          |
                 +--------+--------+
                 |                 |
                 v                 v
          Performance Monitor  Decision Engine
                 |                 |
                 v                 v
          Operational Signals  Configuration Analysis
                 |                 |
                 +--------+--------+
                          |
                          v
                     Audit Records
```

### Core Components

| Component | Description |
|---|---|
| `controller.py` | Main entry point that coordinates simulator communication and workflow execution. |
| `event_ingest.py` | Retrieves, processes, and stores incoming workflow events. |
| `decision_engine.py` | Evaluates workflow performance and configuration decisions using available evidence. |
| `performance_monitor.py` | Monitors performance indicators and operational signals, including caller-ID anomalies and supervisor configuration changes. |
| SQLite | Stores workflow events, processing checkpoints, and audit records. |
| `run.sh` | Starts the application controller. |

## How the System Works

**1. Simulator Communication**

The controller connects to the workflow simulator through its HTTP API to retrieve workflow-related information and coordinate processing.

**2. Event Ingestion**

The ingestion component retrieves incoming events and prepares them for processing and storage.

**3. Persistent Storage**

Events and processing information are stored in SQLite. Checkpoints and duplicate protection help maintain processing continuity.

**4. Performance Monitoring**

The monitoring component examines workflow activity and tracks pickup, engagement, and outcome metrics.

**5. Decision Evaluation**

The decision engine evaluates available performance evidence and considers whether configuration changes are supported by observed results.

**6. Audit and Traceability**

Relevant observations and decision activity are recorded to provide a history that can be inspected later.

---

## Performance Metrics

Formi evaluates workflow performance using three separate measurements.

| Metric | Calculation |
|---|---|
| **Pickup Rate** | Connected Dials / Total Dials |
| **Engagement Rate** | People Engaged to Conclusion / People Who Picked Up |
| **Outcome Rate** | Concluded Leads / Uploaded Leads |

These measurements provide different perspectives on workflow effectiveness.

For example, a workflow may have a reasonable pickup rate but a lower engagement rate. This indicates that successfully connecting with people and keeping them engaged are separate challenges.

Similarly, an improvement in engagement does not automatically prove an improvement in the overall outcome rate.

---

## Scenario Results

### Public 01 – Workflow Performance

This scenario focused on event processing, workflow performance measurement, and configuration evaluation.

**Execution Results**

| Measurement | Result |
|---|---:|
| Ticks Processed | 717 |
| Events Stored | 297,026 |
| Baseline Event Count | 297,024 |
| Overall Conclusion Rate | 0.379 |
| Conclusion Rate Change | +2.9% |
| Pickup Rate | 0.249 |
| Pickup Rate Change | +0.6% |
| Engagement Rate | 0.538 |
| Engagement Rate Change | +1.6% |
| Engagement Gap Captured | 3% |
| Credits Used | 13 |

**Configuration Observation**

One approved `nw_kyc` prompt version change was recorded. This change was associated with an engagement increase of **0.030**, equivalent to 3 percentage points.

The observed result provides evidence of an improvement in that workflow, but it does not establish that the same change will produce similar results across other workflows.

**Key Observations**

- Successfully processed and stored the scenario events.
- Measured pickup, engagement, and outcome performance separately.
- Recorded an approved prompt version change.
- Observed improvements against the reported baseline.

Detailed results: [`reports/public_01_dev.md`](reports/public_01_dev.md)

### Public 02 – Operational Monitoring

This scenario focused on monitoring operational activity and identifying unusual changes.

**Original Execution Results**

| Measurement | Result |
|---|---:|
| Ticks Processed | 960 |
| Events Stored | 137,032 |
| Audit Records | 1,921 |
| Performance Lift | None Recorded |
| Configuration Changes | None Recorded |

**Separate Detector Verification**

A separate verification run tested the operational monitoring capabilities.

| Measurement | Result |
|---|---:|
| Caller-ID Anomalies Identified | 2 |
| Supervisor Configuration Changes Identified | 2 |
| Audit Records | 1,925 |

The detector verification was separate from the original scenario execution. It demonstrated detection and observation, not automated remediation.

**Key Observations**

- Recorded operational activity.
- Identified two caller-ID anomalies during detector verification.
- Observed two supervisor configuration changes.
- Maintained audit records for traceability.

Detailed results: [`reports/public_02_incidents.md`](reports/public_02_incidents.md)

### Public 03 – Historical Load Processing

This scenario focused on processing a larger historical call dataset and generating workflow summaries.

**Execution Results**

| Measurement | Result |
|---|---:|
| Historical Call Events Loaded | 3,240,000 |
| Workflows in Scenario | 12 |
| Workflow Summaries Generated | 4 |
| Calls per Summary | 270,000 |
| Calls Represented in Summaries | 1,080,000 |

The system loaded 3.24 million historical call events and generated summaries for four workflows.

However, the connection timed out before all twelve workflows were validated.

**Key Observations**

- Exercised historical event loading at a larger data volume.
- Generated four workflow summaries.
- Did not establish successful completion across all twelve workflows.
- Full-scale throughput and end-to-end performance remain unverified.

Detailed results: [`reports/public_03_load.md`](reports/public_03_load.md)

---

## Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Application logic and workflow processing. |
| **SQLite** | Persistent storage for events, checkpoints, and audit records. |
| **HTTP API** | Communication with the workflow simulator. |
| **Bash** | Application startup and execution. |
| **Pytest** | Automated testing. |

---

## Installation and Setup

### Prerequisites

- Python 3.13 or a compatible version.
- Git.
- Bash-compatible terminal.
- Project dependencies and the included workflow simulator.

### 1. Clone the Repository

```bash
git clone https://github.com/nikithchowdaryachanta/formi-outcome-first-agent-loop.git

cd formi-outcome-first-agent-loop
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it in Windows Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Workflow Simulator

Run this command in the first terminal:

```bash
python -m sim serve \
  --scenario scenarios/public_01_dev.yaml \
  --run-dir runs/mine01
```

### 5. Start the Controller

Open a second terminal, activate the virtual environment, and execute:

```bash
./run.sh http://127.0.0.1:8700
```

The controller will connect to the simulator through the configured local endpoint.

---

## Testing

The project uses Pytest to validate implemented functionality.

Run the test suite:

```bash
python -m pytest -q tests
```

**Latest Verified Test Result**

```text
6 passed in 20.70s
```

All six tests passed in the latest recorded test run.

This confirms the tested code paths but does not establish full-scale performance or completion of every scenario.

---

## Implementation Status

| Capability | Status |
|---|---|
| HTTP Simulator Communication | Implemented |
| Event Ingestion | Implemented |
| SQLite Persistence | Implemented |
| Processing Checkpoints | Implemented |
| Duplicate Protection | Implemented |
| Workflow Performance Analysis | Implemented |
| Supervisor Configuration Change Observation | Implemented |
| Caller-ID Anomaly Detection | Partially Implemented |
| Governance-Aware Decision Handling | Partially Implemented |
| Shared-Cohort Experimentation | Not Completed |
| Generalized Performance Decay Detection | Not Completed |
| Automated Rollback | Not Completed |
| Automated Caller-ID Remediation | Not Completed |
| Full Supervisor Dashboard | Not Implemented |
| Complete Twelve-Workflow Load Validation | Not Completed |

## Limitations and Future Improvements

The current implementation provides a foundation for workflow monitoring, event processing, performance analysis, and evidence-based decision evaluation.

Further development could focus on:

1. **Advanced anomaly detection:** Expand detection coverage for caller-ID and other operational anomalies.
2. **Decision governance:** Introduce more complete evidence requirements before approving configuration changes.
3. **Performance decay detection:** Identify sustained decreases in workflow performance.
4. **Automated rollback:** Add controlled configuration rollback when required.
5. **Experimentation:** Implement shared-cohort experimentation and improved workflow variant comparisons.
6. **Operational dashboard:** Provide a centralized view of workflow health and configuration activity.
7. **Load validation:** Complete processing and performance validation across all twelve workflows.

---

## Project Documentation

Additional technical details and execution results:

- [Public 01 – Workflow Performance](reports/public_01_dev.md)
- [Public 02 – Operational Monitoring](reports/public_02_incidents.md)
- [Public 03 – Historical Load Processing](reports/public_03_load.md)
- [Additional Project Documentation](README_PROJECT.md)

---

## Summary

Formi brings together workflow event ingestion, persistent storage, performance monitoring, operational signal detection, and evidence-based decision evaluation.

The recorded results demonstrate event processing, metric tracking, operational monitoring, and audit recording across three scenarios. The documented limitations also identify areas requiring further development, including experimentation, automated remediation, rollback, and complete load validation.

**Built with Python, SQLite, HTTP APIs, Bash, and Pytest.**