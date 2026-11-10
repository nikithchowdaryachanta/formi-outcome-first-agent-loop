# Formi — Outcome-First Agent Loop

A Python-based controller for the Formi outbound voice-agent simulator, built around durable event ingestion, auditable decisions, performance monitoring, and governance-aware configuration handling.

**Assessment status:** Public_01 and Public_02 evidence is documented. The captured Public_03 analysis loaded 3,240,000 historical call events but ended with a connection timeout. The requested throughput target was not achieved. See the reports for measured results and limitations.

## What is implemented

- Simulator control through the HTTP API.
- SQLite event persistence with chunk checkpoints and duplicate-safe ingestion.
- Controller audit records.
- Population-level caller-ID anomaly detection.
- Supervisor configuration-change observations.
- Approval-aware configuration handling.
- Separate pickup, engagement, and outcome metrics.

## Quick start

Requires Python 3.13, Git, and Bash. On Windows, use Git Bash.

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
# Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Start the simulator in one terminal:

```bash
python -m sim serve --scenario scenarios/public_01_dev.yaml --run-dir runs/mine01 --force
```

Start the controller in a second terminal:

```bash
./run.sh http://127.0.0.1:8700
```

See [`README_PROJECT.md`](README_PROJECT.md) for full setup, baseline, grading, test, architecture, and troubleshooting instructions.

## Results and evidence

| Scenario | Evidence |
|---|---|
| Public_01 | [Grade report](reports/public_01_dev.md) |
| Public_02 | [Incident report and detector verification](reports/public_02_incidents.md) |
| Public_03 | [Captured load-test output and limitations](reports/public_03_load.md) |

The complete engineering submission, stakeholder responses, scope decisions, and recovery evidence are in [`SUBMISSION.md`](SUBMISSION.md).

## Important limitations

This is an assessment implementation, not a production-ready platform. Public_03 throughput remains below the requested target. Full cohort experimentation, generalised decay rollback, a supervisor dashboard, fair multi-tenant credit allocation, and abrupt process-kill recovery remain incomplete or unverified. The reports and submission document distinguish implemented behaviour from follow-up work.

## Repository guide

- [`README_PROJECT.md`](README_PROJECT.md) — detailed project and operating guide
- [`SUBMISSION.md`](SUBMISSION.md) — assessment submission and evidence
- [`docs/SIMULATOR.md`](docs/SIMULATOR.md) — simulator API contract
- `controller.py`, `decision_engine.py`, `performance_monitor.py` — main implementation
- `tests/` — automated tests
