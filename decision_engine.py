
import sqlite3
import json
import os
import httpx
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8700"
DB_PATH = os.environ.get("FORMI_DB_PATH", "data/formi_events.db")
OUTPUT_PATH = os.environ.get("FORMI_REPORT_PATH", "data/decision_report.json")


def load_call_events():
    """Load all call events from the local event database."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT payload
            FROM events
            WHERE event_type = 'call'
            ORDER BY event_id
        """).fetchall()

    return [json.loads(row[0]) for row in rows]


def percentage(numerator, denominator):
    if denominator == 0:
        return 0.0
    return round(numerator * 100 / denominator, 2)


def wilson_interval(successes, total, z=1.96):
    """Calculate a 95% Wilson confidence interval."""
    if total == 0:
        return None

    p = successes / total
    denominator = 1 + z**2 / total

    center = p + z**2 / (2 * total)
    margin = z * (
        (p * (1 - p) / total + z**2 / (4 * total**2)) ** 0.5
    )

    lower = (center - margin) / denominator
    upper = (center + margin) / denominator

    return [
        round(lower * 100, 2),
        round(upper * 100, 2)
    ]


def calculate_metrics(events):
    """Calculate separate operational and safety metrics."""

    calls = len(events)

    connected = sum(
        event.get("connected") is True
        for event in events
    )

    engaged = sum(
        event.get("engaged") is True
        for event in events
    )

    concluded = sum(
        str(event.get("disposition", "")).startswith("concluded_")
        for event in events
    )

    hallucinations = sum(
        (event.get("qa") or {}).get("hallucination_flag") is True
        for event in events
    )

    pickup_ci = wilson_interval(connected, calls)
    engagement_ci = wilson_interval(engaged, connected)

    return {
        "calls": calls,
        "connected": connected,
        "engaged": engaged,
        "concluded": concluded,
        "hallucinations": hallucinations,

        "pickup_rate_pct": percentage(connected, calls),

        "engagement_rate_pct": percentage(
            engaged, connected
        ),

        "outcome_rate_pct": percentage(
            concluded, calls
        ),

        "hallucination_rate_pct": percentage(
            hallucinations, calls
        ),

        "pickup_95_ci": pickup_ci,
        "engagement_95_ci": engagement_ci,
    }


def group_events(events, dimension):
    """Group events by an actual recorded variant dimension."""

    groups = defaultdict(list)

    for event in events:
        variant = event.get("variant") or {}
        value = variant.get(dimension)

        if value is not None:
            groups[str(value)].append(event)

    return {
        key: calculate_metrics(group)
        for key, group in sorted(groups.items())
    }


def analyse_workflow(workflow, config_data, all_events):

    workflow_id = workflow["workflow_id"]
    current_version = config_data["version"]
    current_config = config_data["config"]

    # IMPORTANT:
    # Do not filter by config_version == current_version.
    # Campaign configuration versions can remain unchanged while
    # prompt_version changes on running campaigns.

    workflow_events = [
        event for event in all_events
        if event.get("workflow_id") == workflow_id
    ]

    overall_metrics = calculate_metrics(workflow_events)

    # Group by actual prompt and caller ID used in each call.
    prompt_evidence = group_events(
        workflow_events, "prompt_version"
    )

    caller_evidence = group_events(
        workflow_events, "caller_id"
    )

    voice_evidence = group_events(
        workflow_events, "voice"
    )

    welcome_evidence = group_events(
        workflow_events, "welcome_message"
    )

    # Preserve configuration version as attribution information.
    observed_versions = sorted({
        event.get("config_version")
        for event in workflow_events
        if event.get("config_version") is not None
    })

    # Campaign-level population breakdown.
    campaign_groups = defaultdict(list)

    for event in workflow_events:
        campaign_id = event.get("campaign_id")

        if campaign_id:
            campaign_groups[campaign_id].append(event)

    campaign_evidence = {
        campaign_id: calculate_metrics(events)
        for campaign_id, events in sorted(campaign_groups.items())
    }

    governance = workflow["governance"]
    objective = workflow["objective"]
    auto_policy = governance["auto_apply"]

    return {
        "workflow_id": workflow_id,

        "current_configuration_version": current_version,

        "observed_campaign_config_versions": observed_versions,

        "primary_objective": objective["primary"],
        "guardrail": objective["guardrail"],

        "current_configuration": current_config,

        "automatic_changes_enabled": auto_policy["enabled"],

        "automatically_allowed_dimensions": auto_policy["allowed_dims"],

        "maximum_automatic_shift": auto_policy["max_shift"],

        "minimum_validation_pass_rate":
            governance["min_validation_pass_rate"],

        "daily_request_limit":
            governance["max_requests_per_24h"],

        "proposal_ttl_hours":
            governance["proposal_ttl_hours"],

        "apply_window_hours":
            governance["apply_window_hours"],

        "analysed_calls": len(workflow_events),

        "overall_metrics": overall_metrics,

        "prompt_version_evidence": prompt_evidence,

        "caller_id_evidence": caller_evidence,

        "voice_evidence": voice_evidence,

        "welcome_message_evidence": welcome_evidence,

        "campaign_evidence": campaign_evidence,

        "decision": {
            "winner_selected": False,
            "configuration_modified": False,
            "causal_improvement_established": False,
            "status": (
                "Historical evidence collected. "
                "Further population-aware evaluation, "
                "guardrail checks and validation are required."
            )
        }
    }


