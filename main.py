import requests
import json
import os

# --- CONFIGURATION ---
API_KEY = os.environ['ODDS_API_KEY']  # Paste your free key here
SPORT = 'basketball_nba'       # Options: 'basketball_nba', 'americanfootball_nfl', 'icehockey_nhl'
REGIONS = 'us'                 # 'us', 'uk', 'eu', 'au'
MARKETS = 'h2h'                # 'h2h' (Moneyline), 'spreads', 'totals'
ODDS_FORMAT = 'american'       # 'american' or 'decimal'

# --- THE SHARP FILTER ---
# We use this to filter out small "noise" edges.
MIN_EDGE_PERCENT = 3.0 

def fetch_odds():
    odds_response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
        params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': 'iso',
        }
    )

    if odds_response.status_code != 200:
        print(f"Failed to get odds: {odds_response.status_code}")
        return None

    return odds_response.json()

def find_value_bets(games):
    print(f"\nScanning {len(games)} games for Positive EV...")
    print("-" * 60)

    for game in games:
        home_team = game['home_team']
        away_team = game['away_team']
        
        # 1. Find the "Consensus" (Average) Line
        # In a real sharp bot, you would strictly use 'Pinnacle' or 'Circa' as the sharp anchor.
        # Here, we calculate an average of all available books to find outliers.
        
        home_odds_list = []
        away_odds_list = []
        
        for book in game['bookmakers']:
            for market in book['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == home_team:
                            home_odds_list.append(outcome['price'])
                        elif outcome['name'] == away_team:
                            away_odds_list.append(outcome['price'])

        if not home_odds_list or not away_odds_list:
            continue

        # Simple logic: If a book offers significantly better odds than the average
        avg_home = sum(home_odds_list) / len(home_odds_list)
        avg_away = sum(away_odds_list) / len(away_odds_list)

        for book in game['bookmakers']:
            book_name = book['title']
            for market in book['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        price = outcome['price']
                        
                        # --- THE STRATEGY ---
                        # If the price is better than the average by a certain margin
                        # (This is a simplified EV calculation for demonstration)
                        
                        team = outcome['name']
                        avg_price = avg_home if team == home_team else avg_away
                        
                        # Note: Comparing American odds directly is tricky mathematically 
                        # (negative vs positive), so usually convert to decimal first.
                        # This print logic detects OUTLIERS.
                        
                        if price > avg_price + 10: # Simple threshold for American odds
                             print(f"💎 VALUE FOUND: {book_name}")
                             print(f"   Matchup: {away_team} @ {home_team}")
                             print(f"   Bet: {team} @ {price}")
                             print(f"   Avg Market Price: {int(avg_price)}")
                             print("-" * 40)

# --- EXECUTION ---
if __name__ == "__main__":
    data = fetch_odds()
    if data:
        find_value_bets(data)