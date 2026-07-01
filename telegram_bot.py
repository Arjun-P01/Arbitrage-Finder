import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BOOK_URLS = {
    "fanduel": "https://sportsbook.fanduel.com",
    "draftkings": "https://sportsbook.draftkings.com",
    "betmgm": "https://sports.betmgm.com",
    "williamhill_us": "https://sportsbook.caesars.com",
    "betrivers": "https://www.betrivers.com",
    "fanatics": "https://sportsbook.fanatics.com",
    "pointsbet": "https://pointsbet.com",
    "bet365": "https://www.bet365.com",
}

def get_book_link(book_name):
    url = BOOK_URLS.get(book_name.lower(), None)
    if url:
        return f'<a href="{url}">{book_name.title()}</a>'
    return book_name.title()

def send_alert(opportunity, total_budget):
    teams = list(opportunity['best_odds'].keys())
    team_a, team_b = teams[0], teams[1]
    book_a, odds_a = opportunity['best_odds'][team_a]
    book_b, odds_b = opportunity['best_odds'][team_b]
    stake_a = opportunity['stakes'][team_a]
    stake_b = opportunity['stakes'][team_b]
    net_profit = round(stake_a * odds_a - total_budget, 2)
    profit_pct = round((net_profit / total_budget) * 100, 2)

    home = opportunity.get('home_team', team_a)
    away = opportunity.get('away_team', team_b)
    league = opportunity.get('league', '')
    market = opportunity.get('market', 'Moneyline')

    message = (
        f"⚡ <b>Arbitrage Opportunity</b>\n\n"
        f"🏆 {league}: {away} @ {home}\n"
        f"📋 Market: {market}\n\n"
        f"Bet 1: <b>{team_a}</b>\n"
        f"  Book: {get_book_link(book_a)}\n"
        f"  Odds: {round(odds_a, 3)}\n"
        f"  Stake: ${stake_a}\n\n"
        f"Bet 2: <b>{team_b}</b>\n"
        f"  Book: {get_book_link(book_b)}\n"
        f"  Odds: {round(odds_b, 3)}\n"
        f"  Stake: ${stake_b}\n\n"
        f"💰 Net Profit: <b>${net_profit} ({profit_pct}%)</b>\n"
        f"📊 Budget: ${total_budget}"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
        }
    )
    return response.ok
