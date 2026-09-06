# modules/text_module.py

import streamlit as st
import time

from services.ai_evaluator import evaluate_recall
from services.scoring import (
    calculate_overall_score,
    has_passed,
    get_performance_level
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

def initialize_text_state():

    defaults = {
        "text_started": False,
        "text_start_time": None,
        "text_expired": False,
        "text_submitted": False,
        "text_result": None
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


# --------------------------------------------------
# RESET
# --------------------------------------------------

def reset_text_module():

    keys = [
        "text_started",
        "text_start_time",
        "text_expired",
        "text_submitted",
        "text_result"
    ]

    for key in keys:

        if key in st.session_state:

            del st.session_state[key]


# --------------------------------------------------
# TIMER
# --------------------------------------------------

def get_remaining_time(reading_time):

    if not st.session_state.text_started:

        return reading_time

    elapsed = (
        time.time()
        - st.session_state.text_start_time
    )

    remaining = max(
        0,
        reading_time - int(elapsed)
    )

    return remaining


def format_time(seconds):

    minutes = seconds // 60

    seconds = seconds % 60

    return f"{minutes:02}:{seconds:02}"


# --------------------------------------------------
# RETENTION MAP
# --------------------------------------------------

def display_retention_map(result):

    st.subheader("🧠 Your Retention Map")

    remembered = result["remembered"]
    partial = result["partial"]
    missed = result["missed"]

    col1, col2, col3 = st.columns(3)

    # ---------------------------
    # REMEMBERED
    # ---------------------------

    with col1:

        st.success(
            f"🟢 Remembered\n\n"
            f"{len(remembered)} concepts"
        )

        if remembered:

            for concept in remembered:

                st.write(
                    f"✓ {concept}"
                )

        else:

            st.write(
                "No concepts were fully recalled."
            )

    # ---------------------------
    # PARTIAL
    # ---------------------------

    with col2:

        st.warning(
            f"🟡 Partially Remembered\n\n"
            f"{len(partial)} concepts"
        )

        if partial:

            for concept in partial:

                st.write(
                    f"~ {concept}"
                )

        else:

            st.write(
                "No partially recalled concepts."
            )

    # ---------------------------
    # MISSED
    # ---------------------------

    with col3:

        st.error(
            f"🔴 Missed\n\n"
            f"{len(missed)} concepts"
        )

        if missed:

            for concept in missed:

                st.write(
                    f"✗ {concept}"
                )

        else:

            st.write(
                "You remembered all key concepts!"
            )


# --------------------------------------------------
# MAIN MODULE
# --------------------------------------------------

def run_text_module(level_data):

    initialize_text_state()

    st.title(
        "📖 Module 2: Reading & Retention"
    )

    st.write(
        """
        Read the passage carefully and try to understand
        the important ideas. Once the reading time ends,
        you will have to recall the content without seeing it.
        """
    )

    # --------------------------------------------------
    # START SCREEN
    # --------------------------------------------------

    if not st.session_state.text_started:

        st.info(
            f"Reading time: "
            f"{format_time(level_data['reading_time'])}"
        )

        if st.button(
            "Start Reading",
            type="primary"
        ):

            st.session_state.text_started = True

            st.session_state.text_start_time = time.time()

            st.rerun()

        return

    # --------------------------------------------------
    # TIMER
    # --------------------------------------------------

    remaining = get_remaining_time(
        level_data["reading_time"]
    )

    st.metric(
        "Remaining Reading Time",
        format_time(remaining)
    )

    progress = (
        remaining
        / level_data["reading_time"]
    )

    st.progress(progress)

    # --------------------------------------------------
    # READING
    # --------------------------------------------------

    if remaining > 0:

        st.subheader(
            level_data["title"]
        )

        st.markdown(
            f"""
            <div style="
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #ccc;
                line-height: 1.8;
                font-size: 17px;
            ">
            {level_data["text"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.warning(
            "Read carefully. The passage will disappear "
            "when your reading time expires."
        )

    # --------------------------------------------------
    # READING TIME FINISHED
    # --------------------------------------------------

    else:

        st.session_state.text_expired = True

        st.warning(
            "⏰ Your reading time has ended."
        )

        st.info(
            "The passage is now hidden. "
            "Recall everything you remember."
        )

    # --------------------------------------------------
    # RECALL
    # --------------------------------------------------

    if st.session_state.text_expired:

        st.divider()

        st.subheader(
            "🧠 What do you remember?"
        )

        st.write(
            """
            Write everything important that you remember
            from the passage. Try to explain the ideas in
            your own words.
            """
        )

        user_response = st.text_area(
            "Your response",
            height=250,
            placeholder=(
                "Write everything you remember..."
            ),
            key="text_user_response"
        )

        if st.button(
            "Submit Recall",
            type="primary"
        ):

            if not user_response.strip():

                st.error(
                    "Please write something before submitting."
                )

                return

            # ------------------------------------------
            # AI EVALUATION
            # ------------------------------------------

            result = evaluate_recall(
                source_text=level_data["text"],
                user_response=user_response,
                key_concepts=level_data[
                    "key_concepts"
                ]
            )

            recall_score = result["accuracy"]

            # ------------------------------------------
            # OVERALL SCORE
            # ------------------------------------------

            overall_score = calculate_overall_score(
                recall_score=recall_score,
                question_score=0,
                attention_score=100
            )

            passed = has_passed(
                overall_score
            )

            result["overall_score"] = overall_score

            result["passed"] = passed

            result["performance"] = (
                get_performance_level(
                    overall_score
                )
            )

            st.session_state.text_result = result

            st.session_state.text_submitted = True

            st.rerun()

    # --------------------------------------------------
    # RESULTS
    # --------------------------------------------------

    if st.session_state.text_submitted:

        result = st.session_state.text_result

        st.divider()

        st.header(
            "📊 Your Results"
        )

        score_col, accuracy_col = st.columns(2)

        with score_col:

            st.metric(
                "Overall Score",
                f"{result['overall_score']}%"
            )

        with accuracy_col:

            st.metric(
                "Recall Accuracy",
                f"{result['accuracy']}%"
            )

        # ------------------------------------------
        # PASS / FAIL
        # ------------------------------------------

        if result["passed"]:

            st.success(
                "🎉 Module completed! "
                "You have achieved the required score."
            )

        else:

            st.error(
                "You did not reach the required score. "
                "Review your weak areas and try again."
            )

        st.write(
            f"**Performance:** "
            f"{result['performance']}"
        )

        # ------------------------------------------
        # FEEDBACK
        # ------------------------------------------

        st.subheader(
            "💬 AI Feedback"
        )

        st.info(
            result["feedback"]
        )

        # ------------------------------------------
        # RETENTION MAP
        # ------------------------------------------

        display_retention_map(
            result
        )

        # ------------------------------------------
        # RESET
        # ------------------------------------------

        if st.button(
            "Try Again"
        ):

            reset_text_module()

            st.rerun()