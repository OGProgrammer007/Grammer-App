import streamlit as st
import pandas as pd
from PIL import Image
import os

# Excel file for scores
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "scores_with_avatars.xlsx")

def load_scores():
    """Load player data from the Excel file."""
    if not os.path.exists(EXCEL_FILE):
        st.error(f"Error: File '{EXCEL_FILE}' not found.")
        return pd.DataFrame(columns=["Name", "Score", "Avatar"])
    
    df = pd.read_excel(EXCEL_FILE)
    return df

def load_avatar(path):
    """Load and resize avatars."""
    if not os.path.exists(path):
        return None
    try:
        image = Image.open(path)
        return image.resize((100, 100))
    except Exception as e:
        st.warning(f"Error loading image '{path}': {e}")
        return None

# Load data
players_df = load_scores()

# Streamlit UI
st.title("Leaderboard")

if players_df.empty:
    st.write("No data available")
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

