# Archive: results snapshots (backup-before-upload rule)

Rob's rule (Nov 24, 2026): **before any upload that modifies PPOTN results,
first save a copy of the previous results here.** No upload ever skips this
step.

## How it works

- Before `data/manual_games.json` is changed in any way, copy the
  then-current `data/manual_games.json` **and** `data/season.json` into a new
  folder:

  `archive/snapshots/<YYYY-MM-DD-HHMM>-before-<short-label>/`

  containing both files, byte-for-byte, exactly as they were before the
  change. Example: `archive/snapshots/2026-12-19-1830-before-dec19-games/`.
- **Snapshots are a permanent log.** They are never modified, overwritten, or
  deleted. If a snapshot name would collide, add seconds or a suffix — never
  reuse a folder.
- The first snapshot, `archive/snapshots/2026-11-24-baseline/`, is the state
  of the data before the first app-driven upload ever happened.

## Rolling back (undoing a bad upload)

1. Pick the snapshot taken just before the bad change.
2. Copy that snapshot's `manual_games.json` back over `data/manual_games.json`
   and commit.
3. The build workflow regenerates `data/season.json` from it automatically —
   the standings return to exactly what they were. (The snapshot's own
   `season.json` copy is kept as a record of what the site displayed at that
   moment, and to verify the rebuild matches.)

## Second layer of protection

Every change to these files is also in the repo's **git history**, so any
previous version of `manual_games.json` or `season.json` can be recovered from
its commit even if a snapshot were somehow missed. The snapshots exist so the
restore point is obvious and named, without digging through commits.
