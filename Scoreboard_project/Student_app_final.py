import streamlit as st
import os
import pygame
from random import randint

# Initialize pygame mixer for background music
pygame.mixer.init()

# Constants for chat interface and colors
GOLD = (255, 223, 0)
BRONZE = (205, 127, 50)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
ENTRY_FONT = pygame.font.Font(None, 36)
SCORE_FONT = pygame.font.Font(None, 30)

# Background music
def play_music():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("funky_music.mp3")
        pygame.mixer.music.play(loops=-1, start=0.0)

# Players and their data
def load_scores():
    scores = {}
    workbook = openpyxl.load_workbook("scores.xlsx")
    sheet = workbook.active

    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=1, max_col=3):
        name, score, avatar = row[0].value, row[1].value, row[2].value
        if name and score and avatar:
            scores[name] = {"score": int(score), "avatar": avatar}

    workbook.close()
    return scores

def load_avatar(path):
    """Load and resize avatars."""
    if not os.path.exists(path):
        print(f"Warning: Avatar '{path}' not found.")
        return None
    # Load and resize the avatar image
    avatar = pygame.image.load(path)
    avatar = pygame.transform.scale(avatar, (50, 50))  # Resize to fit
    return avatar

# Display top players
def display_players():
    players = load_scores()
    sorted_players = sorted(players.items(), key=lambda x: x[1]["score"], reverse=True)

    # Top 5 players
    y_start = 100
    colors = [GOLD, BRONZE] + [WHITE] * max(0, (len(sorted_players) - 1))

    for i, (player, data) in enumerate(sorted_players[:5]):
        player_name = f"{i + 1}. {player}"
        player_score = f"{data['score']} points"
        avatar_path = f"avatars/{data['avatar']}"  # Assuming avatars are stored in a folder named 'avatars'
        avatar = load_avatar(avatar_path)

        # Display avatar, player name, and score
        st.image(avatar, width=50, caption=player_name, use_column_width=False)
        st.text(player_score)
        st.text(" ")

# Chat functionality
if "stage" not in st.session_state:
    st.session_state.stage = "user"
    st.session_state.history = []
    st.session_state.pending = None
    st.session_state.validation = {}

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

# Display chat history
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.stage == "user":
    if user_input := st.chat_input("Enter your message"):
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.pending = user_input
        st.session_state.stage = "validate"
        st.rerun()

elif st.session_state.stage == "validate":
    st.chat_input("Accept, correct, or rewrite the message above.", disabled=True)
    response_sentences, validation_list = validate(st.session_state.pending)
    highlighted_sentences = add_highlights(response_sentences, validation_list)
    with st.chat_message("user"):
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
                {"role": "user", "content": st.session_state.pending}
            )
            st.session_state.pending = None
            st.session_state.validation = {}
            st.session_state.stage = "user"
            st.rerun()
        if cols[2].button("Rewrite message", type="tertiary"):
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
    with st.chat_message("user"):
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
                    {"role": "user", "content": st.session_state.pending}
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
    st.chat_input("Accept, correct, or rewrite the message above.", disabled=True)
    with st.chat_message("user"):
        new = st.text_area("Rewrite the message", value=st.session_state.pending)
        if st.button(
            "Update", type="primary", disabled=new is None or new.strip(". ") == ""
        ):
            st.session_state.history.append({"role": "user", "content": new})
            st.session_state.pending = None
            st.session_state.validation = {}
            st.session_state.stage = "user"
            st.rerun()

# Play background music
play_music()

# Display the players
display_players()
