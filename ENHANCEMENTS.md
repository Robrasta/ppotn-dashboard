# PPOTN Dashboard — Enhancement Tracker

Future work for the dashboard, parked for later. Nothing here is scheduled — this is just a running list so ideas don't get lost between sessions.

Status legend: 🔲 Not started · 🔄 In progress · ✅ Done

---

## 1. 🔲 Scheduling tool, revisited

**Background:** We looked at four ways to track game scheduling — manual config (Claude-assisted), a structured RSVP tally, non-authoritative email skimming, and a shared calendar as source of truth — and went with the manual config approach for now (`config/schedule.json`, surfaced in the "Scheduled Games" sidebar).

**Revisit when:** the manual "just tell Claude the date once it's locked in" step starts to feel like a chore, or quorum-counting by email gets error-prone.

**Likely next step:** either a lightweight RSVP tally (yes/no signup per proposed date, live headcount toward the 7-person quorum) or wiring the sidebar to a shared calendar instead of hand-maintained JSON. Not both — pick one once there's a real pain point to design against.

---

## 2. 🔲 Scenario builder for standings

**Idea:** An interactive "what-if" tool on the dashboard — pick hypothetical finishes for upcoming games (or tweak past ones) and see how the season leaderboard would shift in response. E.g. "if I win the next 3 games, do I catch Whited for 1st?"

**Likely shape:** client-side only — reuse the existing aggregation logic (`build.py`'s scoring math, ported to JS or run against a copy of `season.json`) so it can recompute instantly in the browser without touching the real data or triggering a rebuild.

**Open questions:** how many hypothetical games to allow at once, whether it should support editing past results too (probably not — keep it forward-looking only), and how to keep the UI simple enough that it doesn't compete with the real leaderboard for attention.

---

## 3. 🔲 Photo gallery section

**Idea:** A section for photos from game nights.

**Open questions:**
- Hosting: store images directly in the repo (simple, but GitHub Pages/repo size limits matter once photo volume grows) vs. an external image host.
- Upload workflow: same pattern as `.tdt` uploads (drag files into a repo folder, auto-picked up by the build) vs. something lighter-weight.
- Display: grid with lightbox, grouped by game night/date, tied to the tournament results section, or a totally separate stand-alone page.

---

*Last updated: 2026-07-28*
