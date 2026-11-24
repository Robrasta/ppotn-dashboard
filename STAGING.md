# Staging: PPOTN landing page + tournament app

This branch (`staging-landing`) stages the future structure of ppotn.com.
**Nothing on this branch is live.** GitHub Pages for this repo is configured
(Settings → Pages) as "Deploy from a branch", branch **main**, folder /(root) —
only `main` is published, so this branch can be reviewed safely without
affecting www.ppotn.com.

## What's here

- `landing/index.html` — NEW simple PPOTN landing page: big PPOTN heading and
  two options, "Historical" and "New Game". Below the two cards it also shows
  the **current standings** (Rob, Nov 24, 2026: the standings moved onto the
  landing/splash screen, in a two-column block under the cards; the two cards
  shrank slightly to fit). The figures are a **static snapshot** of the 2026
  standings from `data/season.json` as of Nov 24, 2026 — they do not update
  on this branch. **Go-live checklist item:** when the landing page goes
  live at the root, wire this block to read `data/season.json` live (same
  single fetch the dashboard uses) so the standings never go stale; until
  then, refresh the snapshot by hand if the figures are refreshed for a
  staging review.
- `game/index.html` — the PPOTN Tournament clock app (exported from the Muse
  artifact `ppotn-tournament`), staged to sit alongside the existing site.
- `historical/index.html` — a copy of the legacy dashboard, already moved
  under `historical/` with its relative paths fixed (`../`) and its graphics
  restyled to match the new felt-green + gold look. Staged Nov 24, 2026;
  see the "Historical page" section below.
- Everything else is inherited unchanged from `main` — in particular the
  existing root `index.html` (the current dashboard), `CNAME`, `data/`,
  `config/`, `scripts/`, and `.github/workflows/`.

During staging, the landing page links are relative to its staged location:

- Historical → `../index.html` (the existing site, still at root)
- New Game → `../game/`

## Go-live swap (only when Rob approves)

Go-live happens **only** on Rob's explicit go — never automatically, and
never as a side effect of staging work on this branch.

