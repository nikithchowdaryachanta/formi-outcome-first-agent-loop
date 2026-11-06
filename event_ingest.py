import argparse
import json
import sqlite3
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8700"
DB_PATH = "data/formi_events.db"


def create_database(db):
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")

    db.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY,
            chunk_id INTEGER NOT NULL,
            workflow_id TEXT,
            event_type TEXT NOT NULL,
            event_time TEXT,
            payload TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_workflow_type
        ON events(workflow_id, event_type)
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    db.commit()


def get_checkpoint(db, kind):
    row = db.execute(
        "SELECT value FROM checkpoints WHERE key = ?",
        (f"last_{kind}_chunk",)
    ).fetchone()

    return int(row[0]) if row else -1


def save_checkpoint(db, kind, chunk_id):
    db.execute("""
        INSERT INTO checkpoints(key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, (f"last_{kind}_chunk", str(chunk_id)))

    db.commit()


def ingest_chunk(client, db, chunk):
    chunk_id = chunk["chunk"]

    print(f"\nDownloading chunk {chunk_id}...")
    inserted = 0
    processed = 0
    batch = []

    with client.stream(
        "GET", f"/events/chunks/{chunk_id}"
    ) as response:

        response.raise_for_status()

        for line in response.iter_lines():
            if not line.strip():
                continue

            event = json.loads(line)

            batch.append((
                event["event_id"],
                chunk_id,
                event.get("workflow_id"),
                event.get("type", "unknown"),
                event.get("ts"),
                json.dumps(event)
            ))

            processed += 1

            if len(batch) >= 2000:
                before = db.total_changes

                db.executemany("""
                    INSERT OR IGNORE INTO events
                    (event_id, chunk_id, workflow_id,
                     event_type, event_time, payload)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, batch)

                inserted += db.total_changes - before
                db.commit()
                batch.clear()

            if processed % 20000 == 0:
                print(f"Processed {processed:,} events...")

    if batch:
        before = db.total_changes

        db.executemany("""
            INSERT OR IGNORE INTO events
            (event_id, chunk_id, workflow_id,
             event_type, event_time, payload)
            VALUES (?, ?, ?, ?, ?, ?)
        """, batch)

        inserted += db.total_changes - before
        db.commit()

    return processed, inserted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kind",
        choices=["history", "events"],
        default="history"
    )
    args = parser.parse_args()

    db = sqlite3.connect(DB_PATH, timeout=30)
    create_database(db)

    kind = args.kind
    last_chunk = get_checkpoint(db, kind)

    print("=" * 55)
    print("FORMI EVENT INGESTION ENGINE")
    print("=" * 55)
    print("Event type:", kind)
    print("Last processed chunk:", last_chunk)

    try:
        with httpx.Client(
            base_url=BASE_URL,
            timeout=120
        ) as client:

            health = client.get("/health")
            health.raise_for_status()

            response = client.get(
                "/events/chunks",
                params={
                    "kind": kind,
                    "after": last_chunk
                }
            )
            response.raise_for_status()

            chunks = response.json()

            print("New chunks available:", len(chunks))

            total_processed = 0
            total_inserted = 0

            for chunk in chunks:
                processed, inserted = ingest_chunk(
                    client, db, chunk
                )

                total_processed += processed
                total_inserted += inserted

                # Save checkpoint only after the entire chunk
                # has been successfully downloaded and committed.
                save_checkpoint(
                    db, kind, chunk["chunk"]
                )

                print(
                    f"Chunk {chunk['chunk']} completed: "
                    f"{processed:,} processed, "
                    f"{inserted:,} newly inserted"
                )

            total = db.execute(
                "SELECT COUNT(*) FROM events"
            ).fetchone()[0]

            print("\n" + "=" * 55)
            print("INGESTION COMPLETED")
            print("=" * 55)
            print("Processed:", f"{total_processed:,}")
            print("New records:", f"{total_inserted:,}")
            print("Total database records:", f"{total:,}")

    except httpx.ConnectError:
        print("ERROR: Simulator is not running.")

    except Exception as error:
        print("INGESTION ERROR:", repr(error))

    finally:
        db.close()


if __name__ == "__main__":
    main()
