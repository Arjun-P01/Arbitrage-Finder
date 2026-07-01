import requests

SPORT_KEYS = [
    "baseball_mlb",
    "basketball_nba",
    "soccer_usa_mls",
    "soccer_fifa_world_cup",
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


def find_h2h_totals_arbitrage(game, market_key, total_budget):
    """Find arb for h2h or totals — both have two genuinely opposite outcomes."""
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
                group_key = "main" if market_key == "h2h" else outcome.get("point")

                if group_key not in outcome_groups:
                    outcome_groups[group_key] = {}
                if name not in outcome_groups[group_key] or odds > outcome_groups[group_key][name][1]:
                    outcome_groups[group_key][name] = (bookmaker["key"], odds)

    opportunities = []
    for group_key, best_odds in outcome_groups.items():
        if len(best_odds) < 2:
            continue
        outcomes = list(best_odds.keys())
        odds_a, odds_b = best_odds[outcomes[0]][1], best_odds[outcomes[1]][1]
        total_inverse = sum(1 / v[1] for v in best_odds.values())

        if total_inverse < 1:
            label = "Moneyline" if market_key == "h2h" else f"Total O/U {group_key}"
            opportunities.append({
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "league": game.get("sport_title", ""),
                "start_time": game.get("commence_time", ""),
                "market": label,
                "best_odds": best_odds,
                "stakes": {
                    outcomes[0]: round(total_budget / (1 + odds_a / odds_b), 2),
                    outcomes[1]: round(total_budget / (1 + odds_b / odds_a), 2),
                },
                "total_inverse_odds": total_inverse,
            })
    return opportunities


def find_spread_arbitrage(game, total_budget):
    """Find arb for spreads — must pair the SAME team at +X vs -X across books."""
    # (team, abs_line) -> {'+': (book, odds), '-': (book, odds)}
    spread_groups = {}

    for bookmaker in game.get("bookmakers", []):
        if bookmaker["key"] not in ALLOWED_BOOKS:
            continue
        for market in bookmaker.get("markets", []):
            if market["key"] != "spreads":
                continue
            for outcome in market["outcomes"]:
                name = outcome["name"]
                point = outcome.get("point", 0)
                abs_point = abs(point)
                odds = american_to_decimal(outcome["price"])
                side = "+" if point > 0 else "-"
                key = (name, abs_point)

                if key not in spread_groups:
                    spread_groups[key] = {}
                if side not in spread_groups[key] or odds > spread_groups[key][side][1]:
                    spread_groups[key][side] = (bookmaker["key"], odds)

    opportunities = []
    for (team, abs_point), sides in spread_groups.items():
        if "+" not in sides or "-" not in sides:
            continue
        book_plus, odds_plus = sides["+"]
        book_minus, odds_minus = sides["-"]
        if book_plus == book_minus:
            continue
        total_inverse = 1 / odds_plus + 1 / odds_minus

        if total_inverse < 1:
            name_plus = f"{team} +{abs_point}"
            name_minus = f"{team} -{abs_point}"
            opportunities.append({
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "league": game.get("sport_title", ""),
                "start_time": game.get("commence_time", ""),
                "market": f"Spread {team} ±{abs_point}",
                "best_odds": {
                    name_plus: (book_plus, odds_plus),
                    name_minus: (book_minus, odds_minus),
                },
                "stakes": {
                    name_plus: round(total_budget / (1 + odds_plus / odds_minus), 2),
                    name_minus: round(total_budget / (1 + odds_minus / odds_plus), 2),
                },
                "total_inverse_odds": total_inverse,
            })
    return opportunities


def find_arbitrage_from_api(data, total_budget):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    all_opportunities = []
    for game in data:
        start = game.get("commence_time", "")
        if start and datetime.fromisoformat(start.replace("Z", "+00:00")) < now:
            continue  # skip live/in-progress games
        all_opportunities.extend(find_h2h_totals_arbitrage(game, "h2h", total_budget))
        all_opportunities.extend(find_h2h_totals_arbitrage(game, "totals", total_budget))
        all_opportunities.extend(find_spread_arbitrage(game, total_budget))
    return all_opportunities
