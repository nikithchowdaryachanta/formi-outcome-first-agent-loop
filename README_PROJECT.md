# Formi — Outcome-First Agent Loop

A Python controller for the Formi outbound voice-agent simulator. The project focuses on durable event ingestion, auditable decisions, performance monitoring, and governance-aware configuration handling.

> **Assessment status:** Public_01 and Public_02 results are documented. Public_03 completed its captured decision-analysis stage over 3,240,000 historical call events, but the run ended with a connection timeout and did not establish the requested throughput target. See the reports and `SUBMISSION.md` for the evidence and limitations.

## Contents

- [Architecture](#architecture)
- [Implemented capabilities](#implemented-capabilities)
- [Requirements](#requirements)
- [Setup](#setup)
- [Run a scenario](#run-a-scenario)
- [Tests and code checks](#tests-and-code-checks)
- [Reports and evidence](#reports-and-evidence)
- [Known limitations](#known-limitations)
- [Repository layout](#repository-layout)

## Architecture

The controller communicates with the simulator through its HTTP API. It does not need to read simulator run directories or import simulator internals.

```text
Formi simulator HTTP API
          |
          v
   controller.py
     |       |
     |       +---- Approval and governance handling
     |
     +------------ Event chunk ingestion
                         |
                         v
                    SQLite store
               events / checkpoints /
                 controller audit
                         |
             +-----------+-----------+
             |                       |
             v                       v
     performance_monitor.py     decision_engine.py
     caller-ID anomalies        decision evaluation
     supervisor observations    approval-aware changes
             |                       |
             +-----------+-----------+
                         |
                         v
                Reports and audit trail
```

## Implemented capabilities

- HTTP-API-driven simulation control.
- SQLite-backed event persistence and chunk checkpoints.
- Duplicate-safe event ingestion using stable event identifiers.
- Controller audit records for important actions.
- Population-level caller-ID performance anomaly detection.
- Supervisor configuration-change observations.
- Approval-aware configuration handling and policy-permitted automatic-change boundaries.
- Separate pickup, engagement, and outcome metrics.

These capabilities are not a claim that the full assignment scope is complete. The scope and evidence for each capability are documented in `SUBMISSION.md`.

## Requirements

- Python 3.13 (the implementation was developed and checked with this version).
- Git and Bash. On Windows, Git Bash is suitable.
- Dependencies listed in `requirements.txt`.

## Setup

### Windows (Git Bash)

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run a scenario

Open two terminals in the repository root. Activate `.venv` in each terminal.

### Terminal 1 — start the simulator

Public_01 development scenario:

```bash
python -m sim serve --scenario scenarios/public_01_dev.yaml --run-dir runs/mine01 --force
```

The simulator exposes its API at `http://127.0.0.1:8700`.

### Terminal 2 — start the controller

```bash
./run.sh http://127.0.0.1:8700
```

The controller runs until the scenario finishes. `run.sh` is a Bash script, so use Git Bash on Windows or Bash on Linux.

### Baseline and grading

For a baseline run, start a separate simulator run:

```bash
python -m sim baseline --scenario scenarios/public_01_dev.yaml --run-dir runs/base01
```

After the controller run has finished, generate the grade report:

```bash
python -m sim grade --run runs/mine01 --baseline runs/base01 --out reports/public_01_dev.md
```

For other scenarios, substitute the matching scenario file and use distinct run directories. See `docs/SIMULATOR.md` for the simulator API and operating contract.

## Tests and code checks

Run the automated tests:

```bash
python -m pytest -q tests
```

Run Python syntax checks:

```bash
python -m py_compile controller.py decision_engine.py performance_monitor.py
```

The recorded test result in the submission is **6 tests passed**. Re-run the commands above when changing the code; documentation-only changes do not constitute a new test run.

## Reports and evidence

| File | Contents |
|---|---|
| [`reports/public_01_dev.md`](reports/public_01_dev.md) | Public_01 grade output, baseline comparison, and approval/governance results |
| [`reports/public_02_incidents.md`](reports/public_02_incidents.md) | Public_02 grade output and incident context; separate detector verification is described in `SUBMISSION.md` |
| [`reports/public_03_load.md`](reports/public_03_load.md) | Captured Public_03 decision-analysis output and execution limitations |
| [`SUBMISSION.md`](SUBMISSION.md) | Assignment response, stakeholder decisions, architecture, verified evidence, and scope limitations |
| [`docs/SIMULATOR.md`](docs/SIMULATOR.md) | Simulator API and scenario contract |

### Public_03 interpretation

The captured terminal output reported 3,240,000 historical call events and displayed four workflow summaries. It then reported `CONNECTION ERROR: timed out`. The available evidence does not establish a complete 12-workflow result, a reliable wall-clock throughput benchmark, or achievement of the target of one simulated day in under 10 minutes. Do not interpret the captured output as proof that the load target was met.

## Known limitations

- Public_03 throughput and connection stability require optimisation and a repeatable benchmark.
- A complete shared cohort framework and full multi-dimensional experiment lifecycle are not implemented.
- Generalised decay detection and rollback remain incomplete.
- A consolidated supervisor dashboard and fair multi-tenant credit allocation are not implemented.
- Recovery was demonstrated through controlled controller stop/restart. Abrupt process-kill or machine-failure recovery has not been verified.
- The current evidence does not establish production readiness or completion of all 15 assignment capabilities.

See `SUBMISSION.md` for the detailed capability-by-capability scope assessment and stakeholder responses.

## Repository layout

```text
.
├── controller.py
├── decision_engine.py
├── event_ingest.py
├── performance_monitor.py
├── run.sh
├── requirements.txt
├── README.md                 # Original assignment brief; retained
├── README_PROJECT.md         # Project guide
├── SUBMISSION.md
├── docs/
├── examples/
├── reports/
├── scenarios/
├── sim/
├── stakeholders/
└── tests/
```
