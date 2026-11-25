"""Tests for loading and saving PennyWise JSON data."""

import json

from storage import create_empty_data, load_data, save_data
from main import run_menu


def test_create_empty_data_has_expected_sections() -> None:
    assert create_empty_data() == {
        "expenses": [],
        "goals": [],
        "savings_contributions": [],
        "monthly_budget": None,
    }


def test_load_data_returns_defaults_for_missing_file(tmp_path) -> None:
    assert load_data(tmp_path / "missing.json") == create_empty_data()


def test_load_data_returns_defaults_for_empty_file(tmp_path) -> None:
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("  \n", encoding="utf-8")

    assert load_data(empty_file) == create_empty_data()


def test_save_data_creates_folder_and_loads_saved_data(tmp_path) -> None:
    data_file = tmp_path / "nested" / "pennywise.json"
    data = create_empty_data()
    data["expenses"] = [{"amount": 12.5, "description": "Lunch"}]

    save_data(data, data_file)

    assert load_data(data_file) == data


def test_save_data_writes_readable_json(tmp_path) -> None:
    data_file = tmp_path / "pennywise.json"

    save_data(create_empty_data(), data_file)

    assert json.loads(data_file.read_text(encoding="utf-8")) == create_empty_data()


def test_menu_reports_malformed_json_without_overwriting_file(tmp_path, capsys) -> None:
    data_file = tmp_path / "malformed.json"
    original_contents = "{ this is not valid JSON"
    data_file.write_text(original_contents, encoding="utf-8")

    run_menu(data_file)

    assert "Could not load PennyWise data" in capsys.readouterr().out
    assert data_file.read_text(encoding="utf-8") == original_contents