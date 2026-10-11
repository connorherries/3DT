"""Clean the NBA CSV, calculate analysis metrics, and export demo data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DEMO_DIR = Path(__file__).resolve().parent
INPUT_CSV = DEMO_DIR / "data" / "csv"
OUTPUT_DIR = DEMO_DIR / "generated"
BOTTOM_PLAYERS_TO_REMOVE = 200

REQUIRED_COLUMNS = [
    "Player", "Age", "Team", "Pos", "G", "MP", "3P%", "TRB",
    "AST", "STL", "BLK", "TOV", "PTS",
]

CORE_NUMERIC_COLUMNS = [
    "Age", "G", "MP", "TRB", "AST", "STL", "BLK", "TOV", "PTS",
]
NUMERIC_COLUMNS = [*CORE_NUMERIC_COLUMNS, "3P%"]

#links player data to photo

PHOTO_BY_PLAYER_ID = {
    "antetgi01": "Giannis.png",
    "bookede01": "booker.png",
    "curryst01": "steph.png",
    "davisan02": "AD.png",
    "doncilu01": "luka.png",
    "gilgesh01": "SGA.png",
    "jamesle01": "lebron.png",
    "jokicni01": "jokic.png",
    "tatumja01": "tatum.png",
    "edwaran01": "anthonyedwards.png",
    "brunsja01": "brunson.png",
    "cunnica01": "cade.png",
    "embiijo01": "embiid.avif",
    "brownja02": "jalenbrown.webp",
    "johnsja05": "jalenjohnson.webp",
    "leonaka01": "kawhi.png",
    "duranke01": "kd.webp",
    "maxeyty01": "maxey.avif",
    "wembavi01": "wemby.png",

}
POSITION_METRICS = {
    "points": ("PTS", "points per game"),
    "rebounds": ("TRB", "rebounds per game"),
    "assists": ("AST", "assists per game"),
}
POSITION_ORDER = ("PG", "SG", "SF", "PF", "C")


def read_csv_robust(path: str | Path) -> pd.DataFrame:
    """Read the CSV with common encodings while retaining blank rows for cleaning."""
    path = Path(path)
    decode_errors: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return pd.read_csv(path, encoding=encoding, skip_blank_lines=False)
        except UnicodeDecodeError as error:
            decode_errors.append(f"{encoding}: {error}")
    raise ValueError("Could not decode CSV: " + "; ".join(decode_errors))


def clean_data(data: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Validate fields, clean values, and keep one season-total row per player."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    work = data.copy()
    original_rows = len(work)
    for column in ("Player", "Team", "Pos"):
        work[column] = work[column].astype("string").str.strip()
    for column in NUMERIC_COLUMNS:
        work[column] = pd.to_numeric(work[column], errors="coerce")

    empty_rows = work["Player"].isna() | work["Player"].eq("")
    removed_blank_rows = int(empty_rows.sum())
    work = work.loc[~empty_rows].copy()

    invalid_rows = work[CORE_NUMERIC_COLUMNS].isna().any(axis=1)
    invalid_rows |= work[["Team", "Pos"]].isna().any(axis=1)
    invalid_rows |= work["Team"].eq("") | work["Pos"].eq("")
    removed_invalid_rows = int(invalid_rows.sum())
    work = work.loc[~invalid_rows].copy()

    filled_numeric_values: dict[str, dict[str, float | int]] = {}
    for column in NUMERIC_COLUMNS:
        missing_count = int(work[column].isna().sum())
        if missing_count:
            median = float(work[column].median()) if work[column].notna().any() else 0.0
            work[column] = work[column].fillna(median)
            filled_numeric_values[column] = {"count": missing_count, "median": median}

    if "Player-additional" in work.columns:
        player_key = work["Player-additional"].astype("string").str.strip()
        player_key = player_key.mask(player_key.isna() | player_key.eq(""), work["Player"])
    else:
        player_key = work["Player"]
    work["_player_key"] = player_key.str.casefold()

    season_totals = set(work.loc[work["Team"].eq("2TM"), "_player_key"])
    team_splits = work["_player_key"].isin(season_totals) & work["Team"].ne("2TM")
    removed_trade_splits = int(team_splits.sum())
    work = work.loc[~team_splits].copy()

    before_deduplication = len(work)
    work = work.drop_duplicates(subset="_player_key", keep="first")
    duplicates_removed = before_deduplication - len(work)
    work = work.drop(columns="_player_key").reset_index(drop=True)
    if work.empty:
        raise ValueError("No valid player records remain after cleaning the CSV.")

    report = {
        "original_rows": original_rows,
        "removed_blank_rows": removed_blank_rows,
        "removed_invalid_rows": removed_invalid_rows,
        "filled_numeric_values": filled_numeric_values,
        "removed_trade_split_rows": removed_trade_splits,
        "duplicates_removed": duplicates_removed,
        "final_rows": len(work),
    }
    return work, report


def trim_dataset(
    data: pd.DataFrame,
    trim_count: int = BOTTOM_PLAYERS_TO_REMOVE,
) -> tuple[pd.DataFrame, dict]:
    """Reduce the dataset to a teaching-sized roster by dropping the lowest-scoring players."""
    if trim_count < 0:
        raise ValueError("trim_count cannot be negative")
    if "PTS" not in data.columns:
        raise ValueError("Calculate points per game before trimming the dataset.")

    ranked = data.sort_values("PTS", ascending=False, kind="stable").reset_index(drop=True)
    retained_count = max(0, len(ranked) - trim_count) if len(ranked) else 0
    retained = ranked.head(retained_count).copy() if retained_count else pd.DataFrame(columns=ranked.columns)
    removed_count = len(ranked) - len(retained)
    report = {
        "players_before_trim": len(ranked),
        "trimmed_players_count": removed_count,
        "final_rows": len(retained),
        "lowest_retained_points": float(retained["PTS"].min()) if len(retained) else None,
        "lowest_retained_impact": float(retained["impact"].min()) if len(retained) else None,
    }
    return retained, report


def calculate_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate composite, standardized, percentile, and weighted metrics."""
    work = data.copy()
    points = work["PTS"].to_numpy(dtype=float)
    rebounds = work["TRB"].to_numpy(dtype=float)
    assists = work["AST"].to_numpy(dtype=float)
    steals = work["STL"].to_numpy(dtype=float)
    blocks = work["BLK"].to_numpy(dtype=float)
    turnovers = work["TOV"].to_numpy(dtype=float)

    impact = points + 1.2 * rebounds + 1.5 * assists + 3.0 * (steals + blocks) - turnovers
    work["impact"] = impact
    impact_std = float(np.std(impact))  # Standard deviation of impact
    work["impact_z"] = (impact - float(np.mean(impact))) / impact_std if impact_std else np.zeros(len(work))
    work["points_percentile"] = pd.Series(points).rank(pct=True).to_numpy() * 100

    dimensions = np.column_stack((points, rebounds, assists, steals, blocks, work["3P%"].to_numpy(dtype=float)))
    means = np.mean(dimensions, axis=0)
    standard_deviations = np.std(dimensions, axis=0)
    z_scores = np.divide(  # Calculate z-scores
        dimensions - means,
        standard_deviations,
        out=np.zeros_like(dimensions),
        where=standard_deviations != 0,
    )
    weights = np.array([0.30, 0.20, 0.20, 0.10, 0.10, 0.10])
    work["balanced_score"] = np.round(z_scores @ weights, 3)
    return work.sort_values("PTS", ascending=False, kind="stable").reset_index(drop=True)


