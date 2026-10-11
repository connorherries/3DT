// Add the same navigation and footer to each page.
const pageLinks = [
	["Home", "index.html"],
	["Players", "players.html"],
	["Compare", "compare.html"],
	["Learn", "learn.html"],
	["Quiz", "quiz.html"],
	["Login", "login.html"],
	["Sign up", "signup.html"],
	["Admin", "admin-login.html"],
];

const currentPage = location.pathname.split("/").pop() || "index.html";
const navigationLinks = pageLinks.map(([label, file]) => {
	const active = currentPage === file ? "active" : "";
	return `<li class="nav-item"><a class="nav-link ${active}" href="${file}">${label}</a></li>`;
}).join("");



//header code for all pages
document.querySelector("#site-header").innerHTML = `
	<nav class="navbar navbar-expand-lg navbar-dark site-navbar fixed-top">
		<div class="container">
			<a class="navbar-brand d-flex align-items-center gap-2" href="index.html">
				<img src="images/bmlogomk2.png" width="38" height="38" alt="Basket Metrics">
				<span>Basket Metrics <small class="d-block eyebrow">Demo mode</small></span>
			</a>
			<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#site-navigation" aria-controls="site-navigation" aria-expanded="false" aria-label="Toggle navigation">
				<span class="navbar-toggler-icon"></span>
			</button>
			<div class="collapse navbar-collapse" id="site-navigation">
				<ul class="navbar-nav ms-auto">${navigationLinks}</ul>
			</div>
		</div>
	</nav>`;



//Footer code fro all pages
document.querySelector("#site-footer").innerHTML = `
	<div class="container py-4">
		<div class="row g-4">
			<div class="col-md-5">
				<h2 class="h5">Basket Metrics</h2>
				<p class="mb-0">NBA statistics for exploring player performance and learning the numbers behind the game.</p>
			</div>
			<div class="col-md-3">
				<h2 class="footer-header">Explore</h2>
				<a href="players.html">Players</a><br>
				<a href="compare.html">Compare</a><br>
				<a href="learn.html">Learn the metrics</a><br>
				<a href="quiz.html">Quiz</a>
			</div>
			<div class="col-md-4">
				<h2 class="footer-header">Demo data</h2>
				<p>Player statistics from Basketball Reference 2025-26</p>
				<p class="mb-0">Demo forms do not save account details.</p>
			</div>
		</div>
		<hr>
		<p class="mb-0 small">Educational project · Demonstration mode</p>
	</div>`;