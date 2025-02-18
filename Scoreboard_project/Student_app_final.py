import streamlit as st
import pandas as pd
import os
from PIL import Image
import time
from streamlit.components.v1 import html

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

# Music file path
BACKGROUND_MUSIC = "Scoreboard_project/funky_music.mp3"

# Display instructions for the user to play the music
st.markdown("### Click the play button below to start the music 🎵")

# Embed the music player (users will need to click play)
st.audio(BACKGROUND_MUSIC, start_time=0)

# Embedding confetti effect via JavaScript for infinite loop
confetti_code = """
<html>
  <head>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.4.0/dist/confetti.browser.min.js"></script>
    <script>
      function launchConfetti() {
        var end = Date.now() + (10 * 1000); // 10 seconds of continuous confetti
        var frameId;
        var colors = ['#ff0', '#0f0', '#f00', '#00f', '#0ff'];
        
        function frame() {
          confetti({
            particleCount: 5,
            angle: 60,
            spread: 55,
            origin: { x: Math.random(), y: Math.random() },
            colors: colors
          });
          
          if (Date.now() < end) {
            frameId = requestAnimationFrame(frame);
          } else {
            launchConfetti();  // Repeat the confetti after 10 seconds
          }
        }
        frame();
      }
      window.onload = launchConfetti;
    </script>
  </head>
  <body>
    <h2>Enjoy the infinite confetti! 🎉</h2>
  </body>
</html>
"""

# Display the confetti effect
html(confetti_code, height=500)

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

# Main leaderboard display
def draw_leaderboard(df):
    st.title("🏆 Leaderboard")
    
    if df.empty:
        st.warning("No data available.")
    else:
        # Sort players by score
        sorted_players = sorted(df.iterrows(), key=lambda x: x[1]["Score"], reverse=True)

        # Display top 3 players with gold, silver, and bronze colors
        for i, (index, row) in enumerate(sorted_players[:5]):
            col1, col2 = st.columns([1, 3])
        
            with col1:
                avatar = load_avatar(row["Avatar"])  # Load avatar by file name
                if avatar:
                    # Display avatar without rotation
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
    
        # Scrollable s
