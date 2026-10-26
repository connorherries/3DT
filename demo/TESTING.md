# Test Record

Date: 2026-10-26

## Automated tests

Command run from the workspace root:

```powershell
.\.venv\Scripts\python.exe -m pytest demo/tests -q
```

Result: 4 passed.

| Test case | Expected result | Observed result |
|---|---|---|
| Updated CSV import and analysis | Clean records, derive metrics, and retain one record per player | 582 cleaned; 382 featured; all impact values present |
| League summary row | Reject non-player row with missing core statistics | 1 invalid row removed |
| Traded player totals | Use the `2TM` aggregate instead of team-level splits | 132 split rows removed |
| Remaining duplicate player IDs | Keep one record per player | 19 duplicates removed |
| Missing three-point percentage | Median-impute and report count and value | 51 values filled with median `0.343` |
| Remove lowest-scoring players | Exclude exactly the 200 lowest points-per-game records | 200 removed; 382 retained |
| Synthetic blank row | Remove the blank player record | 1 blank row removed |
| Synthetic malformed games value | Remove the invalid core-stat row | 1 invalid row removed |
| Synthetic missing percentage | Fill from available median | Output contains no missing percentage |
| Missing required columns / no valid rows | Raise a clear `ValueError` | Both cases tested |
| Exports | Create player JSON, summary JSON, cleaned CSV, and three metric charts | All six files created |

## Browser checks

The previous browser smoke checks were against a build with 482 players. They are stale because the current pipeline produces 382 featured players. Re-run and record browser checks for the current build before using them as assessment evidence.

## Remaining assessment evidence

The CSV does not identify its source or season. Confirm teacher approval and record the source URL, access date, and dataset scope before submission. Capture annotated screenshots and retain dated Git history as evidence of the development process.
