# PennyWise Contributor And Agent Guide

## Purpose

PennyWise is a beginner-friendly Python command-line app for expense tracking, monthly spending summaries, savings goals, and rule-based financial guidance. Keep it a terminal application; do not turn it into a web or mobile app.

## Environment Setup

Use Python 3.12. From the project root, create and activate a virtual environment:

```text
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, create the environment with `py -3.12 -m venv .venv` and activate using `.venv\Scripts\Activate.ps1` in PowerShell or `.venv\Scripts\activate.bat` in Command Prompt.

Run the app with:

```text
python main.py
```

Run tests with:

```text
python -m pytest -v
```

## Project Structure

- `main.py`: terminal input/output, main menu, submenus, and calls to feature functions.
- `expenses.py`: expense validation, short reference IDs, and expense list operations.
- `reports.py`: monthly date filtering, totals, percentages, category ranking, and report bars.
- `goals.py`: savings goal validation and editing, contribution handling, progress, and estimated completion time.
- `coach.py`: rule-based recommendations and next-month goal projections.
- `storage.py`: JSON data loading and saving.
- `tests/`: unit and CLI integration tests; all file-based tests should use pytest temporary paths.
- `data/`: local personal finance data; it is ignored by Git.

## Coding Conventions

- Use readable Python 3.12 syntax, four spaces for indentation, and `snake_case` for functions and variables.
- Prefer small functions with clear names and parameters. Keep beginner-facing code direct; avoid unnecessary classes, abstractions, and dependencies.
- Keep calculations and validation in feature modules, separate from terminal prompts and printed output in `main.py`.
- Add or update docstrings when a function's purpose is not obvious. Keep comments focused on reasoning that is not clear from the code.
- Use pytest assertions for known behavior and edge cases. Keep tests independent of real user data.
- Preserve existing CLI menu behavior, data compatibility, expense reference IDs, goal order, and financial calculations unless the user specifically requests a change.

## Data Safety Requirements

- Preserve all existing expenses, savings goals, and contribution history.
- Never print, copy into logs, or otherwise expose real personal financial data.
- Never use the real `data/pennywise_data.json` file in tests; use `tmp_path` or in-memory data.
- Preserve backward compatibility with older JSON records, especially goals without a planned contribution and expenses needing reference-ID migration.
- Do not overwrite malformed user data automatically. Report the problem and leave the source file available for recovery.
- Keep `data/*.json`, `.venv/`, `__pycache__/`, and `.pytest_cache/` excluded from Git.

## Workflow Expectations

- Read the relevant module and tests before editing; make a focused change and run the relevant tests followed by the full suite when appropriate.
- Avoid broad refactoring during feature work. Explain why any nontrivial change is necessary.
- Do not add a dependency unless the existing standard library cannot reasonably meet the requirement.
- Use meaningful commit messages that briefly describe the change, such as `Add monthly spending report tests`. Do not commit or push unless the user explicitly approves.
- Never create or rewrite Git history without explicit user direction.

## Do Not Change Without Approval

- Do not change or remove personal financial data.
- Do not commit or push changes.
- Do not replace the rule-based coach with external AI services or claim that it is generative AI.
- Do not change expense/goal JSON fields or financial formulas without confirming compatibility and updating tests.