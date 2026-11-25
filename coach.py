"""Generate supportive financial insights using simple spending rules."""

from goals import calculate_goal_progress
from reports import build_monthly_report


SPENDING_RULES = {
    "Entertainment": {
        "threshold": 25,
        "message": "Consider reducing entertainment spending.",
    },
    "Shopping": {
        "threshold": 20,
        "message": "Review shopping purchases to see if any are unnecessary.",
    },
    "Food & Dining": {
        "threshold": 30,
        "message": "Consider reviewing dining habits or setting a food budget.",
    },
}


def build_coach_analysis(expenses: list[dict], goals: list[dict], month: int, year: int) -> dict:
    """Return monthly insights without changing expenses or savings goals."""
    report = build_monthly_report(expenses, month, year)
    category_totals = {
        item["category"]: item for item in report["categories"]
    }

    if report["total"] == 0:
        return {
            "month": report["month"],
            "year": report["year"],
            "total": 0,
            "insights": [],
            "message": "There is not enough spending data for this month to provide an analysis.",
            "goal": None,
            "goal_progress": None,
            "goal_projection": None,
        }

    insights = []
    for category, rule in SPENDING_RULES.items():
        spending = category_totals.get(category)
        if spending and spending["percentage"] > rule["threshold"]:
            insights.append(
                {
                    "category": category,
                    "amount": spending["amount"],
                    "percentage": spending["percentage"],
                    "threshold": rule["threshold"],
                    "suggested_reduction": spending["amount"] * 0.20,
                    "message": rule["message"],
                }
            )

    unfinished_goal = next(
        (
            goal
            for goal in goals
            if goal["current_savings"] < goal["target_amount"]
        ),
        None,
    )
    goal_progress = calculate_goal_progress(unfinished_goal) if unfinished_goal else None
    total_suggested_reductions = sum(
        insight["suggested_reduction"] for insight in insights
    )
    goal_projection = (
        calculate_goal_projection(unfinished_goal, total_suggested_reductions)
        if unfinished_goal
        and unfinished_goal.get("planned_monthly_contribution") is not None
        and insights
        else None
    )
    completed_goals_message = (
        "All of your savings goals are complete. Great work!"
        if goals and unfinished_goal is None
        else None
    )

    if not insights:
        if unfinished_goal is None and goals:
            message = "Your spending is within the suggested guidelines, and all savings goals are complete. Great work!"
        else:
            message = "Your spending is within the suggested guidelines. Keep making choices that fit your own financial goals."
    else:
        message = None

    return {
        "month": report["month"],
        "year": report["year"],
        "total": report["total"],
        "insights": insights,
        "message": message,
        "goal": unfinished_goal,
        "goal_progress": goal_progress,
        "goal_projection": goal_projection,
        "completed_goals_message": completed_goals_message,
    }


def calculate_goal_projection(goal: dict, suggested_reductions: float) -> dict:
    """Estimate next month's goal progress with and without redirected reductions."""
    target_amount = goal["target_amount"]
    current_savings = goal["current_savings"]
    planned_contribution = goal["planned_monthly_contribution"]

    current_progress = min(current_savings / target_amount * 100, 100)
    current_plan_progress = min(
        (current_savings + planned_contribution) / target_amount * 100,
        100,
    )
    progress_with_advice = min(
        (current_savings + planned_contribution + suggested_reductions)
        / target_amount
        * 100,
        100,
    )

    return {
        "current_progress": current_progress,
        "current_plan_progress": current_plan_progress,
        "progress_with_advice": progress_with_advice,
        "additional_progress": progress_with_advice - current_plan_progress,
        "suggested_reductions": suggested_reductions,
    }