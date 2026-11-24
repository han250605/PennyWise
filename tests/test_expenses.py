"""Tests for expense validation and management."""

import pytest

from expenses import add_expense, delete_expense, edit_expense
from main import run_menu
from storage import create_empty_data, load_data, save_data


def test_add_expense_records_all_fields_and_unique_id() -> None:
    expenses = []

    first = add_expense(expenses, "12.50", "Food & Dining", "Lunch", "2026-03-10")
    second = add_expense(expenses, 8, "Transportation", "Bus fare", "2026-03-11")

    assert first["amount"] == 12.5
    assert first["category"] == "Food & Dining"
    assert first["description"] == "Lunch"
    assert first["date"] == "2026-03-10"
    assert first["id"]
    assert second["id"] != first["id"]
    assert len(expenses) == 2


def test_edit_expense_updates_selected_fields_and_keeps_id() -> None:
    expenses = []
    added = add_expense(expenses, 12, "Food & Dining", "Lunch", "2026-03-10")

    edited = edit_expense(
        expenses,
        added["id"],
        amount=15,
        description="Dinner",
    )

    assert edited["id"] == added["id"]
    assert edited["amount"] == 15
    assert edited["description"] == "Dinner"
    assert edited["category"] == "Food & Dining"
    assert edited["date"] == "2026-03-10"


def test_delete_expense_removes_and_returns_record() -> None:
    expenses = []
    added = add_expense(expenses, 12, "Food & Dining", "Lunch", "2026-03-10")

    deleted = delete_expense(expenses, added["id"])

    assert deleted == added
    assert expenses == []


@pytest.mark.parametrize("amount", [0, -4, "not a number", "nan", "inf"])
def test_add_expense_rejects_invalid_amount(amount) -> None:
    with pytest.raises(ValueError):
        add_expense([], amount, "Food & Dining", "Lunch", "2026-03-10")


@pytest.mark.parametrize(
    ("category", "description", "expense_date"),
    [
        ("Unlisted", "Lunch", "2026-03-10"),
        ("Food & Dining", "  ", "2026-03-10"),
        ("Food & Dining", "Lunch", "2026-02-30"),
        ("Food & Dining", "Lunch", "03/10/2026"),
    ],
)
def test_add_expense_rejects_invalid_category_description_or_date(
    category, description, expense_date
) -> None:
    with pytest.raises(ValueError):
        add_expense([], 12, category, description, expense_date)


def test_edit_and_delete_report_unknown_ids() -> None:
    with pytest.raises(ValueError, match="No expense found"):
        edit_expense([], "unknown", description="New description")
    with pytest.raises(ValueError, match="No expense found"):
        delete_expense([], "unknown")


def test_expense_changes_can_be_saved_and_loaded(tmp_path) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    add_expense(data["expenses"], 24, "Shopping", "Notebook", "2026-03-12")

    save_data(data, data_file)

    assert load_data(data_file)["expenses"] == data["expenses"]


def test_menu_adds_an_expense_and_saves_it(tmp_path, monkeypatch) -> None:
    data_file = tmp_path / "pennywise.json"
    answers = iter(["1", "18.25", "1", "Groceries", "2026-03-15", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    saved_expenses = load_data(data_file)["expenses"]
    assert len(saved_expenses) == 1
    assert saved_expenses[0]["amount"] == 18.25
    assert saved_expenses[0]["category"] == "Food & Dining"
    assert saved_expenses[0]["description"] == "Groceries"
    assert saved_expenses[0]["date"] == "2026-03-15"