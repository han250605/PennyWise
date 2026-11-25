"""Tests for savings goal calculations and contribution tracking."""

import pytest

from goals import (
    add_contribution,
    calculate_goal_progress,
    create_goal,
    update_goal_name,
    update_goal_target_amount,
    update_monthly_contribution,
)
from main import run_menu
from storage import create_empty_data, load_data, save_data


def test_create_goal_stores_values_and_unique_id() -> None:
    goals = []

    first = create_goal(goals, "  New Laptop  ", 1200, 250)
    second = create_goal(goals, "Vacation", 2000)

    assert first["name"] == "New Laptop"
    assert first["target_amount"] == 1200
    assert first["current_savings"] == 250
    assert first["id"]
    assert second["id"] != first["id"]
    assert len(goals) == 2


def test_add_contribution_updates_goal_and_tracks_separately() -> None:
    goals = []
    contributions = []
    goal = create_goal(goals, "Bike", 1000, 200)

    contribution = add_contribution(goals, contributions, goal["id"], "50.50")

    assert goal["current_savings"] == 250.5
    assert contribution["amount"] == 50.5
    assert contribution["goal_id"] == goal["id"]
    assert contributions == [contribution]


def test_goal_progress_calculates_remaining_and_percentage() -> None:
    goal = {"target_amount": 15000, "current_savings": 6000}

    progress = calculate_goal_progress(goal)

    assert progress["remaining_amount"] == 9000
    assert progress["progress_percentage"] == 40
    assert progress["status"] == "In Progress"
    assert progress["bar"] == "█" * 8 + "░" * 12
    assert progress["estimated_months"] is None


def test_goal_estimated_months_round_up_from_planned_contribution() -> None:
    goal = create_goal([], "Car", 10000, 6000, 1500)

    assert calculate_goal_progress(goal)["estimated_months"] == 3


def test_estimated_months_recalculate_after_contribution() -> None:
    goals = []
    goal = create_goal(goals, "Car", 10000, 1000, 3000)

    add_contribution(goals, [], goal["id"], 2000)

    assert calculate_goal_progress(goal)["estimated_months"] == 3


def test_update_monthly_savings_plan_changes_estimate() -> None:
    goal = create_goal([], "Laptop", 1200, 200, 200)

    update_monthly_contribution(goal, "250")

    assert goal["planned_monthly_contribution"] == 250
    assert calculate_goal_progress(goal)["estimated_months"] == 4


def test_update_goal_name_preserves_other_values() -> None:
    goal = create_goal([], "Old Name", 1200, 200, 200)
    original_goal_id = goal["id"]

    update_goal_name(goal, "New Name")

    assert goal["name"] == "New Name"
    assert goal["id"] == original_goal_id
    assert goal["current_savings"] == 200
    assert goal["target_amount"] == 1200


def test_update_goal_target_preserves_actual_savings() -> None:
    goal = create_goal([], "Car", 15000, 4000, 500)

    update_goal_target_amount(goal, "5000")
    progress = calculate_goal_progress(goal)

    assert goal["target_amount"] == 5000
    assert goal["current_savings"] == 4000
    assert progress["remaining_amount"] == 1000
    assert progress["progress_percentage"] == 80
    assert progress["estimated_months"] == 2


def test_lowering_target_below_balance_marks_goal_achieved() -> None:
    goal = create_goal([], "Car", 15000, 6000, 500)

    update_goal_target_amount(goal, 5000)
    progress = calculate_goal_progress(goal)

    assert goal["current_savings"] == 6000
    assert progress["remaining_amount"] == 0
    assert progress["progress_percentage"] == 100
    assert progress["estimated_months"] == 0
    assert progress["status"] == "Goal achieved!"


@pytest.mark.parametrize("amount", [0, -1, "invalid", float("inf"), float("nan")])
def test_planned_monthly_contribution_must_be_positive_and_finite(amount) -> None:
    with pytest.raises(ValueError):
        create_goal([], "Goal", 1000, 0, amount)


@pytest.mark.parametrize("amount", [0, -1, "invalid", float("inf"), float("nan")])
def test_updated_monthly_plan_must_be_positive_and_finite(amount) -> None:
    goal = create_goal([], "Goal", 1000, 0)

    with pytest.raises(ValueError):
        update_monthly_contribution(goal, amount)

    assert goal["planned_monthly_contribution"] is None


