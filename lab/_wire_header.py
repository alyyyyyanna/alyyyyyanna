"""Point the profile builder at the split header, then draw it once."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "lab"
sys.path.insert(0, str(LAB))

profile_path = ROOT / "content" / "profile.json"
profile = json.loads(profile_path.read_text(encoding="utf-8"))
profile.pop("icon_labels", None)
profile["links"] = [
    {"name": "Facebook", "label": "[link]", "url": "https://facebook.com/your-account"},
    {"name": "GitHub", "label": "[link]", "url": "https://github.com/alyyyyyanna"},
    {"name": "LinkedIn", "label": "[link]", "url": "https://www.linkedin.com/in/your-account"},
]
profile_path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")

source_path = LAB / "build_profile.py"
source = source_path.read_text(encoding="utf-8")

replacements = [
    (
        '    save(ROOT / "assets" / "profile" / "header.svg", build_header(profile, script, italic, serif))\n',
        "    from header_layout import write_header\n"
        "    write_header(profile, script, italic, serif)\n",
    ),
    (
        "def write_readme(projects: list[dict], quote: str, stats: dict) -> None:\n",
        "def write_readme(profile: dict, projects: list[dict], quote: str, stats: dict) -> None:\n",
    ),
    (
        "name, scroll text, welcome line, and the four [link] labels under the portrait: content/profile.json\n",
        "name and the lines under the name: content/profile.json\n"
        "  name and bio. They are drawn into assets/profile/header-words.svg only.\n"
        "account links under the portrait: content/profile.json, the links list\n"
        "  label is the words beside the icon. url is where a click goes.\n"
        "  Type the account there. The icon files in assets/profile/icons stay as they are.\n"
        "  Facebook, GitHub, and LinkedIn are separate pictures, so a click opens url\n"
        "  instead of opening the picture file.\n",
    ),
    (
        """<p align="center">
  <img src="assets/profile/header.svg" alt="Alyanna Marie Minoza" width="100%">
</p>
""",
        "{header_block(profile)}\n",
    ),
    (
        "def write_preview(projects: list[dict]) -> None:\n",
        "def write_preview(profile: dict, projects: list[dict]) -> None:\n",
    ),
    (
        "    img {{ display: block; width: 100%; height: auto; }}\n"
        "    .gap {{ height: 48px; }}\n",
        "    img[width=\"100%\"] {{ display: block; width: 100%; height: auto; }}\n"
        "    img[height=\"32\"] {{ display: inline-block; width: auto; height: 32px; vertical-align: middle; }}\n"
        "    a {{ color: #f7f1e6; text-decoration: none; }}\n"
        "    .gap {{ height: 36px; }}\n",
    ),
    (
        '    <img src="assets/profile/header.svg" alt="">\n    <div class="gap"></div>\n',
        "    {header_block(profile)}\n    <div class=\"gap\"></div>\n",
    ),
    (
        '    <img src="assets/profile/tagline.svg" alt="">\n'
        '    <img src="assets/profile/stack-field.svg" alt="">\n'
        '    <img src="assets/profile/projects-label.svg" alt="">\n',
        '    <img src="assets/profile/tagline.svg" alt="" width="100%">\n'
        '    <img src="assets/profile/stack-field.svg" alt="" width="100%">\n'
        '    <img src="assets/profile/projects-label.svg" alt="" width="100%">\n',
    ),
    (
        '        f\'    <img src="assets/profile/cards/{project["id"]}.svg" alt="">\' for project in projects\n',
        '        f\'    <img src="assets/profile/cards/{project["id"]}.svg" alt="" width="100%">\' for project in projects\n',
    ),
    (
        '        <td width="58%"><img src="assets/profile/activity.svg" alt=""></td>\n'
        '        <td width="42%"><img src="assets/profile/quote.svg" alt=""></td>\n',
        '        <td width="58%"><img src="assets/profile/activity.svg" alt="" width="100%"></td>\n'
        '        <td width="42%"><img src="assets/profile/quote.svg" alt="" width="100%"></td>\n',
    ),
    (
        "    write_readme(projects, quote, stats)\n    write_preview(projects)\n",
        "    from header_layout import header_block\n"
        "    write_readme(profile, projects, quote, stats)\n"
        "    write_preview(profile, projects)\n",
    ),
    (
        "    projects = load_json(ROOT / \"content\" / \"projects.json\")\n"
        "    write_readme(projects, quote, stats)\n",
        "    from header_layout import header_block, write_link_labels\n"
        "    profile = load_json(ROOT / \"content\" / \"profile.json\")\n"
        "    projects = load_json(ROOT / \"content\" / \"projects.json\")\n"
        "    write_link_labels(profile, serif)\n"
        "    write_readme(profile, projects, quote, stats)\n",
    ),
]

for old, new in replacements:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"expected 1 match, found {count} for:\n{old[:180]}")
    source = source.replace(old, new, 1)

# header_block is used inside write_readme's f-string. Import it in that function too.
needle = "def write_readme(profile: dict, projects: list[dict], quote: str, stats: dict) -> None:\n"
insert = needle + "    from header_layout import header_block\n"
if needle not in source:
    raise SystemExit("write_readme signature missing")
source = source.replace(needle, insert, 1)
preview_needle = "def write_preview(profile: dict, projects: list[dict]) -> None:\n"
source = source.replace(preview_needle, preview_needle + "    from header_layout import header_block\n", 1)
source_path.write_text(source, encoding="utf-8")
print("wired build_profile.py")

import build_profile as profile_builder
from header_layout import write_header

script, serif, italic = profile_builder.load_fonts()
profile = profile_builder.load_json(profile_path)
projects = profile_builder.load_json(ROOT / "content" / "projects.json")
stats = {
    "github_contributions": 81,
    "github_streak": 0,
    "leetcode_solved": None,
    "counting_number": 1016,
    "duolingo_username": "",
    "duolingo_streak": None,
}
write_header(profile, script, italic, serif)
quote = profile_builder.quote_for()
profile_builder.write_readme(profile, projects, quote, stats)
profile_builder.write_preview(profile, projects)
print("drew header")
