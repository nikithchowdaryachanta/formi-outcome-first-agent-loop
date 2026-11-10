# Outcome-First Agent Loop — Submission

**Name:** Nikith Achanta
**Date:** 9 November 2026
**Hours actually spent:** 30 hrs
**Language / storage:** Python 3.13 / SQLite

## 0. TL;DR

- Built a Python HTTP-API-based autonomous controller with SQLite event ingestion, checkpoints, audit records and governance-aware configuration handling.
- Public_01 achieved +2.9% overall conclusion-rate improvement and +1.6% engagement improvement against baseline.
- Public_02 exposed caller-ID and supervisor-edit incidents; additional detectors recorded two caller-ID anomalies and two supervisor changes.
- Demonstrated controlled controller stop and restart with zero duplicate event IDs and a valid SQLite database.
- Public_03 processed a captured analysis set of 3,240,000 historical call events, but ended with a connection timeout; the requested throughput target was not met.
- Prioritised reliability, auditability and governance; full cohort experimentation, decay rollback and a supervisor dashboard remain incomplete.

## Evidence and project navigation

- [Project guide and setup instructions](README_PROJECT.md)
- [Public_01 grade report](reports/public_01_dev.md)
- [Public_02 incident report and separate detector verification](reports/public_02_incidents.md)
- [Public_03 captured load-test output and limitations](reports/public_03_load.md)
- [Simulator API and scenario contract](docs/SIMULATOR.md)

## 1. Assumptions

1. The simulator HTTP API is the authoritative source of workflow state, events, configuration and approvals.
2. The controller must not inspect simulator run directories, import simulator internals or use scenario truth unavailable through the API.
3. Simulation advances in 15-minute intervals; cadence, dial windows and capacity belong to the business and are not controller optimisation variables.
4. Event IDs are stable identifiers and can be used for idempotent ingestion.
5. SQLite is sufficient for the local assessment environment, provided writes and checkpoints are durable.
6. Pickup and engagement are distinct measures and must not be combined into one KPI.
7. Workflow policies take precedence over stakeholder assumptions and sales requests.
8. The Public_03 performance measurements must be interpreted in the context of the actual local machine and not presented as a 4-vCPU/8-GB benchmark.

## 2. Scope decisions

| # | Capability | Built / Partial / Cut | Why | What it would take to finish |
|---|---|---|---|---|
| C1 | Event ingestion at load scale | Partial | Chunk ingestion, SQLite persistence, checkpointing and duplicate protection are implemented. Public_03 throughput remains a limitation. | Incremental processing, indexed queries, batching and measured load optimisation. |
| C2 | Shared cohort object | Cut | Workflow-level analysis was prioritised over a complete shared cohort model. | Implement one versioned cohort definition shared by detection, experiments and UI. |
| C3 | Historical bootstrapping | Partial | Historical call events are used for analysis. | Formal pre-D0 bootstrap and reproducible cohort snapshots. |
| C4 | Call-time optimisation | Cut | Changing business-owned cadence or dial windows was intentionally avoided. | Policy-approved per-cohort scheduling research, without changing prohibited constraints. |
| C5 | Caller-ID health | Partial | Population-level caller-ID degradation detection and audit observations are implemented. | Safe rotation, exploration, recovery verification and decay monitoring. |
| C6 | Welcome-message and voice experiments | Partial | Variant evidence and workflow metrics are analysed, but a complete multi-dimensional experiment framework is not implemented. | Randomised allocation, minimum samples, interaction analysis and multiple-comparison correction. |
| C7 | Winner promotion, decay and rollback | Partial | A validated, approved Public_01 change was applied. Generalised decay detection and rollback are incomplete. | Continuous variant monitoring and automatic rollback proposals. |
| C8 | Hallucination incident response | Partial | Public_01 included a validation and approved prompt-fix flow. | Generalised detection, LLM suggestion, validation, approval and post-change verification. |
| C9 | Governance client | Partial | Approval polling, audit records and supervisor-change observations are implemented. | Complete lifecycle handling, batching, expiry, lapse and stale-base re-proposal tests. |
| C10 | Impact scores and dry runs | Partial | Validation evidence exists for the demonstrated change. | Standardised impact calculation, affected-lead counts and reproducible dry runs. |
| C11 | Consolidated supervisor view | Cut | A full dashboard was outside the chosen implementation scope. | Build an API or minimal UI over proposals, experiments, approvals and audit history. |
| C12 | Queryable decision/audit store | Built | SQLite stores events, checkpoints, controller audit records and detection observations. | Add a user-facing audit query interface and retention policy. |
| C13 | Crash recovery | Partial | Controlled controller stop/restart, database integrity and duplicate-free ingestion were verified. | Repeat under multiple failure points and demonstrate completion of the entire scenario after recovery. |
| C14 | Observability | Partial | Tick output, event counts, checkpoints, audit records and credit information are available. | Add structured health metrics, ingest lag, decisions/hour, memory and alert thresholds. |
| C15 | Fair credit allocation | Cut | Multi-tenant credit scheduling was not implemented. | Add tenant budgets, priority policies and starvation protection. |

