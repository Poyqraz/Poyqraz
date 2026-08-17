# Uniqueness audit

Date: 2026-08-17. Claim: original production plus similarity checks, not a global uniqueness proof.

## Gate

| Check | Result |
| --- | --- |
| No third-party README template, stats card, trophy, snake, typing banner, or visitor badge | Pass. Working-tree grep found none of `github-readme-stats`, `snake.svg`, `typing-svg`, `visitor-badge`, `github-profile-trophy`. |
| No copied layout from the five reference profiles | Pass. Graphite engineering console of separately linked cards, not ASCII/neofetch, CRT-green terminal, dithered bio, GitSkins dashboard, or synthwave widgets. |
| Contribution radar is original | Pass. Uses the four GitHub contribution axes, but graphite/cyan/amber instrumentation, corner frames, and `CONTRIBUTION DISTRIBUTION · LAST 90 DAYS` copy. Not a github-readme-stats embed. |
| Language card has no counts | Pass. Tests assert language SVG text contains names and proportional bars only. |
| No star or follower counts | Pass. Generator tests ban those substrings. |
| Clickable composition | Pass. Hero, technical, language, radar, activity, four projects, GitHub, and LinkedIn are distinct links. |

## Data source

- Language mix: GraphQL repository language bytes, forks and the profile repository excluded, top eight languages.
- Radar: GraphQL `contributionsCollection` for the last 90 days: commits, pull requests, code reviews, issues. Percentages are shares of that total, not invented values.

## Render notes

Language and radar cards are 848 px wide. Project and contact cards remain 416 px for two-column GitHub tables.
