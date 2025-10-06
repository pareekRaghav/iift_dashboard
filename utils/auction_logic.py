import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# === Google Sheets Setup ===
def get_gsheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"], scopes=scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("IIFT Auction Sheet")  # Your actual Google Sheet name
    return sheet

def load_players():
    ws = get_gsheet().worksheet("Players")
    df = pd.DataFrame(ws.get_all_records())
    return df

def load_teams():
    ws = get_gsheet().worksheet("Teams")
    df = pd.DataFrame(ws.get_all_records())
    return df

def get_live_player(players_df):
    live = players_df[players_df["Status"] == "Live"]
    if not live.empty:
        return live.iloc[0]
    return None

def sell_player_manual(players_df, teams_df, winner_team, final_bid):
    sheet = get_gsheet()
    ws_players = sheet.worksheet("Players")
    ws_teams = sheet.worksheet("Teams")

    # Update player status
    live_player = get_live_player(players_df)
    if live_player is not None:
        row_idx = players_df.index[players_df["Player Name"] == live_player["Player Name"]][0] + 2
        ws_players.update(f"C{row_idx}", "Sold")
        ws_players.update(f"E{row_idx}", winner_team)
        ws_players.update(f"F{row_idx}", final_bid)

    # Update team info
    team_row = teams_df.index[teams_df["Team Name"] == winner_team][0] + 2
    new_spent = int(teams_df.loc[team_row - 2, "Spent"]) + int(final_bid)
    new_remaining = int(teams_df.loc[team_row - 2, "Remaining Budget"]) - int(final_bid)
    new_players_bought = int(teams_df.loc[team_row - 2, "Players Bought"]) + 1

    ws_teams.update(f"B{team_row}", new_remaining)
    ws_teams.update(f"C{team_row}", new_players_bought)
    ws_teams.update(f"D{team_row}", new_spent)

def start_next_player(players_df):
    sheet = get_gsheet()
    ws = sheet.worksheet("Players")

    # Mark current Live player as Sold if not already
    current_live = players_df[players_df["Status"] == "Live"]
    if not current_live.empty:
        idx = players_df.index[players_df["Status"] == "Live"][0] + 2
        ws.update(f"C{idx}", "Sold")

    # Start next "Upcoming" player
    upcoming = players_df[players_df["Status"] == "Upcoming"]
    if not upcoming.empty:
        next_idx = players_df.index[players_df["Status"] == "Upcoming"][0] + 2
        ws.update(f"C{next_idx}", "Live")
