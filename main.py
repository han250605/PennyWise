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
    assign_missing_reference_ids,
    validate_amount,
    validate_date,
    validate_description,
    validate_category,
)
from goals import (
    add_contribution,
    calculate_goal_progress,
    create_goal,
    get_goal_by_number,
    validate_goal_name,
    validate_initial_savings,
    validate_positive_amount,
    update_monthly_contribution,
    update_goal_name,
    update_goal_target_amount,
)
from coach import build_coach_analysis
from reports import build_monthly_report, validate_month_year
from storage import DATA_FILE, load_data, save_data


def display_expenses(expenses: list[dict]) -> None:
    """Print every expense in a readable table-like format."""
    if not expenses:
        print("No expenses have been recorded yet.")
        return

    print("\n===== RECORDED EXPENSES =====")
    for expense in expenses:
        print(
            f"\nID: {expense['reference_id']}\n"
            f"Amount: ${expense['amount']:.2f}\n"
            f"Category: {expense['category']}\n"
            f"Description: {expense['description']}\n"
            f"Date: {expense['date']}"
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
    print(f"Expense added successfully!\nExpense ID: {expense['reference_id']}")


def edit_expense_from_menu(data: dict, file_path: Path = DATA_FILE) -> None:
    """Find an expense, collect replacement details, and save the changes."""
    display_expenses(data["expenses"])
    if not data["expenses"]:
        return

    expense_id = input("Enter Expense ID: ").strip()
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

    expense_id = input("Enter Expense ID: ").strip()
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


def prompt_goal_name() -> str:
    """Ask until the user enters a non-empty savings goal name."""
    while True:
        try:
            return validate_goal_name(input("Goal name: "))
        except ValueError as error:
            print(error)


def prompt_goal_amount(label: str) -> float:
    """Ask until the user enters a valid positive goal amount."""
    while True:
        try:
            return validate_positive_amount(input(f"{label}: "), label.lower())
        except ValueError as error:
            print(error)


def prompt_initial_savings() -> float:
    """Ask until the user enters valid initial savings, including zero."""
    while True:
        try:
            return validate_initial_savings(input("Amount already saved (use 0 if none): "))
        except ValueError as error:
            print(error)


def display_savings_goals(goals: list[dict]) -> None:
    """Print every savings goal and its progress."""
    print("\n===== SAVINGS GOALS =====")
    if not goals:
        print("\nNo savings goals have been created yet.")
        return

    for number, goal in enumerate(goals, start=1):
        progress = calculate_goal_progress(goal)
        print(f"\n[{number}] {goal['name']}")
        print(f"Target Amount:    ${goal['target_amount']:,.2f}")
        print(f"Current Savings:  ${goal['current_savings']:,.2f}")
        print(f"Remaining Amount: ${progress['remaining_amount']:,.2f}")
        print(
            f"\n{progress['bar']} "
            f"{progress['progress_percentage']:.1f}%"
        )
        print("\nCurrent Savings Plan:")
        monthly_contribution = goal.get("planned_monthly_contribution")
        if monthly_contribution is None:
            print("Monthly savings plan not set")
            if progress["estimated_months"] == 0:
                print("Estimated Time: 0 months")
        else:
            print(f"Monthly Contribution: ${monthly_contribution:,.2f}")
            estimated_months = progress["estimated_months"]
            print(f"Estimated Time: {estimated_months} months")
        print(f"Status: {progress['status']}")


def create_goal_from_menu(data: dict, file_path: Path = DATA_FILE) -> None:
    """Collect savings goal details, create the goal, and save it."""
    name = prompt_goal_name()
    target_amount = prompt_goal_amount("Target amount")
    current_savings = prompt_initial_savings()
    monthly_contribution = prompt_goal_amount("Planned monthly contribution")
    create_goal(
        data["goals"], name, target_amount, current_savings, monthly_contribution
    )
    save_data(data, file_path)
    print("Savings goal created successfully!")


def edit_savings_goal_from_menu(data: dict, file_path: Path = DATA_FILE) -> None:
    """Select a goal and edit its name, target, or monthly contribution."""
    if not data["goals"]:
        print("No savings goals are available. Create a goal first.")
        return

    display_savings_goals(data["goals"])
    try:
        goal = get_goal_by_number(data["goals"], input("Select a goal number: ").strip())
    except ValueError as error:
        print(error)
        return

    while True:
        print("\n===== EDIT SAVINGS GOAL =====")
        print("4. Edit Goal Name")
        print("5. Edit Target Amount")
        print("6. Edit Monthly Contribution")
        print("7. Return to Main Menu")
        choice = input("Select an option: ").strip()

        if choice == "7":
            return
        if choice == "4":
            print(f"Current Goal Name: {goal['name']}")
            update_goal_name(goal, prompt_goal_name())
        elif choice == "5":
            print(f"Current Target Amount: ${goal['target_amount']:,.2f}")
            update_goal_target_amount(goal, prompt_goal_amount("New Target Amount"))
        elif choice == "6":
            monthly_contribution = goal.get("planned_monthly_contribution")
            if monthly_contribution is None:
                print("Current Monthly Contribution: Not set")
            else:
                print(f"Current Monthly Contribution: ${monthly_contribution:,.2f}")
            update_monthly_contribution(
                goal, prompt_goal_amount("New Monthly Contribution")
            )
        else:
            print("Please choose a number from 4 to 7.")
            continue

        save_data(data, file_path)
        progress = calculate_goal_progress(goal)
        print("Savings goal updated successfully!")
        print(f"Remaining Amount: ${progress['remaining_amount']:,.2f}")
        print(f"Progress: {progress['progress_percentage']:.1f}%")
        print(f"Estimated Time: {progress['estimated_months']} months")
        print(f"Status: {progress['status']}")


def add_savings_contribution_from_menu(data: dict, file_path: Path = DATA_FILE) -> None:
    """Select a goal, record a contribution, and save the updated data."""
    if not data["goals"]:
        print("No savings goals are available. Create a goal first.")
        return

    display_savings_goals(data["goals"])
    try:
        goal = get_goal_by_number(data["goals"], input("Select a goal number: ").strip())
    except ValueError as error:
        print(error)
        return

    amount = prompt_goal_amount("Contribution amount")
    contribution = add_contribution(
        data["goals"], data["savings_contributions"], goal["id"], amount
    )
    save_data(data, file_path)
    progress = calculate_goal_progress(goal)
    print(
        f"Added ${contribution['amount']:,.2f} to {goal['name']}. "
        f"Updated savings: ${goal['current_savings']:,.2f}."
    )
    if progress["estimated_months"] is None:
        print("Estimated time is unavailable until a monthly savings plan is set.")
    else:
        print(f"Updated estimated time: {progress['estimated_months']} months.")


def display_financial_coach(data: dict) -> None:
    """Ask for a month and display rule-based financial coaching insights."""
    while True:
        month = input("Month (1-12): ").strip()
        year = input("Year (for example, 2026): ").strip()
        try:
            month, year = validate_month_year(month, year)
            break
        except ValueError as error:
            print(error)

    analysis = build_coach_analysis(data["expenses"], data["goals"], month, year)
    print("\n===== AI FINANCIAL COACH =====")
    print(f"\nMonth: {month_name[month]} {year}")
    print(f"Total Monthly Spending: ${analysis['total']:.2f}")
    print("These guidelines are general suggestions, not universal standards.")

    if analysis["message"]:
        print(f"\n{analysis['message']}")
    else:
        print("\nAI Insight:")
        for insight in analysis["insights"]:
            print(
                f"Your {insight['category'].lower()} spending accounts for "
                f"{insight['percentage']:.1f}% of your monthly expenses."
            )
            print(
                f"This is above the suggested guideline of "
                f"{insight['threshold']}%. {insight['message']}"
            )
            if analysis["goal"]:
                if analysis["goal"].get("planned_monthly_contribution") is None:
                    print(
                        f'Reducing {insight["category"].lower()} expenses by '
                        f"${insight['suggested_reduction']:.2f} per month could help you "
                        f"reach your \"{analysis['goal']['name']}\" savings goal sooner."
                    )
                else:
                    print(
                        f'Reducing {insight["category"].lower()} expenses by '
                        f"${insight['suggested_reduction']:.2f} per month could help you "
                        f"reach your \"{analysis['goal']['name']}\" savings goal sooner."
                    )
            else:
                print(
                    f"Reducing {insight['category'].lower()} expenses by "
                    f"${insight['suggested_reduction']:.2f} per month could increase "
                    "your available savings."
                )

        if analysis["goal"]:
            progress = analysis["goal_progress"]
            if analysis["goal"].get("planned_monthly_contribution") is None:
                print("\nMonthly savings plan not set. Consider setting one to estimate progress.")
            print("\nCurrent Goal Progress:")
            print(f"{progress['bar']} {min(progress['progress_percentage'], 100):.1f}%")
            print(f"Remaining Savings: ${progress['remaining_amount']:,.2f}")
            total_potential_savings = sum(
                insight["suggested_reduction"] for insight in analysis["insights"]
            )
            print(
                f"Potential Additional Savings: ${total_potential_savings:.2f} per month."
            )
            projection = analysis["goal_projection"]
            if projection:
                print("\nProjected Impact on Your Savings Goal:")
                print(f"Current Goal Progress: {projection['current_progress']:.2f}%")
                print(
                    "Next Month (Current Plan): "
                    f"{projection['current_plan_progress']:.2f}%"
                )
                print(
                    "Next Month (With AI Advice): "
                    f"{projection['progress_with_advice']:.2f}%"
                )
                print(
                    f"By redirecting ${projection['suggested_reductions']:.2f} toward "
                    "your savings goal, you could gain an additional "
                    f"{projection['additional_progress']:.2f} percentage points of "
                    "progress next month."
                )
                print(
                    "This projection assumes you maintain your planned monthly "
                    "contribution and successfully redirect the suggested spending "
                    "reduction toward your savings goal. It is an estimate, not a "
                    "guarantee, and does not assume that you can afford either amount."
                )
        elif analysis["completed_goals_message"]:
            print(f"\n{analysis['completed_goals_message']}")

    input("Press Enter to return to the main menu...")


def run_menu(file_path: Path = DATA_FILE) -> None:
    """Load saved data and repeatedly show the main menu."""
    data = load_data(file_path)
    if assign_missing_reference_ids(data["expenses"]):
        save_data(data, file_path)
    while True:
        print("\n===== PENNYWISE =====")
        print("1. Manage Expenses")
        print("2. Monthly Spending Overview")
        print("3. Manage Savings Goals")
        print("4. AI Financial Coach")
        print("5. Exit")

        choice = input("Select an option: ").strip()
        if choice == "1":
            manage_expenses_menu(data, file_path)
        elif choice == "2":
            display_monthly_overview(data)
        elif choice == "3":
            manage_savings_goals_menu(data, file_path)
        elif choice == "4":
            display_financial_coach(data)
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Please choose a number from 1 to 5.")


def manage_expenses_menu(data: dict, file_path: Path = DATA_FILE) -> None:
    """Show expense actions until the user returns to the main menu."""
    while True:
        print("\n===== MANAGE EXPENSES =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. Back to Main Menu")

        choice = input("Select an option: ").strip()
        if choice == "1":
            add_expense_from_menu(data, file_path)
        elif choice == "2":
            display_expenses(data["expenses"])
            input("Press Enter to return to the Manage Expenses submenu...")
        elif choice == "3":
            edit_expense_from_menu(data, file_path)
        elif choice == "4":
            delete_expense_from_menu(data, file_path)
        elif choice == "5":
            return
        else:
            print("Please choose a number from 1 to 5.")


def manage_savings_goals_menu(data: dict, file_path: Path = DATA_FILE) -> None:
    """Show savings actions until the user returns to the main menu."""
    while True:
        print("\n===== MANAGE SAVINGS GOALS =====")
        print("1. Create Savings Goal")
        print("2. View Savings Goals")
        print("3. Add Savings Contribution")
        print("4. Edit Savings Goal")
        print("5. Back to Main Menu")

        choice = input("Select an option: ").strip()
        if choice == "1":
            create_goal_from_menu(data, file_path)
        elif choice == "2":
            display_savings_goals(data["goals"])
            input("Press Enter to return to the Manage Savings Goals submenu...")
        elif choice == "3":
            add_savings_contribution_from_menu(data, file_path)
        elif choice == "4":
            edit_savings_goal_from_menu(data, file_path)
        elif choice == "5":
            return
        else:
            print("Please choose a number from 1 to 5.")


def main() -> None:
    """Start the PennyWise menu."""
    run_menu()


if __name__ == "__main__":
    main()