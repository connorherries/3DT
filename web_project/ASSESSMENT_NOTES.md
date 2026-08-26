# Assessment and proposal alignment

## Proposal alignment

The proposal combines:

- Sports: performance tracking and professional statistics.
- Education: more engaging learning through visual and interactive features.
- Target audience: student athletes / secondary school students and recreational athletes.
- Outcome: a data-driven sports education platform where users browse professional athletes, understand statistics, compare players and complete learning activities.

## AS 91906 alignment

### Raw CSV input

`data/nba_player_stats_2023_24.csv` is read by `app/analysis.py`.

### Complex data processing

The program:

- converts numeric fields safely;
- removes blank/invalid rows;
- fills non-critical missing values using medians;
- removes duplicates;
- calculates several derived features;
- creates a multidimensional NumPy score matrix;
- performs percentile and z-score calculations;
- groups data by position;
- queries/persists data in MySQL.

### NumPy before Matplotlib

The comparison chart is produced from NumPy-normalised values. The scoring/playmaking chart uses `np.polyfit` to calculate a least-squares trendline before Matplotlib renders the result.

### Modular functions

The analysis is broken into reusable functions so the same processing powers the command/test workflow and the website.

### Persistent storage

The cleaned/analyzed dataset is stored in MySQL. `phpMyAdmin` is the management interface.

### Testing

`tests/` includes tests for:

- real dataset processing;
- blank and invalid rows;
- zero-turnover division;
- valid/invalid player comparisons;
- Flask route registration.

## Suggested development evidence to capture

1. First run where a missing dependency or database connection fails.
2. Fix that issue and capture the successful result.
3. MySQL/phpMyAdmin showing the populated `players` and `player_stats` tables.
4. Website player search.
5. Website player comparison and generated chart.
6. Quiz score being saved.
7. Test output showing all tests pass.
8. Git commits showing iterative refinement.
