"""Load and save PennyWise data as a local JSON file."""

import json
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).parent / "data" / "pennywise_data.json"


def create_empty_data() -> dict[str, Any]:
    """Return the starting structure used when no saved data exists."""
    return {
        "expenses": [],
        "goals": [],
        "savings_contributions": [],
        "monthly_budget": None,
    }


def load_data(file_path: Path = DATA_FILE) -> dict[str, Any]:
    """Read saved data, or return an empty structure for a missing or empty file."""
    if not file_path.exists():
        return create_empty_data()

    file_contents = file_path.read_text(encoding="utf-8")
    if not file_contents.strip():
        return create_empty_data()

    loaded_data = json.loads(file_contents)
    if not isinstance(loaded_data, dict):
        raise ValueError("The PennyWise data file must contain a JSON object.")

    empty_data = create_empty_data()
    for key, default_value in empty_data.items():
        loaded_data.setdefault(key, default_value)

    return loaded_data


def save_data(data: dict[str, Any], file_path: Path = DATA_FILE) -> None:
    """Write data to JSON, creating its parent folder if needed."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8",
    )