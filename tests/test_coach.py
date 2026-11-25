"""Tests for the rule-based financial coach."""

import pytest

from coach import build_coach_analysis, calculate_goal_projection
from expenses import add_expense
from goals import create_goal, update_goal_name, update_goal_target_amount
from main import run_menu
from storage import create_empty_data, save_data


def make_expenses(category_amounts: dict[str, float], total: float = 1000) -> list[dict]:
    """Create November expenses with any remainder assigned to Housing."""
    expenses = []
    category_total = sum(category_amounts.values())
    if category_total < total:
        category_amounts = {**category_amounts, "Housing": total - category_total}
    for category, amount in category_amounts.items():
        if amount:
            add_expense(expenses, amount, category, "Test purchase", "2026-11-15")
    return expenses


def test_entertainment_above_threshold_has_dynamic_reduction() -> None:
    analysis = build_coach_analysis(make_expenses({"Entertainment": 300}), [], 11, 2026)

    assert len(analysis["insights"]) == 1
    insight = analysis["insights"][0]
    assert insight["category"] == "Entertainment"
    assert insight["percentage"] == 30
    assert insight["suggested_reduction"] == 60


def test_shopping_above_threshold_triggers_recommendation() -> None:
    analysis = build_coach_analysis(make_expenses({"Shopping": 250}), [], 11, 2026)

    assert [insight["category"] for insight in analysis["insights"]] == ["Shopping"]
    assert analysis["insights"][0]["suggested_reduction"] == 50


def test_food_dining_above_threshold_triggers_recommendation() -> None:
    analysis = build_coach_analysis(make_expenses({"Food & Dining": 350}), [], 11, 2026)

    assert [insight["category"] for insight in analysis["insights"]] == ["Food & Dining"]
    assert analysis["insights"][0]["suggested_reduction"] == 70


def test_spending_exactly_at_threshold_does_not_trigger_rule() -> None:
    analysis = build_coach_analysis(make_expenses({"Entertainment": 250}), [], 11, 2026)

    assert analysis["insights"] == []
    assert "within the suggested guidelines" in analysis["message"]


def test_multiple_rules_trigger_independent_recommendations() -> None:
    expenses = make_expenses(
        {"Entertainment": 300, "Shopping": 250, "Food & Dining": 350},
        total=1000,
    )

    analysis = build_coach_analysis(expenses, [], 11, 2026)

    assert {insight["category"] for insight in analysis["insights"]} == {
        "Entertainment",
        "Shopping",
        "Food & Dining",
    }
    assert sum(insight["suggested_reduction"] for insight in analysis["insights"]) == 180


def test_no_rules_provide_supportive_guidance() -> None:
    analysis = build_coach_analysis(make_expenses({"Entertainment": 100}), [], 11, 2026)

    assert analysis["insights"] == []
    assert analysis["message"]
    assert "within the suggested guidelines" in analysis["message"]


def test_empty_month_reports_insufficient_data() -> None:
    analysis = build_coach_analysis(make_expenses({"Entertainment": 300}), [], 10, 2026)

    assert analysis["total"] == 0
    assert analysis["insights"] == []
    assert "not enough spending data" in analysis["message"]


def test_recommendations_work_without_savings_goals() -> None:
    analysis = build_coach_analysis(make_expenses({"Shopping": 300}), [], 11, 2026)

    assert analysis["insights"]
    assert analysis["goal"] is None
    assert analysis["goal_progress"] is None


def test_first_unfinished_goal_is_attached_to_recommendation() -> None:
    goals = [
        {"id": "done", "name": "Completed Goal", "target_amount": 100, "current_savings": 100},
        {"id": "first-open", "name": "Car", "target_amount": 1000, "current_savings": 400},
        {"id": "second-open", "name": "Trip", "target_amount": 500, "current_savings": 10},
    ]

    analysis = build_coach_analysis(make_expenses({"Entertainment": 300}), goals, 11, 2026)

    assert analysis["goal"]["id"] == "first-open"
    assert analysis["goal_progress"]["progress_percentage"] == 40
    assert analysis["goal_progress"]["remaining_amount"] == 600


def test_goal_projection_calculates_current_and_next_month_progress() -> None:
    goal = {
        "target_amount": 3000,
        "current_savings": 1200,
        "planned_monthly_contribution": 100,
    }
    original_savings = goal["current_savings"]

    projection = calculate_goal_projection(goal, 18)

    assert projection["current_progress"] == 40
    assert projection["current_plan_progress"] == pytest.approx(43.333333)
    assert projection["progress_with_advice"] == pytest.approx(43.933333)
    assert projection["additional_progress"] == pytest.approx(0.6)
    assert projection["suggested_reductions"] == 18
    assert goal["current_savings"] == original_savings


