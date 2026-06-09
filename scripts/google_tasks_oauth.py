"""Get a Google OAuth refresh token for Murchik Cakes Google Tasks integration.

Run locally after creating OAuth Client ID in Google Cloud:
    python scripts/google_tasks_oauth.py

Required environment variables:
    GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

SCOPE = "https://www.googleapis.com/auth/tasks"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"


def main() -> None:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise SystemExit("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET before running this script.")

    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    print("Open this URL in browser, approve access, then paste the authorization code here:\n")
    print(url)
    code = input("\nAuthorization code: ").strip()

    data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        payload = json.loads(resp.read().decode())
    print("\nAdd this variable to Railway API service:")
    print("GOOGLE_REFRESH_TOKEN=" + payload.get("refresh_token", ""))
    if not payload.get("refresh_token"):
        print("\nNo refresh_token returned. Make sure you used prompt=consent and access_type=offline.")


if __name__ == "__main__":
    main()
