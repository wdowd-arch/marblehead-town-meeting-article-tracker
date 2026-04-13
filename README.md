# Marblehead Town Meeting Article Tracker

This repository contains a GitHub Pages-ready static site for **The Marblehead Independent's 2026 Town Meeting Article Tracker**.

The page is an interactive tracker covering all 40 warrant articles for Marblehead's 2026 Annual Town Meeting, with filtering, article-level detail, sponsorship, voting thresholds and recommendation status.

## Files

- `index.html` — the standalone tracker page

## Features

- **Sticky column header** — the black column header bar stays pinned to the top of the viewport as users scroll on both desktop and mobile.
- **Mobile-friendly layout** — at 680px and below, the tracker switches to a card-based layout. The column header displays a two-column grid (article number and title) rather than hiding entirely.
- **Landscape viewing note** — a centered prompt between the badge key and search/filter controls advises phone users to rotate to landscape for the best reading experience.
- **Open Town Meeting context box** — a styled explainer box below the headline area provides background on Marblehead's open town meeting tradition, the 2026 meeting details and the structural deficit driving the Proposition 2½ override debate.
- **Search and filter** — full-text search across article titles, key details, sponsors and notes, plus category and stakes filters.
- **Expandable article details** — tap any highlighted article row to expand for full notes and sponsor information.
- **Badge key and border legend** — visual keys for recommendation badges, result badges and the color-coded left-border stakes indicator.
- **Tiered override explainer** — a callout box at the bottom breaks down the three-tier override structure and its implications.

## Publishing

To publish through GitHub Pages:

1. Create or publish this repository to GitHub.
2. Keep `index.html` in the repo root.
3. In GitHub, go to `Settings` > `Pages`.
4. Set `Source` to `Deploy from a branch`.
5. Choose `main` and `/ (root)`.

## Description

Suggested repo description:

`An interactive GitHub Pages tracker for all 40 warrant articles at Marblehead's 2026 Annual Town Meeting.`
