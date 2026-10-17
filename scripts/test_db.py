
import psycopg

conn = psycopg.connect(
    dbname="spotify_analytics",
    user="postgres",
    host="/var/run/postgresql",
)

try:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user")
        print(cur.fetchone())
finally:
    conn.close()
