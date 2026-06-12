import streamlit as st
from arbitrage import find_arbitrage
import pandas as pd

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