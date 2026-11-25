"""Run the PennyWise command-line application."""

from datetime import date
from calendar import month_name
from pathlib import Path

from expenses import (
    DEFAULT_CATEGORIES,
    add_expense,
    delete_expense,
    edit_expense,
    get_expense_by_id,
    validate_amount,
    validate_date,
    validate_description,
    validate_category,
)
from reports import build_monthly_report, validate_month_year
from storage import DATA_FILE, load_data, save_data


def display_expenses(expenses: list[dict]) -> None:
    """Print every expense in a readable table-like format."""
    if not expenses:
        print("No expenses have been recorded yet.")
        return

    print("\nRecorded expenses:")
    for expense in expenses:
        print(
            f"ID: {expense['id']} | {expense['date']} | "
            f"${expense['amount']:.2f} | {expense['category']} | "
            f"{expense['description']}"
        )


def prompt_amount(current_amount: float | None = None) -> float:
    """Ask until the user enters a valid amount, or keeps the current one."""
    while True:
        prompt = "Amount"
        if current_amount is not None:
            prompt += f" [{current_amount:.2f}; press Enter to keep]"
        try:
            answer = input(f"{prompt}: ").strip()
            if not answer and current_amount is not None:
                return current_amount
            return validate_amount(answer)
        except ValueError as error:
            print(error)


def prompt_category(current_category: str | None = None) -> str:
    """Show valid categories and ask until the user chooses one."""
    while True:
        print("Categories:")
        for number, category in enumerate(DEFAULT_CATEGORIES, start=1):
            print(f"{number}. {category}")

        prompt = "Category number or name"
        if current_category is not None:
            prompt += f" [{current_category}; press Enter to keep]"
        answer = input(f"{prompt}: ").strip()
        if not answer and current_category is not None:
            return current_category

        if answer.isdigit() and 1 <= int(answer) <= len(DEFAULT_CATEGORIES):
            return DEFAULT_CATEGORIES[int(answer) - 1]

        try:
            return validate_category(answer)
        except ValueError as error:
            print(error)


def prompt_description(current_description: str | None = None) -> str:
    """Ask for a non-empty description, or keep the current one."""
    while True:
        prompt = "Description"
        if current_description is not None:
            prompt += " [press Enter to keep]"
        answer = input(f"{prompt}: ")
        if not answer.strip() and current_description is not None:
            return current_description
        try:
            return validate_description(answer)
        except ValueError as error:
            print(error)


def prompt_date(current_date: str | None = None) -> str:
    """Ask for a valid date, defaulting to today for a new expense."""
    while True:
        prompt = "Date (YYYY-MM-DD)"
        if current_date is None:
            prompt += f" [{date.today().isoformat()}]"
        else:
            prompt += " [press Enter to keep]"
        answer = input(f"{prompt}: ").strip()

        if not answer and current_date is not None:
            return current_date
        if not answer:
            answer = date.today().isoformat()

        try:
            return validate_date(answer)
        except ValueError as error:
            print(error)


def add_expense_from_menu(data: dict, file_path: Path = DATA_FILE) -> None:
    """Collect details and save a new expense."""
    amount = prompt_amount()
    category = prompt_category()
    description = prompt_description()
    expense_date = prompt_date()
    expense = add_expense(data["expenses"], amount, category, description, expense_date)
    save_data(data, file_path)
    print(f"Expense added. Its ID is {expense['id']}.")


def edit_expense_from_menu(data: dict, file_path: Path = DATA_FILE) -> None:
    """Find an expense, collect replacement details, and save the changes."""
    display_expenses(data["expenses"])
    if not data["expenses"]:
        return

    expense_id = input("Enter the ID of the expense to edit: ").strip()
    try:
        current_expense = get_expense_by_id(data["expenses"], expense_id)
    except ValueError as error:
        print(error)
        return

    print("Press Enter at a prompt to keep its current value.")
    edit_expense(
        data["expenses"],
        expense_id,
        amount=prompt_amount(current_expense["amount"]),
        category=prompt_category(current_expense["category"]),
        description=prompt_description(current_expense["description"]),
        expense_date=prompt_date(current_expense["date"]),
    )
    save_data(data, file_path)
    print("Expense updated.")


def delete_expense_from_menu(data: dict, file_path: Path = DATA_FILE) -> None:
    """Ask for an expense ID and save the deletion."""
    display_expenses(data["expenses"])
    if not data["expenses"]:
        return

    expense_id = input("Enter the ID of the expense to delete: ").strip()
    try:
        deleted_expense = delete_expense(data["expenses"], expense_id)
    except ValueError as error:
        print(error)
        return

    save_data(data, file_path)
    print(f"Deleted expense: {deleted_expense['description']}.")


def display_monthly_overview(data: dict) -> None:
    """Ask for a month and display its spending report and chart."""
    while True:
        month = input("Month (1-12): ").strip()
        year = input("Year (for example, 2026): ").strip()
        try:
            month, year = validate_month_year(month, year)
            break
        except ValueError as error:
            print(error)

    report = build_monthly_report(data["expenses"], month, year)
    print("\n===== MONTHLY SPENDING OVERVIEW =====")
    print(f"\nMonth: {month_name[month]} {year}")
    print(f"\nTotal Monthly Spending: ${report['total']:.2f}")

    if not report["categories"]:
        print("\nNo expenses were recorded for this month.")
        return

    print()
    for item in report["categories"]:
        print(f"{item['category']:<18} ${item['amount']:>7.2f}")
        print(f"  {item['bar']} {item['percentage']:>5.1f}%\n")

    print(f"\nHighest Spending Category: {report['highest_category']}")
    print(f"Lowest Spending Category: {report['lowest_category']}")


def run_menu(file_path: Path = DATA_FILE) -> None:
    """Load saved data and repeatedly show the expense menu."""
    data = load_data(file_path)
    menu_options = {
        "1": ("Add Expense", lambda saved_data: add_expense_from_menu(saved_data, file_path)),
        "2": ("View Expenses", lambda saved_data: display_expenses(saved_data["expenses"])),
        "3": ("Edit Expense", lambda saved_data: edit_expense_from_menu(saved_data, file_path)),
        "4": ("Delete Expense", lambda saved_data: delete_expense_from_menu(saved_data, file_path)),
        "5": ("Monthly Spending Overview", display_monthly_overview),
    }

    while True:
        print("\n===== PENNYWISE =====")
        for number, (label, _) in menu_options.items():
            print(f"{number}. {label}")
        print("6. Exit")

        choice = input("Select an option: ").strip()
        if choice == "6":
            print("Goodbye.")
            break
        if choice not in menu_options:
            print("Please choose a number from 1 to 6.")
            continue

        _, selected_action = menu_options[choice]
        selected_action(data)


def main() -> None:
    """Start the PennyWise menu."""
    run_menu()


if __name__ == "__main__":
    main()