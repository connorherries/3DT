# Basket Metrics Demo Data Pipeline

The demo reads `data/csv` and uses this Python pipeline to produce player data and visual analysis consumed by its static pages. No database is used.

## Run it

From the workspace root, install the analysis and test dependencies, generate the outputs, then serve the demo over HTTP so the pages can fetch their JSON files:

```powershell
python -m pip install -r demo/requirements.txt
python demo/analyze_data.py
python -m http.server 8000 --directory demo
python -m pytest demo/tests -q
```

Open `http://localhost:8000`. To process another CSV with the same columns, pass its path to `python demo/analyze_data.py path/to/file.csv`. An alternate output directory can be selected with `--output-dir`.

The pipeline writes `generated/players.json`, `generated/analysis_summary.json`, `generated/analysed_players.csv`, and three Matplotlib dashboard images for points, rebounds, and assists.

## Analysis and cleaning choices

- The input reader tries UTF-8 with and without a byte-order mark, then Windows-1252. It preserves blank lines so cleaning can count them.
- Required columns are checked before processing. Blank player rows are removed; rows with missing or non-numeric core statistics, team, or position are removed. Missing three-point percentages are filled with the column median and recorded in the cleaning report.
- The CSV contains a `2TM` season-total row and team-level splits for many traded players. When a season-total row exists, its team splits are excluded so a player is counted once. Any remaining duplicate player IDs are reduced to the first row.
- After cleaning the data, the dataset is trimmed to a teaching-sized roster by removing the lowest-scoring players. The final featured roster is recorded in the analysis summary.
- The composite impact metric is `PTS + 1.2 × TRB + 1.5 × AST + 3 × (STL + BLK) − TOV`. It is a teaching metric, not an official NBA statistic. The script also calculates NumPy z-scores, points percentiles, and a weighted standardized score.
- Each chart has two panels: a points-versus-assists scatter plot with a NumPy least-squares trendline, and the selected position average for points, rebounds, or assists. The Learn page buttons switch among these pre-generated Matplotlib charts. Position bars always follow PG, SG, SF, PF, C order.
- `analysis_summary.json` records cleaning counts, summary statistics, and positional averages. The demo loads the generated player JSON and uses the generated summary and chart on its learning page.

## 91906 assessment fit

NZQA standard 91906 is about using complex programming techniques to develop a computer program. In this project, `analyze_data.py` is the main program; the website displays its output. Techniques to understand and explain include splitting the pipeline into functions, validating and cleaning records, handling duplicate and traded-player rows, using pandas and NumPy for calculations and ranking, and reading and writing files. The tests show how selected cases are checked.

Use the teacher's assessment brief as the source of requirements. Keep your own dated design decisions, test results, feedback, and changes as you work, and be ready to explain the code yourself. Do not invent or backdate process evidence; this README describes the project but does not prove authorship or determine an assessment result.

## Dataset provenance

The supplied file is named `data/csv` and has NBA player-stat columns, but it does not identify its season or source in the file itself. Confirm and record the original source, access date, and teacher approval here before final assessment submission. Do not describe the data as a particular NBA season until its provenance is verified.

## Testing evidence

The tests exercise the updated CSV, blank rows, invalid numeric data, missing percentages, multi-team season totals, missing required columns, empty cleaned input, and generated output files. See [TESTING.md](TESTING.md) for the dated test record; retain screenshots or version history as additional evidence of iterative development.
