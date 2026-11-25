"""Tests for monthly spending report calculations."""

import pytest

from expenses import add_expense
from main import run_menu
from reports import build_monthly_report, validate_month_year
from storage import create_empty_data, save_data


def make_expenses() -> list[dict]:
    """Create sample transactions spanning different categories and months."""
    expenses = []
    add_expense(expenses, 150, "Housing", "Rent", "2026-11-01")
    add_expense(expenses, 120, "Entertainment", "Concert", "2026-11-12")
    add_expense(expenses, 50, "Food & Dining", "Groceries", "2026-11-18")
    add_expense(expenses, 30, "Transportation", "Bus pass", "2026-11-20")
    add_expense(expenses, 900, "Shopping", "Winter coat", "2026-10-25")
    return expenses


def test_monthly_report_filters_by_month_and_year() -> None:
    report = build_monthly_report(make_expenses(), 11, 2026)

    assert report["total"] == 350
    assert len(report["categories"]) == 4


def test_monthly_report_calculates_total_spending() -> None:
    report = build_monthly_report(make_expenses(), "11", "2026")

    assert report["total"] == 350


def test_monthly_report_calculates_category_percentages() -> None:
    report = build_monthly_report(make_expenses(), 11, 2026)
    category_by_name = {item["category"]: item for item in report["categories"]}

    assert category_by_name["Housing"]["percentage"] == pytest.approx(150 / 350 * 100)
    assert category_by_name["Entertainment"]["percentage"] == pytest.approx(120 / 350 * 100)
    assert sum(item["percentage"] for item in report["categories"]) == pytest.approx(100)


def test_monthly_report_sorts_categories_and_identifies_highest_and_lowest() -> None:
    report = build_monthly_report(make_expenses(), 11, 2026)

    assert [item["category"] for item in report["categories"]] == [
        "Housing",
        "Entertainment",
        "Food & Dining",
        "Transportation",
    ]
    assert report["highest_category"] == "Housing"
    assert report["lowest_category"] == "Transportation"


def test_monthly_report_uses_consistent_chart_scale() -> None:
    report = build_monthly_report(make_expenses(), 11, 2026)
    housing = report["categories"][0]
    expected_filled_length = round(housing["percentage"] / 100 * 20)
    if housing["amount"] > 0 and expected_filled_length == 0:
        expected_filled_length = 1

    assert len(housing["bar"]) == 20
    assert housing["bar"] == "█" * expected_filled_length + "░" * (20 - expected_filled_length)


def test_monthly_report_displays_category_and_amount_above_bar(capsys, monkeypatch) -> None:
    from main import display_monthly_overview

    answers = iter(["11", "2026"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    display_monthly_overview({"expenses": make_expenses()})

    output = capsys.readouterr().out
    assert "Housing            $ 150.00\n  " in output
    assert "█" in output
    assert "░" in output


def test_month_without_expenses_returns_zero_and_no_category_names() -> None:
    report = build_monthly_report(make_expenses(), 9, 2026)

    assert report["total"] == 0
    assert report["categories"] == []
    assert report["highest_category"] is None
    assert report["lowest_category"] is None


def test_menu_displays_monthly_report_from_saved_expenses(tmp_path, monkeypatch, capsys) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    add_expense(data["expenses"], 150, "Housing", "Rent", "2026-11-01")
    add_expense(data["expenses"], 50, "Food & Dining", "Groceries", "2026-11-18")
    add_expense(data["expenses"], 500, "Shopping", "Earlier month", "2026-10-25")
    save_data(data, data_file)
    answers = iter(["5", "11", "2026", "6"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    output = capsys.readouterr().out
    assert "Month: November 2026" in output
    assert "Total Monthly Spending: $200.00" in output
    assert "Highest Spending Category: Housing" in output
    assert "Lowest Spending Category: Food & Dining" in output
    assert "Earlier month" not in output


@pytest.mark.parametrize(
    ("month", "year"),
    [(0, 2026), (13, 2026), ("November", 2026), (11, 0), (11, 10000)],
)
def test_month_year_validation_rejects_invalid_values(month, year) -> None:
    with pytest.raises(ValueError):
        validate_month_year(month, year)