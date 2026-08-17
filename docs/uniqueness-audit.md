# Uniqueness audit

Date: 2026-08-17. Claim: original production plus similarity checks, not a global uniqueness proof.

## Gate

| Check | Result |
| --- | --- |
| No third-party README template, stats card, trophy, snake, typing banner, or visitor badge | Pass. Repo grep found none of `github-readme-stats`, `snake.svg`, `typing-svg`, `visitor-badge`, `github-profile-trophy`, `anuraghazra`, `komarev`. |
| No copied layout from the five reference profiles | Pass. References were ASCII/neofetch, CRT-green terminal, dithered key-value bio, GitSkins dashboard with stars, and synthwave banner/stats widgets. This profile is a graphite HUD with a cyanotype iris lock, kinematic chain, optic-rail ticks, and payload-bay cards. |
| No star or follower counts | Pass. Generator tests ban those substrings; live SVGs omit them. |
| Original HUD copy | See searches below. |

## Phrase searches

GitHub code search (`gh search code`, 2026-08-17):

| Query | Result |
| --- | --- |
| `SIGHTLINE PULSES` | 0 hits |
| `PERCEPTION LOCK` | 0 hits |
| `OPTIC RAIL` | 0 hits |
| `ACTUATOR LOOP` | 0 hits |
| `PRIMARY LOCK` in README.md | 0 hits |
| `SIGHTLINE CONSOLE` | 0 GitHub hits, but web search hit Winsted furniture. Label renamed to `BORESIGHT HUD`. |
| `FIELD TELEMETRY` / `PAYLOAD BAY` | Search timed out or rate-limited. Not used as a copied GitHub widget. |

## Data check against GitHub API (same day)

- Owned non-fork projects: 20
- Language mix: Python 14, Jupyter 2
- Featured order: ARTPS, PyFoldable, YOLOv8 tutorial, AUV line tracking
- Latest owned write by `updated_at`: PyFoldable 2026-08-16

## Render notes

SVGs use `viewBox` width 848 so they scale on mobile. Palette is dark graphite with cyan/amber HUD paint, so the panel stays readable on both GitHub themes. Green is reserved for the active decision node and pulse ticks.
