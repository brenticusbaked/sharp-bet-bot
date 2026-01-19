import requests
import json

# --- PASTE YOUR WEBHOOK URL HERE ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1461961795022618799/42QMeyZpcxv1nAt0ui4v15prTzLNWrVnAhoqSm-jeUJsmeDANIb6l_3lwqv7zwujnd58"

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