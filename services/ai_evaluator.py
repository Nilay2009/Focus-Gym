# services/ai_evaluator.py

import re


def normalize_text(text):
    """Clean text for basic comparison."""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def evaluate_recall_demo(
    user_response,
    key_concepts
):
    """
    Temporary AI-evaluation substitute.

    This allows the application to work before
    an actual LLM API is connected.
    """

    if not user_response.strip():

        return {
            "accuracy": 0,
            "remembered": [],
            "partial": [],
            "missed": key_concepts,
            "feedback": "No response was provided."
        }

    response = normalize_text(
        user_response
    )

    remembered = []
    partial = []
    missed = []

    for concept in key_concepts:

        concept_clean = normalize_text(
            concept
        )

        words = concept_clean.split()

        matched_words = [
            word
            for word in words
            if word in response.split()
        ]

        if len(matched_words) == len(words):

            remembered.append(concept)

        elif len(matched_words) > 0:

            partial.append(concept)

        else:

            missed.append(concept)

    total = len(key_concepts)

    if total == 0:

        accuracy = 0

    else:

        accuracy = (
            (
                len(remembered)
                + 0.5 * len(partial)
            )
            / total
        ) * 100

    if accuracy >= 85:

        feedback = (
            "Excellent recall. You remembered "
            "most of the important concepts."
        )

    elif accuracy >= 60:

        feedback = (
            "Good attempt. You remembered several "
            "important ideas, but some concepts were missed."
        )

    else:

        feedback = (
            "Some important concepts were missed. "
            "Try focusing on the main ideas and relationships "
            "between them."
        )

    return {
        "accuracy": round(accuracy, 2),
        "remembered": remembered,
        "partial": partial,
        "missed": missed,
        "feedback": feedback
    }


def evaluate_recall(
    source_text,
    user_response,
    key_concepts
):
    """
    Main evaluation function.

    Currently uses the demo evaluator.

    Replace the implementation here with an
    LLM API call later.

    Keeping this function unchanged means
    the rest of the application does not
    need to change when AI is added.
    """

    return evaluate_recall_demo(
        user_response,
        key_concepts
    )