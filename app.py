import streamlit as st
from arbitrage import find_arbitrage
import pandas as pd
from odds_api import find_arbitrage_from_api, fetch_odds

st.title("Arbitrage Finder")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

budget_input = st.text_input("Enter total budget for arbitrage (e.g. 100)")

if uploaded_file is not None and budget_input:
    try:
        total_budget = float(budget_input)
        df = pd.read_csv(uploaded_file)
        arb = find_arbitrage(df, total_budget)
        if not arb.empty:
            st.success("Arbitrage opportunities found!")
            st.dataframe(arb, use_container_width=True, hide_index=True)
        else:
            st.info("No arbitrage opportunities found in the uploaded file.")
    except ValueError:
        st.error("Please enter a valid number for the budget.")

total_budget = float(budget_input) if budget_input else 100  # Default to 100 if no input

if st.button("Fetch Odds"):
    api_key = st.secrets["ODDS_API_KEY"]
    if api_key:
        odds_data = fetch_odds(api_key)
        if odds_data:
            arb = find_arbitrage_from_api(odds_data, total_budget)
            st.success("Odds fetched successfully!")
            st.json(odds_data)
            st.json(arb)
        else:
            st.error("Failed to fetch odds.")