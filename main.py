"""Start the PennyWise command-line application."""

from storage import load_data


def main() -> None:
    """Load saved data and confirm the application is ready."""
    load_data()
    print("PennyWise is ready. More features will be added in upcoming phases.")


if __name__ == "__main__":
    main()