# Staging: PPOTN landing page + tournament app

This branch (`staging-landing`) stages the future structure of ppotn.com.
**Nothing on this branch is live.** GitHub Pages for this repo is configured
(Settings → Pages) as "Deploy from a branch", branch **main**, folder /(root) —
only `main` is published, so this branch can be reviewed safely without
affecting www.ppotn.com.

## What's here

- `landing/index.html` — NEW simple PPOTN landing page: big PPOTN heading and
  two options, "Historical" and "New Game".
- `game/index.html` — the PPOTN Tournament clock app (exported from the Muse
  artifact `ppotn-tournament`), staged to sit alongside the existing site.
- Everything else is inherited unchanged from `main` — in particular the
  existing root `index.html` (the current dashboard), `CNAME`, `data/`,
  `config/`, `scripts/`, and `.github/workflows/`.

During staging, the landing page links are relative to its staged location:

- Historical → `../index.html` (the existing site, still at root)
- New Game → `../game/`

## Go-live swap (only when Rob approves)

1. Move the current root `index.html` to `historical/index.html`.
   - **Path check required:** the dashboard uses relative paths —
     `fetch('data/season.json')`, `assets/chip-*.png`, `docs/...` links, and
     photo thumbnails under `photos/`. After the move, each of these must be
     prefixed with `../` (or the data/assets/docs/photos folders duplicated
     under `historical/`) or the dashboard will break.
2. Move `landing/index.html` to the root as the new `index.html`.
3. Update the landing links for the final layout:
   - Historical → `./historical/`
   - New Game → `./game/` (unchanged)
4. Remove the "Staging preview" note from the landing page.
5. Merge this branch to `main` (Pages only publishes `main`). Verify
   www.ppotn.com serves the landing page, and that Historical and New Game
   both load, before announcing it to the league.

## Notes

- The repo's build workflow (`.github/workflows/build.yml`) only triggers on
  pushes touching `data/tournaments/**`, `data/manual_games.json`, `config/**`,
  or `scripts/**`, so staging commits like these do not trigger it.
- The tournament app currently keeps game state in the browser only. Its
  "Upload Results" button is a placeholder; saving results centrally is a
  later step.
