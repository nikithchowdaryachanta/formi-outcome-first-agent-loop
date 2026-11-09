# Formi — Outcome-First Agent Loop

## Overview

A Python-based autonomous controller for the Formi simulator. It uses the simulator HTTP API, SQLite persistence, event checkpoints, audit records, performance monitoring and governance-aware configuration handling.

## Requirements

- Python 3.13
- Dependencies from `requirements.txt`
- Git Bash on Windows or Bash on Linux

## Setup

Create and activate the environment on Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the controller

Start the simulator in one terminal:

```bash
python -m sim serve --scenario scenarios/public_01_dev.yaml --run-dir runs/mine01 --force
```

In another terminal:

```bash
./run.sh http://127.0.0.1:8700
```

The controller communicates with the simulator through its HTTP API.

## Implemented capabilities

- Persistent SQLite event ingestion and checkpoints.
- Duplicate-safe event storage.
- Controller audit records.
- Caller-ID performance anomaly detection.
- Supervisor configuration-change observations.
- Approval-aware configuration handling.
- Separate pickup, engagement and outcome metrics.

## Reports

- `reports/public_01_dev.md`
- `reports/public_02_incidents.md`

Public_03 load measurements will be added after the active run is completed and verified.

## Tests

```bash
python -m pytest -q tests
python -m py_compile controller.py decision_engine.py performance_monitor.py
```

## Limitations

The shared cohort framework, complete experiment lifecycle, generalised decay rollback, supervisor dashboard, full credit allocation and abrupt-crash recovery demonstration remain incomplete or require further validation. See `SUBMISSION.md` for scope decisions and verified evidence.