The guiding principle was to prioritise correctness at the event-ingestion and governance boundaries rather than produce superficial implementations of every requested capability. The most important remaining weakness is load performance: Public_03 exposed a substantial throughput limitation that needs engineering work.

## 3. Stakeholders

### 3.1 Sales — Nikhil Rao

**Accepted:**
- Clear outcome reporting and a simple explanation of measurable improvements.
- Faster experiments where evidence and policy permit them.

**Pushed back:**
- A single blended KPI would hide the distinction between pickup and engagement.
- Customer-facing changes cannot bypass required human approvals.
- A persuasive prompt cannot be deployed merely because it performed well in another account.

**Incorrect assumptions:**
- The claim that Kestrel permits unrestricted auto-apply conflicts with its request limits and operating restrictions.
- The claim that Northwind permits automatic KYC changes is inconsistent with the workflow policy.

**Reply (ready to send):**

We can demonstrate measurable improvements, but we will report pickup and engagement separately so that the result remains meaningful. Kestrel's approval limits and Northwind's customer-facing approval requirements remain in force. We will promote only validated changes through the permitted governance route. We can make the demonstration fast without compromising client policy or presenting an unsupported blended score.

### 3.2 Client Compliance — Meera Iyer

**Accepted:**
- Named human approval for customer-facing changes.
- Validation evidence attached to script-change proposals.
- Auditable workflow, variant and decision history.
- Respect for approver working hours and the preference for cautious changes.

**Pushed back:**
- No compliance requirement was rejected. The implementation is not yet a complete 24-hour customer-level audit product.

**Incorrect assumptions:**
- The memo's conditions are consistent with the stated governance boundary. No material policy contradiction was identified.

**Reply (ready to send):**

We agree that customer-facing changes require named approval and validation evidence. The controller records events and governance observations in its own persistent store, allowing decisions to be investigated independently of simulator logs. We will not treat model suggestions as approval or evidence of a winning variant. The current implementation provides the foundation for auditability; a complete customer-level audit interface and operational reporting remain production follow-up items.

### 3.3 Platform and SRE — Kabir Menon

**Accepted:**
- Persistent checkpoints and idempotent event ingestion.
- A controlled stop-and-restart test.
- Avoiding unnecessary stateful infrastructure.
- Making operational health observable.

**Pushed back / limitations:**
- SQLite was selected for the assessment rather than introducing another service.
- The requested target of one simulated day in under 10 wall-clock minutes was not achieved in the observed Public_03 run.
- Peak memory and a controlled 4-vCPU/8-GB benchmark were not measured.

**Incorrect assumptions:**
- The SRE memo's operational requirements were treated as requirements, not as claims that the implementation had already satisfied them.

**Reply (ready to send):**

The controller uses persistent SQLite checkpoints and an idempotent event ledger. We demonstrated controlled stop and restart without duplicate event IDs or database corruption. The current Public_03 run, however, does not meet the requested throughput target. We have identified historical event rescanning as a likely optimisation area. Before production, we would benchmark on the target hardware, add incremental aggregation and expose ingest lag, credit burn and decision latency.

### 3.4 Client Operations Supervisor — Anita Desai

**Accepted:**
- Supervisor edits must not be silently overwritten.
- Kestrel's limit of two requests per day and no requests before 11:00.
- Batch related changes where possible.
- Keep explanations actionable and avoid unnecessary alerts.

**Pushed back:**
- No attempt is made to optimise by changing business-owned dial cadence, windows or capacity.
- A change cannot be applied merely to reduce supervisor involvement.

