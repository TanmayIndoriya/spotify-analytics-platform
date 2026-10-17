SELECT
    id AS listening_event_id,
    track_id,
    track_name,
    artist_names,
    album_name,
    played_at,
    duration_ms,
    ingested_at
FROM {{ source('spotify', 'listening_events') }}
WHERE track_id IS NOT NULL