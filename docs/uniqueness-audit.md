# Uniqueness audit

Date: 2026-08-17. Claim: original production plus similarity checks, not a global uniqueness proof.

## Gate

| Check | Result |
| --- | --- |
| No third-party README template, stats card, trophy, snake, typing banner, or visitor badge | Pass. Working-tree grep found none of `github-readme-stats`, `snake.svg`, `typing-svg`, `visitor-badge`, `github-profile-trophy`. |
| No copied layout from the five reference profiles | Pass. Graphite engineering console of separately linked cards, not ASCII/neofetch, CRT-green terminal, dithered bio, GitSkins dashboard, or synthwave widgets. |
| Contribution radar is original | Pass. Uses the four GitHub contribution axes, but graphite/cyan/amber instrumentation, corner frames, and `CONTRIBUTION DISTRIBUTION · LAST 90 DAYS` copy. Not a github-readme-stats embed. |
| Language card has no counts | Pass. Tests assert language SVG text contains names and proportional bars only. TeX is filtered; fork languages are included. |
| Technical card has no owned-repo count | Pass. Card shows latest update plus an activity-weighted token estimate, not a repository total. |
| No star or follower counts | Pass. Generator tests ban those substrings. |
| Clickable composition | Pass. Hero, technical, language, radar, activity, four projects, GitHub, and LinkedIn are distinct links. |

## Data source

- Language mix: GraphQL language bytes from owned repositories, including forks, excluding the profile repository and TeX. Top eight remaining languages; no invented names.
- Radar: GraphQL `contributionsCollection` for the last 90 days: commits, pull requests, code reviews, issues. Percentages are shares of that total.
- Token burn: estimated from those same 90-day counts with fixed weights (commit 700, PR 1800, review 900, issue 500). Marked `EST.` and `ACTIVITY-WEIGHTED`; not a measured model-token total.

## Render notes

Technical, language, and radar cards are 848 px wide. Project and contact cards remain 416 px for two-column GitHub tables.
