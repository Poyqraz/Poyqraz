"""Checks for the profile SVG generator. Run: python tests/test_generate_profile.py"""

from __future__ import annotations

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
        self.svgs = {
            "telemetry.svg": gp.render_telemetry(self.profile),
            "projects.svg": gp.render_projects(self.profile),
            "activity.svg": gp.render_activity(self.profile),
        }

    def test_svgs_are_valid_xml(self):
        for name, svg in self.svgs.items():
            root = ET.fromstring(svg)
            self.assertTrue(root.tag.endswith("svg"), name)

    def test_svgs_omit_star_and_follower_copy(self):
        blob = "\n".join(self.svgs.values()).lower()
        for banned in ("star", "follower"):
            self.assertNotIn(banned, blob)

    def test_projects_svg_lists_all_four_names(self):
        svg = self.svgs["projects.svg"]
        for name in (
            "ARTPS",
            "PyFoldable",
            "YOLO-v8-Object-Detection-Tutorial-on-CPU-GPU",
            "Line-Tracking-and-Anomaly-Detection",
        ):
            self.assertIn(name, svg)

    def test_activity_svg_uses_recent_pulses_only(self):
        svg = self.svgs["activity.svg"]
        self.assertIn("SIGHTLINE PULSES", svg)
        self.assertIn("ARTPS", svg)


class WriteGuardTests(unittest.TestCase):
    def test_invalid_svg_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            keep = out / "telemetry.svg"
            keep.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
            written = gp.write_if_valid(out, {"telemetry.svg": "<not-xml"})
            self.assertEqual(written, [])
            self.assertEqual(keep.read_text(encoding="utf-8"), "<svg xmlns='http://www.w3.org/2000/svg'/>")


if __name__ == "__main__":
    unittest.main()
