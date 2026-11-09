import sqlite3
import os
import json
from collections import defaultdict
from pathlib import Path


DB_PATH = os.environ.get("FORMI_DB_PATH", "data/formi_events.db")
REPORT_PATH = os.environ.get("FORMI_PERFORMANCE_REPORT_PATH", "data/performance_report.json")


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

def detect_caller_id_anomalies(db, audit_callback=None, current_sim_time=None):
    """
    Detect significant daily caller-ID pickup declines.

    Compares the latest day against the preceding three days.
    Does not automatically change caller-ID configuration.
    """

    from collections import defaultdict

    MIN_CALLS = 500
    MIN_RELATIVE_DECLINE = 0.20

    db.execute("""
        CREATE TABLE IF NOT EXISTS caller_id_anomalies (
            anomaly_key TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            caller_id TEXT NOT NULL,
            observation_day TEXT NOT NULL,
            baseline_pickup_rate REAL NOT NULL,
            observed_pickup_rate REAL NOT NULL,
            relative_decline REAL NOT NULL,
            baseline_engagement_rate REAL,
            observed_engagement_rate REAL,
            detected_at TEXT NOT NULL
        )
    """)

    rows = db.execute("""
        SELECT workflow_id, event_time, payload
        FROM events
        WHERE event_type = 'call'
          AND (? IS NULL OR event_time <= ?)
        ORDER BY event_time
    """, (current_sim_time, current_sim_time)).fetchall()



    daily = defaultdict(
        lambda: {
            "calls": 0,
            "connected": 0,
            "engaged": 0
        }
    )

    for workflow_id, event_time, payload in rows:
        call = json.loads(payload)
        caller_id = (call.get("variant") or {}).get("caller_id")

        if not workflow_id or not caller_id or not event_time:
            continue

        day = event_time[:10]

        # Evaluate completed days only; exclude the current simulation day.
        if current_sim_time and day >= current_sim_time[:10]:
            continue

        item = daily[(workflow_id, caller_id, day)]

        item["calls"] += 1
        item["connected"] += call.get("connected") is True
        item["engaged"] += call.get("engaged") is True

    groups = defaultdict(list)

    for (workflow_id, caller_id, day), metrics in daily.items():
        groups[(workflow_id, caller_id)].append((day, metrics))

    alerts = []

    for (workflow_id, caller_id), days in groups.items():
        days.sort()

        for index in range(3, len(days)):
            observation_day, observed = days[index]
            baseline_days = days[index - 3:index]

            baseline_calls = sum(
                item["calls"] for _, item in baseline_days
            )
            baseline_connected = sum(
                item["connected"] for _, item in baseline_days
            )
            baseline_engaged = sum(
                item["engaged"] for _, item in baseline_days
            )

            if (
                baseline_calls < MIN_CALLS
                or observed["calls"] < MIN_CALLS
                or baseline_connected == 0
            ):
                continue

            baseline_pickup = baseline_connected / baseline_calls
            observed_pickup = (
                observed["connected"] / observed["calls"]
            )

            relative_decline = (
                (baseline_pickup - observed_pickup) / baseline_pickup
                if baseline_pickup else 0
            )

            if relative_decline < MIN_RELATIVE_DECLINE:
                continue

            baseline_engagement = (
                baseline_engaged / baseline_connected
            )

            observed_engagement = (
                observed["engaged"] / observed["connected"]
                if observed["connected"] else 0
            )

            anomaly_key = (
                f"{workflow_id}:{caller_id}:{observation_day}"
            )

            cursor = db.execute("""
                INSERT OR IGNORE INTO caller_id_anomalies (
                    anomaly_key,
                    workflow_id,
                    caller_id,
                    observation_day,
                    baseline_pickup_rate,
                    observed_pickup_rate,
                    relative_decline,
                    baseline_engagement_rate,
                    observed_engagement_rate,
                    detected_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                anomaly_key,
                workflow_id,
                caller_id,
                observation_day,
                baseline_pickup,
                observed_pickup,
                relative_decline,
                baseline_engagement,
                observed_engagement
            ))

            if cursor.rowcount == 1:
                alert = {
                    "workflow_id": workflow_id,
                    "caller_id": caller_id,
                    "day": observation_day,
                    "baseline_pickup_pct": round(
                        baseline_pickup * 100, 2
                    ),
                    "observed_pickup_pct": round(
                        observed_pickup * 100, 2
                    ),
                    "relative_decline_pct": round(
                        relative_decline * 100, 2
                    ),
                    "baseline_engagement_pct": round(
                        baseline_engagement * 100, 2
                    ),
                    "observed_engagement_pct": round(
                        observed_engagement * 100, 2
                    )
                }

                alerts.append(alert)

                if audit_callback is not None:
                    audit_callback(
                        "caller_id_performance_anomaly_detected",
                        alert
                    )

    db.commit()

    return alerts
