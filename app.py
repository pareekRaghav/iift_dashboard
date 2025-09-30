import streamlit as st
from utils.auction_logic import *
import pandas as pd

AUCTIONEER_PASSWORD = "iiftadmin2025"
st.set_page_config(page_title="Live Auction Dashboard", layout="wide")

# 🎨 Custom CSS for background and logos
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1549921296-3a76d4b1574d"); /* Sports background */
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

# 🔒 View Selector
role = st.sidebar.radio("🔒 Select View", ["Team", "Auctioneer"])

# Password protection
if role == "Auctioneer":
    pwd = st.sidebar.text_input("Enter Admin Password", type="password")
    if pwd != AUCTIONEER_PASSWORD:
        st.warning("❌ Incorrect password. Access denied.")
        st.stop()


# Load Data
players_df = load_players()
teams_df = load_teams()
live_player = get_live_player(players_df)

# ============================== AUCTIONEER VIEW ==============================
if role == "Auctioneer":
    st.title("🏆 IIFT Sports Auction Dashboard (Auctioneer View)")

    # Display Current Player
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

    # Bid Buttons
    if live_player is not None:
        st.subheader("💰 Place a Bid")
        current_bid = live_player['Current Bid']
        bid_increment = 100 if (not pd.isna(current_bid) and current_bid >= 1000) else 50
        columns = st.columns(len(teams_df))
        for col, team in zip(columns, teams_df['Team Name']):
            with col:
                if st.button(f"Bid +{bid_increment} for {team}"):
                    place_bid(players_df, team, bid_increment)
                    st.rerun()

    # Sell Player
    if st.button("✅ Sell Player to Highest Bidder"):
        sell_player(players_df, teams_df)
        st.rerun()

    # Next Player
    if st.button("⏭️ Start Next Player"):
        start_next_player(players_df)
        st.rerun()

    # Team Summary
    st.subheader("📊 Team Summary")
    st.dataframe(teams_df)

    # Auction History
    st.subheader("📋 Auction History")
    sold = players_df[players_df['Status'] == 'Sold']
    st.dataframe(sold)

    # Upcoming Players
    st.subheader("⏳ Upcoming Players")
    upcoming = players_df[players_df['Status'] == 'Upcoming']
    st.dataframe(upcoming)

# ============================== TEAM VIEW ==============================
else:
    team_selected = st.sidebar.selectbox("Select Your Team", teams_df['Team Name'])
    team_info = teams_df[teams_df["Team Name"] == team_selected].iloc[0]

    st.title(f"🏁 {team_selected} Team Dashboard")

    st.markdown(f"### 💰 Remaining Budget: ₹{team_info['Remaining Budget']}")
    st.markdown(f"### 🧑‍🤝‍🧑 Players Bought: {team_info['Players Bought']}")
    st.markdown(f"### 🪙 Total Spent: ₹{team_info['Spent']}")

    # List of players bought
    bought_players = players_df[players_df["Sold To"] == team_selected]
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
