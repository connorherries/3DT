"""One-time/automatic CSV -> cleaned analysis -> MySQL importer."""
from pathlib import Path

import database
from analysis import prepare_dataset

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "nba_player_stats_2023_24.csv"


def main() -> None:
    database.wait_for_database()
    database.initialise_schema()
    if database.count_stats() == 0:
        df, report = prepare_dataset(DATA_PATH)
        imported = database.import_dataframe(df, season="2023-24")
        print(f"Imported {imported} records into MySQL.")
        print(f"Cleaning report: {report}")
    else:
        print(f"Database already contains {database.count_stats()} player records; no import needed.")


if __name__ == "__main__":
    main()
