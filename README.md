\# Formi – Outcome-First Agent Loop



An autonomous workflow monitoring and decision system built with Python and SQLite. Formi collects workflow events, monitors operational performance, identifies anomalies, evaluates configuration changes, and maintains an auditable record of system activity.



The system is designed around an outcome-first approach: decisions should be based on measurable workflow performance rather than isolated activity or assumptions.



\---



\## 1. Project Overview



Formi provides a structured way to observe and analyze automated workflows.



Instead of looking only at the number of calls or events processed, it separates performance into three important metrics:



\- \*\*Pickup Rate:\*\* Measures how many dial attempts successfully connect.

\- \*\*Engagement Rate:\*\* Measures how many connected people remain engaged until the interaction reaches its conclusion.

\- \*\*Outcome Rate:\*\* Measures how many uploaded leads reach a concluded outcome.



These metrics help distinguish between connection problems, engagement problems, and overall workflow performance.



The system collects operational data, stores it for analysis, monitors changes, and evaluates whether a configuration adjustment is supported by measurable evidence.



\## 2. System Architecture



The application is organized into separate components, with each component responsible for a specific part of the workflow.



```text

&#x20;            Workflow Simulator

&#x20;                    |

&#x20;                    | HTTP API

&#x20;                    v

&#x20;              Controller

&#x20;                    |

&#x20;                    v

&#x20;              Event Ingestion

&#x20;                    |

&#x20;                    v

&#x20;               SQLite DB

&#x20;                    |

&#x20;         +----------+----------+

&#x20;         |                     |

&#x20;         v                     v

&#x20;  Performance Monitor    Decision Engine

&#x20;         |                     |

&#x20;         v                     v

&#x20;  Operational Signals   Configuration Analysis

&#x20;         |                     |

&#x20;         +----------+----------+

&#x20;                    |

&#x20;                    v

&#x20;             Audit Records

```



\### Component responsibilities



| Component | Responsibility |

|---|---|

| `controller.py` | Acts as the main entry point and coordinates simulator communication and workflow execution. |

| `event\_ingest.py` | Retrieves simulator events, processes incoming data, and stores events in the database. |

| `decision\_engine.py` | Evaluates workflow performance and considers configuration decisions using available evidence. |

| `performance\_monitor.py` | Monitors workflow metrics and identifies operational signals such as caller-ID anomalies and supervisor configuration changes. |

| SQLite database | Maintains event data, processing checkpoints, and audit records. |

| `run.sh` | Provides a convenient way to start the controller. |



This separation makes the application easier to maintain, test, and extend.



\## 3. End-to-End Workflow



The system follows a sequence of connected processing stages.



\### Step 1: Connect to the simulator



The controller communicates with the workflow simulator through its HTTP API.



It uses the simulator endpoint to retrieve workflow-related information and coordinate processing.



\### Step 2: Collect workflow events



The event ingestion component retrieves events and prepares them for storage.



Events are processed incrementally so the system can continue from previously recorded progress.



\### Step 3: Persist data



SQLite is used to store incoming events and related processing information.



The persistence layer supports:



\- Event storage.

\- Processing checkpoints.

\- Duplicate protection.

\- Audit record storage.



This allows the application to maintain a record of previously processed data.



\### Step 4: Monitor performance



The performance monitoring component examines operational information and workflow activity.



It focuses on identifying changes in important performance indicators and operational signals.



\### Step 5: Analyze outcomes



The decision engine evaluates available performance evidence.



It considers whether observed changes indicate a potential improvement or whether additional evidence is needed before a configuration decision is made.



\### Step 6: Maintain traceability



Relevant observations and decision activity are recorded for later inspection.



This makes it possible to understand what the system observed and which actions or changes were recorded.



\---



\## 4. Performance Metrics



Formi separates workflow performance into three metrics.



| Metric | Meaning | Calculation |

|---|---|---|

| Pickup Rate | Percentage of dial attempts that connect | Connected dials / Total dials |

| Engagement Rate | Percentage of connected people who stay until the interaction concludes | People engaged to conclusion / People who picked up |

