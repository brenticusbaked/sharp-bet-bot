import requests
import os
import sys

# --- CONFIGURATION ---
API_KEY = os.environ.get("ODDS_API_KEY")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
SPORT = 'americanfootball_nfl' # Change to 'basketball_nba', 'icehockey_nhl', etc.
REGIONS = 'us'
MARKETS = 'h2h' # Head to Head (Moneyline)
ODDS_FORMAT = 'american'
DATE_FORMAT = 'iso'

# Set this to your standard total bet size (e.g., $100, $500)
TOTAL_INVESTMENT = 100 

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

def american_to_decimal(american_odds):
    """Converts American odds to Decimal odds."""
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1

def calculate_stakes(total_investment, dec_home, dec_away):
    """
    Calculates how much to bet on each side to guarantee equal profit.
    """
    # Implied probabilities
    imp_home = 1 / dec_home
    imp_away = 1 / dec_away
    
    # Total implied probability (should be < 1.0 for arb)
    total_implied = imp_home + imp_away
    
    # Calculate stakes proportional to the probabilities
    stake_home = (imp_home / total_implied) * total_investment
    stake_away = (imp_away / total_implied) * total_investment
    
    # Calculate guaranteed profit
    # Revenue is usually roughly equal regardless of who wins
    revenue = stake_home * dec_home
    profit = revenue - total_investment
    
    return stake_home, stake_away, profit

def find_arbitrage(games):
    alerts_sent = 0
    
    for game in games:
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Track best odds
        best_home_price = -float('inf')
        best_home_book = ""
        best_away_price = -float('inf')
        best_away_book = ""
        
        # 1. Scan books for best lines
        for bookmaker in game['bookmakers']:
            market = next((m for m in bookmaker['markets'] if m['key'] == 'h2h'), None)
            if not market: continue
            
            for outcome in market['outcomes']:
                price = outcome['price']
                if outcome['name'] == home_team:
                    if price > best_home_price:
                        best_home_price = price
                        best_home_book = bookmaker['title']
                elif outcome['name'] == away_team:
                    if price > best_away_price:
                        best_away_price = price
                        best_away_book = bookmaker['title']

        # 2. Check if valid odds were found
        if best_home_price == -float('inf') or best_away_price == -float('inf'):
            continue

        # 3. Calculate Arbitrage
        dec_home = american_to_decimal(best_home_price)
        dec_away = american_to_decimal(best_away_price)
        
        arbitrage_sum = (1 / dec_home) + (1 / dec_away)
        
        # 4. If Sum < 1.0, we have an Arb!
        if arbitrage_sum < 1.0:
            stake_home, stake_away, profit = calculate_stakes(TOTAL_INVESTMENT, dec_home, dec_away)
            roi_percent = (profit / TOTAL_INVESTMENT) * 100
            
            msg = (
                f"🚨 **ARBITRAGE FOUND** ({roi_percent:.2f}% Profit)\n"
                f"Game: {home_team} vs {away_team}\n"
                f"--------------------------------\n"
                f"💰 **Total Bet: ${TOTAL_INVESTMENT}** -> Profit: **${profit:.2f}**\n"
                f"--------------------------------\n"
                f"1️⃣ **Bet ${stake_home:.2f}** on {home_team} ({best_home_price})\n"
                f"   @ {best_home_book}\n\n"
                f"2️⃣ **Bet ${stake_away:.2f}** on {away_team} ({best_away_price})\n"
                f"   @ {best_away_book}\n"
                f"--------------------------------"
            )
            send_alert(msg)
            alerts_sent += 1

    if alerts_sent == 0:
        print("No arbitrage opportunities found.")
    else:
        print(f"Sent {alerts_sent} arbitrage alerts.")

if __name__ == "__main__":
    print("Starting Arbitrage Scanner...")
    data = fetch_odds()
    find_arbitrage(data)
    print("Scan complete.")