**Incorrect assumptions:**
- The memo's anecdote about a previous vendor is not evidence that this controller has the same behaviour. It is treated as a safety concern, not as a simulator policy fact.

**Reply (ready to send):**

Your edits are treated as authoritative observations and are recorded rather than silently overwritten. We will respect the daily request limit and the 11:00 earliest request time. Related changes should be consolidated where the approval workflow supports it. Every proposed customer-facing change must include its reason and supporting validation evidence before it can be applied.

### 3.5 Product — Tara Kulkarni

**Accepted:**
- Pickup and engagement remain separate KPIs.
- Evidence must come from variants that actually ran.
- A winner must update only its own workflow.
- Cohort definitions and evaluation windows must be explicit.

**Pushed back / limitations:**
- A complete shared cohort object, consolidated supervisor surface, per-person call-time optimisation and full factorial welcome-message/voice experimentation were not completed.
- The current implementation does not claim a statistically complete solution for multiple comparisons or interaction effects.
- Expired-proposal re-queueing with fresh data requires additional lifecycle work.

**Incorrect assumptions:**
- No policy contradiction was identified in the core KPI definitions. The wishlist items are product requirements, not evidence that these capabilities already exist.

**Reply (ready to send):**

We preserve pickup and engagement as separate measures and use recorded events rather than treating unexecuted experiment arms as evidence. The current implementation focuses on workflow-level analysis, governance and auditability. A shared cohort object and complete multi-dimensional experimentation framework remain important next steps. We will not promote a result across workflows simply because it performed well in another workflow.

### 3.6 CTO — Aryamann

**Accepted:**
- Explainability and governance are more important than unsupported headline lift.
- Credit usage should be justified by decisions.
- Scope must be explicit.
- Production documentation must be usable by another engineer.

**Pushed back:**
- The current implementation does not claim to solve all 15 capabilities.
- Public_03 performance remains below the stated operational target and must be improved before production.

**Incorrect assumptions:**
- The CTO's instruction to trust the simulator contract is consistent with the implementation approach. No contrary policy claim was identified.

**Reply (ready to send):**

The implementation prioritises persistent ingestion, auditability, governance boundaries and recovery. Public_01 demonstrated a modest positive result, while Public_02 demonstrated the need to distinguish detection from actual performance improvement. Public_03 exposed a throughput weakness that should be addressed before production. I deliberately cut broad features that could not be completed and validated to the same standard.

## 4. Architecture

