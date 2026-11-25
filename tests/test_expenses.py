"""Tests for expense validation and management."""

import pytest

from expenses import (
    add_expense,
    assign_missing_reference_ids,
    delete_expense,
    edit_expense,
)
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
    assert len(first["reference_id"]) == 6
    assert first["reference_id"].isdigit()
    assert first["id"]
    assert first["id"] != first["reference_id"]
    assert second["id"] != first["id"]
    assert second["reference_id"] != first["reference_id"]
    assert len(expenses) == 2


def test_edit_expense_updates_selected_fields_and_keeps_id() -> None:
    expenses = []
    added = add_expense(expenses, 12, "Food & Dining", "Lunch", "2026-03-10")

    edited = edit_expense(
        expenses,
        added["reference_id"],
        amount=15,
        description="Dinner",
    )

    assert edited["id"] == added["id"]
    assert edited["reference_id"] == added["reference_id"]
    assert edited["amount"] == 15
    assert edited["description"] == "Dinner"
    assert edited["category"] == "Food & Dining"
    assert edited["date"] == "2026-03-10"


def test_delete_expense_removes_and_returns_record() -> None:
    expenses = []
    added = add_expense(expenses, 12, "Food & Dining", "Lunch", "2026-03-10")

    deleted = delete_expense(expenses, added["reference_id"])

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

    loaded_expenses = load_data(data_file)["expenses"]
    assert loaded_expenses == data["expenses"]
    assert loaded_expenses[0]["reference_id"] == data["expenses"][0]["reference_id"]


def test_reference_generation_retries_on_collision(monkeypatch) -> None:
    from expenses import generate_reference_id

    expenses = [{"reference_id": "123456"}]
    generated_values = iter([23456, 23457])
    monkeypatch.setattr("expenses.secrets.randbelow", lambda _limit: next(generated_values))

    assert generate_reference_id(expenses) == "123457"


def test_legacy_expenses_receive_unique_references_without_losing_data(monkeypatch) -> None:
    expenses = [
        {
            "id": "original-uuid-1",
            "amount": 42.5,
            "category": "Food & Dining",
            "description": "Lunch",
            "date": "2026-11-23",
        },
        {
            "id": "original-uuid-2",
            "amount": 30,
            "category": "Transportation",
            "description": "Gas",
            "date": "2026-11-24",
            "reference_id": "123456",
        },
    ]
    generated_values = iter([23456, 23457])
    monkeypatch.setattr("expenses.secrets.randbelow", lambda _limit: next(generated_values))

    changed = assign_missing_reference_ids(expenses)

    assert changed
    assert expenses[0]["reference_id"] == "123457"
    assert expenses[1]["reference_id"] == "123456"
    assert expenses[0]["id"] == "original-uuid-1"
    assert expenses[0]["description"] == "Lunch"
    assert expenses[0]["amount"] == 42.5


def test_menu_migrates_and_persists_reference_id_for_legacy_expense(
    tmp_path, monkeypatch
) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    data["expenses"] = [
        {
            "id": "legacy-uuid",
            "amount": 20,
            "category": "Shopping",
            "description": "Book",
            "date": "2026-11-22",
        }
    ]
    save_data(data, data_file)
    monkeypatch.setattr("expenses.secrets.randbelow", lambda _limit: 654321)
    answers = iter(["1", "5", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    loaded_expense = load_data(data_file)["expenses"][0]
    assert loaded_expense["id"] == "legacy-uuid"
    assert loaded_expense["reference_id"] == "754321"
    assert loaded_expense["description"] == "Book"


def test_menu_adds_an_expense_and_saves_it(tmp_path, monkeypatch) -> None:
    data_file = tmp_path / "pennywise.json"
    answers = iter(["1", "1", "18.25", "1", "Groceries", "2026-03-15", "5", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    saved_expenses = load_data(data_file)["expenses"]
    assert len(saved_expenses) == 1
    assert saved_expenses[0]["amount"] == 18.25
    assert saved_expenses[0]["category"] == "Food & Dining"
    assert saved_expenses[0]["description"] == "Groceries"
    assert saved_expenses[0]["date"] == "2026-03-15"