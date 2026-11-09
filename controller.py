import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

import httpx
import event_ingest
import decision_engine
import performance_monitor


DB_PATH = os.environ.get("FORMI_DB_PATH", "data/formi_events.db")
TICK_MINUTES = 15


def audit(db, action, details):
    db.execute("""
        CREATE TABLE IF NOT EXISTS controller_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_at TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT NOT NULL
        )
    """)
    db.execute(
        """
        INSERT INTO controller_audit(recorded_at, action, details)
        VALUES (?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            action,
            json.dumps(details, default=str)
        )
    )
    db.commit()


def record_approval_status(db, approval_id, status):
    """Audit an approval only when its observed status changes."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS approval_observations (
            approval_id TEXT PRIMARY KEY,
            last_status TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    previous = db.execute(
        "SELECT last_status FROM approval_observations WHERE approval_id = ?",
        (approval_id,)
    ).fetchone()

    if previous is None or previous[0] != status:
        audit(
            db,
            "approval_status_changed",
            {
                "approval_id": approval_id,
                "previous_status": previous[0] if previous else None,
                "new_status": status
            }
        )

    db.execute("""
        INSERT INTO approval_observations
            (approval_id, last_status, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(approval_id) DO UPDATE SET
            last_status = excluded.last_status,
            updated_at = excluded.updated_at
    """, (
        approval_id,
        status,
        datetime.now(timezone.utc).isoformat()
    ))
    db.commit()


def ingest_live_events(client, db):
    last_chunk = event_ingest.get_checkpoint(db, "events")

    response = client.get(
        "/events/chunks",
        params={"kind": "events", "after": last_chunk}
    )
    response.raise_for_status()

    chunks = response.json()
    total_processed = 0
    total_inserted = 0

    for chunk in chunks:
        processed, inserted = event_ingest.ingest_chunk(
            client, db, chunk
        )

        # Save the checkpoint after the chunk has been ingested.
        event_ingest.save_checkpoint(
            db, "events", chunk["chunk"]
        )

        total_processed += processed
        total_inserted += inserted

    if chunks:
        print(
            f"Event ingestion: {total_processed:,} processed, "
            f"{total_inserted:,} new records across {len(chunks)} chunks"
        )

    detect_supervisor_changes(db)

    return {
        "chunks": len(chunks),
        "processed": total_processed,
        "inserted": total_inserted
    }



def detect_supervisor_changes(db):
    """Persist and audit supervisor configuration changes exactly once."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS supervisor_change_observations (
            event_id INTEGER PRIMARY KEY,
            workflow_id TEXT,
            version INTEGER,
            changed_dims TEXT NOT NULL,
            event_time TEXT,
            recorded_at TEXT NOT NULL
        )
    """)

    rows = db.execute("""
        SELECT event_id, event_time, workflow_id, payload
        FROM events
        WHERE event_type = 'config_changed'
        ORDER BY event_id
    """).fetchall()

    for event_id, event_time, workflow_id, payload in rows:
        event = json.loads(payload)

        if event.get("actor") != "supervisor":
            continue

        changed_dims = event.get("changed_dims", [])

        cursor = db.execute("""
            INSERT OR IGNORE INTO supervisor_change_observations
                (event_id, workflow_id, version, changed_dims,
                 event_time, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            workflow_id,
            event.get("version"),
            json.dumps(changed_dims),
            event_time,
            datetime.now(timezone.utc).isoformat()
        ))

        if cursor.rowcount == 1:
            details = {
                "event_id": event_id,
                "workflow_id": workflow_id,
                "version": event.get("version"),
                "changed_dims": changed_dims,
                "event_time": event_time,
                "actor": "supervisor"
            }

            audit(db, "supervisor_configuration_change_detected", details)

            print(
                f"Supervisor change detected: {workflow_id}, "
                f"version {event.get('version')}, "
                f"dimensions={changed_dims}"
            )

    db.commit()

def get_approval_items(response_data):
    """Support either a list response or a wrapped API response."""
    if isinstance(response_data, list):
        return response_data

    if isinstance(response_data, dict):
        for key in ("approvals", "items", "results"):
            if isinstance(response_data.get(key), list):
                return response_data[key]

    raise ValueError("Unexpected response format from GET /approvals")


def process_approval(client, db, approval):
    approval_id = approval.get("id") or approval.get("approval_id")
    status = approval.get("status")
    workflow_id = approval.get("workflow_id")

    if not approval_id or not status:
        audit(db, "invalid_approval_record", {"approval": approval})
        return

    record_approval_status(db, approval_id, status)

    if status != "approved":
        return

    if not workflow_id:
        audit(
            db,
            "approval_missing_workflow",
            {"approval_id": approval_id}
        )
        return

    # Do not apply an approval against a configuration it was not based on.
    config_response = client.get(
        f"/workflows/{workflow_id}/config"
    )
    config_response.raise_for_status()

    current_config = config_response.json()
    current_version = current_config.get("version")
    expected_version = approval.get("base_version")

    if current_version != expected_version:
        audit(
            db,
            "approval_not_applied_stale_version",
            {
                "approval_id": approval_id,
                "workflow_id": workflow_id,
                "expected_version": expected_version,
                "current_version": current_version
            }
        )
        print(f"Approval {approval_id}: stale configuration; not applied.")
        return

    try:
        apply_response = client.post(
            f"/workflows/{workflow_id}/apply",
            json={"approval_id": approval_id}
        )

        if apply_response.status_code == 409:
            audit(
                db,
                "approval_apply_conflict",
                {
                    "approval_id": approval_id,
                    "workflow_id": workflow_id,
                    "response": apply_response.text
                }
            )
            print(f"Approval {approval_id}: apply conflict; will recheck.")
            return

        apply_response.raise_for_status()
        result = apply_response.json()

        audit(
            db,
            "approval_applied",
            {
                "approval_id": approval_id,
                "workflow_id": workflow_id,
                "result": result
            }
        )
        print(f"Approval {approval_id}: successfully applied.")

    except httpx.HTTPStatusError:
        raise


def poll_approvals(client, db, extra_approval_id=None):
    response = client.get("/approvals")
    response.raise_for_status()

    approvals = get_approval_items(response.json())

    # Optionally include a specific approval if it was not in the list.
    if extra_approval_id:
        known_ids = {
            item.get("id") or item.get("approval_id")
            for item in approvals
        }

        if extra_approval_id not in known_ids:
            extra_response = client.get(
                f"/approvals/{extra_approval_id}"
            )
            if extra_response.status_code == 404:
                print(f"Approval {extra_approval_id}: not found.")
            else:
                extra_response.raise_for_status()
                approvals.append(extra_response.json())

    for approval in approvals:
        process_approval(client, db, approval)

    return len(approvals)


def run_controller(base_url, max_ticks=None, extra_approval_id=None):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    db = sqlite3.connect(DB_PATH, timeout=30)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")

    event_ingest.create_database(db)

    tick = 0

    try:
        with httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=120
        ) as client:

            health = client.get("/health")
            health.raise_for_status()

            print("\n========== AUTONOMOUS CONTROLLER ==========")
            print("Simulator:", base_url)
            print("Execution mode:", "until scenario finishes")

            # Recover events and approval states after a restart.
            ingest_live_events(client, db)

            recovery_state_response = client.get("/sim/state")
            recovery_state_response.raise_for_status()
            recovery_state = recovery_state_response.json()

            performance_monitor.detect_caller_id_anomalies(
                db,
                audit_callback=lambda action, details: audit(
                    db, action, details
                ),
                current_sim_time=recovery_state.get("ts")
            )

            poll_approvals(client, db, extra_approval_id)

            while True:
                state_response = client.get("/sim/state")
                state_response.raise_for_status()
                before = state_response.json()

                if before.get("finished"):
                    print("\nSimulator reports that the scenario has finished.")
                    break

                if max_ticks is not None and tick >= max_ticks:
                    print(f"\nReached the requested test limit: {max_ticks} ticks.")
                    break

                tick += 1
                print(f"\n========== TICK {tick} ==========")
                print("Simulation time:", before.get("ts"))

                # Record intent before advancing, so an interrupted run
                # leaves evidence that an advance was attempted.
                audit(
                    db,
                    "simulation_advance_requested",
                    {
                        "tick": tick,
                        "minutes": TICK_MINUTES,
                        "before": before.get("ts")
                    }
                )

                advance = client.post(
                    "/sim/advance",
                    json={"minutes": TICK_MINUTES}
                )

                if advance.status_code == 409:
                    print("Simulator refused to advance; checking final state.")
                    break

                advance.raise_for_status()
                advance_result = advance.json()

                audit(
                    db,
                    "simulation_advanced",
                    {
                        "tick": tick,
                        "minutes": TICK_MINUTES,
                        "result": advance_result
                    }
                )

                new_state_response = client.get("/sim/state")
                new_state_response.raise_for_status()
                after = new_state_response.json()

                print("New simulation time:", after.get("ts"))
                print("Credits remaining:", after.get("credits_remaining"))

                # Ingest fresh events before evaluating performance.
                ingest_live_events(client, db)

                performance_monitor.detect_caller_id_anomalies(
                    db,
                    audit_callback=lambda action, details: audit(
                        db, action, details
                    ),
                    current_sim_time=after.get("ts")
                )

                # Process every discoverable approval.
                poll_approvals(client, db, extra_approval_id)

                if after.get("finished"):
                    print("\nScenario completed.")
                    break

            # Final reconciliation and summary.
            ingest_live_events(client, db)

            final_recovery_response = client.get("/sim/state")
            final_recovery_response.raise_for_status()
            final_recovery_state = final_recovery_response.json()

            performance_monitor.detect_caller_id_anomalies(
                db,
                audit_callback=lambda action, details: audit(
                    db, action, details
                ),
                current_sim_time=final_recovery_state.get("ts")
            )

            poll_approvals(client, db, extra_approval_id)

            # Generate the final evidence-based decision report.
            print("\n========== FINAL DECISION ANALYSIS ==========")
            decision_engine.main(base_url)

            audit(
                db,
                "decision_report_generated",
                {
                    "report_path": "data/decision_report.json",
                    "status": "generated"
                }
            )

            final_response = client.get("/sim/state")
            final_response.raise_for_status()
            final_state = final_response.json()

            event_count = db.execute(
                "SELECT COUNT(*) FROM events"
            ).fetchone()[0]

            audit_count = db.execute(
                "SELECT COUNT(*) FROM controller_audit"
            ).fetchone()[0]

            print("\n========== CONTROLLER SUMMARY ==========")
            print("Final simulation time:", final_state.get("ts"))
            print("Scenario finished:", final_state.get("finished"))
            print("Total stored events:", f"{event_count:,}")
            print("Audit records:", f"{audit_count:,}")
            print("Ticks executed:", tick)

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Formi autonomous simulation controller"
    )

    parser.add_argument(
        "sim_url",
        nargs="?",
        default="http://127.0.0.1:8700",
        help="Simulator API URL"
    )

    parser.add_argument(
        "--max-ticks",
        type=int,
        default=None,
        help="Optional tick limit for controlled testing"
    )

    parser.add_argument(
        "--approval-id",
        default=None,
        help="Optional extra approval ID to monitor"
    )

    args = parser.parse_args()

    if args.max_ticks is not None and args.max_ticks < 1:
        parser.error("--max-ticks must be at least 1")

    try:
        run_controller(
            args.sim_url,
            args.max_ticks,
            args.approval_id
        )
    except httpx.HTTPStatusError as error:
        print("\nHTTP ERROR:", error)
        print("Response:", error.response.text)
        sys.exit(1)
    except httpx.RequestError as error:
        print("\nCONNECTION ERROR:", error)
        sys.exit(1)
    except Exception as error:
        print("\nCONTROLLER ERROR:", repr(error))
        sys.exit(1)


if __name__ == "__main__":
    main()
