"""Build unique profile SVGs from GitHub API payloads. Stdlib only."""

from __future__ import annotations

import html
import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "generated"
LOGIN = os.environ.get("PROFILE_LOGIN", "Poyqraz")

FEATURED = (
    ("ARTPS", "primary"),
    ("PyFoldable", "secondary"),
    ("YOLO-v8-Object-Detection-Tutorial-on-CPU-GPU", "secondary"),
    ("Line-Tracking-and-Anomaly-Detection", "secondary"),
)

BLURBS = {
    "ARTPS": "Hybrid AI rover target prioritization for Mars field work.",
    "PyFoldable": "Kinematic analysis of UAV tip-hinged folding wings.",
    "YOLO-v8-Object-Detection-Tutorial-on-CPU-GPU": "CPU/GPU object-detection training notes with YOLOv8.",
    "Line-Tracking-and-Anomaly-Detection": "Teknofest 2024 AUV line tracking and anomaly work.",
}

DISPLAY = {
    "YOLO-v8-Object-Detection-Tutorial-on-CPU-GPU": "YOLOv8 CPU/GPU Tutorial",
    "Line-Tracking-and-Anomaly-Detection": "AUV Line Tracking",
    "Jupyter Notebook": "Jupyter",
}

GRAPHITE = "#0c1014"
PANEL = "#141b21"
LINE = "#24303a"
CYAN = "#5ce1e6"
AMBER = "#e8a23a"
GREEN = "#6ee07a"
TEXT = "#d8e0e6"
MUTED = "#8a97a3"
BANNED = ("star", "follower")
NS = "http://www.w3.org/2000/svg"


def esc(value: str | None) -> str:
    return html.escape(value or "", quote=True)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def collect_profile(user: dict, repos: list, events: list) -> dict:
    owned = [repo for repo in repos if not repo.get("fork")]
    languages = Counter(repo["language"] for repo in owned if repo.get("language"))
    by_name = {repo["name"]: repo for repo in owned}
    featured = []
    for name, role in FEATURED:
        repo = by_name.get(name, {"name": name, "html_url": f"https://github.com/{LOGIN}/{name}"})
        featured.append(
            {
                "name": name,
                "role": role,
                "description": BLURBS.get(name) or repo.get("description") or "Field project.",
                "html_url": repo.get("html_url") or f"https://github.com/{LOGIN}/{name}",
                "language": repo.get("language") or "Python",
                "updated_at": repo.get("updated_at") or "",
            }
        )
    latest = max(owned, key=lambda repo: repo.get("updated_at") or "", default=None)
    newest = max((parse_time(event["created_at"]) for event in events), default=datetime.now(timezone.utc))
    window = newest.date()
    days = [window - timedelta(days=offset) for offset in range(13, -1, -1)]
    counts = Counter()
    repos_by_day: dict[str, set[str]] = {day.isoformat(): set() for day in days}
    for event in events:
        day = parse_time(event["created_at"]).date()
        key = day.isoformat()
        if key not in repos_by_day:
            continue
        counts[key] += 1
        repo_name = event.get("repo", {}).get("name", "").split("/")[-1]
        if repo_name:
            repos_by_day[key].add(repo_name)
    pulses = [
        {"day": day.isoformat(), "count": counts[day.isoformat()], "repos": sorted(repos_by_day[day.isoformat()])}
        for day in days
    ]
    return {
        "login": user.get("login") or LOGIN,
        "name": user.get("name") or LOGIN,
        "owned_projects": len(owned),
        "languages": dict(languages.most_common()),
        "featured": featured,
        "latest_owned": {
            "name": latest["name"],
            "updated_at": (latest.get("updated_at") or "")[:10],
        }
        if latest
        else {"name": "none", "updated_at": ""},
        "pulses": pulses,
    }


def _svg(width: int, height: int, body: str) -> str:
    return (
        f'<svg xmlns="{NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
        f'<rect width="{width}" height="{height}" fill="{GRAPHITE}"/>'
        f"{body}</svg>"
    )


