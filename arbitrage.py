import pandas as pd

def find_arbitrage(df, total_budget):
    df['Arb_Pct'] = 1/df['Odds 1'] + 1/df['Odds 2']

    arbitrage_opportunities = df[df['Arb_Pct'] < 1]  # Show only arbitrage opportunities

    odds_a = arbitrage_opportunities['Odds 1']
    odds_b = arbitrage_opportunities['Odds 2'] 

    stake_a = round(total_budget / (1 + (odds_a / odds_b)), 2)
    stake_b = round(total_budget - stake_a, 2)

    arbitrage_opportunities['Stake A'] = stake_a
    arbitrage_opportunities['Stake B'] = stake_b
    arbitrage_opportunities['Net_Profit'] = round(stake_a * odds_a - total_budget, 2)

    return arbitrage_opportunities