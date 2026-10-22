// Shared page bits. Nav up top, footer below, page content in between.
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
// Mark the current page's link active.
const navigationLinks = pageLinks.map(([label, file]) => {
	const active = currentPage === file ? "active" : "";
	return `<li class="nav-item"><a class="nav-link ${active}" href="${file}">${label}</a></li>`;
}).join("");



// Header markup, reused on every page.
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



// Footer too, shared across the site.
document.querySelector("#site-footer").innerHTML = `
	<div class="container py-4">
		<div class="row g-4">
			<div class="col-md-6">
				<h2 class="h5">Basket Metrics</h2>
				<p class="mb-0">A simple way to explore player stats, compare performance and learn the numbers behind basketball.</p>
			</div>
			<div class="col-md-3">
				<h2 class="footer-header">Explore</h2>
				<a href="players.html">Players</a><br>
				<a href="compare.html">Compare</a><br>
				<a href="learn.html">Learn</a><br>
				<a href="quiz.html">Quiz</a>
			</div>
			<div class="col-md-3">
				<h2 class="footer-header">Data</h2>
				<p class="mb-0">Basketball stats are cleaned and displayed for learning.</p>
			</div>
		</div>
		<hr>
		<p class="mb-0 small">Educational project · Demo mode</p>
	</div>`;