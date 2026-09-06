# modules/video_module.py

import streamlit as st
import time


def initialize_video_state():
    """Initialize all session variables required for Module 1."""

    defaults = {
        "video_started": False,
        "video_start_time": None,
        "video_access_expired": False,
        "mid_question_answered": False,
        "video_recall_submitted": False,
        "video_score": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_video_module():
    """Reset Module 1."""

    keys = [
        "video_started",
        "video_start_time",
        "video_access_expired",
        "mid_question_answered",
        "video_recall_submitted",
        "video_score"
    ]

    for key in keys:
        if key in st.session_state:
            del st.session_state[key]


def get_remaining_time(access_time):
    """Calculate remaining access time."""

    if not st.session_state.video_started:
        return access_time

    elapsed = time.time() - st.session_state.video_start_time
    remaining = max(0, access_time - int(elapsed))

    return remaining


def format_time(seconds):

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    return f"{minutes:02}:{remaining_seconds:02}"


def calculate_question_score(user_answers, questions):

    correct = 0

    for user_answer, question in zip(user_answers, questions):

        if user_answer == question["answer"]:
            correct += 1

    if len(questions) == 0:
        return 0

    return (correct / len(questions)) * 100


def run_video_module(level_data):

    initialize_video_state()

    st.title("🎥 Module 1: Video Retention Challenge")

    st.subheader(level_data["title"])

    st.write(
        """
        Watch the video carefully. You have limited total access time.

        You may pause and rewatch sections, but the challenge will end
        when your viewing window expires.
        """
    )

    # ---------------------------
    # START BUTTON
    # ---------------------------

    if not st.session_state.video_started:

        if st.button("Start Video Challenge", type="primary"):

            st.session_state.video_started = True
            st.session_state.video_start_time = time.time()

            st.rerun()

        return

    # ---------------------------
    # TIMER
    # ---------------------------

    remaining = get_remaining_time(level_data["access_time"])

    st.metric(
        "Remaining Video Access Time",
        format_time(remaining)
    )

    progress = remaining / level_data["access_time"]

    st.progress(progress)

    # ---------------------------
    # VIDEO
    # ---------------------------

    if remaining > 0:

        try:

            video_file = open(
                level_data["video_path"],
                "rb"
            )

            video_bytes = video_file.read()

            st.video(video_bytes)

        except FileNotFoundError:

            st.warning(
                "Video file not found. Add your video to the correct folder."
            )

        # ---------------------------
        # MID-VIDEO QUESTION
        # ---------------------------

        st.divider()

        st.subheader("Attention Check")

        mid_question = level_data["mid_question"]

        answer = st.radio(
            mid_question["question"],
            mid_question["options"],
            key="mid_video_answer"
        )

        if st.button("Submit Attention Check"):

            st.session_state.mid_question_answered = True

            if answer == mid_question["answer"]:

                st.success("Correct! Continue watching carefully.")

            else:

                st.info("Answer recorded. Continue watching.")

    else:

        st.session_state.video_access_expired = True

        st.warning(
            "⏰ Your video access time has ended."
        )

    # ---------------------------
    # FINAL QUESTIONS
    # ---------------------------

    if (
        st.session_state.video_access_expired
        or st.session_state.mid_question_answered
    ):

        st.divider()

        st.header("Final Recall Challenge")

        user_answers = []

        for index, question in enumerate(
            level_data["final_questions"]
        ):

            answer = st.radio(
                question["question"],
                question["options"],
                key=f"final_question_{index}"
            )

            user_answers.append(answer)

        st.subheader(
            "Describe what you remember from the video"
        )

        recall_text = st.text_area(
            "Write everything important that you remember:",
            height=200,
            key="video_recall"
        )

        if st.button(
            "Submit Video Challenge",
            type="primary"
        ):

            question_score = calculate_question_score(
                user_answers,
                level_data["final_questions"]
            )

            # Temporary recall score.
            # Member 2's AI evaluator will replace this.
            recall_score = 50 if len(recall_text) > 50 else 20

            # Mid-question score
            mid_answer = st.session_state.get(
                "mid_video_answer",
                None
            )

            mid_score = 100 if (
                mid_answer
                == level_data["mid_question"]["answer"]
            ) else 0

            # Weighted final score
            final_score = (
                question_score * 0.30
                + recall_score * 0.50
                + mid_score * 0.20
            )

            st.session_state.video_score = round(
                final_score,
                2
            )

            st.session_state.video_recall_submitted = True

            st.rerun()

    # ---------------------------
    # RESULTS
    # ---------------------------

    if st.session_state.video_recall_submitted:

        st.divider()

        st.header("Module 1 Results")

        score = st.session_state.video_score

        st.metric(
            "Overall Video Retention Score",
            f"{score}%"
        )

        if score >= 60:

            st.success(
                "🎉 Module 1 Completed!"
            )

        else:

            st.error(
                "You need at least 60% to pass."
            )

        if st.button("Reset Module 1"):

            reset_video_module()

            st.rerun()