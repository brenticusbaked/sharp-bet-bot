import requests
import time
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = 'YOUR_ODDS_API_KEY'  # Paste your key from the-odds-api.com
DISCORD_WEBHOOK_URL = 'YOUR_DISCORD_WEBHOOK_URL' # Paste your Discord Webhook URL here

SPORT = 'basketball_nba'      
REGIONS = 'us'                 
MARKETS = 'h2h'                
ODDS_FORMAT = 'american'       

def send_discord_alert(title, details, color=65280):
    """Sends a formatted embed message to Discord."""
    data = {
        "embeds": [
            {
                "title": title,
                "description": details,
                "color": color,  # Green = 65280, Red = 16711680
                "footer": {"text": f"SharpBot • {datetime.now().strftime('%H:%M:%S')}"}
            }
        ]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Error sending to Discord: {e}")

def fetch_odds():
    print(f"Fetching odds for {SPORT}...")
    try:
        response = requests.get(
            f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
            params={
                'api_key': API_KEY,
                'regions': REGIONS,
                'markets': MARKETS,
                'oddsFormat': ODDS_FORMAT,
                'dateFormat': 'iso',
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code}")
            send_discord_alert("API Error", f"Status Code: {response.status_code}", 16711680)
            return None
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def find_value_bets(games):
    bets_found = 0
    
    for game in games:
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Collect all odds to find the average
        home_odds = []
        away_odds = []
        
        for book in game['bookmakers']:
            for market in book['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        price = outcome['price']
                        if outcome['name'] == home_team:
                            home_odds.append(price)
                        elif outcome['name'] == away_team:
                            away_odds.append(price)

        if not home_odds or not away_odds:
            continue

        avg_home = sum(home_odds) / len(home_odds)
        avg_away = sum(away_odds) / len(away_odds)

        # Scan for outliers (Value Bets)
        for book in game['bookmakers']:
            book_name = book['title']
            for market in book['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        price = outcome['price']
                        team = outcome['name']
                        
                        # LOGIC: If price is significantly better than average
                        # (Adjust this threshold based on what you consider "Sharp")
                        avg_price = avg_home if team == home_team else avg_away
                        
                        # Threshold: Finding a price +15 points better than average (e.g., +130 vs +115)
                        if price > avg_price + 15: 
                            bets_found += 1
                            msg = (f"**Matchup:** {away_team} @ {home_team}\n"
                                   f"**Bet:** {team} Moneyline\n"
                                   f"**Book:** {book_name} @ {price}\n"
                                   f"**Mkt Avg:** {int(avg_price)}")
                            
                            print(f"Sending Alert: {team} ({price})")
                            send_discord_alert("💎 Sharp Value Found", msg)
                            time.sleep(1) # Prevent Discord rate limits

    if bets_found == 0:
        print("No bets found meeting criteria.")
        # Optional: Send a "Scan Complete" message so you know it ran
        # send_discord_alert("Scan Complete", "No value bets found this run.", 33023)

if __name__ == "__main__":
    # Send a startup ping so you know the link works
    send_discord_alert("🤖 Bot Startup", "SharpBot is online and scanning...", 3447003)
    
    data = fetch_odds()
    if data:
        find_value_bets(data)