@pytest.mark.parametrize("name", ["", "   "])
def test_updated_goal_name_rejects_blank_values(name) -> None:
    goal = create_goal([], "Original", 1000)

    with pytest.raises(ValueError):
        update_goal_name(goal, name)

    assert goal["name"] == "Original"


@pytest.mark.parametrize("amount", [0, -1, "invalid", float("inf"), float("nan")])
def test_updated_goal_target_must_be_positive_and_finite(amount) -> None:
    goal = create_goal([], "Goal", 1000, 200)

    with pytest.raises(ValueError):
        update_goal_target_amount(goal, amount)

    assert goal["target_amount"] == 1000


@pytest.mark.parametrize("current_savings", [15000, 17500])
def test_goal_at_or_over_target_is_achieved_and_bar_is_full(current_savings) -> None:
    progress = calculate_goal_progress(
        {
            "target_amount": 15000,
            "current_savings": current_savings,
            "planned_monthly_contribution": 500,
        }
    )

    assert progress["remaining_amount"] == 0
    assert progress["progress_percentage"] >= 100
    assert progress["bar"] == "█" * 20
    assert progress["status"] == "Goal achieved!"
    assert progress["estimated_months"] == 0


@pytest.mark.parametrize(
    ("name", "target_amount", "current_savings"),
    [
        ("  ", 100, 0),
        ("Laptop", 0, 0),
        ("Laptop", -10, 0),
        ("Laptop", "invalid", 0),
        ("Laptop", 100, -1),
        ("Laptop", 100, "invalid"),
        ("Laptop", float("inf"), 0),
    ],
)
def test_create_goal_rejects_invalid_values(name, target_amount, current_savings) -> None:
    with pytest.raises(ValueError):
        create_goal([], name, target_amount, current_savings)


@pytest.mark.parametrize("amount", [0, -5, "invalid", float("nan")])
def test_add_contribution_rejects_invalid_amount(amount) -> None:
    goals = []
    goal = create_goal(goals, "Camera", 500)

    with pytest.raises(ValueError):
        add_contribution(goals, [], goal["id"], amount)


def test_goal_and_contribution_data_can_be_saved_and_reloaded(tmp_path) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    goal = create_goal(data["goals"], "Trip", 2000, 500)
    add_contribution(data["goals"], data["savings_contributions"], goal["id"], 100)

    save_data(data, data_file)

    loaded_data = load_data(data_file)
    assert loaded_data["goals"] == data["goals"]
    assert loaded_data["savings_contributions"] == data["savings_contributions"]
    assert loaded_data["expenses"] == []


