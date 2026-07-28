# PPOTN League Dashboard

A live, auto-updating HTML dashboard for the PPOTN (Poker Player of the Night) league, built from Tournament Director `.tdt` exports.

## How it works

1. After a tournament finishes in Tournament Director (a winner has been declared), save/export the `.tdt` file.
2. Upload that file into `data/tournaments/` in this repo (via GitHub's web "Add file → Upload files", no git or command line needed).
3. Commit the upload. A GitHub Actions workflow automatically:
   - Parses every `.tdt` file in `data/tournaments/`
   - Computes season stats (winnings, cashes, wins, average finish, etc.) per player
   - Writes the result to `data/season.json`
   - Commits that file back to the repo
4. GitHub Pages redeploys automatically whenever the repo changes, so the dashboard at your Pages URL reflects the new results within about a minute — no manual rebuild step, ever.

Tournaments that haven't finished yet (no winner declared in the file) are automatically skipped and listed at the bottom of the leaderboard card, so a mid-game autosave never corrupts the season stats.

## Repo layout

```
index.html                 the dashboard itself (fetches data/season.json)
data/
  tournaments/*.tdt         raw Tournament Director exports, one per tournament
  season.json               generated — do not hand-edit
scripts/
  build.py                  parses .tdt files and writes data/season.json
.github/workflows/build.yml the automation that runs build.py on every upload
```

## One-time setup

1. Create a new GitHub repository (public, so free GitHub Pages hosting applies) and upload all the files in this package, preserving folder structure.
2. In the repo, go to **Settings → Pages**. Under "Build and deployment", set Source to **Deploy from a branch**, branch **main**, folder **/(root)**. Save.
3. Go to **Settings → Actions → General** and make sure "Workflow permissions" is set to **Read and write permissions** (needed so the build workflow can commit `data/season.json` back).
4. Your dashboard will be live at `https://<your-username>.github.io/<repo-name>/` within a minute or two.

## Running the build locally (optional)

```
python3 scripts/build.py
```

This reads every file in `data/tournaments/` and rewrites `data/season.json`. Useful for checking a new export before uploading it.

## Scoring

"Gross winnings" = the dollar prize amount Tournament Director's payout structure assigned to a player for a given tournament (read directly from each tournament's `Prizes` configuration, so split/tied places are handled correctly). Net = winnings minus buy-in fee paid. Both are tracked; the dashboard leaderboard is sorted by gross winnings.
