# Uniqueness audit

Date: 2026-08-17. Claim: original production plus similarity checks, not a global uniqueness proof.

## Gate

| Check | Result |
| --- | --- |
| No third-party README template, stats card, trophy, snake, typing banner, or visitor badge | Pass. Working-tree grep found none of `github-readme-stats`, `snake.svg`, `typing-svg`, `visitor-badge`, `github-profile-trophy`. |
| No copied layout from the five reference profiles | Pass. This revision is a graphite engineering console of separately linked cards, not ASCII/neofetch, CRT-green terminal, dithered bio, GitSkins dashboard, or synthwave widgets. |
| No star or follower counts | Pass. Generator tests ban those substrings; live SVGs omit them. |
| No game-like copy | Pass. Tests ban `PAYLOAD BAY`, `PRIMARY LOCK`, `SIGHTLINE PULSES`, `BORESIGHT HUD`, and related HUD labels. |
| Clickable composition | Pass. README wraps hero, technical, language, activity, four project, GitHub, and LinkedIn cards in distinct links. |

## Phrase searches

GitHub code search (`gh search code`, 2026-08-17):

| Query | Result |
| --- | --- |
| `ENGINEERING SYSTEMS PROFILE` | 0 hits |
| `ACTIVITY TIMELINE` in README.md | Timed out |
| `CORE SYSTEM` in README.md | Timed out |

Layout uniqueness is carried by the linked card set, cyanotype iris, kinematic MECHANISM / PERCEPTION / DECISION chain, and professional console labels rather than a single slogan.

## Data check against GitHub API (same day)

- Owned non-fork projects excluding the profile repository: 20
- Language mix: Python 14, Jupyter 2
- Featured order: ARTPS, PyFoldable, YOLOv8 tutorial, AUV line tracking
- Latest owned write by `updated_at`: PyFoldable 2026-08-16
- LinkedIn: `https://www.linkedin.com/in/poyrazbaydemir/`

## Render notes

Cards use 416 px or 848 px `viewBox` widths so a two-column GitHub table collapses cleanly on mobile. Palette remains dark graphite with cyan/amber instrumentation. Green is reserved for the core system card, the decision node, and active timeline days.
