<?php 

require_once "database.php"; 

$search = $_GET["search"] ?? ""; 

$sql = "
     SELECT * 
     FROM players
     WHERE player_name LIKE :search
     ORDER BY player_name 
;";

$stmt = $pdo->prepare($sql); 
$stmt->execute([
    "search" => "%" . $search . "%" 
]); 

$players = $stmt->fetchAll(PDO::FETCH_ASSOC); 

?> 

<!DOCTYPE html> 
<html lang="en">

<head>
    <meta charset="UTF-8"> 
    <meta name="viewport" content="width=device-width, initial-scale=1.0"> 
    <title>Players - Basket Metrics</title> <link rel="stylesheet" href="style.css"> 
</head> 

<body> 

<nav class="nav"> 
    <div class="nav-inner"> 
        a class="brand" href="index.php"> 
            Basket Metrics 
        </a>
        
        div class="links"> 
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
    <h1>Player Explorer</h1> 
    
    <p> 
        Search the professional basketball database. 
    </p> 
    
    <form method="GET" class="search-form"> 
    
        <input 
            type="text" 
            name="search" 
            placeholder="Search for a player..." 
            value="<?= htmlspecialchars($search) ?>" 
        > 
            
        <button type="submit"> 
            Search 
        </button> 
    </form> 
    
    <div class="card-grid"> 
    
        <?php if (empty($players)): ?> 
            <div class="card"> 
                <h2>No players found</h2> 
                <p> 
                    Try a different search. 
                </p> 
            </div> 
        <?php else: ?> 
            <?php foreach ($players as $player): ?> 
                <div class="card"> 
                    <h2> 
                        <?= htmlspecialchars($player["player_name"]) ?> 
                    </h2> 
                    
                    <p> 
                        Team: 
                        <?= htmlspecialchars($player["team"]) ?> 
                    </p> 
                    
                    <p> 
                        Position: <?= htmlspecialchars($player["position"]) ?> 
                    </p> 
                    
                    <a 
                        class="button" 
                        href="player.php?id=<?= urlencode($player["id"]) ?>" 
                    > 
                        View Player 
                    </a> 
                </div> 
            <?php endforeach; ?> 
        <?php endif; ?> 
    </div> 
</main> 

<footer class="footer"> 
    <p>© 2026 Basket Metrics · Educational project</p> 
</footer> 

</body> 
</html>