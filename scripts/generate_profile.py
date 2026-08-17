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

PROJECT_FILES = {
    "ARTPS": "project-artps.svg",
    "PyFoldable": "project-pyfoldable.svg",
    "YOLO-v8-Object-Detection-Tutorial-on-CPU-GPU": "project-yolov8.svg",
    "Line-Tracking-and-Anomaly-Detection": "project-auv.svg",
}

AXES = ("commits", "pull_requests", "code_reviews", "issues")
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
GRAPHQL_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        name
        isFork
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def esc(value: str | None) -> str:
    return html.escape(value or "", quote=True)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def contribution_shares(contributions: dict | None) -> dict[str, int]:
    data = contributions or {}
    total = sum(int(data.get(key, 0) or 0) for key in AXES)
    if total <= 0:
        return {key: 0 for key in AXES}
    percents = {key: round(int(data.get(key, 0) or 0) * 100 / total) for key in AXES}
    drift = 100 - sum(percents.values())
    if drift:
        largest = max(AXES, key=lambda key: percents[key])
        percents[largest] += drift
    return percents


def parse_graphql(payload: dict, login: str) -> tuple[dict[str, int], dict[str, int]]:
    user = ((payload or {}).get("data") or {}).get("user") or {}
    if not user:
        raise RuntimeError("unexpected GraphQL payload")
    coll = user.get("contributionsCollection") or {}
    contributions = {
        "commits": int(coll.get("totalCommitContributions") or 0),
        "pull_requests": int(coll.get("totalPullRequestContributions") or 0),
        "code_reviews": int(coll.get("totalPullRequestReviewContributions") or 0),
        "issues": int(coll.get("totalIssueContributions") or 0),
    }
    languages: Counter[str] = Counter()
    for node in ((user.get("repositories") or {}).get("nodes") or []):
        if node.get("isFork") or node.get("name") == login:
            continue
        for edge in ((node.get("languages") or {}).get("edges") or []):
            name = ((edge.get("node") or {}).get("name")) or ""
            if name:
                languages[name] += int(edge.get("size") or 0)
    return dict(languages), contributions


def collect_profile(
    user: dict,
    repos: list,
    events: list,
    language_bytes: dict | None = None,
    contributions: dict | None = None,
) -> dict:
    owned = [repo for repo in repos if not repo.get("fork") and repo.get("name") != LOGIN]
    if language_bytes:
        languages = dict(Counter(language_bytes).most_common(8))
    else:
        languages = dict(Counter(repo["language"] for repo in owned if repo.get("language")).most_common(8))
    by_name = {repo["name"]: repo for repo in owned}
    featured = []
    for name, role in FEATURED:
        repo = by_name.get(name, {"name": name, "html_url": f"https://github.com/{LOGIN}/{name}"})
        featured.append(
            {
                "name": name,
                "role": role,
                "description": BLURBS.get(name) or repo.get("description") or "Engineering project.",
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
        "languages": languages,
        "featured": featured,
        "latest_owned": {
            "name": latest["name"],
            "updated_at": (latest.get("updated_at") or "")[:10],
        }
        if latest
        else {"name": "none", "updated_at": ""},
        "pulses": pulses,
        "contribution_shares": contribution_shares(contributions),
    }


def _svg(width: int, height: int, body: str) -> str:
    return (
        f'<svg xmlns="{NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
        f'<rect width="{width}" height="{height}" fill="{GRAPHITE}"/>'
        f"{body}</svg>"
    )


def _frame(x: int, y: int, w: int, h: int, accent: str = CYAN) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PANEL}" stroke="{LINE}"/>'
        f'<path d="M{x + 8} {y + 8} H{x + 26} M{x + 8} {y + 8} V{y + 26} '
        f'M{x + w - 8} {y + 8} H{x + w - 26} M{x + w - 8} {y + 8} V{y + 26}" '
        f'stroke="{accent}" fill="none" stroke-width="1.6"/>'
    )


def render_technical_profile(profile: dict) -> str:
    latest = profile["latest_owned"]
    body = f"""
    {_frame(8, 8, 400, 124, AMBER)}
    <text x="24" y="36" fill="{AMBER}" font-size="11" letter-spacing="2.4" font-family="ui-monospace, Consolas, monospace">TECHNICAL PROFILE</text>
    <text x="24" y="78" fill="{TEXT}" font-size="32" font-family="ui-monospace, Consolas, monospace">{profile["owned_projects"]}</text>
    <text x="24" y="102" fill="{MUTED}" font-size="12" font-family="ui-monospace, Consolas, monospace">OWNED REPOSITORIES</text>
    <text x="220" y="70" fill="{GREEN}" font-size="11" letter-spacing="1.8" font-family="ui-monospace, Consolas, monospace">LATEST UPDATE</text>
    <text x="220" y="94" fill="{TEXT}" font-size="14" font-family="ui-monospace, Consolas, monospace">{esc(latest["name"])}</text>
    <text x="220" y="114" fill="{MUTED}" font-size="12" font-family="ui-monospace, Consolas, monospace">{esc(latest["updated_at"])}</text>
    """
    return _svg(416, 140, body)