| Outcome Rate | Percentage of uploaded leads that reach a concluded outcome | Concluded leads / Uploaded leads |



These metrics should be interpreted separately.



For example, a workflow can have a reasonable pickup rate but a lower engagement rate. This indicates that connecting with people and keeping them engaged are different problems.



Similarly, an improvement in engagement does not automatically establish an improvement in the overall outcome rate.



\---



\## 5. Scenario Results



\### Public 01 – Workflow Performance



<details>

</details>



The first scenario focused on workflow performance, event processing, and configuration evaluation.



\*\*Recorded results:\*\*



| Measurement | Result |

|---|---:|

| Ticks processed | 717 |

| Events stored | 297,026 |

| Baseline event count | 297,024 |

| Overall conclusion rate | 0.379 |

| Conclusion rate change | +2.9% |

| Pickup rate | 0.249 |

| Pickup rate change | +0.6% |

| Engagement rate | 0.538 |

| Engagement rate change | +1.6% |

| Engagement gap captured | 3% |

| Credits used | 13 |



\*\*Configuration observation\*\*



One approved `nw\_kyc` prompt version change was recorded. The change was associated with an engagement increase of 0.030, equivalent to 3 percentage points.



The result provides evidence of an observed improvement in that workflow. It should not be interpreted as proof that the same change will improve every workflow.



\*\*Key takeaways\*\*



\- The system successfully processed and stored the scenario events.

\- Workflow performance was measured using separate metrics.

\- An approved prompt version change was recorded.

\- The observed results showed improvements over the reported baseline.



Detailed results: \[`reports/public\_01\_dev.md`](reports/public\_01\_dev.md)



\### Public 02 – Operational Monitoring



The second scenario focused on operational monitoring and the identification of unusual activity.



\*\*Original scenario results:\*\*



| Measurement | Result |

|---|---:|

| Ticks processed | 960 |

| Events stored | 137,032 |

| Audit records | 1,921 |

| Performance lift | None recorded |

| Configuration changes | None recorded |



\*\*Separate detector verification\*\*



A separate verification run tested the monitoring capabilities.



| Measurement | Result |

|---|---:|

| Caller-ID anomalies identified | 2 |

| Supervisor configuration changes identified | 2 |

| Audit records | 1,925 |



The detector verification is separate from the original scenario run. The results demonstrate detection and observation, not automated remediation.



\*\*Key takeaways\*\*



\- The system recorded operational activity.

\- Caller-ID anomalies were identified during detector verification.

\- Supervisor configuration changes were observed.

\- Audit records provided traceability for the detected activity.



Detailed results: \[`reports/public\_02\_incidents.md`](reports/public\_02\_incidents.md)



\### Public 03 – Historical Load Processing



The third scenario focused on processing a larger historical dataset.



\*\*Recorded results:\*\*



| Measurement | Result |

|---|---:|

| Historical call events loaded | 3,240,000 |

| Workflows in scenario | 12 |

| Workflow summaries generated | 4 |

| Calls reported per summary | 270,000 |

| Total calls represented in summaries | 1,080,000 |



The process loaded 3.24 million historical call events and generated summaries for four workflows.



However, the connection timed out before all twelve workflows were validated.



\*\*Key takeaways\*\*



\- Large-scale historical event loading was exercised.

\- Four workflow summaries were generated.

\- The run did not establish successful completion across all twelve workflows.

\- Full-scale throughput and end-to-end performance remain unverified.



Detailed results: \[`reports/public\_03\_load.md`](reports/public\_03\_load.md)



\---



\## 6. Technology Stack



| Technology | Usage |

|---|---|

| Python | Application logic and workflow processing |

| SQLite | Event persistence, checkpoints, and audit records |

| HTTP API | Communication with the simulator |

| Bash | Application startup and execution |

| Pytest | Automated testing |



The application uses a lightweight local database and modular Python components to keep the system straightforward to run and maintain.



\---



\## 7. Installation and Setup



\### Prerequisites



\- Python 3.13 or compatible Python version.

\- Git.

\- Bash-compatible terminal.

\- Required project dependencies.

