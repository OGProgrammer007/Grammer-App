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

# Background music file (Make sure the file is located in the same folder or adjust path accordingly)
BACKGROUND_MUSIC = "Scoreboard_project/funky_music.mp3"

# Custom HTML to autoplay background music
st.markdown(f"""
    <audio autoplay loop>
        <source src="{BACKGROUND_MUSIC}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
""", unsafe_allow_html=True)

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
def load_avatar(avatar_filename):
    avatar_path = os.path.join(AVATAR_FOLDER, avatar_filename)
    if avatar_filename and os.path.exists(avatar_path):
        try:
            img = Image.open(avatar_path)
            return img.resize((100, 100))
        except Exception:
            st.warning(f"Could not load avatar: {avatar_path}")
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
        # Display top 3 players with gold, silver, and bronze colors
        for i, row in df.head(5).iterrows():
            col1, col2 = st.columns([1, 3])
        
            with col1:
                avatar = load_avatar(row["Avatar"])  # Load avatar by file name
                if avatar:
                    # Apply rotation to avatar image
                    angle = np.sin(time.time() + i) * 30
                    avatar = rotate_image(avatar, angle)
                    st.image(avatar)
        
            with col2:
                # Apply ranking colors for top 3 players
                if i == 0:
                    rank_color = COLORS["gold"]
                    rank = "1"
                elif i == 1:
                    rank_color = COLORS["silver"]
                    rank = "2"
                elif i == 2:
                    rank_color = COLORS["bronze"]
                    rank = "3"
                else:
                    rank_color = COLORS["blue"]
                    rank = str(i + 1)
                
                st.subheader(f"{rank}. {row['Name']}")
                st.markdown(f"<h3 style='color:{rank_color}'>{row['Score']} points</h3>", unsafe_allow_html=True)
    
        # Scrollable section for all players
        st.subheader("All Players")
        with st.expander("Click to view all players"):
            # Display the remaining players starting from rank 6
            for i, row in df[5:].iterrows():
                col1, col2 = st.columns([1, 3])
            
                with col1:
                    avatar = load_avatar(row["Avatar"])  # Load avatar by file name
                    if avatar:
                        # Apply rotation to avatar image
                        angle = np.sin(time.time() + i) * 30
                        avatar = rotate_image(avatar, angle)
                        st.image(avatar)
            
                with col2:
                    # Starting rank from 6 onward
                    rank = str(i + 6)
                    st.subheader(f"{rank}. {row['Name']}")
                    st.write(f"**Score:** {row['Score']} points")

# Trigger balloons effect
st.balloons()

# Load data and display leaderboard
df = load_scores()
draw_leaderboard(df)
