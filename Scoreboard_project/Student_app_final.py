import streamlit as st
import openpyxl
import os
import math
import numpy as np
from PIL import Image
import io

# Excel file path
EXCEL_FILE = "scores_with_avatars.xlsx"

# Folder where avatar images are stored in the repository
AVATAR_FOLDER = "avatars/"

# Colors
COLORS = {
    "gold": "#FFD700",
    "silver": "#C0C0C0",
    "bronze": "#CD7F32",
    "blue": "#6495ED",
    "white": "#FFFFFF"
}

def load_scores():
    """Load player data from the Excel file."""
    if not os.path.exists(EXCEL_FILE):
        st.error(f"Error: File '{EXCEL_FILE}' not found.")
        return {}

    workbook = openpyxl.load_workbook(EXCEL_FILE)
    sheet = workbook.active
    scores = {}

    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=1, max_col=3):
        name, score, avatar = row[0].value, row[1].value, row[2].value
        if name and score and avatar:
            scores[name] = {"score": int(score), "avatar": avatar}

    workbook.close()
    return scores

def load_avatar(path):
    """Load avatar images."""
    if not os.path.exists(path):
        st.warning(f"Avatar '{path}' not found.")
        return None
    try:
        avatar = Image.open(path)
        avatar = avatar.resize((100, 100))
        return avatar
    except IOError:
        st.error(f"Error loading image '{path}'")
        return None

def rotate_image(image, angle):
    """Rotate image side-to-side effect."""
    return image.rotate(angle, expand=True)

# Load scores and avatars
players = load_scores()
avatars = {name: load_avatar(os.path.join(AVATAR_FOLDER, data["avatar"])) for name, data in players.items()}

def draw_leaderboard(angle):
    """Draw the leaderboard with top 5 players."""
    st.title("Leaderboard")

    if not players:
        st.warning("No data available")
        return

    sorted_players = sorted(players.items(), key=lambda x: x[1]["score"], reverse=True)

    # Top 5 players
    for i, (player, data) in enumerate(sorted_players[:5]):
        player_name = f"{i + 1}. {player}"
        player_score = f"{data['score']} points"

        player_color = COLORS["gold"] if i == 0 else COLORS["silver"] if i == 1 else COLORS["bronze"] if i == 2 else COLORS["white"]
        st.markdown(f"<p style='color:{player_color}; font-size: 24px'>{player_name} - {player_score}</p>", unsafe_allow_html=True)

        # Draw rotating avatar
        avatar = avatars.get(player)
        if avatar:
            rotated_avatar = rotate_image(avatar, np.sin(angle + i) * 30)
            avatar_io = io.BytesIO()
            rotated_avatar.save(avatar_io, format='PNG')
            avatar_io.seek(0)
            st.image(avatar_io, width=100)

def main():
    angle = 0  # Angle for rotating the avatars

    while True:
        draw_leaderboard(angle)
        angle += 0.1
        st.experimental_rerun()  # Refresh the page to update the leaderboard

if __name__ == "__main__":
    main()