def test_multiple_reductions_are_combined_once_in_projection() -> None:
    expenses = make_expenses({"Entertainment": 300, "Shopping": 250}, total=1000)
    goal = {
        "id": "open",
        "name": "Car",
        "target_amount": 1000,
        "current_savings": 400,
        "planned_monthly_contribution": 100,
    }

    analysis = build_coach_analysis(expenses, [goal], 11, 2026)

    assert len(analysis["insights"]) == 2
    assert analysis["goal_projection"]["suggested_reductions"] == 110


def test_goal_projection_caps_progress_at_one_hundred_percent() -> None:
    projection = calculate_goal_projection(
        {"target_amount": 100, "current_savings": 95, "planned_monthly_contribution": 20},
        50,
    )

    assert projection["current_progress"] == 95
    assert projection["current_plan_progress"] == 100
    assert projection["progress_with_advice"] == 100
    assert projection["additional_progress"] == 0


def test_coach_skips_projection_when_plan_is_missing_or_goal_is_complete() -> None:
    expenses = make_expenses({"Shopping": 300})
    missing_plan = {
        "id": "no-plan",
        "name": "Camera",
        "target_amount": 1000,
        "current_savings": 250,
    }
    completed_goal = {
        "id": "complete",
        "name": "Bike",
        "target_amount": 1000,
        "current_savings": 1000,
        "planned_monthly_contribution": 100,
    }

    without_plan = build_coach_analysis(expenses, [missing_plan], 11, 2026)
    completed = build_coach_analysis(expenses, [completed_goal], 11, 2026)

    assert without_plan["goal_projection"] is None
    assert completed["goal"] is None
    assert completed["goal_projection"] is None


def test_no_triggered_recommendation_has_no_projected_extra_savings() -> None:
    goal = {
        "id": "open",
        "name": "Car",
        "target_amount": 1000,
        "current_savings": 400,
        "planned_monthly_contribution": 100,
    }

    analysis = build_coach_analysis(make_expenses({"Shopping": 100}), [goal], 11, 2026)

    assert analysis["insights"] == []
    assert analysis["goal_projection"] is None


def test_coach_projection_uses_updated_goal_name_and_target() -> None:
    goal = create_goal([], "Old Goal", 1000, 400, 100)
    update_goal_name(goal, "Emergency Fund")
    update_goal_target_amount(goal, 2000)

    analysis = build_coach_analysis(
        make_expenses({"Entertainment": 300}), [goal], 11, 2026
    )

    assert analysis["goal"]["name"] == "Emergency Fund"
    assert analysis["goal"]["target_amount"] == 2000
    assert analysis["goal_projection"]["current_progress"] == 20
    assert analysis["goal_projection"]["current_plan_progress"] == 25
    assert analysis["goal_projection"]["progress_with_advice"] == pytest.approx(28)
    assert goal["current_savings"] == 400


def test_completed_goals_receive_positive_feedback_with_triggered_rule() -> None:
    goals = [{"id": "done", "name": "Car", "target_amount": 100, "current_savings": 100}]

    analysis = build_coach_analysis(make_expenses({"Shopping": 300}), goals, 11, 2026)

    assert analysis["insights"]
    assert analysis["completed_goals_message"]
    assert "complete" in analysis["completed_goals_message"]


def test_cli_coach_displays_recommendation_goal_and_return_prompt(
    tmp_path, monkeypatch, capsys
) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    add_expense(data["expenses"], 300, "Entertainment", "Concerts", "2026-11-15")
    add_expense(data["expenses"], 700, "Housing", "Rent", "2026-11-01")
    create_goal(data["goals"], "Buy a Car", 1000, 400, 100)
    save_data(data, data_file)
    answers = iter(["4", "11", "2026", "", "5"])
    prompts = []

    def fake_input(prompt: str = "") -> str:
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)

    run_menu(data_file)

    output = capsys.readouterr().out
    assert "===== AI FINANCIAL COACH =====" in output
    assert "Month: November 2026" in output
    assert "30.0%" in output
    assert "$60.00" in output
    assert '"Buy a Car" savings goal' in output
    assert "Current Goal Progress:" in output
    assert "Remaining Savings: $600.00" in output
    assert "Projected Impact on Your Savings Goal:" in output
    assert "Current Goal Progress: 40.00%" in output
    assert "Next Month (Current Plan): 50.00%" in output
    assert "Next Month (With AI Advice): 56.00%" in output
    assert "6.00 percentage points" in output
    assert "Press Enter to return to the main menu..." in prompts


def test_cli_coach_suggests_plan_for_legacy_goal_without_prompting_for_amount(
    monkeypatch, capsys
) -> None:
    from main import display_financial_coach

    goal = {"id": "legacy", "name": "Camera", "target_amount": 1000, "current_savings": 250}
    data = {"expenses": make_expenses({"Shopping": 300}), "goals": [goal]}
    answers = iter(["11", "2026", ""])
    prompts = []

    def fake_input(prompt: str = "") -> str:
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)

    display_financial_coach(data)

    output = capsys.readouterr().out
    assert "Monthly savings plan not set" in output
    assert "Projected Impact on Your Savings Goal" not in output
    assert "Planned monthly contribution:" not in prompts
    assert goal["current_savings"] == 250