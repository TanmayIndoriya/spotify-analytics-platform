
import json
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def load_listening_history():
    files = sorted(RAW_DIR.glob("recently_played_*.json"))

    if not files:
        print("No raw JSON snapshots found.")
        return

    conn = psycopg.connect(
        dbname="spotify_analytics",
        user="postgres",
        host="/var/run/postgresql",
    )

    inserted = 0
    skipped = 0

    try:
        with conn.cursor() as cur:
            for file_path in files:
                with file_path.open(encoding="utf-8") as file:
                    snapshot = json.load(file)

                events = snapshot["data"].get("items", [])

                for event in events:
                    track = event.get("track")

                    if not track or not track.get("id"):
                        skipped += 1
                        continue

                    cur.execute(
                        """
                        INSERT INTO listening_events (
                            track_id,
                            track_name,
                            artist_names,
                            album_name,
                            played_at,
                            duration_ms,
                            source_file,
                            raw_event
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (track_id, played_at)
                        DO NOTHING
                        RETURNING id;
                        """,
                        (
                            track["id"],
                            track["name"],
                            [
                                artist["name"]
                                for artist in track.get("artists", [])
                            ],
                            track.get("album", {}).get("name"),
                            event["played_at"],
                            track.get("duration_ms"),
                            file_path.name,
                            Jsonb(event),
                        ),
                    )

                    if cur.fetchone():
                        inserted += 1
                    else:
                        skipped += 1

        conn.commit()
        print(f"New events inserted: {inserted}")
        print(f"Duplicate or skipped events: {skipped}")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    load_listening_history()
