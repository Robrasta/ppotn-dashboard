# PPOTN Dashboard — Enhancement Tracker

Future work for the dashboard, parked for later. Nothing here is scheduled — this is just a running list so ideas don't get lost between sessions.

Status legend: 🔲 Not started · 🔄 In progress · ✅ Done

---

## 1. 🔲 Scheduling tool, revisited

**Background:** We looked at four ways to track game scheduling — manual config (Claude-assisted), a structured RSVP tally, non-authoritative email skimming, and a shared calendar as source of truth — and went with the manual config approach for now (`config/schedule.json`, surfaced in the "Scheduled Games" sidebar).

**Revisit when:** the manual "just tell Claude the date once it's locked in" step starts to feel like a chore, or quorum-counting by email gets error-prone.

**Likely next step:** either a lightweight RSVP tally (yes/no signup per proposed date, live headcount toward the 7-person quorum) or wiring the sidebar to a shared calendar instead of hand-maintained JSON. Not both — pick one once there's a real pain point to design against.

---

## 2. 🔄 Scenario builder for standings

**Idea:** An interactive "what-if" tool on the dashboard — pick hypothetical finishes for upcoming games (or tweak past ones) and see how the season leaderboard would shift in response. E.g. "if I win the next 3 games, do I catch Whited for 1st?"

**Status:** In progress — building a client-side scenario builder card. Any visitor can add one or more hypothetical games (buy-in, total players, per-player finish place), computed against the standard 50/30/20 payout split, and see a projected leaderboard with rank-change indicators. Not limited to the big Vegas/final games — works for any hypothetical game size. Nothing is saved server-side; it's a live in-browser sandbox that resets on reload.

**Open questions:** whether to support custom (non-50/30/20) payout splits per hypothetical game, and whether to let a visitor save/share a specific scenario via a URL.

---

## 3. ✅ Photo gallery section

**Idea:** A section for photos from game nights.

**Status:** Done. Grid gallery with lightbox, grouped by month, on the main dashboard (`photos/thumbs` + `photos/full`, driven by `config/photos.json`). Visitors can also submit their own photos for review via a linked Google Form ("+ Submit a photo" in the gallery header) — Rob reviews submissions and adds approved ones to `config/photos.json`. Note: Google's file-upload form questions require the submitter to sign in with a Google account.

---

*Last updated: 2026-07-29*
