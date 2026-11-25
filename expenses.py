"""Create, validate, edit, and delete expense records."""

from datetime import date
from math import isfinite
import secrets
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


def is_valid_reference_id(reference_id: object) -> bool:
    """Return whether a value contains exactly six numeric digits."""
    reference_text = str(reference_id)
    return len(reference_text) == 6 and reference_text.isdigit()


def generate_reference_id(expenses: list[dict]) -> str:
    """Generate a random six-digit reference not already used by an expense."""
    used_ids = {
        str(expense["reference_id"])
        for expense in expenses
        if is_valid_reference_id(expense.get("reference_id"))
    }
    while True:
        reference_id = str(100000 + secrets.randbelow(900000))
        if reference_id not in used_ids:
            return reference_id


def assign_missing_reference_ids(expenses: list[dict]) -> bool:
    """Assign unique short IDs to legacy expenses and report whether data changed."""
    reserved_ids = {
        str(expense["reference_id"])
        for expense in expenses
        if is_valid_reference_id(expense.get("reference_id"))
    }
    seen_ids = set()
    changed = False

    for expense in expenses:
        existing_id = expense.get("reference_id")
        existing_text = str(existing_id)
        if is_valid_reference_id(existing_id) and existing_text not in seen_ids:
            if existing_id != existing_text:
                expense["reference_id"] = existing_text
                changed = True
            seen_ids.add(existing_text)
            continue

        while True:
            new_reference_id = str(100000 + secrets.randbelow(900000))
            if new_reference_id not in reserved_ids and new_reference_id not in seen_ids:
                break
        expense["reference_id"] = new_reference_id
        seen_ids.add(new_reference_id)
        changed = True

    return changed


def get_expense_by_id(expenses: list[dict], expense_id: str) -> dict:
    """Find an expense by short reference ID or legacy internal UUID."""
    for expense in expenses:
        if str(expense.get("reference_id", "")) == str(expense_id):
            return expense
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
        "reference_id": generate_reference_id(expenses),
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