def render_language_distribution(profile: dict) -> str:
    langs = list(profile["languages"].items())[:8]
    total = sum(size for _, size in langs) or 1
    rows = []
    y = 64
    for name, size in langs:
        width = max(16, int(620 * size / total))
        label = DISPLAY.get(name, name)
        rows.append(
            f'<text x="28" y="{y}" fill="{MUTED}" font-size="13" font-family="ui-monospace, Consolas, monospace">{esc(label)}</text>'
            f'<rect x="168" y="{y - 14}" width="{width}" height="16" fill="{CYAN}" opacity="0.88"/>'
        )
        y += 28
    height = max(140, 48 + len(langs) * 28 + 20)
    body = f"""
    {_frame(8, 8, 832, height - 16, CYAN)}
    <text x="28" y="36" fill="{CYAN}" font-size="11" letter-spacing="2.4" font-family="ui-monospace, Consolas, monospace">LANGUAGE DISTRIBUTION</text>
    {"".join(rows)}
    """
    return _svg(848, height, body)


def render_activity_timeline(profile: dict) -> str:
    pulses = profile["pulses"]
    peak = max((item["count"] for item in pulses), default=1) or 1
    bars = []
    names = []
    for i, item in enumerate(pulses):
        x = 24 + i * 57
        h = 8 + int(40 * item["count"] / peak)
        color = GREEN if item["count"] else LINE
        bars.append(f'<rect x="{x}" y="{108 - h}" width="16" height="{h}" fill="{color}"/>')
        bars.append(
            f'<text x="{x}" y="124" fill="{MUTED}" font-size="9" font-family="ui-monospace, Consolas, monospace">{item["day"][5:]}</text>'
        )
        names.extend(item["repos"])
    seen = " · ".join(dict.fromkeys(names)) or "No recent public activity"
    body = f"""
    {_frame(8, 8, 832, 124, CYAN)}
    <text x="24" y="36" fill="{CYAN}" font-size="11" letter-spacing="2.4" font-family="ui-monospace, Consolas, monospace">ACTIVITY TIMELINE</text>
    <text x="220" y="36" fill="{MUTED}" font-size="11" font-family="ui-monospace, Consolas, monospace">{esc(seen)}</text>
    {"".join(bars)}
    """
    return _svg(848, 140, body)


def render_contribution_distribution(profile: dict) -> str:
    shares = profile.get("contribution_shares") or {key: 0 for key in AXES}
    cx, cy, radius = 424, 168, 88
    points = {
        "code_reviews": (cx, cy - radius * shares["code_reviews"] / 100),
        "issues": (cx + radius * shares["issues"] / 100, cy),
        "pull_requests": (cx, cy + radius * shares["pull_requests"] / 100),
        "commits": (cx - radius * shares["commits"] / 100, cy),
    }
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in (points["code_reviews"], points["issues"], points["pull_requests"], points["commits"]))
    labels = []
    if shares["commits"]:
        labels.append(f'<text x="{cx - radius - 8}" y="{cy - 10}" text-anchor="end" fill="{GREEN}" font-size="13" font-family="ui-monospace, Consolas, monospace">{shares["commits"]}%</text>')
    if shares["pull_requests"]:
        labels.append(f'<text x="{cx + 12}" y="{cy + radius + 18}" fill="{GREEN}" font-size="13" font-family="ui-monospace, Consolas, monospace">{shares["pull_requests"]}%</text>')
    if shares["code_reviews"]:
        labels.append(f'<text x="{cx + 12}" y="{cy - radius - 8}" fill="{GREEN}" font-size="13" font-family="ui-monospace, Consolas, monospace">{shares["code_reviews"]}%</text>')
    if shares["issues"]:
        labels.append(f'<text x="{cx + radius + 8}" y="{cy - 10}" fill="{GREEN}" font-size="13" font-family="ui-monospace, Consolas, monospace">{shares["issues"]}%</text>')
    dots = []
    for key, (x, y) in points.items():
        if shares[key]:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{TEXT}"/>')
    body = f"""
    {_frame(8, 8, 832, 284, GREEN)}
    <text x="28" y="36" fill="{GREEN}" font-size="11" letter-spacing="2.4" font-family="ui-monospace, Consolas, monospace">CONTRIBUTION DISTRIBUTION</text>
    <text x="420" y="36" fill="{MUTED}" font-size="11" letter-spacing="1.6" font-family="ui-monospace, Consolas, monospace">LAST 90 DAYS</text>
    <line x1="{cx}" y1="{cy - radius}" x2="{cx}" y2="{cy + radius}" stroke="{GREEN}" stroke-width="1.4"/>
    <line x1="{cx - radius}" y1="{cy}" x2="{cx + radius}" y2="{cy}" stroke="{GREEN}" stroke-width="1.4"/>
    <polygon points="{poly}" fill="{GREEN}" fill-opacity="0.28" stroke="{CYAN}" stroke-width="1.2"/>
    {"".join(dots)}
    {"".join(labels)}
    <text x="{cx}" y="{cy - radius - 14}" text-anchor="middle" fill="{MUTED}" font-size="12" font-family="ui-monospace, Consolas, monospace">CODE REVIEWS</text>
    <text x="{cx}" y="{cy + radius + 32}" text-anchor="middle" fill="{MUTED}" font-size="12" font-family="ui-monospace, Consolas, monospace">PULL REQUESTS</text>
    <text x="{cx - radius - 12}" y="{cy + 4}" text-anchor="end" fill="{MUTED}" font-size="12" font-family="ui-monospace, Consolas, monospace">COMMITS</text>
    <text x="{cx + radius + 12}" y="{cy + 4}" fill="{MUTED}" font-size="12" font-family="ui-monospace, Consolas, monospace">ISSUES</text>
    """
    return _svg(848, 300, body)


