// Main page behavior. Generated player data + summary feed the views below.
let players = [];
let analysisSummary = null;

// Escape player text before it goes into HTML.
function escapeHtml(value) {
	return String(value).replace(/[&<>"']/g, (character) => ({
		"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
	})[character]);
}

// Find the roster entry from an id in the page URL.
function findPlayer(id) {
	return players.find((player) => player.id === Number(id));
}

// A compact card for the player list.
function makePlayerCard(player) {
	return `
		<div class="col-sm-6 col-lg-4">
			<article class="card h-100">
				<div class="card-body d-flex flex-column">
					<div class="d-flex justify-content-between">
						<span class="badge text-bg-warning">${escapeHtml(player.position)}</span>
						<span class="text-secondary">${escapeHtml(player.team)}</span>
					</div>
					<h2 class="h5 mt-4">${escapeHtml(player.name)}</h2>
					<p class="text-secondary">${player.age} years · ${player.games} games · ${player.minutes} MPG</p>
					<div class="d-flex justify-content-between border-top border-bottom py-3 mb-3">
						<span>${player.points} PTS</span>
						<span>${player.rebounds} REB</span>
						<span>${player.assists} AST</span>
					</div>
					<a class="btn btn-outline-success mt-auto" href="player.html?id=${player.id}">View profile</a>
				</div>
			</article>
		</div>`;
}


// Impact leaders first, right on the home page.
function showHomePage() {
	const leaders = [...players].sort((a, b) => b.impact - a.impact).slice(0, 3);
	const topPlayer = leaders[0];
	document.querySelector("#top-impact").textContent = topPlayer.impact;
	document.querySelector("#top-player-name").textContent = topPlayer.name;
	document.querySelector("#leader-list").innerHTML = leaders.map((player, index) => `
		<a class="list-group-item list-group-item-action d-flex justify-content-between" href="player.html?id=${player.id}">
			<span><strong>0${index + 1}</strong> ${escapeHtml(player.name)} <small class="text-secondary">${escapeHtml(player.team)} · ${escapeHtml(player.position)}</small></span>
			<strong>${player.impact}</strong>
		</a>`).join("");
}

// Search, position filter, roster sorting; all wired up here.
function showPlayersPage() {
	const search = document.querySelector("#player-search");
	const filter = document.querySelector("#position-filter");
	const sortSelect = document.querySelector("#player-sort");
	const list = document.querySelector("#player-list");
	const count = document.querySelector("#player-count");

	// Control changed? Run the list update again.
	function updateList() {
		const searchText = search.value.toLowerCase();
		const position = filter.value;
		const sortKey = sortSelect.value;
		const matches = players.filter((player) => {
			const nameMatches = player.name.toLowerCase().includes(searchText);
			const positionMatches = position === "ALL" || player.position === position;
			return nameMatches && positionMatches;
		});

		const sortedMatches = [...matches].sort((first, second) => {
			if (sortKey === "featured") return first.id - second.id;
			const firstValue = Number(first[sortKey] ?? 0);
			const secondValue = Number(second[sortKey] ?? 0);
			return secondValue - firstValue;
		});

		count.textContent = `${sortedMatches.length} of ${players.length} players`;
		list.innerHTML = sortedMatches.length
			? sortedMatches.map(makePlayerCard).join("")
			: `<p class="col">No players found. Try another search.</p>`;
	}

	search.addEventListener("input", updateList);
	filter.addEventListener("change", updateList);
	sortSelect.addEventListener("change", updateList);
	updateList();
}

// URL gives us the player id; fill in their profile.
function showPlayerPage() {
	const id = new URLSearchParams(location.search).get("id");
	const player = findPlayer(id) || players[0];
	const photo = player.photo
		? `<img src="${escapeHtml(player.photo)}" alt="Photo of ${escapeHtml(player.name)}" class="img-fluid rounded player-photo" width="150" height="150">`
		: "";
	const stats = [
		["Points", player.points, "PTS"],
		["Rebounds", player.rebounds, "REB"],
		["Assists", player.assists, "AST"],
		["Three-point", `${player.three}%`, "3P%"],
		["Steals", player.steals, "SPG"],
		["Blocks", player.blocks, "BPG"],
	];

	document.querySelector("#player-detail").innerHTML = `
		<p class="eyebrow">${escapeHtml(player.team)} · ${escapeHtml(player.position)}</p>

		<div class="d-flex flex-wrap justify-content-between align-items-end mb-4">
			${photo}
			<div><h1>${escapeHtml(player.name)}</h1><p class="text-secondary">Age ${player.age} · ${player.games} games played</p></div>
			<p class="impact-number">Impact score: ${player.impact}</p>
		</div>
		<div class="row row-cols-2 row-cols-md-3 row-cols-lg-6 g-3 mb-5">
			${stats.map(([label, value, unit]) => `
				<div class="col"><div class="stat-tile h-100 p-3"><small>${unit}</small><strong>${value}</strong><span>${label}</span></div></div>
			`).join("")}
		</div>
		<section class="mb-4">
			<h2>What the numbers mean</h2>
			<p>${player.points} points per game shows scoring. ${player.assists} assists per game shows how often the player helps a teammate score.</p>
			<p>The impact score is a custom learning metric made from several statistics.</p>
		</section>
		<a class="btn btn-success" href="compare.html?first=${player.id}">Compare this player</a>`;
}

