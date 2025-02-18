import streamlit as st
import pandas as pd
import os
from PIL import Image
import time
from random import randint

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

# Chat widget embed code (from Tawk.to)
st.markdown("""
<script type="text/javascript">
    var Tawk_API=Tawk_API||{}, Tawk_LoadStart=new Date();
    (function(){
        var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
        s1.async=true;
        s1.src='https://embed.tawk.to/your_tawkto_id/default';
        s1.charset='UTF-8';
        s1.setAttribute('crossorigin','*');
        s0.parentNode.insertBefore(s1,s0);
    })();
</script>
""", unsafe_allow_html=True)

# Chat system implementation
if "stage" not in st.session_state:
    st.session_state.stage = "user"
    st.session_state.history = []
    st.session_state.pending = None
    st.session_state.validation = {}

def chat_stream():
    for i in range(randint(3, 9)):
        yield "Simulated assistant response... "
        time.sleep(0.2)

def validate(response):
    response_sentences = response.split(". ")
    response_sentences = [
        sentence.strip(". ") + "."
        for sentence in response_sentences
        if sentence.strip(". ") != ""
    ]
    validation_list = [
        True if sentence.count(" ") > 4 else False for sentence in response_sentences
    ]
    return response_sentences, validation_list

def add_highlights(response_sentences, validation_list, bg="red", text="red"):
    return [
        f":{text}[:{bg}-background[" + sentence + "]]" if not is_valid else sentence
        for sentence, is_valid in zip(response_sentences, validation_list)
    ]

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
    
        # Scrollable section for all players
        st.subheader("All Players")
        with st.expander("Click to view all players"):
            # Display the remaining players starting from rank 6
            for i, (index, row) in enumerate(sorted_players[5:]):
                col1, col2 = st.columns([1, 3])
            
                with col1:
                    avatar = load_avatar(row["Avatar"])  # Load avatar by file name
                    if avatar:
                        # Display avatar without rotation
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

# Display chat messages
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input handling
if st.session_state.stage == "user":
    if user_input := st.chat_input("Enter a prompt"):
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            response = st.write_stream(chat_stream())
            st.session_state.pending = response
            st.session_state.stage = "validate"
            st.rerun()

elif st.session_state.stage == "validate":
    st.chat_input("Accept, correct, or rewrite the answer above.", disabled=True)
    response_sentences, validation_list = validate(st.session_state.pending)
    highlighted_sentences = add_highlights(response_sentences, validation_list)
    with st.chat_message("assistant"):
        st.markdown(" ".join(highlighted_sentences))
        st.divider()
        cols = st.columns(3)
        if cols[0].button(
            "Correct errors", type="primary", disabled=all(validation_list)
        ):
            st.session_state.validation = {
                "sentences": response_sentences,
                "valid": validation_list,
            }
            st.session_state.stage = "correct"
            st.rerun()
        if cols[1].button("Accept"):
            st.session_state.history.append(
                {"role": "assistant", "content": st.session_state.pending}
            )
            st.session_state.pending = None
            st.session_state.validation = {}
            st.session_state.stage = "user"
            st.rerun()
        if cols[2].button("Rewrite answer", type="tertiary"):
            st.session_state.stage = "rewrite"
            st.rerun()

elif st.session_state.stage == "correct":
    st.chat_input("Accept, correct, or rewrite the answer above.", disabled=True)
    response_sentences = st.session_state.validation["sentences"]
    validation_list = st.session_state.validation["valid"]
    highlighted_sentences = add_highlights(
        response_sentences, validation_list, "gray", "gray"
    )
    if not all(validation_list):
        focus = validation_list.index(False)
        highlighted_sentences[focus] = ":red[:red" + highlighted_sentences[focus][11:]
    else:
        focus = None
    with st.chat_message("assistant"):
        st.markdown(" ".join(highlighted_sentences))
        st.divider()
        if focus is not None:
            new_sentence = st.text_input(
                "Replacement text:", value=response_sentences[focus]
            )
            cols = st.columns(2)
            if cols[0].button(
                "Update", type="primary", disabled=len(new_sentence.strip()) < 1
            ):
                st.session_state.validation["sentences"][focus] = (
                    new_sentence.strip(". ") + "."
                )
                st.session_state.validation["valid"][focus] = True
                st.session_state.pending = " ".join(
                    st.session_state.validation["sentences"]
                )
                st.rerun()
            if cols[1].button("Remove"):
                st.session_state.validation["sentences"].pop(focus)
                st.session_state.validation["valid"].pop(focus)
                st.session_state.pending = " ".join(
                    st.session_state.validation["sentences"]
                )
                st.rerun()
        else:
            cols = st.columns(2)
            if cols[0].button("Accept", type="primary"):
                st.session_state.history.append(
                    {"role": "assistant", "content": st.session_state.pending}
                )
                st.session_state.pending = None
                st.session_state.validation = {}
                st.session_state.stage = "user"
                st.rerun()
            if cols[1].button("Re-validate"):
                st.session_state.validation = {}
                st.session_state.stage = "validate"
                st.rerun()

elif st.session_state.stage == "rewrite":
    st.chat_input("Accept, correct, or rewrite the answer above.", disabled=True)
    with st.chat_message("assistant"):
        new = st.text_area("Rewrite the answer", value=st.session_state.pending)
        if st.button(
            "Update", type="primary", disabled=new is None or new.strip(". ") == ""
        ):
            st.session_state.history.append({"role": "assistant", "content": new})
            st.session_state.pending = None
            st.session_state.validation = {}
            st.session_state.stage = "user"
            st.rerun()
