"""One-shot builder for the static hero SVG. Run: python scripts/build_hero.py"""

from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AVATAR = ROOT / "assets" / "avatar.jpg"
OUT = ROOT / "assets" / "hero.svg"
CONTACTS = ROOT / "assets"


def rail() -> str:
    ticks = []
    for i in range(50):
        x = 24 + i * 16
        y = 242 if i % 4 == 0 else 244
        h = 8 if i % 4 == 0 else 4
        ticks.append(f'<rect x="{x}" y="{y}" width="1" height="{h}"/>')
    return "".join(ticks)


def write_contact_cards() -> None:
    github = """<svg xmlns="http://www.w3.org/2000/svg" width="416" height="72" viewBox="0 0 416 72" role="img" aria-label="GitHub">
  <rect width="416" height="72" fill="#0c1014"/>
  <rect x="8" y="8" width="400" height="56" fill="#141b21" stroke="#24303a"/>
  <path d="M16 16 H34 M16 16 V34" stroke="#5ce1e6" fill="none" stroke-width="1.6"/>
  <text x="28" y="42" fill="#5ce1e6" font-size="12" letter-spacing="2.4" font-family="ui-monospace, Consolas, monospace">GITHUB</text>
  <text x="140" y="42" fill="#d8e0e6" font-size="14" font-family="ui-monospace, Consolas, monospace">github.com/Poyqraz</text>
</svg>
"""
    linkedin = """<svg xmlns="http://www.w3.org/2000/svg" width="416" height="72" viewBox="0 0 416 72" role="img" aria-label="LinkedIn">
  <rect width="416" height="72" fill="#0c1014"/>
  <rect x="8" y="8" width="400" height="56" fill="#141b21" stroke="#24303a"/>
  <path d="M16 16 H34 M16 16 V34" stroke="#e8a23a" fill="none" stroke-width="1.6"/>
  <text x="28" y="42" fill="#e8a23a" font-size="12" letter-spacing="2.4" font-family="ui-monospace, Consolas, monospace">LINKEDIN</text>
  <text x="150" y="42" fill="#d8e0e6" font-size="14" font-family="ui-monospace, Consolas, monospace">poyrazbaydemir</text>
</svg>
"""
    (CONTACTS / "contact-github.svg").write_text(github, encoding="utf-8")
    (CONTACTS / "contact-linkedin.svg").write_text(linkedin, encoding="utf-8")