// Set up selectors and stat bars for both players.
function showComparePage() {
	const firstSelect = document.querySelector("#compare-first");
	const secondSelect = document.querySelector("#compare-second");
	const results = document.querySelector("#comparison-results");
	const options = players.map((player) => `<option value="${player.id}">${escapeHtml(player.name)} · ${escapeHtml(player.team)}</option>`).join("");
	const params = new URLSearchParams(location.search);

	firstSelect.innerHTML = options;
	secondSelect.innerHTML = options;
	firstSelect.value = findPlayer(params.get("first"))?.id || players[0].id;
	secondSelect.value = findPlayer(params.get("second"))?.id || players[1].id;

	// Selection changed, refresh names and bars.
	function updateComparison() {
		const first = findPlayer(firstSelect.value);
		const second = findPlayer(secondSelect.value);
		const stats = [["Points", "points"], ["Rebounds", "rebounds"], ["Assists", "assists"], ["Steals", "steals"], ["Blocks", "blocks"], ["Three-point %", "three"]];

		results.innerHTML = `
			<div class="row g-4 mb-4">
				<div class="col-md-6"><h2>${escapeHtml(first.name)}</h2><p class="text-secondary">${escapeHtml(first.team)} · ${escapeHtml(first.position)}</p></div>
				<div class="col-md-6 text-md-end"><h2>${escapeHtml(second.name)}</h2><p class="text-secondary">${escapeHtml(second.team)} · ${escapeHtml(second.position)}</p></div>
			</div>
			${stats.map(([label, key]) => {
				const max = Math.max(first[key], second[key]) || 1;
				const firstWidth = Math.round(first[key] / max * 100);
				const secondWidth = Math.round(second[key] / max * 100);
				return `<div class="row align-items-center mb-3">
					<div class="col-2">${first[key]}</div>
					<div class="col-8"><p class="small text-center mb-1">${label}</p>
						<div class="progress mb-1"><div class="progress-bar compare-first-bar" style="width: ${firstWidth}%"></div></div>
						<div class="progress"><div class="progress-bar compare-second-bar" style="width: ${secondWidth}%"></div></div>
					</div>
					<div class="col-2 text-end">${second[key]}</div>
				</div>`;
			}).join("")}`;
	}

	firstSelect.addEventListener("change", updateComparison);
	secondSelect.addEventListener("change", updateComparison);
	updateComparison();
}

// Position summary goes here; metric buttons swap the charts.
function showLearnPage() {
	const rows = analysisSummary.position_summary;
	document.querySelector("#position-summary").innerHTML = rows.map((row) => `
		<tr><th>${escapeHtml(row.position)}</th><td>${row.player_count}</td><td>${row.average_points.toFixed(1)}</td><td>${row.average_impact.toFixed(1)}</td></tr>
	`).join("");
	const chartOptions = {
		points: { src: "generated/analysis_dashboard_points.png", label: "points per game" },
		rebounds: { src: "generated/analysis_dashboard_rebounds.png", label: "rebounds per game" },
		assists: { src: "generated/analysis_dashboard_assists.png", label: "assists per game" },
	};
	const chart = document.querySelector("#analysis-dashboard");
	const metricButtons = document.querySelectorAll("#position-average-controls [data-metric]");
	metricButtons.forEach((button) => button.addEventListener("click", () => {
		const selected = chartOptions[button.dataset.metric] || chartOptions.points;
		chart.src = selected.src;
		chart.alt = `Scatter plot with a points-versus-assists trendline and average ${selected.label} by position`;
		metricButtons.forEach((option) => {
			const active = option === button;
			option.classList.toggle("btn-success", active);
			option.classList.toggle("btn-outline-success", !active);
			option.setAttribute("aria-pressed", String(active));
		});
	}));
}


