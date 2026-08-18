"""Reusable sports data-analysis functions for the web application and assessment.

The module deliberately keeps the complex data-processing work separate from Flask so
it can be tested independently and clearly evidenced for NCEA AS 91906.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "player", "age", "team", "position", "games", "minutes_per_game",
    "fg_pct", "three_pct", "ft_pct", "oreb_per_game", "dreb_per_game",
    "rpg", "apg", "spg", "bpg", "tov_per_game", "pts_per_game",
]
TEXT_COLUMNS = {"player", "team", "position"}
NUMERIC_COLUMNS = [c for c in REQUIRED_COLUMNS if c not in TEXT_COLUMNS]


def read_csv_robust(path: str | Path) -> pd.DataFrame:
    """Read CSV using several common encodings and keep blank rows for validation."""
    path = Path(path)
    errors: list[str] = []
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return pd.read_csv(path, encoding=encoding, skip_blank_lines=False)
        except UnicodeDecodeError as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError("Could not decode CSV: " + "; ".join(errors))


def validate_columns(df: pd.DataFrame) -> None:
    """Ensure all required fields exist before manipulating the dataset."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean text, coerce malformed numbers, remove unusable rows and report changes."""
    validate_columns(df)
    work = df.copy()
    original_rows = len(work)

    for column in TEXT_COLUMNS:
        work[column] = work[column].astype("string").str.strip()

    for column in NUMERIC_COLUMNS:
        work[column] = pd.to_numeric(work[column], errors="coerce")

    empty_rows = work["player"].isna() | (work["player"].str.len() == 0)
    removed_empty = int(empty_rows.sum())
    work = work.loc[~empty_rows].copy()

    critical_numeric = ["games", "minutes_per_game", "pts_per_game"]
    invalid_critical = work[critical_numeric].isna().any(axis=1)
    removed_critical = int(invalid_critical.sum())
    work = work.loc[~invalid_critical].copy()

    filled_values: dict[str, float] = {}
    for column in NUMERIC_COLUMNS:
        missing_count = int(work[column].isna().sum())
        if missing_count:
            median = float(work[column].median())
            work[column] = work[column].fillna(median)
            filled_values[column] = median

    before_dedup = len(work)
    work = work.drop_duplicates(subset=["player", "team"], keep="first").reset_index(drop=True)
    duplicates_removed = before_dedup - len(work)

    report = {
        "original_rows": original_rows,
        "final_rows": len(work),
        "removed_blank_rows": removed_empty,
        "removed_critical_rows": removed_critical,
        "filled_numeric_columns": filled_values,
        "duplicates_removed": duplicates_removed,
    }
    return work, report


def z_scores(values: pd.Series) -> pd.Series:
    """Calculate NumPy z-scores while safely handling zero-variance columns."""
    arr = values.to_numpy(dtype=float)
    mean = np.mean(arr)
    std = np.std(arr)
    if std == 0 or np.isnan(std):
        return pd.Series(np.zeros(len(arr)), index=values.index)
    return pd.Series((arr - mean) / std, index=values.index)


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived performance metrics using NumPy and pandas operations."""
    work = df.copy()
    work["fg_attempts_proxy"] = np.where(
        work["fg_pct"] > 0,
        (work["pts_per_game"] / 2) / work["fg_pct"],
        0,
    )
    attempts = work["fg_attempts_proxy"].to_numpy(dtype=float)
    points = work["pts_per_game"].to_numpy(dtype=float)
    turnovers = work["tov_per_game"].to_numpy(dtype=float)
    assists = work["apg"].to_numpy(dtype=float)

    work["scoring_efficiency"] = np.divide(
        points, attempts, out=np.zeros(len(work)), where=attempts != 0
    )
    work["assist_to_turnover"] = np.divide(
        assists, turnovers, out=np.zeros(len(work)), where=turnovers != 0
    )
    work["stocks_per_game"] = work["spg"] + work["bpg"]
    work["total_rebounds_check"] = work["oreb_per_game"] + work["dreb_per_game"]

    raw_impact = (
        points
        + 1.2 * work["rpg"].to_numpy(dtype=float)
        + 1.5 * assists
        + 3.0 * work["stocks_per_game"].to_numpy(dtype=float)
        - turnovers
    )
    work["composite_impact"] = raw_impact
    work["impact_z"] = z_scores(work["composite_impact"])
    points_array = work["pts_per_game"].to_numpy(dtype=float)
    work["pts_percentile"] = np.array([
        np.mean(points_array <= x) * 100 for x in points_array
    ])

    dimensions = ["pts_per_game", "rpg", "apg", "spg", "bpg", "ft_pct"]
    z_matrix = np.column_stack([z_scores(work[col]).to_numpy() for col in dimensions])
    weights = np.array([0.30, 0.20, 0.20, 0.10, 0.10, 0.10])
    work["balanced_score"] = np.round(z_matrix @ weights, 3)
    return work.sort_values("composite_impact", ascending=False).reset_index(drop=True)


def prepare_dataset(path: str | Path) -> tuple[pd.DataFrame, dict]:
    """Run the full CSV -> clean -> derived metrics pipeline."""
    raw = read_csv_robust(path)
    cleaned, report = clean_data(raw)
    analysed = calculate_metrics(cleaned)
    return analysed, report


def filter_players(
    df: pd.DataFrame,
    query: str = "",
    position: str = "ALL",
    min_games: int = 0,
) -> pd.DataFrame:
    """Filter by text, position and minimum games using composable conditions."""
    result = df.copy()
    query = query.strip().lower()
    if query:
        result = result[result["player"].str.lower().str.contains(query, na=False)]
    if position.upper() != "ALL":
        result = result[result["position"].str.upper() == position.upper()]
    result = result[result["games"] >= min_games]
    return result


def position_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build a grouped statistical summary for positional analysis."""
    grouped = df.groupby("position").agg(
        players=("player", "count"),
        avg_points=("pts_per_game", "mean"),
        avg_rebounds=("rpg", "mean"),
        avg_assists=("apg", "mean"),
        avg_impact=("composite_impact", "mean"),
        points_std=("pts_per_game", "std"),
    )
    return grouped.round(3).sort_values("avg_impact", ascending=False)


