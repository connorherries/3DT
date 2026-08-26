from __future__ import annotations

from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from analysis import build_quiz_questions, compare_players, plot_comparison, prepare_dataset
import database

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "nba_player_stats_2023_24.csv"
GENERATED_DIR = ROOT / "app" / "static" / "generated"
app = Flask(__name__)
app.secret_key = "sports-analytics-learning-hub"

METRIC_EXPLANATIONS = {
    "pts_per_game": "Points per game: average points scored per game.",
    "rpg": "Rebounds per game: average rebounds collected per game.",
    "apg": "Assists per game: average passes leading directly to made baskets.",
    "spg": "Steals per game: average steals recorded per game.",
    "bpg": "Blocks per game: average shots blocked per game.",
    "ft_pct": "Free-throw percentage: percentage of free throws made.",
    "composite_impact": "Composite Impact Score: an educational weighting created for this project. It is not an official NBA metric.",
}


def bootstrap_database() -> None:
    """Create tables and import the starter CSV if the database is empty."""
    database.wait_for_database()
    database.initialise_schema()
    if database.count_stats() == 0:
        df, report = prepare_dataset(DATA_PATH)
        database.import_dataframe(df, season="2023-24")
        print(f"Imported {len(df)} analysed player records. Cleaning report: {report}")


@app.context_processor
def inject_globals():
    return {"metric_explanations": METRIC_EXPLANATIONS}


@app.get("/")
def home():
    leaderboard = database.fetch_dashboard(10)
    return render_template("index.html", leaderboard=leaderboard)


@app.get("/players")
def players():
    search = request.args.get("search", "")
    position = request.args.get("position", "ALL")
    rows = database.search_players(search, position)
    positions = database.get_positions()
    return render_template("players.html", players=rows, positions=positions, search=search, selected_position=position)


@app.get("/player/<path:player_name>")
def player(player_name: str):
    row = database.get_player(player_name)
    if row is None:
        flash("Player not found.", "error")
        return redirect(url_for("players"))
    return render_template("player.html", player=row)


@app.route("/compare", methods=["GET", "POST"])
def compare():
    players = database.search_players()
    selected_first = request.form.get("first", "") if request.method == "POST" else request.args.get("first", "")
    selected_second = request.form.get("second", "") if request.method == "POST" else request.args.get("second", "")
    comparison = None
    chart_url = None
    if selected_first and selected_second:
        rows = database.get_comparison(selected_first, selected_second)
        if len(rows) != 2:
            flash("Select two different valid players.", "error")
        else:
            import pandas as pd
            df = pd.DataFrame(rows).set_index("player")
            # Reuse the same NumPy/Matplotlib analysis logic used by the assessment pipeline.
            comparison = df
            chart = plot_comparison(comparison, GENERATED_DIR, filename="comparison.png")
            chart_url = url_for("static", filename="generated/" + chart.name)
    return render_template(
        "compare.html",
        players=players,
        selected_first=selected_first,
        selected_second=selected_second,
        comparison=comparison,
        chart_url=chart_url,
    )


@app.get("/learn")
def learn():
    positions = database.get_position_summary()
    return render_template("learn.html", positions=positions)


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    import pandas as pd

    rows = database.search_players()
    df = pd.DataFrame(rows)
    if request.method == "POST":
        # The quiz is generated from live database records so the learning component is data-driven.
        questions = request.form.getlist("question")
        score = 0
        for index, prompt in enumerate(questions):
            answer = request.form.get(f"answer_{index}", "")
            correct = request.form.get(f"correct_{index}", "")
            if answer == correct:
                score += 1
        total = len(questions)
        database.save_quiz_attempt(score, total)
        return render_template("quiz_result.html", score=score, total=total)

    questions = build_quiz_questions(df, number=5)
    return render_template("quiz.html", questions=questions)


@app.get("/health")
def health():
    return {"status": "ok", "database_rows": database.count_stats()}


if __name__ == "__main__":
    bootstrap_database()
    app.run(host="0.0.0.0", port=5000, debug=False)