def main() -> None:
    img = base64.b64encode(AVATAR.read_bytes()).decode()
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="848" height="268" viewBox="0 0 848 268" role="img" aria-label="Poyraz Baydemir engineering systems profile">
  <defs>
    <clipPath id="iris"><circle cx="134" cy="118" r="78"/></clipPath>
    <filter id="cyanotype" color-interpolation-filters="sRGB">
      <feColorMatrix type="matrix" values="0.18 0.28 0.22 0 0.02  0.22 0.48 0.28 0 0.12  0.28 0.42 0.55 0 0.18  0 0 0 1 0"/>
    </filter>
    <pattern id="mesh" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M24 0 H0 V24" fill="none" stroke="#5ce1e6" stroke-width="0.4" opacity="0.12"/>
    </pattern>
  </defs>
  <rect width="848" height="268" fill="#0c1014"/>
  <rect width="848" height="268" fill="url(#mesh)"/>
  <rect x="16" y="16" width="236" height="216" fill="#141b21" stroke="#5ce1e6" stroke-width="1.2"/>
  <path d="M28 28 H56 M28 28 V56 M240 28 H212 M240 28 V56 M28 220 H56 M28 220 V192 M240 220 H212 M240 220 V192" fill="none" stroke="#5ce1e6" stroke-width="2.2"/>
  <circle cx="134" cy="118" r="92" fill="none" stroke="#5ce1e6" opacity="0.35"/>
  <circle cx="134" cy="118" r="84" fill="none" stroke="#e8a23a" opacity="0.55" stroke-dasharray="2 6"/>
  <line x1="134" y1="28" x2="134" y2="40" stroke="#5ce1e6"/>
  <line x1="134" y1="196" x2="134" y2="208" stroke="#5ce1e6"/>
  <line x1="44" y1="118" x2="56" y2="118" stroke="#5ce1e6"/>
  <line x1="212" y1="118" x2="224" y2="118" stroke="#5ce1e6"/>
  <image href="data:image/jpeg;base64,{img}" x="56" y="40" width="156" height="156" clip-path="url(#iris)" filter="url(#cyanotype)" preserveAspectRatio="xMidYMid slice"/>
  <circle cx="134" cy="118" r="78" fill="none" stroke="#5ce1e6" stroke-width="1.4"/>
  <text x="134" y="216" text-anchor="middle" fill="#5ce1e6" font-size="11" letter-spacing="3.2" font-family="ui-monospace, Consolas, monospace">VISION SYSTEMS</text>
  <text x="272" y="42" fill="#e8a23a" font-size="11" letter-spacing="2.2" font-family="ui-monospace, Consolas, monospace">ENGINEERING SYSTEMS PROFILE</text>
  <text x="272" y="84" fill="#d8e0e6" font-size="28" letter-spacing="2" font-family="ui-monospace, Consolas, monospace">POYRAZ BAYDEMİR</text>
  <text x="272" y="112" fill="#8a97a3" font-size="13" font-family="ui-monospace, Consolas, monospace">A Mechanical Engineer Who Enjoys Artificial Intelligence</text>
  <circle cx="286" cy="158" r="8" fill="none" stroke="#e8a23a" stroke-width="1.6"/>
  <circle cx="286" cy="158" r="3" fill="#e8a23a"/>
  <line x1="294" y1="158" x2="368" y2="158" stroke="#e8a23a"/>
  <circle cx="376" cy="158" r="8" fill="none" stroke="#5ce1e6" stroke-width="1.6"/>
  <circle cx="376" cy="158" r="3" fill="#5ce1e6"/>
  <line x1="384" y1="158" x2="458" y2="158" stroke="#5ce1e6"/>
  <circle cx="466" cy="158" r="8" fill="none" stroke="#6ee07a" stroke-width="1.6"/>
  <circle cx="466" cy="158" r="3" fill="#6ee07a"/>
  <text x="286" y="186" text-anchor="middle" fill="#e8a23a" font-size="10" letter-spacing="1.5" font-family="ui-monospace, Consolas, monospace">MECHANISM</text>
  <text x="376" y="186" text-anchor="middle" fill="#5ce1e6" font-size="10" letter-spacing="1.5" font-family="ui-monospace, Consolas, monospace">PERCEPTION</text>
  <text x="466" y="186" text-anchor="middle" fill="#6ee07a" font-size="10" letter-spacing="1.5" font-family="ui-monospace, Consolas, monospace">DECISION</text>
  <text x="560" y="154" fill="#8a97a3" font-size="12" font-family="ui-monospace, Consolas, monospace">Selcuk University</text>
  <text x="560" y="176" fill="#8a97a3" font-size="12" font-family="ui-monospace, Consolas, monospace">Ordu / Konya</text>
  <text x="560" y="198" fill="#5ce1e6" font-size="11" font-family="ui-monospace, Consolas, monospace">MECHANICS · PERCEPTION · AUTONOMY</text>
  <rect x="16" y="240" width="816" height="16" fill="#141b21"/>
  <g fill="#5ce1e6" opacity="0.7">{rail()}</g>
  <text x="690" y="252" fill="#e8a23a" font-size="9" letter-spacing="2" font-family="ui-monospace, Consolas, monospace">SYSTEMS PROFILE</text>
  <rect x="272" y="24" width="120" height="2" fill="#5ce1e6">
    <animate attributeName="x" values="272;700;272" dur="9s" repeatCount="indefinite"/>
  </rect>
</svg>
"""
    OUT.write_text(svg, encoding="utf-8")
    write_contact_cards()
    print(OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
