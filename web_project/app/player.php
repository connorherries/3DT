<?php

require_once "database.php";

$id = $_GET["id"] ?? null;

if (!$id || !ctype_digit($id)) {
    die("Invalid player ID.");
}

$sql = "
    SELECT
        p.id,
        p.player_name,
        p.age,
        p.team,
        p.position,
        s.season,
        s.games,
        s.minutes_per_game,
        s.fg_pct,
        s.three_pct,
        s.ft_pct,
        s.oreb_per_game,
        s.dreb_per_game,
        s.rpg,
        s.apg,
        s.spg,
        s.bpg,
        s.tov_per_game,
        s.pts_per_game,
        s.scoring_efficiency,
        s.assist_to_turnover,
        s.stocks_per_game,
        s.composite_impact,
        s.balanced_score
    FROM players p
    LEFT JOIN player_stats s
        ON p.id = s.player_id
    WHERE p.id = :id
    ORDER BY s.season DESC
    LIMIT 1
";

$stmt = $pdo->prepare($sql);

$stmt->execute([
    ":id" => $id
]);

$player = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$player) {
    die("Player not found.");
}

?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>
        <?= htmlspecialchars($player["player_name"]) ?> - Basket Metrics
    </title>

    <link rel="stylesheet" href="style.css">
</head>

<body>

    <nav class="nav">
        <div class="nav-inner">

            <a class="brand" href="index.php">
                Basket Metrics
            </a>

            <div class="links">
                <a href="players.php">Players</a>
                <a href="compare.php">Compare</a>
                <a href="learn.php">Learn</a>
                <a href="quiz.php">Quiz</a>
            </div>

        </div>
    </nav>

    <main class="container">

        <h1>
            <?= htmlspecialchars($player["player_name"]) ?>
        </h1>

        <p>
            <?= htmlspecialchars($player["team"]) ?>
            ·
            <?= htmlspecialchars($player["position"]) ?>
        </p>

        <div class="stat-grid">

            <div class="stat">
                <p>Points</p>

                <div class="stat-value">
                    <?= htmlspecialchars($player["pts_per_game"]) ?>
                </div>
            </div>

            <div class="stat">
                <p>Rebounds</p>

                <div class="stat-value">
                    <?= htmlspecialchars($player["rpg"]) ?>
                </div>
            </div>

            <div class="stat">
                <p>Assists</p>

                <div class="stat-value">
                    <?= htmlspecialchars($player["apg"]) ?>
                </div>
            </div>

            <div class="stat">
                <p>3P%</p>

                <div class="stat-value">
                    <?= htmlspecialchars($player["three_pct"]) ?>%
                </div>
            </div>

        </div>

        <section class="card">

            <h2>What do these statistics mean?</h2>

            <p>
                Points per game measures how many points a player scores
                on average during each game.
            </p>

            <p>
                Rebounds measure how many rebounds a player collects per game.
            </p>

            <p>
                Assists measure passes that directly lead to a made basket.
            </p>

            <p>
                Three-point percentage measures the percentage of attempted
                three-point shots that are made.
            </p>

        </section>

        <a class="button" href="compare.php">
            Compare This Player
        </a>

    </main>

    <footer class="footer">
        <p>© 2026 Basket Metrics · Educational project</p>
    </footer>

</body>

</html>