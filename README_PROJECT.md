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
```

On Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

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
