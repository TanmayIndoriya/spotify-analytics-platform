
import psycopg

conn = psycopg.connect(
    dbname="spotify_analytics",
    user="postgres",
    host="/var/run/postgresql",
)

try:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS listening_events (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                track_id TEXT NOT NULL,
                track_name TEXT NOT NULL,
                artist_names TEXT[] NOT NULL,
                album_name TEXT,
                played_at TIMESTAMPTZ NOT NULL,
                duration_ms INTEGER,
                ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                source_file TEXT,
                raw_event JSONB NOT NULL,
                CONSTRAINT uq_listening_event
                    UNIQUE (track_id, played_at)
            );
        """)
    conn.commit()
    print("Table listening_events is ready.")
finally:
    conn.close()
