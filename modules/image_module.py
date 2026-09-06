# modules/image_module.py

import streamlit as st
import time

from services.ai_evaluator import evaluate_recall
from services.scoring import (
    calculate_overall_score,
    has_passed,
    get_performance_level
)


# =========================================================
# SESSION STATE
# =========================================================

def initialize_image_state():

    defaults = {
        "image_started": False,
        "image_start_time": None,
        "image_expired": False,
        "image_submitted": False,
        "image_result": None
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# =========================================================
# RESET
# =========================================================

def reset_image_module():

    keys = [
        "image_started",
        "image_start_time",
        "image_expired",
        "image_submitted",
        "image_result"
    ]

    for key in keys:

        if key in st.session_state:
            del st.session_state[key]


# =========================================================
# TIMER
# =========================================================

def get_remaining_time(viewing_time):

    if not st.session_state.image_started:
        return viewing_time

    elapsed = (
        time.time()
        - st.session_state.image_start_time
    )

    remaining = max(
        0,
        viewing_time - int(elapsed)
    )

    return remaining


def format_time(seconds):

    minutes = seconds // 60
    seconds = seconds % 60

    return f"{minutes:02}:{seconds:02}"


# =========================================================
# RETENTION MAP
# =========================================================

def display_retention_map(result):

    st.subheader("🧠 Visual Retention Map")

    remembered = result["remembered"]
    partial = result["partial"]
    missed = result["missed"]

    col1, col2, col3 = st.columns(3)

    # -----------------------------------------------------
    # REMEMBERED
    # -----------------------------------------------------

    with col1:

        st.success(
            f"🟢 Accurately Remembered\n\n"
            f"{len(remembered)} details"
        )

        if remembered:

            for item in remembered:

                st.write(
                    f"✓ {item}"
                )

        else:

            st.write(
                "No major details were accurately recalled."
            )

    # -----------------------------------------------------
    # PARTIALLY REMEMBERED
    # -----------------------------------------------------

    with col2:

        st.warning(
            f"🟡 Partially Remembered\n\n"
            f"{len(partial)} details"
        )

        if partial:

            for item in partial:

                st.write(
                    f"~ {item}"
                )

        else:

            st.write(
                "No partially recalled details."
            )

    # -----------------------------------------------------
    # MISSED
    # -----------------------------------------------------

    with col3:

        st.error(
            f"🔴 Missed\n\n"
            f"{len(missed)} details"
        )

        if missed:

            for item in missed:

                st.write(
                    f"✗ {item}"
                )

        else:

            st.write(
                "You recalled all important details!"
            )


# =========================================================
# MAIN MODULE
# =========================================================

def run_image_module(level_data):

    initialize_image_state()

    st.title(
        "🖼️ Module 3: Visual Observation & Recall"
    )

    st.write(
        """
        Observe the image carefully and remember as many
        important details as possible. The image will only
        be visible for a limited amount of time.
        """
    )

    # =====================================================
    # START SCREEN
    # =====================================================

    if not st.session_state.image_started:

        st.info(
            f"You will have "
            f"{format_time(level_data['image_view_time'])} "
            f"to observe the image."
        )

        st.write(
            "Try to focus on important objects, people, "
            "actions, locations and relationships."
        )

        if st.button(
            "Start Observation",
            type="primary"
        ):

            st.session_state.image_started = True

            st.session_state.image_start_time = time.time()

            st.rerun()

        return

    # =====================================================
    # TIMER
    # =====================================================

    remaining = get_remaining_time(
        level_data["image_view_time"]
    )

    st.metric(
        "Remaining Observation Time",
        format_time(remaining)
    )

    progress = (
        remaining
        / level_data["image_view_time"]
    )

    st.progress(progress)

    # =====================================================
    # SHOW IMAGE
    # =====================================================

    if remaining > 0:

        try:

            st.image(
                level_data["image_path"],
                use_container_width=True
            )

        except Exception:

            st.error(
                "Image could not be loaded. "
                "Please check the image path."
            )

        st.warning(
            "👀 Observe carefully. "
            "The image will disappear when the timer ends."
        )

        # Automatically refresh the page
        # so that the timer updates.

        time.sleep(1)

        st.rerun()

    # =====================================================
    # IMAGE EXPIRED
    # =====================================================

    else:

        st.session_state.image_expired = True

        st.warning(
            "⏰ Observation time has ended."
        )

        st.info(
            "The image is now hidden. "
            "Describe everything you remember."
        )

    # =====================================================
    # RECALL SECTION
    # =====================================================

    if st.session_state.image_expired:

        st.divider()

        st.subheader(
            "🧠 What do you remember?"
        )

        st.write(
            """
            Describe everything you remember from the image.

            Try to include:
            - Important objects
            - People
            - Actions
            - Locations
            - Relationships between objects
            - Any other significant details
            """
        )

        user_response = st.text_area(
            "Describe the image from memory:",
            height=250,
            placeholder=(
                "Example: I remember seeing..."
            ),
            key="image_user_response"
        )

        if st.button(
            "Submit Visual Recall",
            type="primary"
        ):

            if not user_response.strip():

                st.error(
                    "Please describe what you remember "
                    "before submitting."
                )

                return

            # =================================================
            # AI EVALUATION
            # =================================================

            result = evaluate_recall(

                source_text=(
                    level_data["image_description"]
                ),

                user_response=user_response,

                key_concepts=(
                    level_data["image_key_details"]
                )
            )

            # =================================================
            # SCORE
            # =================================================

            recall_score = result["accuracy"]

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

            st.session_state.image_result = result

            st.session_state.image_submitted = True

            st.rerun()

    # =====================================================
    # RESULTS
    # =====================================================

    if st.session_state.image_submitted:

        result = st.session_state.image_result

        st.divider()

        st.header(
            "📊 Visual Recall Results"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Overall Score",
                f"{result['overall_score']}%"
            )

        with col2:

            st.metric(
                "Visual Recall Accuracy",
                f"{result['accuracy']}%"
            )

        # =================================================
        # PASS / FAIL
        # =================================================

        if result["passed"]:

            st.success(
                "🎉 Module 3 completed! "
                "You achieved the required score."
            )

        else:

            st.error(
                "You did not reach the required score. "
                "Try again and focus on the important details."
            )

        st.write(
            f"**Performance:** "
            f"{result['performance']}"
        )

        # =================================================
        # AI FEEDBACK
        # =================================================

        st.subheader(
            "💬 AI Feedback"
        )

        st.info(
            result["feedback"]
        )

        # =================================================
        # RETENTION MAP
        # =================================================

        display_retention_map(
            result
        )

        # =================================================
        # TRY AGAIN
        # =================================================

        if st.button(
            "Try Again"
        ):

            reset_image_module()

            st.rerun()