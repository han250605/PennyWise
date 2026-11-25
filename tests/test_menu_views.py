"""Integration tests for viewing expense and savings records from the menu."""

from expenses import add_expense
from goals import create_goal
from main import run_menu
from storage import create_empty_data, save_data


def test_menu_view_actions_show_saved_records_before_returning(tmp_path, monkeypatch, capsys) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    expense = add_expense(data["expenses"], 24, "Shopping", "Notebook", "2026-03-12")
    goal = create_goal(data["goals"], "New Laptop", 1200, 300)
    save_data(data, data_file)

    answers = iter(["1", "2", "", "5", "3", "2", "", "5", "5"])
    prompts = []

    def fake_input(prompt: str = "") -> str:
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)

    run_menu(data_file)

    output = capsys.readouterr().out
    expense_return_prompt = "Press Enter to return to the Manage Expenses submenu..."
    savings_return_prompt = "Press Enter to return to the Manage Savings Goals submenu..."
    assert "===== MANAGE EXPENSES =====" in output
    assert "===== MANAGE SAVINGS GOALS =====" in output
    assert "Notebook" in output
    assert f"ID: {expense['reference_id']}" in output
    assert expense["id"] not in output
    assert "[1] New Laptop" in output
    assert goal["id"] not in output
    assert prompts == [
        "Select an option: ",
        "Select an option: ",
        expense_return_prompt,
        "Select an option: ",
        "Select an option: ",
        "Select an option: ",
        savings_return_prompt,
        "Select an option: ",
        "Select an option: ",
    ]


def test_menu_view_actions_show_empty_messages_before_returning(
    tmp_path, monkeypatch, capsys
) -> None:
    data_file = tmp_path / "pennywise.json"
    answers = iter(["1", "2", "", "5", "3", "2", "", "5", "5"])
    prompts = []

    def fake_input(prompt: str = "") -> str:
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)

    run_menu(data_file)

    output = capsys.readouterr().out
    expense_return_prompt = "Press Enter to return to the Manage Expenses submenu..."
    savings_return_prompt = "Press Enter to return to the Manage Savings Goals submenu..."
    assert "No expenses have been recorded yet." in output
    assert "No savings goals have been created yet." in output
    assert prompts == [
        "Select an option: ",
        "Select an option: ",
        expense_return_prompt,
        "Select an option: ",
        "Select an option: ",
        "Select an option: ",
        savings_return_prompt,
        "Select an option: ",
        "Select an option: ",
    ]


def test_invalid_main_and_submenu_choices_are_handled(tmp_path, monkeypatch, capsys) -> None:
    answers = iter(["bad", "1", "bad", "5", "3", "9", "5", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(tmp_path / "pennywise.json")

    output = capsys.readouterr().out
    assert output.count("Please choose a number from 1 to 5.") == 3


def test_expense_add_edit_delete_all_work_inside_expenses_submenu(
    tmp_path, monkeypatch, capsys
) -> None:
    from expenses import secrets

    data_file = tmp_path / "pennywise.json"
    monkeypatch.setattr(secrets, "randbelow", lambda _limit: 234567)
    answers = iter(
        [
            "1", "1", "25", "1", "Lunch", "2026-11-24",
            "3", "334567", "30", "1", "Dinner", "2026-11-25",
            "4", "334567", "5", "5",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    output = capsys.readouterr().out
    assert "Expense added successfully!" in output
    assert "Expense updated." in output
    assert "Deleted expense: Dinner." in output
    assert "===== MANAGE EXPENSES =====" in output