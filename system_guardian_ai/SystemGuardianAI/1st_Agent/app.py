"""
app.py — simple Streamlit UI for the flight finder agent.

SETUP:
    pip install streamlit

    Make sure this file sits in the SAME FOLDER as your agent file
    (the one with find_cheapest_flight in it). If your agent file is
    named "flight.py" instead of "flight_finder_agent.py", change the
    import line below to match.

RUN:
    streamlit run app.py
"""

import streamlit as st

# Adjust this import to match whatever you named your agent file.
# If your file is flight.py, use: from flight import find_cheapest_flight
from flight_finder_agent import find_cheapest_flight

st.set_page_config(page_title="Cheapest Flight Finder", page_icon="✈️")

st.title("✈️ Cheapest Flight Finder")
st.caption("Give it a route and date — the agent resolves airport codes, searches, and picks the cheapest option.")

with st.form("flight_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin_city = st.text_input("From (city)", placeholder="e.g. Patna")
    with col2:
        destination_city = st.text_input("To (city)", placeholder="e.g. Mumbai")

    date = st.text_input("Date (YYYY-MM-DD)", placeholder="e.g. 2026-08-21")

    submitted = st.form_submit_button("Find cheapest flight")

if submitted:
    if not origin_city or not destination_city or not date:
        st.error("Please fill in all three fields.")
    else:
        with st.spinner("Agent is searching and comparing flights..."):
            try:
                result = find_cheapest_flight(origin_city, destination_city, date)
                st.success("Done")
                st.markdown(result)
            except Exception as e:
                st.error(f"Something went wrong: {e}")