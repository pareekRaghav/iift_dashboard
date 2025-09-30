import pandas as pd

# File paths
PLAYER_FILE = "data/players.csv"
TEAM_FILE = "data/teams.csv"

# Load CSVs
def load_players():
    return pd.read_csv(PLAYER_FILE)

def load_teams():
    return pd.read_csv(TEAM_FILE)

def save_players(df):
    df.to_csv(PLAYER_FILE, index=False)

def save_teams(df):
    df.to_csv(TEAM_FILE, index=False)

# Get current player
def get_live_player(df):
    live = df[df['Status'] == 'Live']
    return live.iloc[0] if not live.empty else None

# Move to next player
def start_next_player(df):
    upcoming = df[df['Status'] == 'Upcoming']
    if not upcoming.empty:
        idx = upcoming.index[0]
        df.at[idx, 'Status'] = 'Live'
        save_players(df)

# Place a bid
def place_bid(player_df, team_name, bid_increment):
    idx = player_df[player_df['Status'] == 'Live'].index[0]
    current_bid = player_df.at[idx, 'Current Bid']
    base_price = player_df.at[idx, 'Base Price']
    current_bid = base_price if pd.isna(current_bid) else current_bid
    new_bid = current_bid + bid_increment
    player_df.at[idx, 'Current Bid'] = new_bid
    player_df.at[idx, 'Highest Bidder'] = team_name
    save_players(player_df)

# Sell player
def sell_player(player_df, team_df):
    idx = player_df[player_df['Status'] == 'Live'].index[0]
    team_name = player_df.at[idx, 'Highest Bidder']
    final_price = player_df.at[idx, 'Current Bid']

    if pd.isna(team_name) or pd.isna(final_price):
        return  # No valid bid placed

    # Update player
    player_df.at[idx, 'Sold To'] = team_name
    player_df.at[idx, 'Final Price'] = final_price
    player_df.at[idx, 'Status'] = 'Sold'
    save_players(player_df)

    # Update team
    t_idx = team_df[team_df['Team Name'] == team_name].index[0]
    team_df.at[t_idx, 'Spent'] += final_price
    team_df.at[t_idx, 'Remaining Budget'] -= final_price
    team_df.at[t_idx, 'Players Bought'] += 1
    save_teams(team_df)
