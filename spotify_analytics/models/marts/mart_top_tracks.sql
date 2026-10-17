SELECT
    track_id,
    track_name,
    artist_names,
    COUNT(*) AS play_count,
    ROUND(
        SUM(COALESCE(duration_ms, 0)) / 60000.0,
        2
    ) AS estimated_listening_minutes,
    MAX(played_at) AS last_played_at
FROM {{ ref('fct_listening_history') }}
GROUP BY
    track_id,
    track_name,
    artist_names