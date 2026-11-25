"""Calculate monthly spending summaries from recorded expenses."""

from datetime import date


CHART_WIDTH = 20


def validate_month_year(month: int | str, year: int | str) -> tuple[int, int]:
    """Convert and validate a month and year entered by the user."""
    try:
        numeric_month = int(month)
        numeric_year = int(year)
    except (TypeError, ValueError) as error:
        raise ValueError("Month and year must be whole numbers.") from error

    if numeric_month < 1 or numeric_month > 12:
        raise ValueError("Month must be a number from 1 to 12.")
    if numeric_year < 1 or numeric_year > 9999:
        raise ValueError("Year must be between 1 and 9999.")

    return numeric_month, numeric_year


def build_monthly_report(
    expenses: list[dict], month: int | str, year: int | str
) -> dict:
    """Calculate totals and category percentages for one calendar month."""
    numeric_month, numeric_year = validate_month_year(month, year)
    matching_expenses = [
        expense
        for expense in expenses
        if date.fromisoformat(expense["date"]).month == numeric_month
        and date.fromisoformat(expense["date"]).year == numeric_year
    ]

    category_totals = {}
    for expense in matching_expenses:
        category = expense["category"]
        category_totals[category] = category_totals.get(category, 0) + expense["amount"]

    total_spending = sum(category_totals.values())
    category_breakdown = []
    for category, amount in category_totals.items():
        percentage = amount / total_spending * 100 if total_spending else 0
        filled_length = round(percentage / 100 * CHART_WIDTH)
        if amount > 0 and filled_length == 0:
            filled_length = 1
        category_breakdown.append(
            {
                "category": category,
                "amount": amount,
                "percentage": percentage,
                "bar": "█" * filled_length + "░" * (CHART_WIDTH - filled_length),
            }
        )

    category_breakdown.sort(key=lambda item: item["amount"], reverse=True)
    highest_category = category_breakdown[0]["category"] if category_breakdown else None
    lowest_category = category_breakdown[-1]["category"] if category_breakdown else None

    return {
        "month": numeric_month,
        "year": numeric_year,
        "total": total_spending,
        "categories": category_breakdown,
        "highest_category": highest_category,
        "lowest_category": lowest_category,
    }