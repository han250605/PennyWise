"""Create, validate, edit, and delete expense records."""

from datetime import date
from math import isfinite
from uuid import uuid4


DEFAULT_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Housing",
    "Entertainment",
    "Shopping",
    "Education",
    "Healthcare",
    "Other",
]


def validate_amount(amount: float | str) -> float:
    """Convert an amount to a positive, finite number."""
    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError) as error:
        raise ValueError("Enter a valid number for the amount.") from error

    if not isfinite(numeric_amount) or numeric_amount <= 0:
        raise ValueError("The amount must be a positive number.")

    return numeric_amount


def validate_category(category: str) -> str:
    """Return a category if it matches one of the available categories."""
    cleaned_category = category.strip()
    if cleaned_category not in DEFAULT_CATEGORIES:
        raise ValueError("Choose one of the listed expense categories.")
    return cleaned_category


def validate_description(description: str) -> str:
    """Remove extra whitespace and require a non-empty description."""
    cleaned_description = description.strip()
    if not cleaned_description:
        raise ValueError("The description cannot be empty.")
    return cleaned_description


def validate_date(expense_date: str) -> str:
    """Check that a date is valid and written as YYYY-MM-DD."""
    try:
        parsed_date = date.fromisoformat(expense_date)
    except (TypeError, ValueError) as error:
        raise ValueError("Enter a valid date in YYYY-MM-DD format.") from error
    return parsed_date.isoformat()


def get_expense_by_id(expenses: list[dict], expense_id: str) -> dict:
    """Find one expense by ID, or explain that it could not be found."""
    for expense in expenses:
        if expense["id"] == expense_id:
            return expense
    raise ValueError(f"No expense found with ID {expense_id}.")


def add_expense(
    expenses: list[dict],
    amount: float | str,
    category: str,
    description: str,
    expense_date: str,
) -> dict:
    """Validate and add a new expense to the list."""
    new_expense = {
        "id": uuid4().hex,
        "amount": validate_amount(amount),
        "category": validate_category(category),
        "description": validate_description(description),
        "date": validate_date(expense_date),
    }
    expenses.append(new_expense)
    return new_expense


def edit_expense(
    expenses: list[dict],
    expense_id: str,
    amount: float | str | None = None,
    category: str | None = None,
    description: str | None = None,
    expense_date: str | None = None,
) -> dict:
    """Update supplied expense fields while keeping its ID unchanged."""
    expense = get_expense_by_id(expenses, expense_id)
    updated_fields = {
        "amount": validate_amount(amount if amount is not None else expense["amount"]),
        "category": validate_category(category if category is not None else expense["category"]),
        "description": validate_description(
            description if description is not None else expense["description"]
        ),
        "date": validate_date(expense_date if expense_date is not None else expense["date"]),
    }
    expense.update(updated_fields)
    return expense


def delete_expense(expenses: list[dict], expense_id: str) -> dict:
    """Remove and return an expense by ID."""
    expense = get_expense_by_id(expenses, expense_id)
    expenses.remove(expense)
    return expense