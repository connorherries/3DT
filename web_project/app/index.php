<?php
require_once "database.php";
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Basket Metrics</title>
    <link rel="stylesheet" href="style.css">
    <link
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
    rel="stylesheet"
    >
</head>

<body>

<nav class="navbar navbar-expand-lg navbar-dark bg-dark">

    <div class="container">

        <a
            class="navbar-brand fw-bold"
            href="index.php"
        >
            Basket Metrics
        </a>


        <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
        >

            <span class="navbar-toggler-icon"></span>

        </button>


        <div
            class="collapse navbar-collapse"
            id="navbarNav"
        >

            <ul class="navbar-nav ms-auto">

                <li class="nav-item">

                    <a
                        class="nav-link"
                        href="players.php"
                    >
                        Players
                    </a>

                </li>


                <li class="nav-item">

                    <a
                        class="nav-link"
                        href="compare.php"
                    >
                        Compare
                    </a>

                </li>


                <li class="nav-item">

                    <a
                        class="nav-link"
                        href="learn.php"
                    >
                        Learn
                    </a>

                </li>


                <li class="nav-item">

                    <a
                        class="nav-link"
                        href="quiz.php"
                    >
                        Quiz
                    </a>

                </li>


                <li class="nav-item">

                    <a
                        class="nav-link"
                        href="login.php"
                    >
                        Login
                    </a>

                    <a
                        class="nav-link"
                        href="signup.php"
                    >
                        Signup
                    </a>

                    <a
                        class="nav-link"
                        href="adminlogin.php"
                    >
                        Admin Login
                    </a>
                    <a
                        class="nav-link"
                        href="adminsignup.php"
                    >
                        Admin Signup
                    </a>

                </li>

            </ul>

        </div>

    </div>

</nav>

<main class="container">

    <h1>Learn basketball through the data.</h1>

    <p>
        Explore professional players, compare statistics,
        and learn what the numbers mean.
    </p>

    <a href="players.php" class="button">
        Explore Players
    </a>

</main>

<footer class="footer">
    <p>© 2026 Basket Metrics · Educational project</p>
</footer>

<script
    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"
></script>

</body>
</html>