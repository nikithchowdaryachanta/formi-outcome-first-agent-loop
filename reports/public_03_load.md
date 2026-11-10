# Public_03 Load Test Report

## Execution status

The Public_03 scenario reported completion in the terminal. The final decision-analysis output stated that it loaded **3,240,000 historical call events**.

After the displayed analysis, the terminal reported:

```text
CONNECTION ERROR: timed out
```

Accordingly, this report records the captured analysis output and does not claim an error-free end-to-end run.

## Captured workflow results

The terminal output displayed the following four workflow summaries. Each displayed workflow reported 270,000 calls.

| Workflow | Calls | Pickup rate | Engagement rate | Outcome rate | Hallucinations |
|---|---:|---:|---:|---:|---:|
| `nort_renewal_0` | 270,000 | 26.34% | 54.77% | 14.43% | 1,033 |
| `nort_kyc_1` | 270,000 | 21.32% | 59.53% | 12.69% | 840 |
| `nort_cancel_2` | 270,000 | 24.25% | 49.88% | 12.10% | 939 |
| `kest_renewal_0` | 270,000 | 26.35% | 54.23% | 14.29% | 1,068 |

These are the four summaries visible in the captured terminal output. They are not presented as a complete summary of all 12 scenario workflows.

## Decision and governance observations

For the four displayed workflows:

- Current configuration version was 1.
- Only prompt version P1 was shown in the prompt-version evidence.
- No winner was selected.
- No configuration was modified.
- Automatic changes were enabled for `nort_renewal_0`, `nort_cancel_2`, and `kest_renewal_0`.
- Automatic changes were disabled for `nort_kyc_1`.
- The permitted automatic-change dimensions varied by workflow and were reported by the decision engine.

## Limitations and interpretation

- The terminal reported a connection timeout after the displayed decision analysis.
- The captured output does not provide a complete result for all 12 workflows.
- No baseline comparison is included in the captured output.
- No verified wall-clock throughput, memory, or CPU benchmark is available.
- The requested target of one simulated day in under 10 wall-clock minutes was not achieved, as recorded in `SUBMISSION.md`.

The results demonstrate that the decision-analysis stage processed a substantial historical event set, but they also expose throughput and connection-stability limitations. Further optimisation and a repeatable benchmark on the target hardware are required before claiming the load objective is met.

See [`SUBMISSION.md`](../SUBMISSION.md) for the overall assessment and scope decisions.
