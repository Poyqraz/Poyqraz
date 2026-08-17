"""Checks for the profile SVG generator. Run: python tests/test_generate_profile.py"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_profile as gp  # noqa: E402

SAMPLE_USER = {
    "login": "Poyqraz",
    "name": "Poyraz BAYDEMİR",
    "public_repos": 29,
    "followers": 25,
    "following": 82,
}

SAMPLE_REPOS = [
    {
        "name": "ARTPS",
        "fork": False,
        "language": "Python",
        "description": "Autonomous Rover Target Prioritization System using hybrid AI for Mars exploration",
        "html_url": "https://github.com/Poyqraz/ARTPS",
        "updated_at": "2026-08-14T20:46:17Z",
        "stargazers_count": 9,
    },
    {
        "name": "PyFoldable",
        "fork": False,
        "language": "Python",
        "description": None,
        "html_url": "https://github.com/Poyqraz/PyFoldable",
        "updated_at": "2026-08-16T12:20:06Z",
        "stargazers_count": 0,
    },
    {
        "name": "YOLO-v8-Object-Detection-Tutorial-on-CPU-GPU",
        "fork": False,
        "language": "Python",
        "description": "YOLOv8 object detection tutorial",
        "html_url": "https://github.com/Poyqraz/YOLO-v8-Object-Detection-Tutorial-on-CPU-GPU",
        "updated_at": "2025-01-05T03:56:04Z",
        "stargazers_count": 7,
    },
    {
        "name": "Line-Tracking-and-Anomaly-Detection",
        "fork": False,
        "language": "Python",
        "description": "Teknofest 2024 AUV Project.",
        "html_url": "https://github.com/Poyqraz/Line-Tracking-and-Anomaly-Detection",
        "updated_at": "2025-07-16T18:43:01Z",
        "stargazers_count": 2,
    },
    {
        "name": "Colab-YOLO-V8-Object-Detection",
        "fork": False,
        "language": "Jupyter Notebook",
        "description": "yolo v8 object detection",
        "html_url": "https://github.com/Poyqraz/Colab-YOLO-V8-Object-Detection",
        "updated_at": "2024-05-05T19:27:31Z",
        "stargazers_count": 2,
    },
    {
        "name": "worldwideview",
        "fork": True,
        "language": "TypeScript",
        "description": "forked dashboard",
        "html_url": "https://github.com/Poyqraz/worldwideview",
        "updated_at": "2026-05-11T14:43:32Z",
        "stargazers_count": 0,
    },
]

SAMPLE_EVENTS = [
    {
        "type": "PushEvent",
        "created_at": "2026-08-17T13:49:47Z",
        "repo": {"name": "Poyqraz/ARTPS"},
    },
    {
        "type": "PushEvent",
        "created_at": "2026-08-17T08:50:17Z",
        "repo": {"name": "Poyqraz/ARTPS"},
    },
    {
        "type": "PullRequestEvent",
        "created_at": "2026-08-16T13:41:42Z",
        "repo": {"name": "Poyqraz/PyFoldable"},
    },
    {
        "type": "PushEvent",
        "created_at": "2026-08-04T12:00:00Z",
        "repo": {"name": "Poyqraz/ARTPS"},
    },
]

BANNED_COPY = (
    "payload bay",
    "primary lock",
    "sightline pulses",
    "boresight hud",
    "field telemetry",
    "signal bands",
    "actuator loop",
    "perception lock",
    "star",
    "follower",
)

REQUIRED_HEADINGS = (
    "TECHNICAL PROFILE",
    "LANGUAGE DISTRIBUTION",
    "ACTIVITY TIMELINE",
    "CORE SYSTEM",
    "FEATURED PROJECT",
)

CARD_FILES = (
    "technical-profile.svg",
    "language-distribution.svg",
    "activity-timeline.svg",
    "project-artps.svg",
    "project-pyfoldable.svg",
    "project-yolov8.svg",
    "project-auv.svg",
)


class CollectProfileTests(unittest.TestCase):
    def setUp(self):
        self.profile = gp.collect_profile(SAMPLE_USER, SAMPLE_REPOS, SAMPLE_EVENTS)

    def test_owned_count_excludes_forks(self):
        self.assertEqual(self.profile["owned_projects"], 5)

    def test_language_mix_ignores_forks(self):
        self.assertEqual(self.profile["languages"], {"Python": 4, "Jupyter Notebook": 1})

    def test_featured_order_puts_artps_first(self):
        names = [item["name"] for item in self.profile["featured"]]
        self.assertEqual(
            names,
            [
                "ARTPS",
                "PyFoldable",
                "YOLO-v8-Object-Detection-Tutorial-on-CPU-GPU",
                "Line-Tracking-and-Anomaly-Detection",
            ],
        )
        self.assertEqual(self.profile["featured"][0]["role"], "primary")
        self.assertEqual([item["role"] for item in self.profile["featured"][1:]], ["secondary"] * 3)

    def test_profile_has_no_star_or_follower_fields(self):
        blob = str(self.profile).lower()
        for banned in ("star", "follower"):
            self.assertNotIn(banned, blob)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.profile = gp.collect_profile(SAMPLE_USER, SAMPLE_REPOS, SAMPLE_EVENTS)
        self.svgs = gp.render_cards(self.profile)

    def test_render_cards_emits_atomic_files(self):
        self.assertEqual(set(self.svgs), set(CARD_FILES))

    def test_svgs_are_valid_xml(self):
        for name, svg in self.svgs.items():
            root = ET.fromstring(svg)
            self.assertTrue(root.tag.endswith("svg"), name)

    def test_svgs_use_professional_headings(self):
        blob = "\n".join(self.svgs.values())
        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, blob)

    def test_svgs_omit_banned_copy(self):
        blob = "\n".join(self.svgs.values()).lower()
        for banned in BANNED_COPY:
            self.assertNotIn(banned, blob)

    def test_project_cards_contain_repo_names(self):
        mapping = {
            "project-artps.svg": "ARTPS",
            "project-pyfoldable.svg": "PyFoldable",
            "project-yolov8.svg": "YOLO-v8-Object-Detection-Tutorial-on-CPU-GPU",
            "project-auv.svg": "Line-Tracking-and-Anomaly-Detection",
        }
        for filename, name in mapping.items():
            self.assertIn(name, self.svgs[filename])

    def test_activity_card_uses_recent_work(self):
        svg = self.svgs["activity-timeline.svg"]
        self.assertIn("ACTIVITY TIMELINE", svg)
        self.assertIn("ARTPS", svg)


class WriteGuardTests(unittest.TestCase):
    def test_invalid_svg_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            keep = out / "technical-profile.svg"
            keep.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
            written = gp.write_if_valid(out, {"technical-profile.svg": "<not-xml"})
            self.assertEqual(written, [])
            self.assertEqual(keep.read_text(encoding="utf-8"), "<svg xmlns='http://www.w3.org/2000/svg'/>")


class ReadmeInteractionTests(unittest.TestCase):
    def setUp(self):
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_readme_wraps_visible_cards_in_links(self):
        for src in (
            "assets/hero.svg",
            "assets/generated/technical-profile.svg",
            "assets/generated/language-distribution.svg",
            "assets/generated/activity-timeline.svg",
            "assets/generated/project-artps.svg",
            "assets/generated/project-pyfoldable.svg",
            "assets/generated/project-yolov8.svg",
            "assets/generated/project-auv.svg",
            "assets/contact-github.svg",
            "assets/contact-linkedin.svg",
        ):
            pattern = rf'<a href="[^"]+">\s*<img src="{re.escape(src)}"'
            self.assertRegex(self.readme, pattern, src)

    def test_readme_uses_linkedin_url(self):
        self.assertIn("https://www.linkedin.com/in/poyrazbaydemir/", self.readme)

    def test_readme_drops_combined_project_and_telemetry_svgs(self):
        self.assertNotIn("projects.svg", self.readme)
        self.assertNotIn("telemetry.svg", self.readme)
        self.assertNotIn("activity.svg", self.readme)


if __name__ == "__main__":
    unittest.main()