def _ticks(x: int, y: int, w: int) -> str:
    marks = []
    for i in range(0, w + 1, 16):
        h = 8 if i % 64 == 0 else 4
        marks.append(f'<rect x="{x + i}" y="{y}" width="1" height="{h}" fill="{CYAN}" opacity="0.45"/>')
    return "".join(marks)


def render_telemetry(profile: dict) -> str:
    langs = list(profile["languages"].items())[:4]
    total = sum(count for _, count in langs) or 1
    x = 220
    bands = []
    for name, count in langs:
        width = max(8, int(220 * count / total))
        label = DISPLAY.get(name, name)
        bands.append(
            f'<rect x="{x}" y="64" width="{width}" height="18" fill="{CYAN}" opacity="0.85"/>'
            f'<text x="{x}" y="100" fill="{MUTED}" font-size="11" font-family="ui-monospace, Consolas, monospace">{esc(label)} {count}</text>'
        )
        x += width + 12
    latest = profile["latest_owned"]
    body = f"""
    <rect x="16" y="16" width="816" height="108" fill="{PANEL}" stroke="{LINE}" />
    <text x="28" y="38" fill="{AMBER}" font-size="11" letter-spacing="3" font-family="ui-monospace, Consolas, monospace">FIELD TELEMETRY</text>
    <text x="28" y="78" fill="{TEXT}" font-size="36" font-family="ui-monospace, Consolas, monospace">{profile["owned_projects"]}</text>
    <text x="28" y="102" fill="{MUTED}" font-size="12" font-family="ui-monospace, Consolas, monospace">OWNED PROJECTS</text>
    <text x="220" y="38" fill="{CYAN}" font-size="11" letter-spacing="3" font-family="ui-monospace, Consolas, monospace">SIGNAL BANDS</text>
    {"".join(bands)}
    <text x="560" y="38" fill="{GREEN}" font-size="11" letter-spacing="3" font-family="ui-monospace, Consolas, monospace">LAST FIELD WRITE</text>
    <text x="560" y="78" fill="{TEXT}" font-size="16" font-family="ui-monospace, Consolas, monospace">{esc(latest["name"])}</text>
    <text x="560" y="102" fill="{MUTED}" font-size="12" font-family="ui-monospace, Consolas, monospace">{esc(latest["updated_at"])}</text>
    {_ticks(28, 114, 790)}
    """
    return _svg(848, 140, body)


def render_projects(profile: dict) -> str:
    primary = profile["featured"][0]
    secondaries = profile["featured"][1:]
    cards = []
    for i, item in enumerate(secondaries):
        x = 16 + i * 272
        cards.append(
            f"""
            <g>
            <title>{esc(item["name"])}</title>
            <rect x="{x}" y="176" width="260" height="88" fill="{PANEL}" stroke="{LINE}"/>
            <path d="M{x + 8} {176 + 8} H{x + 24} M{x + 8} {176 + 8} V{176 + 24}" stroke="{AMBER}" fill="none"/>
            <text x="{x + 14}" y="198" fill="{AMBER}" font-size="10" letter-spacing="2" font-family="ui-monospace, Consolas, monospace">PAYLOAD BAY {i + 1}</text>
            <text x="{x + 14}" y="218" fill="{TEXT}" font-size="12" font-family="ui-monospace, Consolas, monospace">{esc(DISPLAY.get(item["name"], item["name"]))}</text>
            <text x="{x + 14}" y="246" fill="{MUTED}" font-size="11" font-family="ui-monospace, Consolas, monospace">{esc(item["description"])}</text>
            </g>
            """
        )
    body = f"""
    <rect x="16" y="16" width="816" height="148" fill="{PANEL}" stroke="{CYAN}" stroke-width="1.2"/>
    <path d="M28 28 H52 M28 28 V52 M800 28 H776 M800 28 V52 M28 152 H52 M28 152 V128 M800 152 H776 M800 152 V128" stroke="{CYAN}" fill="none" stroke-width="2"/>
    <circle cx="780" cy="40" r="6" fill="none" stroke="{GREEN}"/>
    <circle cx="780" cy="40" r="2" fill="{GREEN}"/>
    <text x="36" y="44" fill="{CYAN}" font-size="11" letter-spacing="3" font-family="ui-monospace, Consolas, monospace">PRIMARY LOCK</text>
    <text x="36" y="78" fill="{TEXT}" font-size="28" font-family="ui-monospace, Consolas, monospace">{esc(primary["name"])}</text>
    <text x="36" y="108" fill="{MUTED}" font-size="14" font-family="ui-monospace, Consolas, monospace">{esc(primary["description"])}</text>
    <text x="36" y="136" fill="{AMBER}" font-size="12" font-family="ui-monospace, Consolas, monospace">ACTUATOR LOOP · {esc(primary["language"])}</text>
    {"".join(cards)}
    """
    return _svg(848, 280, body)


