import sqlite3
import json
from collections import defaultdict
from pathlib import Path


DB_PATH = "data/formi_events.db"
REPORT_PATH = "data/performance_report.json"


def load_events():
    """Load historical call and lead events from SQLite."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    calls = conn.execute(
        "SELECT payload FROM events WHERE event_type = 'call'"
    ).fetchall()

    leads = conn.execute(
        "SELECT payload FROM events WHERE event_type = 'lead'"
    ).fetchall()

    conn.close()

    call_events = [json.loads(row["payload"]) for row in calls]
    lead_events = [json.loads(row["payload"]) for row in leads]

    return call_events, lead_events


def percentage(numerator, denominator):
    """Safely calculate a percentage."""

    if denominator == 0:
        return 0.0

    return round((numerator / denominator) * 100, 2)


def analyse_workflow(workflow_id, calls, leads):
    """Calculate performance metrics for one workflow."""

    connected = [c for c in calls if c.get("connected") is True]

    engaged = [c for c in calls if c.get("engaged") is True]

    concluded = [
        c for c in calls
        if str(c.get("disposition", "")).startswith("concluded_")
    ]

    interested = [
        c for c in calls
        if c.get("disposition") == "concluded_interested"
    ]

    hallucinations = [
        c for c in calls
        if (c.get("qa") or {}).get("hallucination_flag") is True
    ]

    adherence_values = [
        (c.get("qa") or {}).get("flow_adherence")
        for c in calls
        if isinstance((c.get("qa") or {}).get("flow_adherence"), (int, float))
    ]

    metrics = {
        "workflow_id": workflow_id,
        "total_calls": len(calls),
        "total_leads": len(leads),

        "connected_calls": len(connected),
        "engaged_calls": len(engaged),
        "concluded_calls": len(concluded),
        "interested_calls": len(interested),

        "pickup_rate_pct": percentage(
            len(connected), len(calls)
        ),

        "engagement_rate_pct": percentage(
            len(engaged), len(connected)
        ),

        "outcome_rate_pct": percentage(
            len(concluded), len(leads)
        ),

        "interest_rate_pct": percentage(
            len(interested), len(leads)
        ),

        "hallucination_count": len(hallucinations),

        "hallucination_rate_pct": percentage(
            len(hallucinations), len(calls)
        ),

        "average_flow_adherence": round(
            sum(adherence_values) / len(adherence_values), 4
        ) if adherence_values else None,
    }

    return metrics


def analyse_variants(calls):
    """Compare performance across individual experiment variants."""

    groups = defaultdict(list)

    for call in calls:
        variant = call.get("variant", {})

        for dimension in (
            "caller_id",
            "voice",
            "welcome_message",
            "prompt_version",
        ):
            value = variant.get(dimension)

            if value is not None:
                groups[(dimension, value)].append(call)

    results = []

    for (dimension, value), group in sorted(groups.items()):

        connected = [
            c for c in group if c.get("connected") is True
        ]

        engaged = [
            c for c in group if c.get("engaged") is True
        ]

        results.append({
            "dimension": dimension,
            "value": value,
            "total_calls": len(group),
            "connected_calls": len(connected),
            "engaged_calls": len(engaged),

            "pickup_rate_pct": percentage(
                len(connected), len(group)
            ),

            "engagement_rate_pct": percentage(
                len(engaged), len(connected)
            ),
        })

    return results


def main():

    print("=" * 65)
    print("FORMI PERFORMANCE MONITORING ENGINE")
    print("=" * 65)

    calls, leads = load_events()

    print(f"\nTotal call events: {len(calls):,}")
    print(f"Total lead events: {len(leads):,}")

    workflow_ids = sorted({
        event["workflow_id"]
        for event in calls + leads
        if event.get("workflow_id")
    })

    workflow_reports = {}

    print("\nWORKFLOW PERFORMANCE")
    print("-" * 65)

    for workflow_id in workflow_ids:

        workflow_calls = [
            c for c in calls
            if c.get("workflow_id") == workflow_id
        ]

        workflow_leads = [
            l for l in leads
            if l.get("workflow_id") == workflow_id
        ]

        metrics = analyse_workflow(
            workflow_id,
            workflow_calls,
            workflow_leads
        )

        workflow_reports[workflow_id] = metrics

        print(f"\nWorkflow: {workflow_id}")
        print(f"  Calls: {metrics['total_calls']:,}")
        print(f"  Leads: {metrics['total_leads']:,}")
        print(f"  Pickup rate: {metrics['pickup_rate_pct']}%")
        print(f"  Engagement rate: {metrics['engagement_rate_pct']}%")
        print(f"  Outcome rate: {metrics['outcome_rate_pct']}%")
        print(f"  Interest rate: {metrics['interest_rate_pct']}%")
        print(f"  Hallucinations: {metrics['hallucination_count']}")
        print(
            "  Average flow adherence:",
            metrics["average_flow_adherence"]
        )

    variant_reports = analyse_variants(calls)

    report = {
        "source": "historical_event_database",
        "total_calls": len(calls),
        "total_leads": len(leads),
        "workflows": workflow_reports,
        "variant_comparisons": variant_reports,
    }

    Path(REPORT_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\n" + "=" * 65)
    print("VARIANT COMPARISON")
    print("=" * 65)

    for item in variant_reports:
        print(
            f"{item['dimension']}={item['value']}: "
            f"calls={item['total_calls']:,}, "
            f"pickup={item['pickup_rate_pct']}%, "
            f"engagement={item['engagement_rate_pct']}%"
        )

    print("\n" + "=" * 65)
    print("REPORT SAVED")
    print(REPORT_PATH)
    print("=" * 65)


if __name__ == "__main__":
    main()