def render_project_card(item: dict) -> str:
    heading = "CORE SYSTEM" if item["role"] == "primary" else "FEATURED PROJECT"
    accent = GREEN if item["role"] == "primary" else AMBER
    title = DISPLAY.get(item["name"], item["name"])
    body = f"""
    {_frame(8, 8, 400, 144, accent)}
    <title>{esc(item["name"])}</title>
    <text x="24" y="36" fill="{accent}" font-size="11" letter-spacing="2.4" font-family="ui-monospace, Consolas, monospace">{heading}</text>
    <text x="24" y="68" fill="{TEXT}" font-size="18" font-family="ui-monospace, Consolas, monospace">{esc(title)}</text>
    <text x="24" y="98" fill="{MUTED}" font-size="12" font-family="ui-monospace, Consolas, monospace">{esc(item["description"])}</text>
    <text x="24" y="126" fill="{CYAN}" font-size="12" font-family="ui-monospace, Consolas, monospace">{esc(item["language"])}</text>
    """
    return _svg(416, 160, body)


def render_cards(profile: dict) -> dict[str, str]:
    cards = {
        "technical-profile.svg": render_technical_profile(profile),
        "language-distribution.svg": render_language_distribution(profile),
        "activity-timeline.svg": render_activity_timeline(profile),
        "contribution-distribution.svg": render_contribution_distribution(profile),
    }
    for item in profile["featured"]:
        cards[PROJECT_FILES[item["name"]]] = render_project_card(item)
    return cards


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
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "poyqraz-engineering-profile"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _graphql(token: str, login: str) -> dict:
    now = datetime.now(timezone.utc)
    variables = {
        "login": login,
        "from": (now - timedelta(days=90)).strftime("%Y-%m-%dT00:00:00Z"),
        "to": now.strftime("%Y-%m-%dT23:59:59Z"),
    }
    payload = json.dumps({"query": GRAPHQL_QUERY, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "poyqraz-engineering-profile",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if not isinstance(data, dict) or data.get("errors"):
        raise RuntimeError("unexpected GraphQL payload")
    return data


def fetch_profile(login: str, token: str | None) -> dict:
    if not token:
        raise RuntimeError("GITHUB_TOKEN required for GraphQL metrics")
    user = _get(f"https://api.github.com/users/{login}", token)
    # ponytail: one page of 100 covers this profile; add Link pagination if owned repos exceed 100
    repos = _get(f"https://api.github.com/users/{login}/repos?per_page=100&type=owner&sort=updated", token)
    events = _get(f"https://api.github.com/users/{login}/events/public?per_page=100", token)
    if not isinstance(user, dict) or not isinstance(repos, list) or not isinstance(events, list):
        raise RuntimeError("unexpected GitHub payload")
    language_bytes, contributions = parse_graphql(_graphql(token, login), login)
    return collect_profile(user, repos, events, language_bytes, contributions)


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    try:
        profile = fetch_profile(LOGIN, token)
        svgs = render_cards(profile)
    except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError, KeyError) as exc:
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