def render_activity(profile: dict) -> str:
    pulses = profile["pulses"]
    peak = max((item["count"] for item in pulses), default=1) or 1
    bars = []
    names = []
    for i, item in enumerate(pulses):
        x = 28 + i * 58
        h = 8 + int(36 * item["count"] / peak)
        color = GREEN if item["count"] else LINE
        bars.append(f'<rect x="{x}" y="{88 - h}" width="18" height="{h}" fill="{color}"/>')
        bars.append(f'<text x="{x}" y="104" fill="{MUTED}" font-size="9" font-family="ui-monospace, Consolas, monospace">{item["day"][5:]}</text>')
        names.extend(item["repos"])
    seen = " · ".join(dict.fromkeys(names)) or "quiet rail"
    body = f"""
    <rect x="16" y="12" width="816" height="96" fill="{PANEL}" stroke="{LINE}"/>
    <text x="28" y="32" fill="{CYAN}" font-size="11" letter-spacing="3" font-family="ui-monospace, Consolas, monospace">SIGHTLINE PULSES</text>
    <text x="220" y="32" fill="{MUTED}" font-size="11" font-family="ui-monospace, Consolas, monospace">{esc(seen)}</text>
    {"".join(bars)}
    {_ticks(28, 86, 790)}
    """
    return _svg(848, 120, body)


def _banned_hit(svg: str) -> bool:
    low = svg.lower()
    return any(word in low for word in BANNED)


def write_if_valid(out_dir: Path, svgs: dict[str, str]) -> list[str]:
    parsed = {}
    for name, svg in svgs.items():
        try:
            root = ET.fromstring(svg)
        except ET.ParseError:
            return []
        if not root.tag.endswith("svg") or _banned_hit(svg):
            return []
        parsed[name] = svg
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, svg in parsed.items():
        path = out_dir / name
        path.write_text(svg, encoding="utf-8")
        written.append(name)
    return written


def _get(url: str, token: str | None) -> object:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "poyqraz-sightline-console"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_profile(login: str, token: str | None) -> dict:
    user = _get(f"https://api.github.com/users/{login}", token)
    # ponytail: one page of 100 covers this profile; add Link pagination if owned repos exceed 100
    repos = _get(f"https://api.github.com/users/{login}/repos?per_page=100&type=owner&sort=updated", token)
    events = _get(f"https://api.github.com/users/{login}/events/public?per_page=100", token)
    if not isinstance(user, dict) or not isinstance(repos, list) or not isinstance(events, list):
        raise RuntimeError("unexpected GitHub payload")
    return collect_profile(user, repos, events)


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    try:
        profile = fetch_profile(LOGIN, token)
        svgs = {
            "telemetry.svg": render_telemetry(profile),
            "projects.svg": render_projects(profile),
            "activity.svg": render_activity(profile),
        }
    except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"keep existing SVGs: {exc}", file=sys.stderr)
        return 1
    written = write_if_valid(OUT_DIR, svgs)
    if not written:
        print("keep existing SVGs: validation failed", file=sys.stderr)
        return 1
    print("wrote " + ", ".join(written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
