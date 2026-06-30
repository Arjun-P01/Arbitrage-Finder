import requests

SPORT_KEYS = [
    "basketball_nba",
    "baseball_mlb",
]

ALLOWED_BOOKS = {
    "draftkings",
    "fanduel",
    "betmgm",
    "betrivers",
    "fanatics",
    "williamhill_us",
}

def fetch_odds(api_key, sport_key=None):
    all_data = []
    url = f"https://api.theoddsapi.com/odds/?apiKey={api_key}"
    
    if sport_key:
        url += f"&sport_key={sport_key}"
    
    response = requests.get(url)
    data = response.json()
    
    if data.get('success') and data.get('data'):
        all_data.extend(data['data'])
    return all_data

def fetch_all_odds(api_key):
    all_data = []
    
    for sport_key in SPORT_KEYS:
        data = fetch_odds(api_key, sport_key)
        print(f"{sport_key}: {len(data)} games fetched.")
        all_data.extend(data)
    
    return all_data

def american_to_decimal(odds):
    if odds > 0:
        return (odds / 100) + 1
    else:
        return (100 / abs(odds)) + 1

def get_best_odds(data):
    best_odds = {}
    
    for book in data['books']:
        book_name = book['book']

        if book_name not in ALLOWED_BOOKS:
            continue

        if book['market'] == 'h2h':  # Only consider head-to-head markets
            
            for name in book['outcomes']:
                team = name['name']
                odds = name['price']
                decimal_odds = american_to_decimal(odds)
                
                if team not in best_odds or decimal_odds > best_odds[team][1]:
                    best_odds[team] = (book_name, decimal_odds)
                
    return best_odds

def check_arbitrage(best_odds):
    total_inverse_odds = sum(1/odds[1] for odds in best_odds.values())
    return total_inverse_odds < 1, total_inverse_odds

def find_arbitrage_from_api(data, total_budget) -> list:
    arbitrage_opportunities = []

    for game in data:
        best_odds = get_best_odds(game)
        teams = list(best_odds.keys())
        odds_a = best_odds[teams[0]][1]
        odds_b = best_odds[teams[1]][1]
        is_arbitrage, total_inverse_odds = check_arbitrage(best_odds)

        if is_arbitrage:
            stake_a = round(total_budget / (1 + odds_a/odds_b), 2)
            stake_b = round(total_budget / (1 + odds_b/odds_a), 2)
            arbitrage_opportunities.append({
                "home_team": game['home_team'],
                "away_team": game['away_team'],
                "league": game['league'],
                "start_time": game['start_time'],
                "best_odds": best_odds,
                "stakes": {teams[0]: stake_a, teams[1]: stake_b},
                "total_inverse_odds": total_inverse_odds
            })

    return arbitrage_opportunities