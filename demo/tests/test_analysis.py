from pathlib import Path

import pandas as pd
import pytest

from demo.analyze_data import (
    INPUT_CSV,
    POSITION_ORDER,
    calculate_metrics,
    clean_data,
    generate_analysis,
    position_averages,
    read_csv_robust,
    trim_dataset,
)


# Supplied file should clean up, trim down, positions should look right.
def test_updated_csv_is_cleaned_and_analysed():
    raw_data = read_csv_robust(INPUT_CSV)
    cleaned, report = clean_data(raw_data)
    all_metrics = calculate_metrics(cleaned)
    featured, selection_report = trim_dataset(all_metrics)
    expected = all_metrics.sort_values("PTS", ascending=False, kind="stable").head(len(cleaned) - 200)
    analysed = calculate_metrics(featured)

    assert len(analysed) == 382
    assert selection_report["trimmed_players_count"] == 200
    assert "players_before_trim" in selection_report
    assert featured["Player"].tolist() == expected["Player"].tolist()
    assert report["removed_invalid_rows"] >= 1
    assert report["removed_trade_split_rows"] >= 50
    assert analysed["Player"].is_unique
    assert analysed["impact"].notna().all()
    for metric in ("PTS", "TRB", "AST"):
        assert tuple(position_averages(analysed, metric).index) == POSITION_ORDER


# Small fixture for blanks, bad values, missing stats and traded-player rows.
def test_cleaning_handles_blank_invalid_missing_and_trade_rows():
    rows = [
        ["Alpha Player", "alpha01", 25, "2TM", "PG", 60, 34.0, 0.400, 5.0, 7.0, 1.0, 0.5, 3.0, 25.0],
        ["Alpha Player", "alpha01", 25, "AAA", "PG", 30, 34.0, 0.400, 5.0, 7.0, 1.0, 0.5, 3.0, 25.0],
        ["Alpha Player", "alpha01", 25, "BBB", "PG", 30, 34.0, 0.400, 5.0, 7.0, 1.0, 0.5, 3.0, 25.0],
        ["Broken Player", "broken01", 24, "CCC", "SG", "bad", 30.0, 0.350, 4.0, 4.0, 1.0, 0.3, 2.0, 18.0],
        ["Beta Player", "beta01", 23, "DDD", "SF", 40, 31.0, None, 6.0, 3.0, 0.8, 0.2, 1.0, 16.0],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None],
    ]
    columns = [
        "Player", "Player-additional", "Age", "Team", "Pos", "G", "MP", "3P%",
        "TRB", "AST", "STL", "BLK", "TOV", "PTS",
    ]

    cleaned, report = clean_data(pd.DataFrame(rows, columns=columns))

    assert cleaned["Player"].tolist() == ["Alpha Player", "Beta Player"]
    assert report["removed_blank_rows"] == 1
    assert report["removed_invalid_rows"] == 1
    assert report["removed_trade_split_rows"] == 2
    assert cleaned["3P%"].notna().all()


# Two bad inputs here, both should give readable errors.
def test_missing_required_column_and_empty_cleaned_data_are_reported():
    with pytest.raises(ValueError, match="Missing required columns"):
        clean_data(pd.DataFrame({"Player": ["Only a name"]}))

    empty = pd.DataFrame(columns=read_csv_robust(INPUT_CSV).columns)
    with pytest.raises(ValueError, match="No valid player records remain"):
        clean_data(empty)


# Quick check the exports, including all three selectable charts.
def test_analysis_exports_json_csv_and_chart(tmp_path: Path):
    files = generate_analysis(INPUT_CSV, tmp_path)

    assert set(files) == {
        "players", "summary", "cleaned_csv",
        "chart_points", "chart_rebounds", "chart_assists",
    }
    assert all(path.exists() and path.stat().st_size > 0 for path in files.values())
    assert len(pd.read_json(files["players"])) == 382
    assert "position_summary" in pd.read_json(files["summary"], typ="series")
    assert len({files[key].read_bytes() for key in ("chart_points", "chart_rebounds", "chart_assists")}) == 3
