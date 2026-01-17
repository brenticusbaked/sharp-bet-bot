import requests
import os
import sys

# --- CONFIGURATION ---
# We grab these from GitHub Secrets (explained in Phase 3)
API_KEY = os.environ.get("ODDS_API_KEY")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
SPORT = 'americanfootball_nfl'
REGIONS = 'us'
MARKETS = 'h2h' # Moneyline
ODDS_FORMAT = 'american'
DATE_FORMAT = 'iso'

def fetch_odds():
    if not API_KEY:
        print("Error: API Key is missing.")
        sys.exit(1)

    url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds'
    params = {
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching odds: {e}")
        return []

def send_alert(message):
    if not WEBHOOK_URL:
        print("Alert skipped: No Webhook URL found.")
        return
    
    data = {"content": message}
    requests.post(WEBHOOK_URL, json=data)

def find_sharp_bets(games):
    alerts_sent = 0
    
    for game in games:
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Dictionary to store odds for this game: {'DraftKings': -110, 'Pinnacle': -130}
        home_odds = {}
        
        for bookmaker in game['bookmakers']:
            book_name = bookmaker['title']
            # Find the market for h2h (moneyline)
            market = next((m for m in bookmaker['markets'] if m['key'] == 'h2h'), None)
            
            if market:
                for outcome in market['outcomes']:
                    if outcome['name'] == home_team:
                        home_odds[book_name] = outcome['price']

        # --- THE SHARP LOGIC ---
        # Look for a difference between a "Sharp" book (e.g., Pinnacle/Unibet) and others
        # Note: The Odds API sometimes lists Pinnacle under distinct keys or regions (eu)
        
        # Simplified Example: Find discrepancies > 20 points in American odds
        if not home_odds: 
            continue

        best_price = max(home_odds.values())
        worst_price = min(home_odds.values())
        
        # If the gap between books is massive (Arbitrage or strong opinion)
        if (best_price - worst_price) >= 20: 
            msg = f"🚨 **SHARP ALERT**: {home_team} vs {away_team}\n" \
                  f"Spread detected: {worst_price} to {best_price}\n" \
                  f"Check books: {list(home_odds.keys())}"
            send_alert(msg)
            alerts_sent += 1

    if alerts_sent == 0:
        print("No sharp bets found in this run.")
    else:
        print(f"Sent {alerts_sent} alerts.")

if __name__ == "__main__":
    print("Starting Sharp Bot Scanner...")
    data = fetch_odds()
    find_sharp_bets(data)
    print("Scan complete.")