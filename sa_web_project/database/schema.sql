CREATE DATABASE IF NOT EXISTS sports_hub;
USE sports_hub;

CREATE TABLE IF NOT EXISTS players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(120) NOT NULL,
    age INT NOT NULL,
    team VARCHAR(20) NOT NULL,
    position VARCHAR(10) NOT NULL,
    UNIQUE KEY uq_player_team (player_name, team)
) ENGINE=InnoDB;

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

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    score INT NOT NULL,
    total_questions INT NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