def build_summary(data: pd.DataFrame, cleaning_report: dict) -> dict:
    """Create concise cohort and position summaries for the learning page."""
    position_rows = data.groupby("Pos").agg(
        player_count=("Player", "count"),
        average_points=("PTS", "mean"),
        average_impact=("impact", "mean"),
    )
    position_rows = position_rows.reindex(ordered_position_names(position_rows.index)).reset_index()
    position_summary = [
        {
            "position": row.Pos,
            "player_count": int(row.player_count),
            "average_points": round(float(row.average_points), 2),
            "average_impact": round(float(row.average_impact), 2),
        }
        for row in position_rows.itertuples(index=False)
    ]
    points = data["PTS"].to_numpy(dtype=float)
    return {
        "player_count": len(data),
        "mean_points": round(float(np.mean(points)), 2),
        "std_points": round(float(np.std(points)), 2),
        "mean_impact": round(float(np.mean(data["impact"].to_numpy(dtype=float))), 2),
        "top_scorer": str(data.iloc[0]["Player"]),
        "position_summary": position_summary,
        "cleaning_report": cleaning_report,
    }


def make_player_records(data: pd.DataFrame) -> list[dict]:
    """Map cleaned CSV records to the names and units used by the demo pages."""
    records = []
    for index, row in data.iterrows():
        player_id = str(row.get("Player-additional", ""))
        records.append({
            "id": index + 1,
            "name": str(row["Player"]),
            "team": str(row["Team"]),
            "position": str(row["Pos"]),
            "age": int(row["Age"]),
            "games": int(row["G"]),
            "minutes": round(float(row["MP"]), 1),
            "points": round(float(row["PTS"]), 1),
            "rebounds": round(float(row["TRB"]), 1),
            "assists": round(float(row["AST"]), 1),
            "steals": round(float(row["STL"]), 1),
            "blocks": round(float(row["BLK"]), 1),
            "three": round(float(row["3P%"] * 100), 1),
            "impact": round(float(row["impact"]), 1),
            "photo": f"images/{PHOTO_BY_PLAYER_ID[player_id]}"
            if player_id in PHOTO_BY_PLAYER_ID else "",
        })
    return records