```text
              Simulator HTTP API
                      |
                      v
             Autonomous Controller
                      |
          +-----------+-----------+
          |                       |
          v                       v
     Advance simulation      Read event chunks
          |                       |
          +-----------+-----------+
                      |
                      v
               SQLite Store
          +-----------+-----------+
          |           |           |
          v           v           v
        events    checkpoints   controller_audit
          |           |
          |      last_events_chunk
          |
          +----------------------+
                      |
                      v
            Performance Monitoring
             /                 \
            v                   v
    Caller-ID anomaly      Supervisor-change
       detection             observation
            \                   /
             +--------+--------+
                      |
                      v
             Decision / Governance
                      |
             Approval or permitted
                 auto-apply
                      |
                      v
             Simulator configuration
                      |
                      v
                Reports / Audit

## 5. Implementation and verified results

### 5.1 Public_01 — baseline comparison

The Public_01 controller run completed 717 ticks and stored 297,026 events. The baseline contained 297,024 events.

| Workflow | Conclusion rate | Change vs baseline | Pickup | Change vs baseline | Engagement | Change vs baseline |
|---|---:|---:|---:|---:|---:|---:|
| ks_cancel | 0.350 | +5.2% | 0.243 | +2.0% | 0.498 | +1.4% |
| nw_kyc | 0.372 | +2.2% | 0.236 | -2.5% | 0.620 | +5.0% |
| nw_renewal | 0.424 | +0.9% | 0.265 | +0.4% | 0.547 | +0.3% |
| ALL | 0.379 | +2.9% | 0.249 | +0.6% | 0.538 | +1.6% |

One configuration change was validated and applied through approval: nw_kyc version 2. The change improved engagement by 0.030 in the recorded evaluation. It was not automatically applied.

The overall engagement gap captured was 3%. Therefore, the result should be described as a modest measured improvement, not as a complete optimisation of all underperforming cohorts.

Governance observations:
- One approval request was created and approved.
- One change was applied through the approval route.
- No automatic changes were applied.
- No apply conflicts or lapsed approvals were recorded.
- The run reported no incidents.

Credits used: 13. One validation run and one LLM fix call were recorded.

Detailed report: `reports/public_01_dev.md`.

### 5.2 Public_02 — incident detection

The fresh Public_02 run completed 960 ticks and stored 137,032 events. It produced 1,925 controller audit records.

The performance report showed no measured change against baseline:

| Workflow | Conclusion rate | Pickup | Engagement |
|---|---:|---:|---:|
| ks_cancel | 0.248 | 0.184 | 0.476 |
| nw_kyc | 0.375 | 0.242 | 0.592 |
| nw_renewal | 0.427 | 0.262 | 0.548 |
| ALL | 0.334 | 0.222 | 0.530 |

The controller detected and recorded two caller-ID performance anomalies for ks_cancel:
- 7 January 2027: baseline pickup 19.89%, observed pickup 9.47%, relative decline 52.41%.
- 8 January 2027: baseline pickup 14.77%, observed pickup 7.78%, relative decline 47.32%.

The controller also recorded two supervisor configuration changes:
- ks_cancel, version 2, prompt_version changed.
- nw_renewal, version 2, voice changed.

Duplicate observations are prevented using stable event identifiers and database uniqueness constraints. Reprocessing the same observations does not create duplicate audit entries.

No configuration changes were applied in this Public_02 run. Detection and recording of an incident should not be confused with automatically resolving it.

Detailed report: `reports/public_02_incidents.md`.

## 6. Persistence and recovery evidence

The controller stores ingested events in SQLite and maintains a `last_events_chunk` checkpoint. Event ingestion uses stable event IDs and duplicate-safe insertion.

A controlled stop-and-restart test was performed against the same simulator and database:
- After the first controller execution, the database contained 0 events because the simulator had not yet emitted an event chunk.
- A subsequent execution advanced the simulator and ingested 13,703 events.
- A further restart ingested additional events and brought the total to 17,006.
- The final database contained 17,006 distinct event IDs, with zero duplicate IDs.
- The checkpoint had advanced to chunk 50.
- The audit table contained 263 records.

This verifies persistence and continuation across controller executions. It is a controlled restart test; it does not, by itself, prove recovery from an abrupt process kill or machine failure. A separate forced-termination test must be completed and documented before claiming that level of crash recovery.

## 7. Automated tests and code checks

The following checks were run during implementation:

- `python -m pytest -q tests` — 6 tests passed.
- `python -m py_compile controller.py decision_engine.py performance_monitor.py` — completed successfully.
- `git diff --check` — no whitespace errors reported.

The caller-ID detector was also checked for duplicate suppression: the first detection created one alert, while a repeated run created no additional alert. An incomplete current day was excluded from detection.

## 8. Public_03 load test

Public_03 was executed and reported scenario completion. The final decision analysis loaded 3,240,000 historical call events.

The captured final output displayed the following four workflow summaries, each with 270,000 calls:

| Workflow | Calls | Pickup rate | Engagement rate | Outcome rate | Hallucinations |
|---|---:|---:|---:|---:|---:|
| nort_renewal_0 | 270,000 | 26.34% | 54.77% | 14.43% | 1,033 |
| nort_kyc_1 | 270,000 | 21.32% | 59.53% | 12.69% | 840 |
| nort_cancel_2 | 270,000 | 24.25% | 49.88% | 12.10% | 939 |
| kest_renewal_0 | 270,000 | 26.35% | 54.23% | 14.29% | 1,068 |

All four displayed workflows remained on configuration version 1. Only P1 prompt evidence was displayed. No winner was selected and no configuration was modified.

**Execution limitation:** The terminal reported `CONNECTION ERROR: timed out` after the final decision analysis. The captured output does not establish complete results for all workflows or a verified wall-clock throughput benchmark. The requested target of one simulated day in under 10 wall-clock minutes was not achieved. Public_03 therefore demonstrates substantial event-analysis workload but also exposes a throughput and connection-stability limitation that requires further optimisation.

Detailed captured results are documented in `reports/public_03_load.md`.