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

    answers = iter(["2", "", "7", "", "9"])
    prompts = []

    def fake_input(prompt: str = "") -> str:
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)

    run_menu(data_file)

    output = capsys.readouterr().out
    return_prompt = "Press Enter to return to the menu..."
    assert "Notebook" in output
    assert f"ID: {expense['reference_id']}" in output
    assert expense["id"] not in output
    assert "[1] New Laptop" in output
    assert goal["id"] not in output
    assert prompts == [
        "Select an option: ",
        return_prompt,
        "Select an option: ",
        return_prompt,
        "Select an option: ",
    ]


def test_menu_view_actions_show_empty_messages_before_returning(
    tmp_path, monkeypatch, capsys
) -> None:
    data_file = tmp_path / "pennywise.json"
    answers = iter(["2", "", "7", "", "9"])
    prompts = []

    def fake_input(prompt: str = "") -> str:
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)

    run_menu(data_file)

    output = capsys.readouterr().out
    return_prompt = "Press Enter to return to the menu..."
    assert "No expenses have been recorded yet." in output
    assert "No savings goals have been created yet." in output
    assert prompts == [
        "Select an option: ",
        return_prompt,
        "Select an option: ",
        return_prompt,
        "Select an option: ",
    ]