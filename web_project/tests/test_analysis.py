from pathlib import Path

import pandas as pd

from app.analysis import calculate_metrics, clean_data, compare_players, prepare_dataset

ROOT = Path(__file__).resolve().parents[1]


def test_real_dataset_pipeline():
    df, report = prepare_dataset(ROOT / "data" / "nba_player_stats_2023_24.csv")
    assert len(df) > 0
    assert report["final_rows"] == len(df)
    assert "balanced_score" in df.columns


def test_edge_case_cleaning():
    df, report = prepare_dataset(ROOT / "data" / "test_edge_cases.csv")
    assert len(df) >= 2
    assert report["removed_blank_rows"] >= 1
    assert report["removed_critical_rows"] >= 1


def test_zero_turnover_does_not_crash():
    df = pd.DataFrame({
        "player": ["A"], "age": [20], "team": ["T"], "position": ["PG"], "games": [10],
        "minutes_per_game": [20], "fg_pct": [0.5], "three_pct": [0.4], "ft_pct": [0.8],
        "oreb_per_game": [1], "dreb_per_game": [2], "rpg": [3], "apg": [4], "spg": [1],
        "bpg": [0], "tov_per_game": [0], "pts_per_game": [20],
    })
    cleaned, _ = clean_data(df)
    analysed = calculate_metrics(cleaned)
    assert analysed.loc[0, "assist_to_turnover"] == 0


def test_compare_requires_two_valid_names():
    df, _ = prepare_dataset(ROOT / "data" / "nba_player_stats_2023_24.csv")
    result = compare_players(df, "Joel Embiid", "Luka Doncic")
    assert list(result.index) == ["Joel Embiid", "Luka Doncic"]
