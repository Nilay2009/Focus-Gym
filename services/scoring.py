# services/scoring.py


PASSING_SCORE = 60


def calculate_overall_score(
    recall_score,
    question_score=0,
    attention_score=0
):
    """
    Calculate the overall score for a module.

    Recall is given the highest weight because
    retention is the primary goal of the application.
    """

    overall_score = (
        recall_score * 0.60
        + question_score * 0.20
        + attention_score * 0.20
    )

    return round(overall_score, 2)


def has_passed(score, passing_score=PASSING_SCORE):
    """Check whether the user has passed."""

    return score >= passing_score


def get_performance_level(score):

    if score >= 85:
        return "Excellent"

    elif score >= 70:
        return "Good"

    elif score >= PASSING_SCORE:
        return "Passed"

    else:
        return "Needs Improvement"