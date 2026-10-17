
import os
import secrets
import threading
import webbrowser

from dotenv import load_dotenv
from flask import Flask, request, redirect
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

import json
from datetime import datetime, timezone
from pathlib import Path

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI",
    "http://127.0.0.1:8888/callback",
)

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing Spotify credentials in .env")

SCOPE = "user-read-recently-played"

oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".spotify_token_cache",
    open_browser=False,
)

app = Flask(__name__)
expected_state = secrets.token_urlsafe(24)


@app.route("/")
def login():
    auth_url = oauth.get_authorize_url(state=expected_state)
    return redirect(auth_url)


@app.route("/callback")
def callback():
    returned_state = request.args.get("state")
    code = request.args.get("code")
    error = request.args.get("error")

    if returned_state != expected_state:
        return "State mismatch. Authorization rejected.", 400

    if error:
        return f"Spotify authorization failed: {error}", 400

    if not code:
        return "No authorization code received.", 400

    try:
        token_info = oauth.get_access_token(
            code, check_cache=False
        )
        sp = Spotify(auth=token_info["access_token"])

        result = sp.current_user_recently_played(limit=10)

        # Locate the project root
        project_root = Path(__file__).resolve().parents[1]

        # Create a unique filename for each ingestion run
        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ"
        )

        output_dir = project_root / "data" / "raw"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"recently_played_{timestamp}.json"

        # Save the original API response with ingestion metadata
        raw_data = {
            "source": "spotify_recently_played",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": result,
        }

        with output_file.open("w", encoding="utf-8") as file:
            json.dump(raw_data, file, indent=2, ensure_ascii=False)

        print(f"Raw data saved to: {output_file}")

        print("\nRecently played tracks:")
        for item in result["items"]:
            track = item["track"]
            artists = ", ".join(
                artist["name"] for artist in track["artists"]
            )
            print(
                f'{item["played_at"]} | '
                f'{track["name"]} | {artists}'
            )

        return "Spotify authentication successful! Check your terminal."

    except Exception:
        app.logger.exception("Spotify API request failed")
        return "Authentication or API request failed. Check the terminal logs.", 500


if __name__ == "__main__":
    print("Starting local callback server at", REDIRECT_URI)
    print("Opening Spotify authorization in your browser...")

    threading.Timer(
        1.0,
        lambda: webbrowser.open("http://127.0.0.1:8888/"),
    ).start()

    app.run(host="127.0.0.1", port=8888, debug=False)