def main(base_url=BASE_URL):

    print("=" * 70)
    print("FORMI DECISION AND GOVERNANCE ENGINE")
    print("=" * 70)

    events = load_call_events()

    print(f"\nLoaded {len(events):,} historical call events.")

    with httpx.Client(
        base_url=base_url,
        timeout=30
    ) as client:

        health = client.get("/health")
        health.raise_for_status()

        response = client.get("/workflows")
        response.raise_for_status()

        workflows = response.json()

        report = {
            "engine": "decision_and_governance",
            "source": "historical_events_and_simulator_http_api",

            "generated_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),

            "total_call_events": len(events),

            "workflows": {},

            "safety": {
                "winner_selected": False,
                "automatic_configuration_changes": False,
                "simulator_time_advanced": False,
                "governance_bypassed": False
            }
        }

        for workflow in workflows:

            workflow_id = workflow["workflow_id"]

            config_response = client.get(
                f"/workflows/{workflow_id}/config"
            )
            config_response.raise_for_status()

            config_data = config_response.json()

            result = analyse_workflow(
                workflow,
                config_data,
                events
            )

            report["workflows"][workflow_id] = result

            metrics = result["overall_metrics"]

            print(f"\nWorkflow: {workflow_id}")
            print("-" * 50)

            print(
                f"Current config version: "
                f"{result['current_configuration_version']}"
            )

            print(
                f"Observed campaign config versions: "
                f"{result['observed_campaign_config_versions']}"
            )

            print(
                f"Primary objective: "
                f"{result['primary_objective']}"
            )

            print(f"Total calls: {metrics['calls']:,}")

            print(
                f"Pickup rate: "
                f"{metrics['pickup_rate_pct']}%"
            )

            print(
                f"Engagement rate: "
                f"{metrics['engagement_rate_pct']}%"
            )

            print(
                f"Outcome rate: "
                f"{metrics['outcome_rate_pct']}%"
            )

            print(
                f"Hallucinations: "
                f"{metrics['hallucinations']}"
            )

            print("\nPrompt version evidence:")

            for prompt, evidence in result[
                "prompt_version_evidence"
            ].items():

                print(
                    f"  {prompt}: "
                    f"calls={evidence['calls']:,}, "
                    f"pickup={evidence['pickup_rate_pct']}%, "
                    f"engagement={evidence['engagement_rate_pct']}%"
                )

            print(
                "\nAutomatic changes enabled: "
                f"{result['automatic_changes_enabled']}"
            )

            print(
                "Permitted automatic dimensions: "
                f"{result['automatically_allowed_dimensions']}"
            )

            print("Winner selected: No")
            print("Configuration modified: No")

    Path(OUTPUT_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(report, file, indent=2)

    print("\n" + "=" * 70)
    print("DECISION ANALYSIS COMPLETED")
    print(f"Report saved: {OUTPUT_PATH}")
    print("No simulator configuration was modified.")
    print("=" * 70)


if __name__ == "__main__":
    main()
