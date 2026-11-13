"""The top of the page: a night-sky portrait, the name beside it, and separate account icons.

Name, bio, and the words beside each icon come from content/profile.json.
The icon pictures themselves do not contain the account.
"""

from __future__ import annotations

import math
import re

import build_profile as b

CREAM = b.CREAM
GOLD = b.GOLD
PURPLE = b.PURPLE
PINK = b.PINK
STAR = b.STAR


def portrait_frame(cx: float, cy: float, rx: float, ry: float) -> str:
    diamonds = []
    for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
        fx = cx + (rx + 11) * math.cos(angle)
        fy = cy + (ry + 11) * math.sin(angle)
        diamonds.append(
            f'<g transform="translate({fx:.1f},{fy:.1f}) scale(0.62)" fill="{GOLD}">'
            f'<path d="M0 -6.5 L4.6 0 L0 6.5 L-4.6 0 Z"/></g>'
        )
    return f'''
    <ellipse cx="{cx}" cy="{cy}" rx="{rx + 18}" ry="{ry + 18}" fill="none" stroke="{PURPLE}" stroke-width="1.15"
      stroke-dasharray="1.5 7" opacity="0.8">
      <animate attributeName="stroke-dashoffset" from="0" to="-40" dur="9s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse id="orbit" cx="{cx}" cy="{cy}" rx="{rx + 18}" ry="{ry + 18}" fill="none"/>
    <circle r="2.2" fill="#fff6d8">
      <animateMotion dur="18s" repeatCount="indefinite">
        <mpath href="#orbit"/>
      </animateMotion>
    </circle>
    <ellipse cx="{cx}" cy="{cy}" rx="{rx + 4}" ry="{ry + 4}" fill="none" stroke="{PURPLE}" stroke-width="1.25" opacity="0.9"/>
    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{GOLD}" stroke-width="1.7">
      <animate attributeName="stroke-opacity" values="0.65;1;0.65" dur="6s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="{cx}" cy="{cy}" rx="{rx - 7}" ry="{ry - 8}" fill="none" stroke="{CREAM}" stroke-width="0.7" opacity="0.45"/>
    {''.join(diamonds)}
    '''


def panel(width: float, height: float, body: str, title: str, desc: str, fade_left: bool, fade_right: bool) -> str:
    left = "#000" if fade_left else "#fff"
    right = "#000" if fade_right else "#fff"
    side = 0.08
    vert = 0.05
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="assetTitle assetDesc">
<title id="assetTitle">{b.xml(title)}</title>
<desc id="assetDesc">{b.xml(desc)}</desc>
<defs>
  <linearGradient id="fadeX" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{left}"/>
    <stop offset="{side}" stop-color="#fff"/>
    <stop offset="{1 - side}" stop-color="#fff"/>
    <stop offset="1" stop-color="{right}"/>
  </linearGradient>
  <linearGradient id="fadeY" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000"/>
    <stop offset="{vert}" stop-color="#fff"/>
    <stop offset="{1 - vert}" stop-color="#fff"/>
    <stop offset="1" stop-color="#000"/>
  </linearGradient>
  <mask id="fadeMX" maskUnits="userSpaceOnUse" x="0" y="0" width="{width}" height="{height}">
    <rect width="{width}" height="{height}" fill="url(#fadeX)"/>
  </mask>
  <mask id="edgeFade" maskUnits="userSpaceOnUse" x="0" y="0" width="{width}" height="{height}">
    <rect width="{width}" height="{height}" fill="url(#fadeY)" mask="url(#fadeMX)"/>
  </mask>