def ordered_position_names(available_positions) -> list[str]:
    """Return standard positions in basketball order, then any extra labels."""
    available = set(available_positions)
    ordered = [position for position in POSITION_ORDER if position in available]
    ordered.extend(sorted(available - set(POSITION_ORDER)))
    return ordered


def position_averages(data: pd.DataFrame, metric_column: str) -> pd.Series:
    """Calculate one position average series in a stable left-to-right order."""
    means = data.groupby("Pos")[metric_column].mean()
    return means.reindex(ordered_position_names(means.index))


def plot_analysis(
    data: pd.DataFrame,
    output_path: str | Path,
    average_metric: str = "points",
) -> Path:
    """Save a trendline chart and a selectable position-average chart."""
    if average_metric not in POSITION_METRICS:
        raise ValueError(f"Unsupported position-average metric: {average_metric}")
    metric_column, metric_label = POSITION_METRICS[average_metric]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    x_values = data["AST"].to_numpy(dtype=float)
    y_values = data["PTS"].to_numpy(dtype=float)
    figure, (scatter_axis, position_axis) = plt.subplots(1, 2, figsize=(12, 5))
    scatter_axis.scatter(
        x_values,
        y_values,
        alpha=1,
        color="#a83c2e",
        edgecolors="white",
        linewidths=0.4,
    )
    if len(x_values) > 1 and np.ptp(x_values) > 0:
        coefficients = np.polyfit(x_values, y_values, 1)
        trend_x = np.linspace(float(np.min(x_values)), float(np.max(x_values)), 100)
        scatter_axis.plot(trend_x, np.polyval(coefficients, trend_x), color="#203d38", linewidth=2)
    scatter_axis.set(title="Scoring and playmaking", xlabel="Assists per game", ylabel="Points per game")
    scatter_axis.grid(alpha=0.25)

    position_means = position_averages(data, metric_column)
    position_axis.bar(position_means.index, position_means.to_numpy(dtype=float), color="#c7d273")
    position_axis.set(
        title=f"Average {metric_label} by position",
        xlabel="Position",
        ylabel=metric_label.capitalize(),
    )
    position_axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
    return output_path


def generate_analysis(
    input_path: str | Path = INPUT_CSV,
    output_dir: str | Path = OUTPUT_DIR,
) -> dict[str, Path]:
    """Run the full CSV-to-cleaned-exports and visualization workflow."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_data = read_csv_robust(input_path)
    cleaned_data, cleaning_report = clean_data(raw_data)
    cleaning_report["cleaned_rows"] = cleaning_report.pop("final_rows")
    all_metrics = calculate_metrics(cleaned_data)
    featured_data, selection_report = trim_dataset(all_metrics)
    cleaning_report.update(selection_report)
    analysed_data = calculate_metrics(featured_data)
    summary = build_summary(analysed_data, cleaning_report)
    players_path = output_dir / "players.json"
    summary_path = output_dir / "analysis_summary.json"
    cleaned_path = output_dir / "analysed_players.csv"
    chart_paths = {}
    for metric in POSITION_METRICS:
        chart_path = output_dir / f"analysis_dashboard_{metric}.png"
        plot_analysis(analysed_data, chart_path, average_metric=metric)
        chart_paths[f"chart_{metric}"] = chart_path
    players_path.write_text(
        json.dumps(make_player_records(analysed_data), ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    analysed_data.to_csv(cleaned_path, index=False)
    return {
        "players": players_path,
        "summary": summary_path,
        "cleaned_csv": cleaned_path,
        **chart_paths,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a basketball player statistics CSV.")
    parser.add_argument("input_csv", nargs="?", type=Path, default=INPUT_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    arguments = parser.parse_args()
    generated_files = generate_analysis(arguments.input_csv, arguments.output_dir)
    for label, path in generated_files.items():
        print(f"{label}: {path}")
