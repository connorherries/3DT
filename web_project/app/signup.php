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

    <title>Sign Up - Basket Metrics</title>

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

            <h1>Create Your Account</h1>

            <p>
                Join Basket Metrics and start learning through statistics.
            </p>

        </div>


        <form action="#" method="POST">

            <div class="form-group">

                <label for="name">
                    Full Name
                </label>

                <input
                    type="text"
                    id="name"
                    name="name"
                    placeholder="Enter your full name"
                    required
                >

            </div>


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
                    placeholder="Create a password"
                    required
                >

            </div>


            <div class="form-group">

                <label for="confirm-password">
                    Confirm Password
                </label>

                <input
                    type="password"
                    id="confirm-password"
                    name="confirm-password"
                    placeholder="Confirm your password"
                    required
                >

            </div>


            <button
                type="submit"
                class="auth-button"
            >
                Create Account
            </button>

        </form>


        <div class="auth-footer">

            <p>
                Already have an account?
                <a href="login.php">
                    Login
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