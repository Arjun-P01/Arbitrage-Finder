import requests

SPORT_KEYS = [
    "baseball_mlb",
    "basketball_nba",
    "soccer_usa_mls",
]

ALLOWED_BOOKS = {
    "draftkings",
    "fanduel",
    "betmgm",
    "betrivers",
    "fanatics",
    "williamhill_us",
}

BASE_URL = "https://api.the-odds-api.com/v4/sports"


def fetch_odds(api_key, sport_key):
    url = (
        f"{BASE_URL}/{sport_key}/odds/"
        f"?apiKey={api_key}&regions=us&markets=h2h&oddsFormat=american"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return []
    return response.json()


def fetch_all_odds(api_key):
    all_data = []
    for sport_key in SPORT_KEYS:
        games = fetch_odds(api_key, sport_key)
        all_data.extend(games)
    return all_data


def american_to_decimal(odds):
    if odds > 0:
        return (odds / 100) + 1
    else:
        return (100 / abs(odds)) + 1


def get_best_odds(game):
    best_odds = {}
    for bookmaker in game.get("bookmakers", []):
        if bookmaker["key"] not in ALLOWED_BOOKS:
            continue
        for market in bookmaker.get("markets", []):
            if market["key"] != "h2h":
                continue
            for outcome in market["outcomes"]:
                team = outcome["name"]
                decimal_odds = american_to_decimal(outcome["price"])
                if team not in best_odds or decimal_odds > best_odds[team][1]:
                    best_odds[team] = (bookmaker["key"], decimal_odds)
    return best_odds


def check_arbitrage(best_odds):
    total_inverse_odds = sum(1 / odds[1] for odds in best_odds.values())
    return total_inverse_odds < 1, total_inverse_odds


def find_arbitrage_from_api(data, total_budget):
    arbitrage_opportunities = []
    for game in data:
        best_odds = get_best_odds(game)
        if len(best_odds) < 2:
            continue
        teams = list(best_odds.keys())
        odds_a = best_odds[teams[0]][1]
        odds_b = best_odds[teams[1]][1]
        is_arbitrage, total_inverse_odds = check_arbitrage(best_odds)
        if is_arbitrage:
            stake_a = round(total_budget / (1 + odds_a / odds_b), 2)
            stake_b = round(total_budget / (1 + odds_b / odds_a), 2)
            arbitrage_opportunities.append({
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "league": game.get("sport_title", ""),
                "start_time": game.get("commence_time", ""),
                "best_odds": best_odds,
                "stakes": {teams[0]: stake_a, teams[1]: stake_b},
                "total_inverse_odds": total_inverse_odds,
            })
    return arbitrage_opportunities
