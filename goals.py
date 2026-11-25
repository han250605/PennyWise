"""Create savings goals and track contributions toward them."""

from math import isfinite
from uuid import uuid4


PROGRESS_BAR_WIDTH = 20


def validate_goal_name(name: str) -> str:
    """Return a cleaned goal name or raise an error if it is blank."""
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("The goal name cannot be empty.")
    return cleaned_name


def validate_positive_amount(amount: float | str, label: str) -> float:
    """Convert an amount to a positive, finite number."""
    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Enter a valid number for {label}.") from error

    if not isfinite(numeric_amount) or numeric_amount <= 0:
        raise ValueError(f"{label.capitalize()} must be a positive number.")
    return numeric_amount


def validate_initial_savings(amount: float | str) -> float:
    """Convert initial savings to a finite number that cannot be negative."""
    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError) as error:
        raise ValueError("Enter a valid number for initial savings.") from error

    if not isfinite(numeric_amount) or numeric_amount < 0:
        raise ValueError("Initial savings cannot be negative.")
    return numeric_amount


def calculate_goal_progress(goal: dict) -> dict:
    """Return remaining amount, progress percentage, status, and progress bar."""
    target_amount = goal["target_amount"]
    current_savings = goal["current_savings"]
    remaining_amount = max(0, target_amount - current_savings)
    progress_percentage = current_savings / target_amount * 100
    filled_length = round(min(progress_percentage, 100) / 100 * PROGRESS_BAR_WIDTH)
    if current_savings > 0 and filled_length == 0:
        filled_length = 1

    achieved = current_savings >= target_amount
    return {
        "remaining_amount": remaining_amount,
        "progress_percentage": progress_percentage,
        "bar": "█" * filled_length + "░" * (PROGRESS_BAR_WIDTH - filled_length),
        "status": "Goal achieved!" if achieved else "In Progress",
    }


def create_goal(
    goals: list[dict],
    name: str,
    target_amount: float | str,
    current_savings: float | str = 0,
) -> dict:
    """Validate and append a new goal to the goals list."""
    clean_name = validate_goal_name(name)
    valid_target = validate_positive_amount(target_amount, "target amount")
    valid_savings = validate_initial_savings(current_savings)
    goal = {
        "id": uuid4().hex,
        "name": clean_name,
        "target_amount": valid_target,
        "current_savings": valid_savings,
    }
    goals.append(goal)
    return goal


def get_goal_by_id(goals: list[dict], goal_id: str) -> dict:
    """Find one goal by ID or raise a clear error."""
    for goal in goals:
        if goal["id"] == goal_id:
            return goal
    raise ValueError(f"No savings goal found with ID {goal_id}.")


def get_goal_by_number(goals: list[dict], selection: int | str) -> dict:
    """Return a goal selected by its one-based position in the displayed list."""
    try:
        goal_number = int(selection)
    except (TypeError, ValueError) as error:
        raise ValueError("Enter a valid goal number.") from error

    if goal_number < 1 or goal_number > len(goals):
        raise ValueError("Choose a number from the displayed goal list.")
    return goals[goal_number - 1]


def add_contribution(
    goals: list[dict], contributions: list[dict], goal_id: str, amount: float | str
) -> dict:
    """Add a positive contribution to a goal and record it separately."""
    goal = get_goal_by_id(goals, goal_id)
    valid_amount = validate_positive_amount(amount, "contribution")
    goal["current_savings"] += valid_amount
    contribution = {
        "id": uuid4().hex,
        "goal_id": goal_id,
        "amount": valid_amount,
    }
    contributions.append(contribution)
    return contribution