import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BOOK_URLS = {
    "bovada": "https://www.bovada.lv",
    "betonlineag": "https://www.betonline.ag",
    "mybookieag": "https://mybookie.ag",
    "betus": "https://www.betus.com.pa",
    "lowvig": "https://www.lowvig.ag",
    "fanduel": "https://sportsbook.fanduel.com",
    "draftkings": "https://sportsbook.draftkings.com",
    "betmgm": "https://sports.betmgm.com",
    "williamhill_us": "https://sportsbook.caesars.com",
    "betrivers": "https://www.betrivers.com",
    "fanatics": "https://sportsbook.fanatics.com",
}

def get_book_link(book_name):
    url = BOOK_URLS.get(book_name.lower(), None)
    if url:
        return f'<a href="{url}">{book_name.title()}</a>'
    return book_name.title()

def send_alert(opportunity, total_budget):
    home = opportunity.get('home_team', '')
    away = opportunity.get('away_team', '')
    league = opportunity.get('league', '')
    market = opportunity.get('market', 'Moneyline')
    profit_pct = round((1 - opportunity['total_inverse_odds']) * 100, 2)

    bets_text = ""
    for i, (name, (book, odds)) in enumerate(opportunity['best_odds'].items(), 1):
        stake = opportunity['stakes'][name]
        bets_text += (
            f"Bet {i}: <b>{name}</b>\n"
            f"  Book: {get_book_link(book)}\n"
            f"  Odds: {round(odds, 3)}\n"
            f"  Stake: ${stake}\n\n"
        )

    net_profit = round(total_budget * profit_pct / 100, 2)

    message = (
        f"⚡ <b>Arbitrage Opportunity</b>\n\n"
        f"🏆 {league}: {away} @ {home}\n"
        f"📋 Market: {market}\n\n"
        f"{bets_text}"
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
    if response.ok:
        return response.json()["result"]["message_id"], message
    return None, message


def mark_gone(message_id, original_text):
    gone_text = "🔴 <b>GONE</b>\n\n" + original_text
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "message_id": message_id,
            "text": gone_text,
            "parse_mode": "HTML",
        }
    )
