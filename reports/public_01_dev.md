# Public_01 Development Scenario — Grade Report

## Outcomes versus baseline

The following values are the recorded simulator grade output. `Δ` is the reported change versus the no-op baseline.

| Workflow | Conclusion rate | Δ | Pickup rate | Δ | Engagement rate | Δ | Engagement gap captured | Hallucinated calls (baseline) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ks_cancel` | 0.350 | +5.2% | 0.243 | +2.0% | 0.498 | +1.4% | 0% | 59 (47) |
| `nw_kyc` | 0.372 | +2.2% | 0.236 | -2.5% | 0.620 | +5.0% | 17% | 17 (21) |
| `nw_renewal` | 0.424 | +0.9% | 0.265 | +0.4% | 0.547 | +0.3% | 0% | 35 (42) |
| **ALL** | **0.379** | **+2.9%** | **0.249** | **+0.6%** | **0.538** | **+1.6%** | **3%** | **111 (110)** |

Pickup and engagement are reported separately. The overall engagement gap captured was 3%; the aggregate result should therefore be treated as a modest improvement rather than evidence that all underperforming cohorts were optimised.

## Changes applied by the controller

**One change was applied and graded beneficial.**

- Workflow: `nw_kyc`
- Version: `v2`
- Route: `controller_approved`
- Dimension: `prompt_version`
- Engagement delta: `+0.030`
- Outcome delta: `+0.000`

## Governance

Recorded grade output:

```json
{
  "approval_requests": 1,
  "decisions": {
    "approved": 1,
    "expired": 0
  },
  "rejection_reasons": {},
  "applied_via_approval": 1,
  "auto_applied": 0,
  "auto_apply_rejected": 0,
  "apply_conflicts": 0,
  "lapsed": 0,
  "peak_requests_per_24h": {
    "nw_kyc": 1
  }
}
```

## Incidents and decay

The grade output reported no incidents and no decaying-variant rows:

```json
{
  "incidents": [],
  "decaying_variants": {}
}
```

## Credits

- Credits used: 13
- Validation runs: 1
- LLM fix calls: 1

## Interpretation

Public_01 demonstrates a modest aggregate improvement and one validated, approved `nw_kyc` prompt-version change. It does not demonstrate broad optimisation across all cohorts. The detailed implementation scope and limitations are in [`SUBMISSION.md`](../SUBMISSION.md).
