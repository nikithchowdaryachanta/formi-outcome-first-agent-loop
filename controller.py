import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone

import httpx
import event_ingest


BASE_URL = "http://127.0.0.1:8700"
DB_PATH = "data/formi_events.db"


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
            json.dumps(details)
        )
    )
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

        event_ingest.save_checkpoint(
            db, "events", chunk["chunk"]
        )

        total_processed += processed
        total_inserted += inserted

        print(
            f"Chunk {chunk['chunk']}: "
            f"{processed:,} processed, "
            f"{inserted:,} inserted"
        )

    print(
        f"Live ingestion: {total_processed:,} processed, "
        f"{total_inserted:,} new records"
    )

    return {
        "chunks": len(chunks),
        "processed": total_processed,
        "inserted": total_inserted
    }


def check_approval(client, db, approval_id):
    response = client.get(f"/approvals/{approval_id}")
    response.raise_for_status()

    approval = response.json()
    status = approval.get("status")
    workflow_id = approval.get("workflow_id")

    print(f"Approval {approval_id}: {status}")

    if status == "approved":
        print("Approval granted. Checking current configuration...")

        config_response = client.get(
            f"/workflows/{workflow_id}/config"
        )
        config_response.raise_for_status()

        current_config = config_response.json()
        current_version = current_config.get("version")

        if current_version != approval.get("base_version"):
            audit(
                db,
                "approval_not_applied_stale_version",
                {
                    "approval_id": approval_id,
                    "expected_version": approval.get("base_version"),
                    "current_version": current_version
                }
            )
            print("Configuration version changed. Not applying.")
            return

        apply_response = client.post(
            f"/workflows/{workflow_id}/apply",
            json={"approval_id": approval_id}
        )
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

        print("Approved configuration successfully applied.")

    elif status in ("rejected", "expired", "lapsed", "applied"):
        audit(
            db,
            "approval_status",
            {
                "approval_id": approval_id,
                "status": status
            }
        )
        print("No application action required.")

    else:
        audit(
            db,
            "approval_pending",
            {
                "approval_id": approval_id,
                "status": status
            }
        )
        print("Waiting for the simulated approver.")


def run_controller(ticks, approval_id):
    db = sqlite3.connect(DB_PATH, timeout=30)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")

    event_ingest.create_database(db)

    try:
        with httpx.Client(
            base_url=BASE_URL,
            timeout=120
        ) as client:

            health = client.get("/health")
            health.raise_for_status()

            print("\n========== AUTONOMOUS CONTROLLER ==========")

            # Recover any events left unprocessed by an earlier run.
            ingest_live_events(client, db)

            for tick in range(1, ticks + 1):
                state = client.get("/sim/state")
                state.raise_for_status()
                before = state.json()

                if before.get("finished"):
                    print("Simulation has finished.")
                    break

                print(f"\n========== TICK {tick}/{ticks} ==========")
                print("Current time:", before["ts"])

                # The controller, not the user, advances simulation time.
                advance = client.post(
                    "/sim/advance",
                    json={"minutes": 15}
                )

                if advance.status_code == 409:
                    print("Simulator cannot advance further.")
                    break

                advance.raise_for_status()
                advance_result = advance.json()

                audit(
                    db,
                    "simulation_advanced",
                    {
                        "minutes": 15,
                        "before": before,
                        "result": advance_result
                    }
                )

                new_state = client.get("/sim/state")
                new_state.raise_for_status()
                after = new_state.json()

                print("New time:", after["ts"])
                print(
                    "Credits remaining:",
                    after["credits_remaining"]
                )

                ingest_live_events(client, db)

                check_approval(client, db, approval_id)

            print("\n========== CONTROLLER FINISHED ==========")

            final_state = client.get("/sim/state")
            final_state.raise_for_status()

            print(
                "Final simulator time:",
                final_state.json()["ts"]
            )

            count = db.execute(
                "SELECT COUNT(*) FROM events"
            ).fetchone()[0]

            print("Total stored events:", f"{count:,}")

            audit_count = db.execute(
                "SELECT COUNT(*) FROM controller_audit"
            ).fetchone()[0]

            print("Audit records:", audit_count)

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Formi autonomous simulation controller"
    )

    parser.add_argument(
        "--ticks",
        type=int,
        default=1,
        help="Number of 15-minute simulation ticks (default: 1)"
    )

    parser.add_argument(
        "--approval-id",
        default="apr_00001",
        help="Existing approval request to monitor"
    )

    args = parser.parse_args()

    if args.ticks < 1:
        parser.error("--ticks must be at least 1")

    try:
        run_controller(args.ticks, args.approval_id)

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
