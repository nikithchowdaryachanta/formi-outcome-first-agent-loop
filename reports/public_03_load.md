\# Public\_03 Load Test Report



\## Execution status



The Public\_03 scenario reported completion. The final decision analysis loaded \*\*3,240,000 historical call events\*\*.



A connection timeout occurred after the decision analysis output. Therefore, the scenario's final analysis output was produced, but a completely error-free execution is not claimed.



\## Workflow results



The following four workflow summaries were visible in the final output. Each reported 270,000 calls.



| Workflow | Calls | Pickup rate | Engagement rate | Outcome rate | Hallucinations |

|---|---:|---:|---:|---:|---:|

| nort\_renewal\_0 | 270,000 | 26.34% | 54.77% | 14.43% | 1,033 |

| nort\_kyc\_1 | 270,000 | 21.32% | 59.53% | 12.69% | 840 |

| nort\_cancel\_2 | 270,000 | 24.25% | 49.88% | 12.10% | 939 |

| kest\_renewal\_0 | 270,000 | 26.35% | 54.23% | 14.29% | 1,068 |



\## Decision and governance observations



\- All four displayed workflows were on configuration version 1.

\- Only prompt version P1 was observed in the displayed evidence.

\- No winner was selected for any of the four displayed workflows.

\- No configuration was modified.

\- Automatic changes were enabled for three displayed workflows and disabled for nort\_kyc\_1.

\- Automatic changes were restricted to the permitted dimensions shown by the decision engine.



\## Limitations



\- The final output ended with `CONNECTION ERROR: timed out`.

\- The output provided does not establish a complete wall-clock performance benchmark.

\- Baseline comparisons and a complete all-workflow summary were not available in the captured output.

\- These results should be treated as the observed final decision analysis, not as proof that every end-to-end operation completed without errors.



