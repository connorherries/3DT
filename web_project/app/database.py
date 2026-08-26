"""MySQL persistence layer used by the Flask website."""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "sports_user"),
    "password": os.getenv("DB_PASSWORD", "sports_password"),
    "database": os.getenv("DB_NAME", "sports_hub"),
}


@contextmanager
def get_connection() -> Iterator[mysql.connector.MySQLConnection]:
    """Open and close a MySQL connection in one safe context."""
    connection = mysql.connector.connect(**DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()


def wait_for_database(retries: int = 30, delay: float = 2.0) -> None:
    """Wait for MySQL to accept connections so Codespaces/Docker starts reliably."""
    import time

    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with get_connection() as conn:
                if conn.is_connected():
                    return
        except Exception as exc:  # startup race; retry intentionally
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Could not connect to MySQL after {retries} attempts: {last_error}")


def initialise_schema() -> None:
    """Create application tables if they do not already exist."""
    statements = [
        """
        CREATE TABLE IF NOT EXISTS players (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player_name VARCHAR(120) NOT NULL,
            age INT NOT NULL,
            team VARCHAR(20) NOT NULL,
            position VARCHAR(10) NOT NULL,
            UNIQUE KEY uq_player_team (player_name, team)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS player_stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player_id INT NOT NULL,
            season VARCHAR(20) NOT NULL,
            games INT NOT NULL,
            minutes_per_game DECIMAL(6,2) NOT NULL,
            fg_pct DECIMAL(6,3) NOT NULL,
            three_pct DECIMAL(6,3) NOT NULL,
            ft_pct DECIMAL(6,3) NOT NULL,
            oreb_per_game DECIMAL(6,2) NOT NULL,
            dreb_per_game DECIMAL(6,2) NOT NULL,
            rpg DECIMAL(6,2) NOT NULL,
            apg DECIMAL(6,2) NOT NULL,
            spg DECIMAL(6,2) NOT NULL,
            bpg DECIMAL(6,2) NOT NULL,
            tov_per_game DECIMAL(6,2) NOT NULL,
            pts_per_game DECIMAL(6,2) NOT NULL,
            scoring_efficiency DECIMAL(8,4) NOT NULL,
            assist_to_turnover DECIMAL(8,4) NOT NULL,
            stocks_per_game DECIMAL(8,3) NOT NULL,
            composite_impact DECIMAL(10,4) NOT NULL,
            balanced_score DECIMAL(10,4) NOT NULL,
            UNIQUE KEY uq_player_season (player_id, season),
            CONSTRAINT fk_stats_player FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            score INT NOT NULL,
            total_questions INT NOT NULL,
            percentage DECIMAL(5,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """,
    ]
    with get_connection() as conn:
        cursor = conn.cursor()
        for statement in statements:
            cursor.execute(statement)
        conn.commit()
        cursor.close()


def count_stats() -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM player_stats")
        value = int(cursor.fetchone()[0])
        cursor.close()
        return value


def import_dataframe(df, season: str = "2023-24") -> int:
    """Insert cleaned/analysed pandas records into normalised MySQL tables."""
    inserted = 0
    with get_connection() as conn:
        cursor = conn.cursor()
        for row in df.to_dict("records"):
            cursor.execute(
                """
                INSERT INTO players (player_name, age, team, position)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE age=VALUES(age), position=VALUES(position)
                """,
                (str(row["player"]), int(row["age"]), str(row["team"]), str(row["position"])),
            )
            cursor.execute(
                "SELECT id FROM players WHERE player_name=%s AND team=%s",
                (str(row["player"]), str(row["team"])),
            )
            player_id = int(cursor.fetchone()[0])
            cursor.execute(
                """
                INSERT INTO player_stats (
                    player_id, season, games, minutes_per_game, fg_pct, three_pct, ft_pct,
                    oreb_per_game, dreb_per_game, rpg, apg, spg, bpg, tov_per_game,
                    pts_per_game, scoring_efficiency, assist_to_turnover, stocks_per_game,
                    composite_impact, balanced_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                          %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    games=VALUES(games), minutes_per_game=VALUES(minutes_per_game),
                    fg_pct=VALUES(fg_pct), three_pct=VALUES(three_pct), ft_pct=VALUES(ft_pct),
                    oreb_per_game=VALUES(oreb_per_game), dreb_per_game=VALUES(dreb_per_game),
                    rpg=VALUES(rpg), apg=VALUES(apg), spg=VALUES(spg), bpg=VALUES(bpg),
                    tov_per_game=VALUES(tov_per_game), pts_per_game=VALUES(pts_per_game),
                    scoring_efficiency=VALUES(scoring_efficiency),
                    assist_to_turnover=VALUES(assist_to_turnover),
                    stocks_per_game=VALUES(stocks_per_game),
                    composite_impact=VALUES(composite_impact),
                    balanced_score=VALUES(balanced_score)
                """,
                (
                    player_id, season, int(row["games"]), float(row["minutes_per_game"]),
                    float(row["fg_pct"]), float(row["three_pct"]), float(row["ft_pct"]),
                    float(row["oreb_per_game"]), float(row["dreb_per_game"]), float(row["rpg"]),
                    float(row["apg"]), float(row["spg"]), float(row["bpg"]), float(row["tov_per_game"]),
                    float(row["pts_per_game"]), float(row["scoring_efficiency"]),
                    float(row["assist_to_turnover"]), float(row["stocks_per_game"]),
                    float(row["composite_impact"]), float(row["balanced_score"]),
                ),
            )
            inserted += 1
        conn.commit()
        cursor.close()
    return inserted


def fetch_dashboard(limit: int = 10) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.player_name AS player, p.team, p.position,
                   s.pts_per_game, s.rpg, s.apg, s.composite_impact, s.balanced_score
            FROM players p
            JOIN player_stats s ON s.player_id = p.id
            ORDER BY s.composite_impact DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows


def search_players(search: str = "", position: str = "ALL") -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        params: list = []
        where = []
        if search:
            where.append("LOWER(p.player_name) LIKE %s")
            params.append(f"%{search.lower()}%")
        if position and position.upper() != "ALL":
            where.append("p.position = %s")
            params.append(position.upper())
        clause = " WHERE " + " AND ".join(where) if where else ""
        cursor.execute(
            f"""
            SELECT p.player_name AS player, p.team, p.position, p.age,
                   s.games, s.minutes_per_game, s.pts_per_game, s.rpg, s.apg,
                   s.spg, s.bpg, s.ft_pct, s.composite_impact, s.balanced_score
            FROM players p
            JOIN player_stats s ON s.player_id = p.id
            {clause}
            ORDER BY s.composite_impact DESC
            LIMIT 100
            """,
            params,
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows


def get_player(player_name: str) -> dict | None:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.player_name AS player, p.team, p.position, p.age,
                   s.season, s.games, s.minutes_per_game, s.fg_pct, s.three_pct,
                   s.ft_pct, s.rpg, s.apg, s.spg, s.bpg, s.tov_per_game,
                   s.pts_per_game, s.scoring_efficiency, s.assist_to_turnover,
                   s.stocks_per_game, s.composite_impact, s.balanced_score
            FROM players p
            JOIN player_stats s ON s.player_id = p.id
            WHERE p.player_name = %s
            LIMIT 1
            """,
            (player_name,),
        )
        row = cursor.fetchone()
        cursor.close()
        return row


def get_positions() -> list[str]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT position FROM players ORDER BY position")
        values = [str(item[0]) for item in cursor.fetchall()]
        cursor.close()
        return values


def get_comparison(first: str, second: str) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.player_name AS player, p.position, s.pts_per_game, s.rpg, s.apg,
                   s.spg, s.bpg, s.ft_pct, s.composite_impact, s.balanced_score
            FROM players p
            JOIN player_stats s ON s.player_id = p.id
            WHERE p.player_name IN (%s, %s)
            ORDER BY FIELD(p.player_name, %s, %s)
            """,
            (first, second, first, second),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows


def get_position_summary() -> list[dict]:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.position,
                   COUNT(*) AS players,
                   ROUND(AVG(s.pts_per_game), 2) AS avg_points,
                   ROUND(AVG(s.rpg), 2) AS avg_rebounds,
                   ROUND(AVG(s.apg), 2) AS avg_assists,
                   ROUND(AVG(s.composite_impact), 2) AS avg_impact
            FROM players p
            JOIN player_stats s ON s.player_id = p.id
            GROUP BY p.position
            ORDER BY avg_impact DESC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows


def save_quiz_attempt(score: int, total: int) -> None:
    percentage = round(score / total * 100, 2) if total else 0
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO quiz_attempts (score, total_questions, percentage) VALUES (%s, %s, %s)",
            (score, total, percentage),
        )
        conn.commit()
        cursor.close()