</defs>
<g mask="url(#edgeFade)">
{body}
</g>
</svg>
'''


def sky(width: float, height: float, glow_x: float, blob_x: float, blob_y: float, blob_fill: str) -> str:
    return f'''
    <rect width="{width}" height="{height}" fill="#090712"/>
    <radialGradient id="glow" gradientUnits="userSpaceOnUse" cx="{glow_x}" cy="{height * 0.28:.1f}" r="{max(width, height) * 0.95:.1f}">
      <stop offset="0%" stop-color="#2a2144"/>
      <stop offset="48%" stop-color="#141024"/>
      <stop offset="100%" stop-color="#090712"/>
    </radialGradient>
    <rect width="{width}" height="{height}" fill="url(#glow)"/>
    <ellipse cx="{blob_x}" cy="{blob_y}" rx="168" ry="72" fill="{blob_fill}" opacity="0.16"/>
    '''


def drifting_stars(width: float, height: float, count: int, seed: int) -> str:
    return f'''
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0; 8 -12; 0 0" dur="14s" repeatCount="indefinite"/>
      {b.star_field(width, height, count, seed, margin=28)}
    </g>'''


def build_portrait_panel() -> str:
    width, height = 340, 300
    cx, cy, rx, ry = 176, 156, 68, 84
    portrait = b.ROOT / "assets" / "portrait.png"
    photo = ""
    if portrait.exists():
        photo = f'''
        <clipPath id="portraitClip">
          <ellipse cx="{cx}" cy="{cy}" rx="{rx - 12}" ry="{ry - 14}"/>
        </clipPath>
        <image href="{b.data_uri(portrait)}" x="{cx - rx + 6}" y="{cy - ry + 4}" width="{(rx - 6) * 2}" height="{(ry - 4) * 2}"
          preserveAspectRatio="xMidYMid slice" clip-path="url(#portraitClip)"/>
        '''
    body = f'''
    {sky(width, height, 460, 150, 108, PURPLE)}
    {b.star_field(width, height, 16, 21, margin=18)}
    {drifting_stars(width, height, 5, 30)}
    <ellipse cx="{cx}" cy="{cy}" rx="{rx + 26}" ry="{ry + 28}" fill="{PURPLE}" opacity="0.14"/>
    {photo}
    {portrait_frame(cx, cy, rx, ry)}
    '''
    return panel(width, height, body, "Portrait", "The portrait at the top of the page.", True, False)


def build_words_panel(profile: dict, script: b.Font, italic: b.Font) -> str:
    width, height = 580, 426
    name = profile["name"]
    name_size = 52
    while script.measure(name, name_size, tracking=-0.6) > 500 and name_size > 32:
        name_size -= 1
    bio_size = 16.0
    bio_lines = b.wrap(italic, profile["bio"], bio_size, 500)
    while len(bio_lines) > 7 and bio_size > 13:
        bio_size -= 0.4
        bio_lines = b.wrap(italic, profile["bio"], bio_size, 500)
    name_x, name_y = width / 2, 86
    name_width = script.measure(name, name_size, tracking=-0.6)
    leading = bio_size + 6.5
    rule_y = name_y + 24
    bio_y = rule_y + 36
    twinkles = []
    for sx, sy, scale, begin in (
        (name_x - name_width / 2 - 16, name_y - 28, 0.42, 0.2),
        (name_x + name_width / 2 + 14, name_y - 22, 0.5, 1.1),
        (name_x - 20, name_y - 48, 0.32, 1.7),
    ):
        twinkles.append(
            f'<g transform="translate({sx:.1f},{sy:.1f}) scale({scale})">'
            f'<g>'
            f'<animate attributeName="opacity" values="0.25;1;0.25" dur="3.2s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<path d="{STAR}" fill="{GOLD}"/>'
            f"</g></g>"
        )
    body = f'''
    {sky(width, height, 120, 400, 300, PINK)}
    {b.star_field(width, height, 14, 8, margin=20)}
    {drifting_stars(width, height, 5, 14)}
    {''.join(twinkles)}
    {script.draw(name, name_x, name_y, name_size, CREAM, "middle", tracking=-0.6)[0]}
    {b.gold_rule(70, width - 70, rule_y)}
    {b.draw_lines(italic, bio_lines, name_x, bio_y, bio_size, "#d9c6d0", leading, "middle")}
    '''
    return panel(
        width,
        height,
        body,
        name,
        "The name and the lines under it. Edit them in content/profile.json.",
        False,
        True,
    )


def icon_badge(path: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img">
  <circle cx="32" cy="32" r="30" fill="#1a1230" stroke="{GOLD}" stroke-width="1.5"/>
  <circle cx="32" cy="32" r="26.5" fill="none" stroke="{PURPLE}" stroke-width="1.1">
    <animate attributeName="stroke-opacity" values="0.3;0.95;0.3" dur="4.8s" repeatCount="indefinite"/>
  </circle>
  <g transform="translate(17,17) scale(1.25)" fill="{CREAM}">
    <path d="{path}"/>
  </g>
</svg>
'''


