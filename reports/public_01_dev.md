# Grade report — public_01_dev

## Outcomes vs baseline (no-op controller)

| workflow | conclusion rate | Δ | pickup | Δ | engagement | Δ | engagement gap captured | hallucinated calls (base) |
|---|---|---|---|---|---|---|---|---|
| ks_cancel | 0.350 | +5.2% | 0.243 | +2.0% | 0.498 | +1.4% | 0% | 59 (47) |
| nw_kyc | 0.372 | +2.2% | 0.236 | -2.5% | 0.620 | +5.0% | 17% | 17 (21) |
| nw_renewal | 0.424 | +0.9% | 0.265 | +0.4% | 0.547 | +0.3% | 0% | 35 (42) |
| ALL | 0.379 | +2.9% | 0.249 | +0.6% | 0.538 | +1.6% | 3% | 111 (110) |

## Changes applied by the controller

1 applied — beneficial: 1

- nw_kyc v2 (controller_approved) dims=['prompt_version'] engageΔ=+0.030 didΔ=+0.000 → **beneficial**

## Governance

```
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

## Incidents

```
[]
```

## Decaying variants — share of in-population calls still on the variant, by day after onset

```
{}
```

Credits used: 13 · validation runs: 1 · LLM fix calls: 1