import requests
import json
import time

# --- CONFIGURATION (PASTE YOURS HERE) ---
ODDS_API_KEY = deb7282bba754878565cce93307dcdc7
DISCORD_WEBHOOK_URL = https://discord.com/api/webhooks/1461961795022618799/42QMeyZpcxv1nAt0ui4v15prTzLNWrVnAhoqSm-jeUJsmeDANIb6l_3lwqv7zwujnd58
# ----------------------------------------

def run_diagnostics():
    print("--- STARTING DIAGNOSTICS ---")
    
    # TEST 1: Check Discord Connection
    print("\n1. Testing Discord Webhook...")
    try:
        payload = {"content": "✅ **Test:** Diagnostic script is running."}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        
        print(f"   HTTP Status Code: {response.status_code}")
        
        if 200 <= response.status_code < 300:
            print("   ✅ Discord Connection: SUCCESS")
        else:
            print(f"   ❌ Discord Connection: FAILED (Server said: {response.text})")
            
    except Exception as e:
        print(f"   ❌ Discord Connection: CRASHED ({e})")

    # TEST 2: Check Odds API Connection
    print("\n2. Testing The Odds API...")
    try:
        url = f'https://api.the-odds-api.com/v4/sports/basketball_nba/odds?api_key={ODDS_API_KEY}&regions=us&markets=h2h&oddsFormat=american'
        response = requests.get(url)
        
        print(f"   HTTP Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            game_count = len(data)
            print(f"   ✅ Odds API Connection: SUCCESS")
            print(f"   Found {game_count} upcoming NBA games.")
            
            # Print the first game found just to prove we have data
            if game_count > 0:
                first_game = data[0]['home_team'] + " vs " + data[0]['away_team']
                print(f"   Sample Game: {first_game}")
        else:
            print(f"   ❌ Odds API Connection: FAILED (Server said: {response.text})")

    except Exception as e:
        print(f"   ❌ Odds API Connection: CRASHED ({e})")

    print("\n--- DIAGNOSTICS COMPLETE ---")

# --- KEEPS WINDOW OPEN ---
if __name__ == "__main__":
    run_diagnostics()
    input("\nPress ENTER to close this window...")

import requests
import json

# --- PASTE YOUR WEBHOOK URL HERE ---
WEBHOOK_URL = ""

def test_connection():
    print(f"Attempting to connect to: {WEBHOOK_URL[:30]}...")

    # 1. SIMPLE TEXT TEST (Easiest to pass)
    payload = {
        "content": "✅ **Test Message:** If you see this, the connection works."
    }

    # 2. Add Headers (Discord blocks requests without a User-Agent sometimes)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python-Requests/2.31"
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        
        # --- THE CRITICAL DEBUG STEP ---
        print(f"\nHTTP Status Code: {response.status_code}")
        print(f"Server Response: {response.text}")

        if response.status_code == 204:
            print("\nSUCCESS! Discord received the message (204 No Content is normal).")
        elif response.status_code == 400:
            print("\n❌ ERROR 400: Bad Request.")
            print("Check: Did you copy the Webhook URL correctly?")
        elif response.status_code == 401:
            print("\n❌ ERROR 401: Unauthorized.")
            print("Check: Delete the Webhook in Discord and create a new one.")
        elif response.status_code == 404:
            print("\n❌ ERROR 404: Not Found.")
            print("Check: The Webhook URL is invalid or the channel was deleted.")
        else:
            print(f"\n❌ UNKNOWN ERROR: {response.status_code}")

    except Exception as e:
        print(f"\n❌ CRASH: The script failed to send the request.\nError: {e}")

if __name__ == "__main__":
    test_connection()