def test_menu_creates_goal_and_saves_it(tmp_path, monkeypatch, capsys) -> None:
    data_file = tmp_path / "pennywise.json"
    answers = iter(["3", "1", "Emergency fund", "5000", "300", "250", "5", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    saved_data = load_data(data_file)
    assert len(saved_data["goals"]) == 1
    assert saved_data["goals"][0]["name"] == "Emergency fund"
    assert saved_data["goals"][0]["target_amount"] == 5000
    assert saved_data["goals"][0]["current_savings"] == 300
    assert saved_data["goals"][0]["planned_monthly_contribution"] == 250
    assert saved_data["expenses"] == []
    output = capsys.readouterr().out
    assert "Savings goal created successfully!" in output
    assert saved_data["goals"][0]["id"] not in output


def test_menu_adds_contribution_without_creating_expense(
    tmp_path, monkeypatch, capsys
) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    create_goal(data["goals"], "New phone", 1000, 100, 100)
    second_goal = create_goal(data["goals"], "Camera", 1500, 200, 200)
    save_data(data, data_file)
    answers = iter(["3", "3", "2", "75", "5", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    saved_data = load_data(data_file)
    assert saved_data["goals"][0]["current_savings"] == 100
    assert saved_data["goals"][1]["id"] == second_goal["id"]
    assert saved_data["goals"][1]["current_savings"] == 275
    assert saved_data["savings_contributions"][0]["amount"] == 75
    assert saved_data["savings_contributions"][0]["goal_id"] == second_goal["id"]
    assert saved_data["expenses"] == []
    output = capsys.readouterr().out
    assert "[1] New phone" in output
    assert "[2] Camera" in output
    assert second_goal["id"] not in output
    assert "Updated savings: $275.00" in output
    assert "Updated estimated time: 7 months." in output


def test_menu_rejects_invalid_goal_number_without_changing_goals(
    tmp_path, monkeypatch, capsys
) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    goal = create_goal(data["goals"], "Bike", 800, 100)
    save_data(data, data_file)
    answers = iter(["3", "3", "2", "5", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    saved_data = load_data(data_file)
    output = capsys.readouterr().out
    assert saved_data["goals"][0] == goal
    assert saved_data["savings_contributions"] == []
    assert "Choose a number from the displayed goal list." in output


def test_view_goals_displays_progress_and_empty_list(capsys) -> None:
    from main import display_savings_goals

    display_savings_goals([])
    display_savings_goals(
        [{"id": "goal-1", "name": "Camera", "target_amount": 500, "current_savings": 250}]
    )

    output = capsys.readouterr().out
    assert "No savings goals have been created yet." in output
    assert "[1] Camera" in output
    assert "Remaining Amount: $250.00" in output
    assert "50.0%" in output
    assert "Status: In Progress" in output
    assert "goal-1" not in output


def test_goal_display_numbers_goals_in_creation_order(capsys) -> None:
    from main import display_savings_goals

    display_savings_goals(
        [
            {"id": "internal-uuid-a", "name": "Car", "target_amount": 100, "current_savings": 0},
            {"id": "internal-uuid-b", "name": "Laptop", "target_amount": 200, "current_savings": 0},
        ]
    )

    output = capsys.readouterr().out
    assert "[1] Car" in output
    assert "[2] Laptop" in output
    assert "internal-uuid" not in output


def test_old_goal_displays_unset_monthly_savings_plan(capsys) -> None:
    from main import display_savings_goals

    display_savings_goals(
        [{"id": "old-id", "name": "Older Goal", "target_amount": 100, "current_savings": 25}]
    )

    assert "Monthly savings plan not set" in capsys.readouterr().out


def test_edit_goal_can_update_savings_plan_from_numbered_submenu(
    tmp_path, monkeypatch
) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    create_goal(data["goals"], "Car", 10000, 4000)
    save_data(data, data_file)
    answers = iter(["3", "4", "1", "6", "1500", "7", "5", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    saved_goal = load_data(data_file)["goals"][0]
    assert saved_goal["planned_monthly_contribution"] == 1500
    assert calculate_goal_progress(saved_goal)["estimated_months"] == 4


def test_edit_goal_menu_updates_name_and_target_without_changing_contributions(
    tmp_path, monkeypatch, capsys
) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    goal = create_goal(data["goals"], "Old Car", 15000, 4000, 500)
    data["savings_contributions"] = [
        {"id": "contribution-id", "goal_id": goal["id"], "amount": 4000}
    ]
    save_data(data, data_file)
    answers = iter(["3", "4", "1", "4", "New Car", "5", "5000", "7", "5", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    saved_data = load_data(data_file)
    edited_goal = saved_data["goals"][0]
    assert edited_goal["name"] == "New Car"
    assert edited_goal["target_amount"] == 5000
    assert edited_goal["current_savings"] == 4000
    assert edited_goal["id"] == goal["id"]
    assert saved_data["savings_contributions"] == data["savings_contributions"]
    assert calculate_goal_progress(edited_goal)["estimated_months"] == 2
    output = capsys.readouterr().out
    assert "Current Goal Name: Old Car" in output
    assert "Current Target Amount: $15,000.00" in output
    assert "Savings goal updated successfully!" in output


def test_edit_goal_menu_displays_achieved_state_when_target_drops_below_savings(
    tmp_path, monkeypatch, capsys
) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    create_goal(data["goals"], "Car", 15000, 6000, 500)
    save_data(data, data_file)
    answers = iter(["3", "4", "1", "5", "5000", "7", "5", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    output = capsys.readouterr().out
    assert "Remaining Amount: $0.00" in output
    assert "Progress: 100.0%" in output
    assert "Estimated Time: 0 months" in output
    assert "Status: Goal achieved!" in output


def test_planned_contribution_is_persisted(tmp_path) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    create_goal(data["goals"], "Vacation", 3000, 500, 250)

    save_data(data, data_file)

    assert load_data(data_file)["goals"][0]["planned_monthly_contribution"] == 250