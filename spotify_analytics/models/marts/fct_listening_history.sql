SELECT
    listening_event_id,
    track_id,
    track_name,
    artist_names,
    album_name,
    played_at,
    duration_ms,
    DATE(played_at) AS played_date,
    EXTRACT(HOUR FROM played_at) AS played_hour
FROM {{ ref('stg_listening_events') }}