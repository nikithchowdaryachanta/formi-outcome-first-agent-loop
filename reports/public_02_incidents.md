# Public_02 Incidents Scenario — Grade Report

## Outcomes versus baseline

The following values are the recorded simulator grade output. `Δ` is the reported change versus the no-op baseline.

| Workflow | Conclusion rate | Δ | Pickup rate | Δ | Engagement rate | Δ | Engagement gap captured | Hallucinated calls (baseline) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ks_cancel` | 0.248 | +0.0% | 0.184 | +0.0% | 0.476 | +0.0% | 0% | 330 (330) |
| `nw_kyc` | 0.375 | +0.0% | 0.242 | +0.0% | 0.592 | +0.0% | 0% | 31 (31) |
| `nw_renewal` | 0.427 | +0.0% | 0.262 | +0.0% | 0.548 | +0.0% | 5% | 55 (55) |
| **ALL** | **0.334** | **+0.0%** | **0.222** | **+0.0%** | **0.530** | **+0.0%** | **3%** | **416 (416)** |

The original Public_02 grade run showed no measured lift versus baseline.

## Changes and governance in the grade run

No configuration changes were applied in this grade run.

```json
{
  "approval_requests": 0,
  "decisions": {
    "expired": 0
  },
  "rejection_reasons": {},
  "applied_via_approval": 0,
  "auto_applied": 0,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {}
}
```

## Scenario incidents reported by the simulator grade output

### Caller-ID flag

- Type: `did_flagged`
- Workflow: `ks_cancel`
- Time: D2 10:00
- Flagged DID share by day: D2 50.9%, D3 50.2%, D4 49.0%, D5 50.4%, D6 49.2%, D7 50.2%, D8 49.9%, D9 49.6%.

### Supervisor edits

- `ks_cancel` — D3 11:30; the grade output did not provide an MTTR or `fixed_by` value.
- `nw_renewal` — D5 15:00.

The grade report's incident list describes simulator incidents; it does not by itself prove that the controller detected or resolved them.

## Separate detector verification run

A separate fresh Public_02 v2 controller run was used to verify the added detection and audit observations. This evidence is distinct from the original grade comparison above:

- Two caller-ID performance anomalies were recorded for `ks_cancel`:
  - 7 January 2027: baseline pickup 19.89%, observed pickup 9.47%, relative decline 52.41%.
  - 8 January 2027: baseline pickup 14.77%, observed pickup 7.78%, relative decline 47.32%.
- Two supervisor configuration changes were recorded:
  - `ks_cancel`, version 2, `prompt_version` changed.
  - `nw_renewal`, version 2, `voice` changed.
- The detector tables and audit records used stable event identifiers to suppress duplicate observations.

Detection and audit recording are not the same as incident remediation. The Public_02 run did not apply a configuration change or demonstrate that the flagged caller ID was rotated.

## Credits

- Credits used: 0
- Validation runs: 0
- LLM fix calls: 0

## Interpretation

Public_02 demonstrates the difference between identifying and recording incidents and actually resolving them. The baseline comparison showed no lift, and the separate detector verification established anomaly and supervisor-change observations without claiming automatic remediation. See [`SUBMISSION.md`](../SUBMISSION.md) for the complete scope and recovery caveats.
