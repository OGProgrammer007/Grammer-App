import streamlit as st
import pandas as pd
import os
import time
from PIL import Image
import numpy as np

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

# Simulate rotating avatars
def rotate_image(image, angle):
    return image.rotate(angle, expand=True)

# Main leaderboard display
def draw_leaderboard(df):
    st.title("🏆 Leaderboard")
    
    if df.empty:
        st.warning("No data available.")
    else:
        players_df = players_df.sort_values(by="Score", ascending=False)
    
    # Display top 5 players
     for i, row in players_df.head(5).iterrows():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            avatar = load_avatar(row["Avatar"])
            if avatar:
                st.image(avatar)
        
        with col2:
            st.subheader(f"{i+1}. {row['Name']}")
            st.write(f"**Score:** {row['Score']} points")
    
    # Expandable section for remaining players
    with st.expander("View all players"):
        st.dataframe(players_df)


    
    # Animated effect for avatars
    angle = 0  
    while True:
        cols = st.columns(2)  # Create two columns for better layout
        for i, row in top_5.iterrows():
            name, score, avatar_path = row["Name"], row["Score"], row["Avatar"]
            color = COLORS["gold"] if i == 0 else COLORS["silver"] if i == 1 else COLORS["bronze"] if i == 2 else COLORS["white"]
            
            avatar = load_avatar(avatar_path)
            if avatar:
                avatar = rotate_image(avatar, np.sin(angle + i) * 30)

            with cols[0]:
                st.markdown(f"<h3 style='color:{color}'>{i + 1}. {name}</h3>", unsafe_allow_html=True)

            with cols[1]:
                st.markdown(f"<h3 style='color:#6495ED'>{score} points</h3>", unsafe_allow_html=True)
                
                if avatar:
                    st.image(avatar)

        angle += 0.1
        time.sleep(0.05)  # Refresh effect
        st.rerun()

# Load data and display leaderboard
df = load_scores()
draw_leaderboard(df)