// Short quiz from player stats, new set when restarted.
function showQuizPage() {
	const questionTypes = [
		{ stat: "points", text: "Who scored more points per game?" },
		{ stat: "rebounds", text: "Who recorded more rebounds per game?" },
		{ stat: "assists", text: "Who recorded more assists per game?" },
		{ stat: "steals", text: "Who recorded more steals per game?" },
		{ stat: "blocks", text: "Who recorded more blocks per game?" },
		{ stat: "three", text: "Who has the higher three-point percentage?" },
		{ stat: "impact", text: "Who has the higher impact score?" },
		{ stat: "games", text: "Who played more games?" },
		{ stat: "minutes", text: "Who averaged more minutes per game?" },
		{ stat: "age", text: "Who is older?" },
	];
	const quiz = document.querySelector("#quiz-content");
	const questionCount = 8;
	let questionIndex = 0;
	let score = 0;
	let questions = [];

	// Skip ties, and pairs we've already used.
	function makeQuestions() {
		const selected = [];
		const used = new Set();
		let attempts = 0;
		while (selected.length < questionCount && attempts < 1000) {
			attempts += 1;
			const first = players[Math.floor(Math.random() * players.length)];
			const second = players[Math.floor(Math.random() * players.length)];
			const questionType = questionTypes[Math.floor(Math.random() * questionTypes.length)];
			if (first === second || first[questionType.stat] === second[questionType.stat]) continue;
			const key = [first.id, second.id].sort((a, b) => a - b).join(":") + questionType.stat;
			if (used.has(key)) continue;
			used.add(key);
			selected.push({ ...questionType, first, second });
		}
		return selected;
	}

	// Show the next question, or the score when we're done.
	function showQuestion() {
		if (questionIndex === questions.length) {
			quiz.innerHTML = `<div class="quiz-box text-center"><h1>Quiz complete</h1><p class="score-result">${score} / ${questions.length}</p><button id="restart-quiz" class="btn btn-success">Try again</button></div>`;
			return;
		}

		const question = questions[questionIndex];
		quiz.innerHTML = `
			<p class="text-secondary">Question ${questionIndex + 1} of ${questions.length}</p>
			<div class="progress mb-4"><div class="progress-bar bg-success" style="width: ${questionIndex / questions.length * 100}%"></div></div>
			<div class="quiz-box">
				<h1>${question.text}</h1>
				<div class="d-grid gap-2 mt-4">
					<button class="btn btn-outline-success answer-button" data-name="${escapeHtml(question.first.name)}">${escapeHtml(question.first.name)}</button>
					<button class="btn btn-outline-success answer-button" data-name="${escapeHtml(question.second.name)}">${escapeHtml(question.second.name)}</button>
				</div>
				<p id="quiz-feedback" class="mt-3" aria-live="polite"></p>
				<button id="next-question" class="btn btn-success" hidden>Next question</button>
			</div>`;
	}

	quiz.addEventListener("click", (event) => {
		const answerButton = event.target.closest(".answer-button");
		if (answerButton) {
			const question = questions[questionIndex];
			const winner = question.first[question.stat] > question.second[question.stat] ? question.first.name : question.second.name;
			const correct = answerButton.dataset.name === winner;
			if (correct) score += 1;
			quiz.querySelector("#quiz-feedback").textContent = correct ? "Correct!" : `The answer was ${winner}.`;
			quiz.querySelectorAll(".answer-button").forEach((button) => button.disabled = true);
			quiz.querySelector("#next-question").hidden = false;
		}

		if (event.target.id === "next-question") {
			questionIndex += 1;
			showQuestion();
		}

		if (event.target.id === "restart-quiz") {
			questionIndex = 0;
			score = 0;
			questions = makeQuestions();
			showQuestion();
		}
	});

	questions = makeQuestions();
	showQuestion();
}

// Account forms are just demos; submitted details don't get stored.
function showFormMessage() {
	const form = document.querySelector("#demo-form");
	const nameInput = form.querySelector("#name");
	const updateNameValidity = () => {
		if (nameInput) {
			const name = nameInput.value.trim();
			const error = name.length < 2
				? "Enter a name with at least 2 characters."
				: /[0-9]/.test(name) ? "Names cannot contain numbers." : "";
			nameInput.setCustomValidity(error);
		}
	};
	nameInput?.addEventListener("input", updateNameValidity);
	form.addEventListener("submit", (event) => {
		event.preventDefault();
		updateNameValidity();
		if (!form.reportValidity()) return;
		document.querySelector("#form-message").textContent = "Demo submitted. No information was saved.";
	});
}


const page = document.body.dataset.page;
// Hand off to the view this page asked for.
function renderPage() {
	if (page === "home") showHomePage();
	if (page === "players") showPlayersPage();
	if (page === "player") showPlayerPage();
	if (page === "compare") showComparePage();
	if (page === "learn") showLearnPage();
	if (page === "quiz") showQuizPage();
}

if (page === "login" || page === "signup" || page.startsWith("admin-")) {
	showFormMessage();
} else {
	Promise.all([
		fetch("generated/players.json").then((response) => {
			if (!response.ok) throw new Error("Player data is missing. Run python analyze_data.py first.");
			return response.json();
		}),
		fetch("generated/analysis_summary.json").then((response) => {
			if (!response.ok) throw new Error("Analysis summary is missing. Run python analyze_data.py first.");
			return response.json();
		}),
	]).then(([playerData, summary]) => {
		if (!Array.isArray(playerData) || playerData.length === 0) throw new Error("The generated player data is empty.");
		players = playerData;
		analysisSummary = summary;
		renderPage();
	}).catch((error) => {
		console.error(error);
		document.querySelector("main")?.insertAdjacentHTML("afterbegin", `<div class="alert alert-danger" role="alert">${escapeHtml(error.message)} Serve this folder over HTTP, then reload the page.</div>`);
	});
}