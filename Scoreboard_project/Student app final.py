import streamlit as st
import pandas as pd

# File name for the Excel file
EXCEL_FILE = "scores_with_avatars.xlsx"

# Function to load scores from the Excel file
def load_scores():
    try:
        df = pd.read_excel(EXCEL_FILE)
        df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Error loading scores: {e}")
        return pd.DataFrame(columns=["Name", "Score", "Avatar"])

# Streamlit App UI
st.title("🏆 Leaderboard")

# Load and display the scores
df = load_scores()

if not df.empty:
    st.subheader("Top 5 Players")
    
    for index, row in df.head(5).iterrows():
        col1, col2, col3 = st.columns([1, 3, 2])
        
        # Show Avatar if available
        if pd.notna(row["Avatar"]):
            col1.image(row["Avatar"], width=80)
        
        col2.write(f"**{index+1}. {row['Name']}**")
        col3.write(f"**{row['Score']} points**")
    
    st.subheader("📜 Full Leaderboard")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No data available. Please upload a valid scores_with_avatars.xlsx file.")

