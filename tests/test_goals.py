"""Tests for savings goal calculations and contribution tracking."""

import pytest

from goals import add_contribution, calculate_goal_progress, create_goal
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


@pytest.mark.parametrize("current_savings", [15000, 17500])
def test_goal_at_or_over_target_is_achieved_and_bar_is_full(current_savings) -> None:
    progress = calculate_goal_progress(
        {"target_amount": 15000, "current_savings": current_savings}
    )

    assert progress["remaining_amount"] == 0
    assert progress["progress_percentage"] >= 100
    assert progress["bar"] == "█" * 20
    assert progress["status"] == "Goal achieved!"


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
    answers = iter(["6", "Emergency fund", "5000", "300", "9"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    run_menu(data_file)

    saved_data = load_data(data_file)
    assert len(saved_data["goals"]) == 1
    assert saved_data["goals"][0]["name"] == "Emergency fund"
    assert saved_data["goals"][0]["target_amount"] == 5000
    assert saved_data["goals"][0]["current_savings"] == 300
    assert saved_data["expenses"] == []
    output = capsys.readouterr().out
    assert "Savings goal created successfully!" in output
    assert saved_data["goals"][0]["id"] not in output


def test_menu_adds_contribution_without_creating_expense(
    tmp_path, monkeypatch, capsys
) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    first_goal = create_goal(data["goals"], "New phone", 1000, 100)
    second_goal = create_goal(data["goals"], "Camera", 1500, 200)
    save_data(data, data_file)
    answers = iter(["8", "2", "75", "9"])
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


def test_menu_rejects_invalid_goal_number_without_changing_goals(
    tmp_path, monkeypatch, capsys
) -> None:
    data_file = tmp_path / "pennywise.json"
    data = create_empty_data()
    goal = create_goal(data["goals"], "Bike", 800, 100)
    save_data(data, data_file)
    answers = iter(["8", "2", "9"])
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