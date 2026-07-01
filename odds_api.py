import requests

SPORT_KEYS = [
    "baseball_mlb",
    "basketball_nba",
    "soccer_usa_mls",
]

ALLOWED_BOOKS = {
    "bovada",
    "betonlineag",
    "mybookieag",
    "betus",
    "lowvig",
}

BASE_URL = "https://api.the-odds-api.com/v4/sports"


def fetch_odds(api_key, sport_key):
    url = (
        f"{BASE_URL}/{sport_key}/odds/"
        f"?apiKey={api_key}&regions=us&markets=h2h,spreads,totals&oddsFormat=american"
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


def find_market_arbitrage(game, market_key, total_budget):
    """Find arbitrage for a specific market within one game."""
    outcome_groups = {}

    for bookmaker in game.get("bookmakers", []):
        if bookmaker["key"] not in ALLOWED_BOOKS:
            continue
        for market in bookmaker.get("markets", []):
            if market["key"] != market_key:
                continue
            for outcome in market["outcomes"]:
                name = outcome["name"]
                odds = american_to_decimal(outcome["price"])

                if market_key == "h2h":
                    group_key = "main"
                elif market_key == "totals":
                    group_key = outcome.get("point")
                elif market_key == "spreads":
                    group_key = abs(outcome.get("point", 0))

                if group_key not in outcome_groups:
                    outcome_groups[group_key] = {}
                if name not in outcome_groups[group_key] or odds > outcome_groups[group_key][name][1]:
                    outcome_groups[group_key][name] = (bookmaker["key"], odds)

    opportunities = []
    for group_key, best_odds in outcome_groups.items():
        if len(best_odds) < 2:
            continue
        outcomes = list(best_odds.keys())
        odds_a = best_odds[outcomes[0]][1]
        odds_b = best_odds[outcomes[1]][1]
        total_inverse = sum(1 / v[1] for v in best_odds.values())

        if total_inverse < 1:
            stake_a = round(total_budget / (1 + odds_a / odds_b), 2)
            stake_b = round(total_budget / (1 + odds_b / odds_a), 2)

            if market_key == "h2h":
                market_label = "Moneyline"
            elif market_key == "totals":
                market_label = f"Total O/U {group_key}"
            else:
                market_label = f"Spread ±{group_key}"

            opportunities.append({
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "league": game.get("sport_title", ""),
                "start_time": game.get("commence_time", ""),
                "market": market_label,
                "best_odds": best_odds,
                "stakes": {outcomes[0]: stake_a, outcomes[1]: stake_b},
                "total_inverse_odds": total_inverse,
            })
    return opportunities


def find_arbitrage_from_api(data, total_budget):
    all_opportunities = []
    for game in data:
        for market_key in ["h2h", "totals", "spreads"]:
            opps = find_market_arbitrage(game, market_key, total_budget)
            all_opportunities.extend(opps)
    return all_opportunities
