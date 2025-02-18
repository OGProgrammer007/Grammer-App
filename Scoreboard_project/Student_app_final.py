import streamlit as st
import pandas as pd
import os
from PIL import Image
import numpy as np
import time

# Excel file path
EXCEL_FILE = "Scoreboard_project/scores_with_avatars.xlsx"

# Colors
COLORS = {
    "gold": "#FFD700",
    "silver": "#C0C0C0",
    "bronze": "#CD7F32",
    "blue": "#6495ED",
    "white": "#FFFFFF"
}

# Folder where avatar images are stored in the repository
AVATAR_FOLDER = "Scoreboard_project/"

# Funky music file path
MUSIC_FILE = "Scoreboard_project/funky_music.mp3"

# Load player scores from Excel
def load_scores():
    if not os.path.exists(EXCEL_FILE):
        st.error(f"Error: File '{EXCEL_FILE}' not found.")
        return pd.DataFrame(columns=["Name", "Score", "Avatar"])

    try:
        df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
        df = df.dropna(subset=["Name", "Score"])  # Remove empty rows
        df["Score"] = df["Score"].astype(int)  # Ensure scores are integers
        return df.sort_values(by="Score", ascending=False)
    except Exception as e:
        st.error(f"Failed to read the Excel file: {e}")
        return pd.DataFrame(columns=["Name", "Score", "Avatar"])

# Load and resize avatars
def load_avatar(path):
    if path and os.path.exists(path):
        try:
            img = Image.open(path)
            return img.resize((100, 100))
        except Exception:
            st.warning(f"Could not load avatar: {path}")
            return None
    return None

# Simulate rotating avatars side to side
def rotate_image(image, angle):
    # Apply side-to-side rotation
    return image.rotate(angle, expand=True)

# Main leaderboard display
def draw_leaderboard(df):
    st.title("🏆 Leaderboard")
    
    if df.empty:
        st.warning("No data available.")
    else:
        # Sorting the players based on their scores in descending order
        sorted_players = df.sort_values(by="Score", ascending=False)

        # Display top 3 players with gold, silver, and bronze labels
        for i, row in sorted_players.head(3).iterrows():
            col1, col2 = st.columns([1, 3])

            with col1:
                avatar_path = os.path.join(AVATAR_FOLDER, row["Avatar"])
                avatar = load_avatar(avatar_path)
                if avatar:
                    # Apply rotation
                    angle = np.sin(time.time()) * 30  # Continuous rotation effect
                    rotated_avatar = rotate_image(avatar, angle)
                    st.image(rotated_avatar, width=100)

            with col2:
                color = COLORS["gold"] if i == 0 else COLORS["silver"] if i == 1 else COLORS["bronze"]
                st.subheader(f"{i + 1}. {row['Name']}", color=color)
                st.write(f"**{row['Score']} points**")
        
        # Display remaining players (from 4th onward)
        for i, row in sorted_players.iloc[3:].iterrows():
            col1, col2 = st.columns([1, 3])

            with col1:
                avatar_path = os.path.join(AVATAR_FOLDER, row["Avatar"])
                avatar = load_avatar(avatar_path)
                if avatar:
                    # Apply rotation
                    angle = np.sin(time.time()) * 30  # Continuous rotation effect
                    rotated_avatar = rotate_image(avatar, angle)
                    st.image(rotated_avatar, width=100)

            with col2:
                st.subheader(f"{i + 1}. {row['Name']}", color=COLORS["white"])
                st.write(f"**{row['Score']} points**")
    
        # Expandable section for remaining players
        with st.expander("View all players"):
            st.dataframe(sorted_players)
    
# Load data and display leaderboard
df = load_scores()
draw_leaderboard(df)

# Play funky music in the background
st.audio(MUSIC_FILE, format="audio/mp3", start_time=0)
