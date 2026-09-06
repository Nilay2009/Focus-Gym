import streamlit as st

from data.content import CONTENT
from modules.video_module import run_video_module


# ---------------------------
# PAGE CONFIGURATION
# ---------------------------

st.set_page_config(
    page_title="Focus & Retention",
    page_icon="🧠",
    layout="wide"
)


# ---------------------------
# SESSION STATE
# ---------------------------

if "selected_genre" not in st.session_state:
    st.session_state.selected_genre = None

if "selected_level" not in st.session_state:
    st.session_state.selected_level = 1

if "current_module" not in st.session_state:
    st.session_state.current_module = 1


# ---------------------------
# SIDEBAR
# ---------------------------

with st.sidebar:

    st.title("🧠 Focus Trainer")

    st.divider()

    genres = list(CONTENT.keys())

    selected_genre = st.selectbox(
        "Choose a Genre",
        genres
    )

    st.session_state.selected_genre = selected_genre

    available_levels = list(
        CONTENT[selected_genre].keys()
    )

    selected_level = st.selectbox(
        "Choose a Level",
        available_levels
    )

    st.session_state.selected_level = selected_level

    st.divider()

    st.write("### Your Progress")

    st.write(
        f"Genre: **{selected_genre}**"
    )

    st.write(
        f"Level: **{selected_level}**"
    )


# ---------------------------
# MAIN PAGE
# ---------------------------

st.title("🧠 Adaptive Focus & Retention Trainer")

st.write(
    """
    Improve your concentration and retention through
    progressively challenging video, text, and visual exercises.
    """
)

st.divider()


# ---------------------------
# MODULE NAVIGATION
# ---------------------------

col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "🎥 Module 1\nVideo Challenge",
        use_container_width=True
    ):

        st.session_state.current_module = 1


with col2:

    if st.button(
        "📖 Module 2\nText Challenge",
        use_container_width=True
    ):

        st.session_state.current_module = 2


with col3:

    if st.button(
        "🖼️ Module 3\nImage Challenge",
        use_container_width=True
    ):

        st.session_state.current_module = 3


st.divider()


# ---------------------------
# LOAD CURRENT LEVEL DATA
# ---------------------------

level_data = CONTENT[
    st.session_state.selected_genre
][
    st.session_state.selected_level
]


# ---------------------------
# DISPLAY MODULE
# ---------------------------

if st.session_state.current_module == 1:

    run_video_module(level_data)


elif st.session_state.current_module == 2:

    st.title("📖 Module 2")

    st.info(
        "Member 2 will connect the Text Retention Module here."
    )


elif st.session_state.current_module == 3:

    st.title("🖼️ Module 3")

    st.info(
        "Member 3 will connect the Image Retention Module here."
    )