1. Move the current root `index.html` to `historical/index.html`.
   - **Move it WHOLE and unmodified** apart from the relative-path fixes
     below — do not rebuild, strip, or "improve" any part of it. In
     particular, the dashboard's built-in analytics and finish-modeling
     features (the Scenario / What-if / projected-finish tooling) must ALL be
     preserved exactly as they are (Rob confirmed Nov 24, 2026). No rebuild of
     those features is needed or wanted: they read the same
     `data/season.json` the bot regenerates, so they keep working on the moved
     page as long as the data path resolves.
   - **Path check required:** the dashboard uses relative paths —
     `fetch('data/season.json')`, `assets/chip-*.png`, `docs/...` links, and
     photo thumbnails under `photos/`. After the move, each of these must be
     prefixed with `../` (or the data/assets/docs/photos folders duplicated
     under `historical/`) or the dashboard will break — including the
     analytics, which fetch `data/season.json` the same way.
   **Must-keep under Historical (Rob confirmed Nov 24, 2026):** everything
   below carries over with the moved page — none of it is optional:
   - **Past champions record** — the historical list of previous PPOTN
     champions, driven by `config/history.json`.
   - **Photo gallery** — all pictures under `photos/`, indexed by
     `config/photos.json`, **including the ability to add new photos
     later** (new photo files plus a `config/photos.json` entry must keep
     working the same way after the move).
   - **Analytics and finish-modeling** — the Scenario / What-if /
     projected-finish tooling (see step 1 above).
   - **The champions sound Easter egg** — clicking a champion's card in
     the champions/dynasty list plays that champion's hidden sound clip.
     Rob first said this could be dropped, then reversed himself on
     Nov 24, 2026: **it is MUST-KEEP, same as everything else on this
     list.** It should survive automatically because the page moves
     whole, but make sure its assets come along: the clips live in
     `assets/` (`assets/jones-sound.mp3`, `assets/harrison-sound.mp3`,
     `assets/grissom-sound.mp3`, `assets/whited-sound.mp3`,
     `assets/klinect-sound.mp3`, `assets/tawse-sound.mp3`,
     `assets/hernandez-sound.mp3`, wired up in the page's SOUND_MAP), so
     the `../assets/` path fix in step 1 must cover them — if the sound
     stops working after the move, a path broke; fix the path, don't
     drop the feature.
2. Move `landing/index.html` to the root as the new `index.html`.
3. Update the landing links for the final layout:
   - Historical → `./historical/`
   - New Game → `./game/` (unchanged)
4. Remove the "Staging preview" note from the landing page.
5. **Keep the passphrase gate at the site entry (Rob, Nov 24, 2026 —
   MUST-KEEP).** The current site is protected by a passphrase-gate
   overlay (in the current root `index.html`). In the new structure the
   gate must protect the site's entry point: a visitor hitting the new
   landing page at the root must pass the same passphrase check — the
   existing passphrase, whose value is intentionally not recorded
   anywhere in this repo or its docs — before they can reach either
   Historical or New Game, exactly as the site is protected today.
   Carry the gate over to the landing page as part of the swap; do not
   launch the new structure without it.
6. Merge this branch to `main` (Pages only publishes `main`). Verify
   www.ppotn.com serves the landing page, and that Historical and New Game
   both load, before announcing it to the league.
7. **Wire the landing-page standings block to live data.** The standings
   block under the landing cards is a static snapshot while staged (see
   "What's here"). At go-live, replace the snapshot with a live read of
   `data/season.json` so the landing standings always match Historical.

## Historical page (staged Nov 24, 2026)

`historical/index.html` on this branch is the legacy dashboard, copied from
`main`'s root `index.html` (67,950 bytes; 68,742 bytes after the edits below)
with ONLY these changes:

- **Relative paths fixed for `historical/`:** every `data/`, `config/`,
  `assets/`, `photos/`, `docs/` reference now carries the `../` prefix — the
  `data/season.json` fetch, the chip images, the three `docs/` links, the
  champion sound clips (`../assets/<surname>-sound.mp3`) and Graham card
  photo, and the gallery photo paths (the URLs come from the data, so the
  prefix was applied where the page consumes them: the gallery thumbnail
  `src` and the lightbox image `src`).
- **CSS-only visual restyle** to align with the landing page / tournament
  app: felt green (`#14532d` / `#0b3d20`) radial glow over a deep
  green-black background, dark green panels (`#16241a` / `#1d2f21`,
  `#2c4230` lines), gold (`#f2c94c` / `#d4a017`) headings and accents,
  cream text, 18px card corners with the game's soft shadow, and a serif
  display font on headings. No layout, markup, IDs/classes, JavaScript, or
  text content was changed.
- **Features verified intact** by a before/after marker inventory (counts
  identical): passphrase gate, the single `data/season.json` fetch,
  analytics + Scenario / What-if modeling, champions record, champion
  sound clips + photo pop, photo gallery + lightbox, and the scrolling
  message banner. At go-live, step 1's move is already done — this file
  replaces the "move it whole" step; just verify it once more.

- **Layout update (Rob, Nov 24, 2026):** the 2026 standings (Season Leaderboard) section was removed from this page — the standings now live on the landing splash screen; the Champions (League History) card moved to the top of the main content and the Photo Gallery to the very bottom of the page (last section); all other features verified intact after the change.

**Banner message (Rob, Nov 24, 2026):** the page renders the scrolling
banner from `data.message` inside `data/season.json` (the build folds
`config/message.json` into it). The current banner text stays as-is.
Going forward, BOTH ways of setting the banner stay open — neither is
retired: (1) Rob asks Amber to update `config/message.json` directly via
GitHub, and (2) the email option remains — Rob may later authorize other
hosts to send banner messages to Amber's Muse Mail address
(robharrison@muse.ai), with Rob authorizing who; he will design that
later.

## Notes

- The repo's build workflow (`.github/workflows/build.yml`) only triggers on
  pushes touching `data/tournaments/**`, `data/manual_games.json`, `config/**`,
  or `scripts/**`, so staging commits like these do not trigger it.
- The tournament app currently keeps game state in the browser only. Its
  "Upload Results" button is a placeholder; saving results centrally is a
  later step.

## Upload protocol (when Upload Results goes live)

Every results upload follows these steps, in order. **No upload ever skips
step 1.**

1. **Snapshot the previous results.** Copy the current
   `data/manual_games.json` and `data/season.json` into
   `archive/snapshots/<YYYY-MM-DD-HHMM>-before-<short-label>/` (see
   `archive/README.md`). Snapshots are permanent — never modified or deleted —
   so any previous standings can be restored.
2. **Rob reviews and approves** the new game record before anything is
   written.
3. **Append** the approved game object to `data/manual_games.json` (the
   per-game source of truth) and commit.
4. **The bot rebuilds the standings** — the build workflow regenerates
   `data/season.json` automatically.
5. **Verify** www.ppotn.com shows the new standings before calling it done.

## GO-LIVE EXECUTED (Nov 24, 2026 — Rob's explicit "go")

Rob approved go-live on Nov 24, 2026. The new structure was merged to `main`:

- Root `index.html` is now the new PPOTN app (landing splash with the
  flashing message banner, New Game / Statistics / Historical cards, the
  2026 standings panel with the "Detailed standings" link, and the Next Up
  card), carrying the whole approved preview feature set (Game Setup,
  seat draw, tournament clock, Statistics with Consistency + Scenario
  Modeler + Bragging Rights, Detailed Standings, Historical record book).
  The splash refreshes its banner, standings, and Next Up live from
  `data/season.json`.
- The site's existing passphrase gate (SHA-256 overlay from the old root
  page, unchanged mechanism and hash) protects the new root entry.
- `game/index.html` is the latest standalone tournament app.
- `statistics/index.html` opens the same app on the Statistics view.
- `historical/index.html` remains the restyled, data-driven legacy
  dashboard (champions, gallery, analytics, scenario, sounds intact).
- A pre-go-live snapshot of the live data files sits in
  `archive/snapshots/2026-11-24-1555-before-golive/`.
- Rollback: revert the go-live merge commit on `main` (or reset `main`
  to ee0d191e, the pre-go-live head) and Pages republishes the old site.
