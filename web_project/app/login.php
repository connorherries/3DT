<?php
?>
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Login - Basket Metrics</title>

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
            <a href="login.php">Login</a>
            <a href="signup.php">Sign up</a>
            <a href="adminlogin.php">Admin Login</a>
            <a href="adminsignup.php">Admin Signup</a>
            <a href="quiz.php">Quiz</a>

        </div>

    </div>

</nav>


<main class="auth-container">

    <div class="auth-card">

        <div class="auth-header">

            <h1>Welcome Back</h1>

            <p>
                Login to continue using Basket Metrics.
            </p>

        </div>


        <form action="#" method="POST">

            <div class="form-group">

                <label for="email">
                    Email Address
                </label>

                <input
                    type="email"
                    id="email"
                    name="email"
                    placeholder="Enter your email"
                    required
                >

            </div>


            <div class="form-group">

                <label for="password">
                    Password
                </label>

                <input
                    type="password"
                    id="password"
                    name="password"
                    placeholder="Enter your password"
                    required
                >

            </div>


            <button
                type="submit"
                class="auth-button"
            >
                Login
            </button>

        </form>


        <div class="auth-footer">

            <p>
                Don't have an account?
                <a href="signup.php">
                    Sign up
                </a>
            </p>

        </div>

    </div>

</main>


<footer class="footer">

    <p>
        © 2026 Basket Metrics · Educational project
    </p>

</footer>

</body>
</html>