def compare_players(df: pd.DataFrame, first: str, second: str) -> pd.DataFrame:
    """Return side-by-side metrics for two named players."""
    lookup = {name.lower(): name for name in df["player"]}
    if first.lower() not in lookup or second.lower() not in lookup:
        raise ValueError("Both player names must exist in the dataset.")
    players = [lookup[first.lower()], lookup[second.lower()]]
    cols = [
        "pts_per_game", "rpg", "apg", "spg", "bpg", "ft_pct",
        "composite_impact", "balanced_score",
    ]
    return df[df["player"].isin(players)][["player", "position"] + cols].set_index("player")


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return a correlation matrix for key performance dimensions."""
    return df[["pts_per_game", "apg", "rpg", "spg", "bpg", "ft_pct", "composite_impact"]].corr().round(3)


def plot_scoring_vs_assists(df: pd.DataFrame, output_dir: str | Path) -> Path:
    """Render a scatter plot plus NumPy least-squares trendline."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    x = df["apg"].to_numpy(dtype=float)
    y = df["pts_per_game"].to_numpy(dtype=float)
    coefficients = np.polyfit(x, y, 1)
    trend = np.poly1d(coefficients)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x, y)
    order = np.argsort(x)
    ax.plot(x[order], trend(x[order]), linewidth=2)
    ax.set_xlabel("Assists per game")
    ax.set_ylabel("Points per game")
    ax.set_title("NBA 2023–24: Scoring vs Playmaking")
    ax.grid(alpha=0.25)
    path = output / "scoring_vs_assists.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_comparison(comparison: pd.DataFrame, output_dir: str | Path, filename: str = "player_comparison.png") -> Path:
    """Render a two-player normalised comparison chart."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    metrics = ["pts_per_game", "rpg", "apg", "spg", "bpg", "ft_pct"]
    matrix = comparison[metrics].to_numpy(dtype=float)
    mins = matrix.min(axis=0)
    maxs = matrix.max(axis=0)
    ranges = np.where((maxs - mins) == 0, 1, maxs - mins)
    normalised = (matrix - mins) / ranges

    x = np.arange(len(metrics))
    width = 0.38
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, normalised[0], width, label=comparison.index[0])
    ax.bar(x + width / 2, normalised[1], width, label=comparison.index[1])
    ax.set_xticks(x, ["Points", "Rebounds", "Assists", "Steals", "Blocks", "FT%"])
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Normalised value (0–1 within comparison)")
    ax.set_title(f"Player comparison: {comparison.index[0]} vs {comparison.index[1]}")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    path = output / filename
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def build_quiz_questions(df: pd.DataFrame, number: int = 5) -> list[dict]:
    """Generate data-driven active-recall comparison questions."""
    players = df.sample(n=min(number + 2, len(df)), random_state=42).reset_index(drop=True)
    questions: list[dict] = []
    metrics = [
        ("pts_per_game", "Who scored more points per game?"),
        ("apg", "Who recorded more assists per game?"),
        ("rpg", "Who recorded more rebounds per game?"),
        ("composite_impact", "Who has the higher Composite Impact Score?"),
    ]
    for i in range(number):
        left = players.iloc[i]
        right = players.iloc[i + 1]
        column, prompt = metrics[i % len(metrics)]
        winner = left["player"] if left[column] > right[column] else right["player"]
        questions.append({
            "question": f"{prompt} {left['player']} or {right['player']}?",
            "left": left["player"],
            "right": right["player"],
            "winner": winner,
            "metric": column,
        })
    return questions


def save_quiz_result(score: int, total: int, output_dir: str | Path) -> Path:
    """Persist a simple quiz result for local evidence/debugging."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / "quiz_results.json"
    payload = {"score": score, "total": total, "percentage": round(score / total * 100, 1) if total else 0}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
