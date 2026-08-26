<?php

require_once "database.php";

/*
 * Get all players for the dropdown menus.
 */

$playerQuery = $pdo->query("
    SELECT id, player_name, team, position
    FROM players
    ORDER BY player_name
");

$players = $playerQuery->fetchAll(PDO::FETCH_ASSOC);


/*
 * Get selected players from the URL.
 */

$player1Id = $_GET["player1"] ?? "";
$player2Id = $_GET["player2"] ?? "";

$player1 = null;
$player2 = null;


/*
 * Get player 1 and their statistics.
 */

if (ctype_digit((string) $player1Id)) {

    $stmt = $pdo->prepare("
        SELECT
            p.id,
            p.player_name,
            p.team,
            p.position,

            s.season,
            s.pts_per_game,
            s.rpg,
            s.apg,
            s.fg_pct,
            s.three_pct,
            s.ft_pct,
            s.spg,
            s.bpg,
            s.tov_per_game,
            s.scoring_efficiency,
            s.assist_to_turnover,
            s.stocks_per_game,
            s.composite_impact

        FROM players p

        LEFT JOIN player_stats s
            ON p.id = s.player_id

        WHERE p.id = :id

        ORDER BY s.season DESC

        LIMIT 1
    ");

    $stmt->execute([
        ":id" => $player1Id
    ]);

    $player1 = $stmt->fetch(PDO::FETCH_ASSOC);
}


/*
 * Get player 2 and their statistics.
 */

if (ctype_digit((string) $player2Id)) {

    $stmt = $pdo->prepare("
        SELECT
            p.id,
            p.player_name,
            p.team,
            p.position,

            s.season,
            s.pts_per_game,
            s.rpg,
            s.apg,
            s.fg_pct,
            s.three_pct,
            s.ft_pct,
            s.spg,
            s.bpg,
            s.tov_per_game,
            s.scoring_efficiency,
            s.assist_to_turnover,
            s.stocks_per_game,
            s.composite_impact

        FROM players p

        LEFT JOIN player_stats s
            ON p.id = s.player_id

        WHERE p.id = :id

        ORDER BY s.season DESC

        LIMIT 1
    ");

    $stmt->execute([
        ":id" => $player2Id
    ]);

    $player2 = $stmt->fetch(PDO::FETCH_ASSOC);
}


/*
 * Helper function for safely displaying numbers.
 */

function displayStat($value, $suffix = "")
{
    if ($value === null || $value === "") {
        return "N/A";
    }

    return htmlspecialchars((string) $value) . $suffix;
}

?>

<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Compare Players - Basket Metrics</title>

    <link
        rel="stylesheet"
        href="style.css"
    >

</head>

<body>

<nav class="nav">

    <div class="nav-inner">

        <a
            class="brand"
            href="index.php"
        >
            Basket Metrics
        </a>

        <div class="links">

            <a href="players.php">Players</a>
            <a href="compare.php">Compare</a>
            <a href="login.php">Login</a>
            <a href="signup.php">Sign up</a>
            <a href="adminlogin.php">Admin Login</a>
            <a href="adminsignup.php">Admin Signup</a>
            <a href="quiz.php">Quiz</a>

        </div>

    </div>

</nav>


<main class="container">


    <section>

        <h1>Compare Players</h1>

        <p>
            Select two professional players and compare
            their performance statistics.
        </p>


        <form
            method="GET"
            action="compare.php"
            class="compare-form"
        >

            <div class="card">

                <h2>Player 1</h2>

                <select
                    name="player1"
                    required
                >

                    <option value="">
                        Select a player
                    </option>

                    <?php foreach ($players as $player): ?>

                        <option
                            value="<?= htmlspecialchars($player["id"]) ?>"
                            <?= ((string) $player1Id === (string) $player["id"]) ? "selected" : "" ?>
                        >

                            <?= htmlspecialchars($player["player_name"]) ?>

                            -
                            <?= htmlspecialchars($player["team"]) ?>

                        </option>

                    <?php endforeach; ?>

                </select>

            </div>


            <div class="card">

                <h2>Player 2</h2>

                <select
                    name="player2"
                    required
                >

                    <option value="">
                        Select a player
                    </option>

                    <?php foreach ($players as $player): ?>

                        <option
                            value="<?= htmlspecialchars($player["id"]) ?>"
                            <?= ((string) $player2Id === (string) $player["id"]) ? "selected" : "" ?>
                        >

                            <?= htmlspecialchars($player["player_name"]) ?>

                            -
                            <?= htmlspecialchars($player["team"]) ?>

                        </option>

                    <?php endforeach; ?>

                </select>

            </div>


            <button
                type="submit"
                class="button"
            >
                Compare Players
            </button>

        </form>

    </section>


    <?php if ($player1 && $player2): ?>

        <?php if ($player1["id"] === $player2["id"]): ?>

            <section class="card">

                <h2>Choose two different players</h2>

                <p>
                    A comparison requires two different players.
                </p>

            </section>

        <?php else: ?>

            <section>

                <h2>

                    <?= htmlspecialchars($player1["player_name"]) ?>

                    vs

                    <?= htmlspecialchars($player2["player_name"]) ?>

                </h2>

                <p>

                    <?= htmlspecialchars($player1["team"]) ?>

                    vs

                    <?= htmlspecialchars($player2["team"]) ?>

                </p>


                <div class="comparison-grid">


                    <div class="comparison-stat card">

                        <h3>Points Per Game</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["pts_per_game"]) ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["pts_per_game"]) ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Rebounds Per Game</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["rpg"]) ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["rpg"]) ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Assists Per Game</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["apg"]) ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["apg"]) ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Field Goal %</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["fg_pct"], "%") ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["fg_pct"], "%") ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Three Point %</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["three_pct"], "%") ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["three_pct"], "%") ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Free Throw %</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["ft_pct"], "%") ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["ft_pct"], "%") ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Steals Per Game</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["spg"]) ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["spg"]) ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Blocks Per Game</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["bpg"]) ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["bpg"]) ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Turnovers Per Game</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["tov_per_game"]) ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["tov_per_game"]) ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Scoring Efficiency</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["scoring_efficiency"]) ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["scoring_efficiency"]) ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Assist / Turnover</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["assist_to_turnover"]) ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["assist_to_turnover"]) ?>
                            </strong>

                        </div>

                    </div>


                    <div class="comparison-stat card">

                        <h3>Composite Impact</h3>

                        <div class="comparison-values">

                            <strong>
                                <?= displayStat($player1["composite_impact"]) ?>
                            </strong>

                            <span>vs</span>

                            <strong>
                                <?= displayStat($player2["composite_impact"]) ?>
                            </strong>

                        </div>

                    </div>


                </div>

            </section>


            <section class="card">

                <h2>What can we learn?</h2>

                <p>
                    A useful comparison does not mean that one player
                    is automatically better than the other.
                    Different statistics represent different parts
                    of basketball performance.
                </p>

                <p>
                    Points per game focuses on scoring, while assists
                    and rebounds describe other ways a player can
                    contribute.
                </p>

                <p>
                    Try comparing players with similar positions or
                    roles to make the results more meaningful.
                </p>

            </section>

        <?php endif; ?>

    <?php endif; ?>


</main>


<footer class="footer">

    <p>
        © 2026 Basket Metrics · Educational project
    </p>

</footer>


</body>
</html>