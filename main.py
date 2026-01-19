import requests
import os
from dotenv import load_dotenv

# 1. Load the secrets from the .env file
load_dotenv()

# 2. Get the keys securely
API_KEY = os.getenv('ODDS_API_KEY')
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# --- Check if they loaded correctly (Optional Debugging) ---
if not API_KEY or not WEBHOOK_URL:
    print("❌ Error: Could not load keys. Check your .env file.")
    exit()
else:
    print("✅ Keys loaded securely.")

# --- THE REST OF YOUR CODE BELOW ---
def send_discord_alert(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})

if __name__ == "__main__":
    send_discord_alert("This message was sent using hidden keys!")