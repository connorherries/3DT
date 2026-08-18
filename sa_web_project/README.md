# Sports Analytics Learning Hub

A web-based sports education platform built around the **Sports + Education** proposal and designed to satisfy the main programming/data-analysis requirements of **NCEA Level 3 Digital Technologies AS 91906**.

## What this version does

- Imports the raw NBA CSV through a Python/pandas data pipeline.
- Cleans blank rows, invalid numeric values and duplicates.
- Uses NumPy to calculate derived performance metrics, z-scores, percentiles and a weighted comparison score.
- Uses Matplotlib to create analytical comparison charts.
- Stores cleaned/derived player statistics in **MySQL**.
- Uses **phpMyAdmin** as the browser-based database management tool.
- Provides a Flask website with:
  - player search/filtering
  - player study pages
  - two-player comparison
  - visual analysis
  - metric explanations
  - active-recall quiz
  - quiz result persistence in MySQL
- Includes automated tests for edge cases and core analysis logic.

## Important architecture point

**phpMyAdmin is not the database.** MySQL is the database engine; phpMyAdmin is used to manage it. The Flask website connects directly to MySQL.

## Run in GitHub Codespaces

Open the repository in a Codespace. Then run:

```bash
docker compose up -d --build
```

The web container waits for MySQL, creates the schema, imports the starter CSV if the database is empty, and starts Flask.

Then open:

- **Website:** port `5000`
- **phpMyAdmin:** port `8080`

### phpMyAdmin login

Server: `db`

Username: `sports_user`

Password: `sports_password`

Database: `sports_hub`

You can also use the MySQL root account:

Username: `root`

Password: `root_password`

## Useful commands

### Start everything

```bash
docker compose up -d --build
```

### See logs

```bash
docker compose logs -f web
```

### Stop everything

```bash
docker compose down
```

### Stop and delete the database volume

**Warning: this resets the MySQL data.**

```bash
docker compose down -v
```

### Run the Python tests locally

```bash
python -m pip install -r requirements.txt
pytest -q
```

## AS 91906 evidence

The project keeps the complex processing in `app/analysis.py` so the code can be clearly explained and tested. The website layer is `app/main.py`, while `app/database.py` demonstrates persistent storage and query logic.

For your assessment evidence, document:

1. the original CSV;
2. the cleaning process and why each rule was chosen;
3. the NumPy-derived metrics;
4. the Matplotlib visualisations;
5. the MySQL schema and queries;
6. the Flask website features;
7. tests using missing data, invalid data types and empty rows;
8. debugging/refinement changes with dates or Git commits.

## Scope note

The included dataset is a **starter 2023–24 NBA dataset**. Before final assessment submission, replace or expand it with the larger teacher-approved dataset you intend to use and document the dataset source/permissions.
