import streamlit as st
from utils.auction_logic import *
import pandas as pd

# ======================= CONFIG ==========================
AUCTIONEER_PASSWORD = "iiftadmin2025"
TEAM_PASSWORDS = {
    "Team A": "passA",
    "Team B": "passB",
    "Team C": "passC",
    "Team D": "passD",
    # Add more teams here
}

st.set_page_config(page_title="Live Auction Dashboard", layout="wide")

# =================== Custom CSS ==========================
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1549921296-3a76d4b1574d");
        background-size: cover;
        background-attachment: fixed;
    }
    .logo-left {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 100px;
        z-index: 1;
    }
    .logo-right {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 100px;
        z-index: 1;
    }
    </style>
""", unsafe_allow_html=True)

# =================== View Selector =========================
role = st.sidebar.radio("🔒 Select View", ["Public", "Team", "Auctioneer"])

# =================== Load Data =========================
players_df = load_players()
teams_df = load_teams()
live_player = get_live_player(players_df)

# =================== AUCTIONEER VIEW ========================
if role == "Auctioneer":
    pwd = st.sidebar.text_input("Enter Admin Password", type="password")
    if pwd != AUCTIONEER_PASSWORD:
        st.warning("❌ Incorrect password. Access denied.")
        st.stop()

    st.title("🏆 IIFT Sports Auction Dashboard (Auctioneer View)")

    if live_player is not None:
        st.subheader("🎯 Player on Auction")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(live_player['Image URL'], width=220)
        with col2:
            st.markdown(f"**Name:** {live_player['Player Name']}")
            st.markdown(f"**Sport:** {live_player['Sport']}")
            st.markdown(f"**Base Price:** ₹{live_player['Base Price']}")
            st.markdown(f"**Current Bid:** ₹{live_player['Current Bid']}")
            st.markdown(f"**Highest Bidder:** {live_player['Highest Bidder']}")
    else:
        st.warning("No live player. Start next auction.")

    # Manual Winner Selection
    if live_player is not None:
        st.subheader("✅ Finalize Auction")
        winner_team = st.selectbox("Select Winning Team", teams_df['Team Name'])
        final_bid = st.number_input("Enter Final Bid Amount (₹)", min_value=int(live_player['Base Price']), step=50)
        if st.button("💾 Confirm Sale"):
            sell_player_manual(players_df, teams_df, winner_team, final_bid)
            st.success(f"Player sold to {winner_team} for ₹{final_bid}")
            st.rerun()

    if st.button("⏭️ Start Next Player"):
        start_next_player(players_df)
        st.rerun()

    st.subheader("📊 Team Summary")
    st.dataframe(teams_df)

    st.subheader("📋 Auction History")
    sold = players_df[players_df['Status'] == 'Sold']
    st.dataframe(sold)

    st.subheader("⏳ Upcoming Players")
    upcoming = players_df[players_df['Status'] == 'Upcoming']
    st.dataframe(upcoming)

# =================== TEAM VIEW ========================
elif role == "Team":
    selected_team = st.sidebar.selectbox("Select Your Team", list(TEAM_PASSWORDS.keys()))
    pwd = st.sidebar.text_input("Enter Team Password", type="password")

    if TEAM_PASSWORDS.get(selected_team) != pwd:
        st.warning("❌ Incorrect password for team. Access denied.")
        st.stop()

    team_info = teams_df[teams_df["Team Name"] == selected_team].iloc[0]

    st.title(f"🏁 {selected_team} Team Dashboard")

    st.markdown(f"### 💰 Remaining Budget: ₹{team_info['Remaining Budget']}")
    st.markdown(f"### 🧑‍🤝‍🧑 Players Bought: {team_info['Players Bought']}")
    st.markdown(f"### 🪙 Total Spent: ₹{team_info['Spent']}")

    bought_players = players_df[players_df["Sold To"] == selected_team]
    st.subheader("📦 Players Bought")
    st.dataframe(bought_players[["Player Name", "Sport", "Final Price"]])

    st.subheader("👀 Current Player on Auction")
    if live_player is not None:
        st.markdown(f"**Name:** {live_player['Player Name']}")
        st.markdown(f"**Sport:** {live_player['Sport']}")
        st.markdown(f"**Current Bid:** ₹{live_player['Current Bid']}")
        st.markdown(f"**Highest Bidder:** {live_player['Highest Bidder']}")
        st.image(live_player['Image URL'], width=250)
    else:
        st.info("No player on auction currently.")

# =================== PUBLIC VIEW ========================
else:
    st.title("👀 Public Auction View")

    st.subheader("🎯 Current Player on Auction")
    if live_player is not None:
        st.markdown(f"**Name:** {live_player['Player Name']}")
        st.markdown(f"**Sport:** {live_player['Sport']}")
        st.markdown(f"**Current Bid:** ₹{live_player['Current Bid']}")
        st.markdown(f"**Highest Bidder:** {live_player['Highest Bidder']}")
        st.image(live_player['Image URL'], width=250)
    else:
        st.info("No player on auction currently.")

    st.subheader("📋 Players Sold So Far")
    sold = players_df[players_df['Status'] == 'Sold']
    st.dataframe(sold[["Player Name", "Sport", "Final Price", "Sold To"]])