\- Workflow simulator included in the project environment.



\### Step 1: Clone the repository



```bash

git clone https://github.com/nikithchowdaryachanta/formi-outcome-first-agent-loop.git

cd formi-outcome-first-agent-loop

```



\### Step 2: Create a virtual environment



```bash

python -m venv .venv

```



Activate it in Git Bash on Windows:



```bash

source .venv/Scripts/activate

```



\### Step 3: Install dependencies



```bash

pip install -r requirements.txt

```



\### Step 4: Start the simulator



Run the simulator in the first terminal:



```bash

python -m sim serve \\

&#x20; --scenario scenarios/public\_01\_dev.yaml \\

&#x20; --run-dir runs/mine01

```



\### Step 5: Start the controller



Open a second terminal, activate the virtual environment, and execute:



```bash

./run.sh http://127.0.0.1:8700

```



The controller will connect to the simulator using the configured local endpoint.



\---



\## 8. Running Tests



The project uses Pytest for automated testing.



Run the test suite:



```bash

python -m pytest -q tests

```



\*\*Latest verified result:\*\*



```text

......                                                                   \[100%]

6 passed in 20.70s

```



All six tests passed in the latest recorded test run.



The test result verifies the tested code paths; it does not establish full-scale performance or completion of every scenario.



\---



\## 9. Current Implementation Status



| Capability | Status |

|---|---|

| HTTP simulator communication | Implemented |

| Event ingestion | Implemented |

| SQLite persistence | Implemented |

| Processing checkpoints | Implemented |

| Duplicate protection | Implemented |

| Workflow performance analysis | Implemented |

| Supervisor configuration change observation | Implemented |

| Caller-ID anomaly detection | Partially implemented |

| Governance-aware decision handling | Partially implemented |

| Shared-cohort experimentation | Not completed |

| Generalized performance decay detection | Not completed |

| Automated rollback | Not completed |

| Automated caller-ID remediation | Not completed |

| Full supervisor dashboard | Not implemented |

| Complete twelve-workflow load validation | Not completed |



\---



\## 10. Known Limitations and Future Improvements



The current implementation provides a foundation for workflow monitoring, event processing, and evidence-based decision evaluation. Some capabilities still require additional development.



Potential improvements include:



1\. \*\*Expand anomaly detection:\*\* Improve detection coverage for caller-ID and other operational anomalies.

2\. \*\*Strengthen decision governance:\*\* Add more complete evidence requirements before configuration changes are approved.

3\. \*\*Add performance decay detection:\*\* Identify sustained decreases in workflow performance.

4\. \*\*Implement rollback support:\*\* Provide a controlled way to reverse configuration changes when required.

5\. \*\*Improve experimentation:\*\* Introduce shared-cohort experimentation and more complete comparison of workflow variants.

6\. \*\*Expand operational visibility:\*\* Develop a dashboard for monitoring workflow health and configuration activity.

7\. \*\*Complete load validation:\*\* Verify processing across all twelve workflows and measure end-to-end performance.



These improvements would make the system more comprehensive and reliable as its monitoring and decision-making capabilities expand.



\---



\## 11. Project Documentation



Additional technical details and scenario observations are available in:



\- \[`reports/public\_01\_dev.md`](reports/public\_01\_dev.md) – Workflow performance and configuration observations.

\- \[`reports/public\_02\_incidents.md`](reports/public\_02\_incidents.md) – Operational monitoring and anomaly detection.

\- \[`reports/public\_03\_load.md`](reports/public\_03\_load.md) – Historical event loading and workflow summaries.

\- \[`README\_PROJECT.md`](README\_PROJECT.md) – Additional project information.



\---



\## Project Summary



Formi combines event ingestion, persistent storage, workflow performance monitoring, operational signal detection, and evidence-based decision evaluation.



The implementation demonstrates event processing, metric tracking, operational monitoring, and audit recording across three scenarios. It also documents the areas that need further development, including complete experimentation, automated remediation, rollback, and full-scale load validation.



\*\*Built with Python, SQLite, HTTP APIs, Bash, and Pytest.\*\*