FACEBOOK_MARK = (
    "M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125"
    " 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235"
    " 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385"
    "C19.612 23.027 24 18.062 24 12.073z"
)
LINKEDIN_MARK = (
    "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136"
    " 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37"
    " 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063"
    " 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542"
    "C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0"
    " 22.222 0h.003z"
)


def write_social_icons() -> None:
    folder = b.ROOT / "assets" / "profile" / "icons"
    marks = {
        "facebook": FACEBOOK_MARK,
        "github": b.GITHUB_MARK,
        "linkedin": LINKEDIN_MARK,
    }
    for name, path in marks.items():
        b.save(folder / f"{name}.svg", icon_badge(path))


def link_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def social_links(profile: dict) -> list[dict]:
    found = profile.get("links")
    if found:
        return list(found)
    return [
        {"name": "Facebook", "label": "[link]", "url": "https://facebook.com/your-account"},
        {"name": "GitHub", "label": "[link]", "url": "https://github.com/alyyyyyanna"},
        {"name": "LinkedIn", "label": "[link]", "url": "https://www.linkedin.com/in/your-account"},
    ]


def label_svg(serif: b.Font, label: str) -> str:
    size = 18
    text_width = serif.measure(label, size, tracking=0.2)
    width = text_width + 22
    height = 32
    text = serif.draw(label, 11, 22.5, size, CREAM, tracking=0.2)[0]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height}" viewBox="0 0 {width:.2f} {height}" role="img">
  <rect width="{width:.2f}" height="{height}" rx="16" fill="#141024"/>
  {text}
</svg>
'''


def write_link_labels(profile: dict, serif: b.Font) -> None:
    folder = b.ROOT / "assets" / "profile" / "icons"
    for item in social_links(profile):
        label = item.get("label") or "[link]"
        b.save(folder / f"{link_slug(item['name'])}-label.svg", label_svg(serif, label))


def link_rows(profile: dict) -> str:
    rows = []
    for item in social_links(profile):
        slug = link_slug(item["name"])
        url = (item.get("url") or "").strip() or "https://example.com/your-account"
        label = item.get("label") or "[link]"
        rows.append(
            f'<a href="{b.xml(url)}"><img src="assets/profile/icons/{slug}.svg" width="32" height="32" alt="{b.xml(item["name"])}">'
            f'&nbsp;<img src="assets/profile/icons/{slug}-label.svg" height="32" alt="{b.xml(label)}"></a>'
        )
    return "<br>\n".join(rows)


def header_block(profile: dict) -> str:
    words = f'{profile.get("name", "")}. {profile.get("bio", "")}'
    return f'''<table cellspacing="0" cellpadding="0">
<tr>
<td width="37%" align="center" valign="top">
<img src="assets/profile/header-portrait.svg" alt="" width="100%">
{link_rows(profile)}
</td>
<td width="63%" valign="top">
<img src="assets/profile/header-words.svg" alt="{b.xml(words)}" width="100%">
</td>
</tr>
</table>'''


def write_header(profile: dict, script: b.Font, italic: b.Font, serif: b.Font) -> None:
    b.save(b.ROOT / "assets" / "profile" / "header-portrait.svg", build_portrait_panel())
    b.save(b.ROOT / "assets" / "profile" / "header-words.svg", build_words_panel(profile, script, italic))
    write_social_icons()
    write_link_labels(profile, serif)
    old_header = b.ROOT / "assets" / "profile" / "header.svg"
    if old_header.exists():
        old_header.unlink()
        print("removed header.svg")
