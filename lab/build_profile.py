"""Build the profile pictures from the files in content/.

Edit those files, then run this script again.
The daily workflow only refreshes the quote and the activity numbers.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import random
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets" / "fonts"
TZ = timezone(timedelta(hours=8))

CREAM = "#f7f1e6"
PINK = "#e7b4c4"
GOLD = "#e6c36a"
GOLD_DEEP = "#c4a15a"
PURPLE = "#7d6bb8"
INK = "#2c211c"
INK_SOFT = "#4a382e"
CARD = "#1a1230"
CARD_BAR = "#261848"
MUTED = "#c9bfd2"
DIM = "#8f86a0"
YELLOW = "#f6c431"
# GitHub's contribution levels, empty box first.
CONTRIBUTION_LEVELS = ("#2a2344", "#0e4429", "#006d32", "#26a641", "#39d353")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

STAR = (
    "M0 -10 L2.35 -3.09 L9.51 -3.09 L3.63 1.18 L5.88 8.09 "
    "L0 3.82 L-5.88 8.09 L-3.63 1.18 L-9.51 -3.09 L-2.35 -3.09 Z"
)
# Marks from Simple Icons (ISC), drawn small and in the page colors.
GITHUB_MARK = (
    "M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577"
    " 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756"
    "-1.333-1.756-1.09-.745.083-.73.083-.73 1.205.085 1.84 1.237 1.84 1.237 1.07 1.834"
    " 2.807 1.304 3.492.997.108-.775.418-1.305.762-1.605-2.665-.3-5.466-1.332-5.466-5.93"
    " 0-1.31.468-2.38 1.236-3.22-.124-.303-.536-1.524.117-3.176 0 0 1.008-.322 3.3 1.23"
    ".957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.29-1.552 3.297-1.23"
    " 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.91 1.235 3.22 0 4.61-2.807"
    " 5.625-5.48 5.92.43.372.823 1.102.823 2.222 0 1.606-.015 2.896-.015 3.286 0 .322.216"
    ".694.825.576C20.565 21.796 24 17.3 24 12c0-6.63-5.37-12-12-12z"
)
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


def xml(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


class Font:
    def __init__(self, path: Path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upem = self.font["head"].unitsPerEm

    def _glyph(self, char: str):
        name = self.cmap.get(ord(char))
        if name is None:
            return "", self.upem * 0.33
        pen = SVGPathPen(self.glyphs)
        self.glyphs[name].draw(pen)
        return pen.getCommands(), self.glyphs[name].width

    def measure(self, text: str, size: float, tracking: float = 0) -> float:
        scale = size / self.upem
        width = 0.0
        for index, char in enumerate(text):
            _, advance = self._glyph(char)
            width += advance * scale
            if index != len(text) - 1:
                width += tracking
        return width

    def draw(
        self,
        text: str,
        x: float,
        y: float,
        size: float,
        fill: str,
        anchor: str = "start",
        tracking: float = 0,
        opacity: float = 1,
    ) -> tuple[str, float]:
        width = self.measure(text, size, tracking)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        scale = size / self.upem
        parts = []
        cursor = x
        for index, char in enumerate(text):
            commands, advance = self._glyph(char)
            if commands:
                parts.append(
                    f'<g transform="translate({cursor:.2f},{y:.2f}) scale({scale:.5f},{-scale:.5f})">'
                    f'<path d="{commands}" fill="{fill}"/></g>'
                )
            cursor += advance * scale
            if index != len(text) - 1:
                cursor += tracking
        alpha = "" if opacity == 1 else f' opacity="{opacity}"'
        return f"<g{alpha}>{''.join(parts)}</g>", width

    def line_rise(self, text: str, size: float) -> float:
        """Pixels from the baseline up to the middle of the short letters."""
        scale = size / self.upem
        glyf = self.font["glyf"]
        mids = []
        for char in text:
            name = self.cmap.get(ord(char))
            if not name:
                continue
            glyph = glyf[name]
            if glyph.numberOfContours == 0 or glyph.yMax >= self.upem * 0.5:
                continue
            mids.append((glyph.yMin + glyph.yMax) / 2 * scale)
        if not mids:
            return size * 0.3
        return sum(mids) / len(mids)


def wrap(font: Font, text: str, size: float, max_width: float, tracking: float = 0) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if font.measure(trial, size, tracking) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(
    font: Font,
    lines: list[str],
    x: float,
    y: float,
    size: float,
    fill: str,
    leading: float,
    anchor: str = "start",
    tracking: float = 0,
) -> str:
    return "\n".join(
        font.draw(line, x, y + index * leading, size, fill, anchor, tracking)[0]
        for index, line in enumerate(lines)
    )


def save(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def document(width: float, height: float, defs: str, body: str, title: str, desc: str, fade: bool = True, side: float = 0.075, vert: float = 0.045) -> str:
    fade_xml = ""
    mask = ""
    if fade:
        fade_xml = f'''
        <linearGradient id="fadeX" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#000"/>
          <stop offset="{side}" stop-color="#fff"/>
          <stop offset="{1 - side}" stop-color="#fff"/>
          <stop offset="1" stop-color="#000"/>
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
        </mask>'''
        mask = ' mask="url(#edgeFade)"'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="assetTitle assetDesc">
<title id="assetTitle">{xml(title)}</title>
<desc id="assetDesc">{xml(desc)}</desc>
<defs>{fade_xml}
{defs}
</defs>
<g{mask}>
{body}
</g>
</svg>
'''


def night(width: float, height: float) -> str:
    return f'''
    <radialGradient id="night" cx="50%" cy="28%" r="85%">
      <stop offset="0%" stop-color="#2a2144"/>
      <stop offset="48%" stop-color="#141024"/>
      <stop offset="100%" stop-color="#090712"/>
    </radialGradient>
    <rect width="{width}" height="{height}" fill="url(#night)"/>
    <ellipse cx="{width * 0.18}" cy="{height * 0.32}" rx="{width * 0.28}" ry="{height * 0.16}" fill="#7d6bb8" opacity="0.16"/>
    <ellipse cx="{width * 0.78}" cy="{height * 0.72}" rx="{width * 0.3}" ry="{height * 0.16}" fill="#e7b4c4" opacity="0.1"/>
    '''


def star_field(width: float, height: float, count: int, seed: int, margin: float = 24) -> str:
    rng = random.Random(seed)
    parts = []
    for _ in range(count):
        x = rng.uniform(margin, width - margin)
        y = rng.uniform(margin, height - margin)
        radius = rng.choice([0.7, 0.9, 1.15, 1.5, 2.1, 2.8])
        fill = rng.choice(["#fff6d8", "#fff6d8", "#f0d7a2", "#e7b4c4"])
        opacity = rng.uniform(0.28, 0.9)
        if radius > 1.8 and rng.random() < 0.7:
            duration = rng.choice([2.8, 3.6, 4.8, 5.6])
            begin = rng.uniform(0, 2.5)
            parts.append(
                f'<g transform="translate({x:.1f},{y:.1f}) scale({radius / 10:.3f})" fill="{fill}">'
                f'<animate attributeName="opacity" values="{opacity:.2f};1;{opacity:.2f}" dur="{duration}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
                f'<path d="{STAR}"/></g>'
            )
        else:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.2f}" fill="{fill}" opacity="{opacity:.2f}"/>')
    return "\n".join(parts)


def gold_rule(x1: float, x2: float, y: float) -> str:
    mid = (x1 + x2) / 2
    dots = []
    cursor = x1 + 14
    while cursor < mid - 34:
        dots.append(f'<circle cx="{cursor:.1f}" cy="{y}" r="1.25" fill="{GOLD}"/>')
        cursor += 18
    cursor = mid + 34
    while cursor < x2 - 10:
        dots.append(f'<circle cx="{cursor:.1f}" cy="{y}" r="1.25" fill="{GOLD}"/>')
        cursor += 18
    return f'''
    <line x1="{x1}" y1="{y}" x2="{mid - 26}" y2="{y}" stroke="{GOLD}" stroke-width="1.35"/>
    <line x1="{mid + 26}" y1="{y}" x2="{x2}" y2="{y}" stroke="{GOLD}" stroke-width="1.35"/>
    <g fill="{GOLD}" transform="translate({mid},{y})">
      <path d="M-16 0 L-11 -3.4 L-6 0 L-11 3.4 Z"/>
      <path d="M0 -6.5 L4.6 0 L0 6.5 L-4.6 0 Z"/>
      <path d="M16 0 L11 -3.4 L6 0 L11 3.4 Z"/>
    </g>
    {''.join(dots)}
    '''


def yellow_star(x: float, y: float, scale: float = 2.5) -> str:
    return (
        f'<g transform="translate({x},{y}) scale({scale})">'
        f'<g><animateTransform attributeName="transform" type="scale" values="1;1.08;1" dur="3.8s" repeatCount="indefinite"/>'
        f'<path d="{STAR}" fill="{YELLOW}" stroke="#c48a12" stroke-width="0.45" stroke-linejoin="round"/>'
        f"</g></g>"
    )


def data_uri(path: Path) -> str:
    raw = path.read_bytes()
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def inline_svg(path: Path, prefix: str, x: float, y: float, width: float, height: float) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<\?xml[^>]*\?>", "", text)
    match = re.search(r"<svg\b([^>]*)>(.*)</svg>\s*$", text, re.S)
    if not match:
        raise ValueError(f"Could not read {path}")
    attrs, inner = match.group(1), match.group(2)
    viewbox = re.search(r'viewBox="([^"]+)"', attrs)
    box = viewbox.group(1) if viewbox else f"0 0 {width} {height}"
    inner = re.sub(r'\bid="([^"]+)"', lambda item: f'id="{prefix}{item.group(1)}"', inner)
    inner = re.sub(r"url\(#([^)]+)\)", lambda item: f"url(#{prefix}{item.group(1)})", inner)
    inner = re.sub(r'href="#([^"]+)"', lambda item: f'href="#{prefix}{item.group(1)}"', inner)
    inner = re.sub(r'xlink:href="#([^"]+)"', lambda item: f'xlink:href="#{prefix}{item.group(1)}"', inner)
    return (
        f'<svg x="{x}" y="{y}" width="{width}" height="{height}" viewBox="{box}" overflow="visible">'
        f"{inner}</svg>"
    )


def load_fonts() -> tuple[Font, Font, Font]:
    return (
        Font(FONT_DIR / "GreatVibes.ttf"),
        Font(FONT_DIR / "Cormorant.ttf"),
        Font(FONT_DIR / "CormorantItalic.ttf"),
    )


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def shown_quote(line: str) -> str:
    """The words on the picture. Credits after an em dash are left off."""
    text = line.strip()
    for mark in (" — ", " – "):
        if mark in text:
            text = text.split(mark, 1)[0].rstrip()
    return text


def quotes() -> list[str]:
    lines = []
    for line in (ROOT / "content" / "quotes.txt").read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(shown_quote(stripped))
    return lines or ["quotes that change every day"]


def today() -> datetime:
    return datetime.now(TZ)


def quote_for(day: datetime | None = None) -> str:
    items = quotes()
    current = day or today()
    return items[current.date().toordinal() % len(items)]


def digits(value) -> str:
    number = int(value or 0)
    return f"{number:04d}" if number < 10000 else str(number)


def fetch_json(url: str, timeout: int = 20):
    request = urllib.request.Request(url, headers={"User-Agent": "alyyyyyanna-profile"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def refresh_stats(stats: dict, advance_counter: bool = True) -> dict:
    username = (stats.get("github_username") or "").strip()
    if username:
        try:
            payload = fetch_json(f"https://github-contributions-api.jogruber.de/v4/{username}")
            by_date = {item["date"]: item["count"] for item in payload.get("contributions", [])}
            current = today().date()
            year_total = payload.get("total", {}).get(str(current.year))
            if year_total is None:
                year_total = sum(count for day, count in by_date.items() if day <= current.isoformat())
            stats["github_contributions"] = year_total
            cursor = today().date()
            if by_date.get(cursor.isoformat(), 0) == 0:
                cursor -= timedelta(days=1)
            streak = 0
            while by_date.get(cursor.isoformat(), 0) > 0:
                streak += 1
                cursor -= timedelta(days=1)
            stats["github_streak"] = streak
            stats["github_calendar"] = [
                {
                    "date": item["date"],
                    "count": item.get("count", 0),
                    "level": item.get("level", 0),
                }
                for item in payload.get("contributions", [])
                if "date" in item
            ]
            print(f"github {username}: {stats['github_contributions']} this year, streak {streak}")
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as error:
            print(f"github stats stayed as they were ({error})")

    leetcode = (stats.get("leetcode_username") or "").strip()
    if leetcode:
        solved = None
        for url in (
            f"https://alfa-leetcode-api.onrender.com/{leetcode}/solved",
            f"https://leetcode-stats-api.herokuapp.com/{leetcode}",
        ):
            try:
                payload = fetch_json(url)
                solved = payload.get("solvedProblem") or payload.get("totalSolved")
                if solved is None and isinstance(payload.get("solved"), dict):
                    solved = payload["solved"].get("solvedProblem")
                easy = payload.get("easySolved")
                medium = payload.get("mediumSolved")
                hard = payload.get("hardSolved")
                if isinstance(payload.get("solved"), dict):
                    easy = easy or payload["solved"].get("easy")
                    medium = medium or payload["solved"].get("medium")
                    hard = hard or payload["solved"].get("hard")
                if solved is not None:
                    stats["leetcode_solved"] = solved
                    stats["leetcode_easy"] = easy or 0
                    stats["leetcode_medium"] = medium or 0
                    stats["leetcode_hard"] = hard or 0
                    print(f"leetcode {leetcode}: {solved}")
                    break
            except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as error:
                print(f"leetcode lookup missed {url} ({error})")
        if solved is None:
            print("leetcode number left unchanged")

    duolingo = (stats.get("duolingo_username") or "").strip()
    if duolingo:
        try:
            request = urllib.request.Request(
                f"https://www.duolingo.com/2017-06-30/users?username={duolingo}",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            user = payload["users"][0]
            stats["duolingo_streak"] = user.get("streak", 0)
            print(f"duolingo {duolingo}: streak {stats['duolingo_streak']}")
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as error:
            print(f"duolingo stayed on the counting number ({error})")
            stats["duolingo_streak"] = None

    if advance_counter and not duolingo:
        current = today().date()
        last = datetime.fromisoformat(stats.get("counting_number_as_of") or current.isoformat()).date()
        elapsed = (current - last).days
        if elapsed > 0:
            stats["counting_number"] = int(stats.get("counting_number") or 0) + elapsed
            stats["counting_number_as_of"] = current.isoformat()
            print(f"counting number is now {stats['counting_number']}")
    return stats


def portrait_frame(cx: float, cy: float, rx: float, ry: float) -> str:
    """A thin gold ring and the same diamond used on the rules below."""
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
    """One half of the header. The shared edge stays solid so the two halves read as one sky."""
    left = "#000" if fade_left else "#fff"
    right = "#000" if fade_right else "#fff"
    side = 0.08
    vert = 0.05
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="assetTitle assetDesc">
<title id="assetTitle">{xml(title)}</title>
<desc id="assetDesc">{xml(desc)}</desc>
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


def sky(width: float, height: float, glow_x: float) -> str:
    return f'''
    <rect width="{width}" height="{height}" fill="#090712"/>
    <radialGradient id="glow" gradientUnits="userSpaceOnUse" cx="{glow_x}" cy="{height * 0.28:.1f}" r="{max(width, height) * 0.95:.1f}">
      <stop offset="0%" stop-color="#2a2144"/>
      <stop offset="48%" stop-color="#141024"/>
      <stop offset="100%" stop-color="#090712"/>
    </radialGradient>
    <rect width="{width}" height="{height}" fill="url(#glow)"/>
    '''


def drifting_stars(width: float, height: float, count: int, seed: int) -> str:
    return f'''
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0; 8 -12; 0 0" dur="14s" repeatCount="indefinite"/>
      {star_field(width, height, count, seed, margin=28)}
    </g>'''


def build_portrait_panel() -> str:
    width, height = 340, 300
    cx, cy, rx, ry = 176, 156, 68, 84
    portrait = ROOT / "assets" / "portrait.png"
    photo = ""
    if portrait.exists():
        photo = f'''
        <clipPath id="portraitClip">
          <ellipse cx="{cx}" cy="{cy}" rx="{rx - 12}" ry="{ry - 14}"/>
        </clipPath>
        <image href="{data_uri(portrait)}" x="{cx - rx + 6}" y="{cy - ry + 4}" width="{(rx - 6) * 2}" height="{(ry - 4) * 2}"
          preserveAspectRatio="xMidYMid slice" clip-path="url(#portraitClip)"/>
        '''
    body = f'''
    {sky(width, height, 460)}
    {star_field(width, height, 16, 21, margin=18)}
    {drifting_stars(width, height, 5, 30)}
    <ellipse cx="{cx}" cy="{cy}" rx="{rx + 36}" ry="{ry + 40}" fill="{PURPLE}" opacity="0.12"/>
    {photo}
    {portrait_frame(cx, cy, rx, ry)}
    '''
    return panel(width, height, body, "Portrait", "The portrait at the top of the page.", True, False)


def build_words_panel(profile: dict, script: Font, italic: Font) -> str:
    width, height = 580, 426
    name = profile["name"]
    name_size = 52
    while script.measure(name, name_size, tracking=-0.6) > 500 and name_size > 32:
        name_size -= 1
    bio_size = 16
    bio_lines = wrap(italic, profile["bio"], bio_size, 500)
    while len(bio_lines) > 7 and bio_size > 13:
        bio_size -= 0.4
        bio_lines = wrap(italic, profile["bio"], bio_size, 500)
    name_x, name_y = width / 2, 86
    name_width = script.measure(name, name_size, tracking=-0.6)
    leading = bio_size + 6.5
    rule_y = name_y + 22
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
    {sky(width, height, 120)}
    {star_field(width, height, 14, 8, margin=20)}
    {drifting_stars(width, height, 5, 14)}
    {''.join(twinkles)}
    {script.draw(name, name_x, name_y, name_size, CREAM, "middle", tracking=-0.6)[0]}
    {gold_rule(70, width - 70, rule_y)}
    {draw_lines(italic, bio_lines, name_x, bio_y, bio_size, "#d9c6d0", leading, "middle")}
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


def write_social_icons() -> None:
    folder = ROOT / "assets" / "profile" / "icons"
    marks = {"facebook": FACEBOOK_MARK, "github": GITHUB_MARK, "linkedin": LINKEDIN_MARK}
    for name, path in marks.items():
        save(folder / f"{name}.svg", icon_badge(path))


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


def label_svg(serif: Font, label: str) -> str:
    size = 18
    text_width = serif.measure(label, size, tracking=0.2)
    gap = 8
    pill = text_width + 22
    width = gap + pill
    height = 32
    text = serif.draw(label, gap + 11, 22.5, size, CREAM, tracking=0.2)[0]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height}" viewBox="0 0 {width:.2f} {height}" role="img">
  <rect x="{gap}" width="{pill:.2f}" height="{height}" rx="16" fill="#141024"/>
  {text}
</svg>
'''


def write_link_labels(profile: dict, serif: Font) -> None:
    folder = ROOT / "assets" / "profile" / "icons"
    for item in social_links(profile):
        label = item.get("label") or "[link]"
        save(folder / f"{link_slug(item['name'])}-label.svg", label_svg(serif, label))


def link_rows(profile: dict) -> str:
    rows = []
    for item in social_links(profile):
        slug = link_slug(item["name"])
        url = (item.get("url") or "").strip() or "https://example.com/your-account"
        label = item.get("label") or "[link]"
        rows.append(
            f'<a href="{xml(url)}"><img align="absmiddle" src="assets/profile/icons/{slug}.svg" width="32" height="32" alt="{xml(item["name"])}">'
            f'<img align="absmiddle" src="assets/profile/icons/{slug}-label.svg" height="32" alt="{xml(label)}"></a>'
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
<img src="assets/profile/header-words.svg" alt="{xml(words)}" width="100%">
</td>
</tr>
</table>'''


def build_tagline(profile: dict, script: Font, italic: Font) -> str:
    width, height = 920, 220
    line_size = 58
    while script.measure(profile["tagline_line_1"], line_size, -0.4) > 500 and line_size > 36:
        line_size -= 1
    body = f'''
    {night(width, height)}
    {star_field(width, height, 16, 3)}
    {script.draw(profile["tagline_line_1"], 48, 92, line_size, CREAM, tracking=-0.5)[0]}
    {script.draw(profile["tagline_line_2"], 48, 162, line_size + 4, CREAM, tracking=-0.5)[0]}
    <path d="M500 64 H630" fill="none" stroke="{PURPLE}" stroke-width="2" stroke-linecap="round" stroke-dasharray="1.6 8">
      <animate attributeName="stroke-dashoffset" from="0" to="-40" dur="3.4s" repeatCount="indefinite"/>
    </path>
    <rect x="626" y="58" width="12" height="12" rx="2" fill="#c4b6f0"/>
    <path d="M638 64 H748" fill="none" stroke="{PURPLE}" stroke-width="2" stroke-linecap="round" stroke-dasharray="1.6 8">
      <animate attributeName="stroke-dashoffset" from="0" to="-40" dur="3.4s" repeatCount="indefinite"/>
    </path>
    <rect x="744" y="59.5" width="9" height="9" rx="1.6" fill="{GOLD}"/>
    <path d="M754 64 C792 64 804 34 820 28" fill="none" stroke="{PURPLE}" stroke-width="2" stroke-linecap="round" stroke-dasharray="1.6 8">
      <animate attributeName="stroke-dashoffset" from="0" to="-40" dur="3.4s" repeatCount="indefinite"/>
    </path>
    <rect x="828" y="6" width="70" height="70" rx="16" fill="#241c44" stroke="{PURPLE}" stroke-width="2"/>
    <g transform="translate(863,41)">
      <circle r="13" fill="none" stroke="{GOLD}" stroke-width="1.5"/>
      <ellipse rx="22" ry="7" fill="none" stroke="{PINK}" stroke-width="1.35" transform="rotate(-18)"/>
      <g>
        <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="9s" repeatCount="indefinite"/>
        <circle cx="22" cy="0" r="2.5" fill="#fff6d8"/>
      </g>
    </g>
    {italic.draw(profile["welcome_line_1"], 812, 118, 13, "#d9c6d0", "end")[0]}
    {italic.draw(profile["welcome_line_2"], 812, 138, 13, "#d9c6d0", "end")[0]}
    '''
    return document(width, height, "", body, profile["tagline_line_1"] + " " + profile["tagline_line_2"], "The line under the scroll.")


def stack_icons() -> list[Path]:
    folder = ROOT / "assets" / "stacks"
    found = []
    for path in sorted(folder.iterdir() if folder.exists() else []):
        if path.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg", ".webp"} and not path.name.startswith("."):
            found.append(path)
    return found


def place_icon(path: Path, index: int, x: float, y: float, size: float = 46) -> str:
    if path.suffix.lower() == ".svg":
        return inline_svg(path, f"stack{index}", x - size / 2, y - size / 2, size, size)
    return (
        f'<image href="{data_uri(path)}" x="{x - size / 2}" y="{y - size / 2}" '
        f'width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet"/>'
    )


def stack_label(path: Path) -> str:
    stem = re.sub(r"^\d+-", "", path.stem)
    return {
        "cplusplus": "c++",
        "javascript": "js",
        "typescript": "ts",
        "html": "html",
    }.get(stem, stem)


def build_stack(script: Font, serif: Font) -> str:
    icons = stack_icons()
    per_row = 6
    size = 44
    gap_x = 132
    gap_y = 92
    rows = math.ceil(len(icons) / per_row) if icons else 0
    width = 920
    top = 96
    # Quiet sky above and below the marks, so the two rules still frame them.
    content_h = (rows - 1) * gap_y + size if rows else 0
    quiet = 58
    field = quiet + content_h + quiet if rows else 250
    height = top + field + 96
    bottom_rule = height - 96
    band_mid = (top + bottom_rule) / 2
    first_y = band_mid - content_h / 2 + size / 2 if rows else band_mid
    placed = []
    for index, path in enumerate(icons):
        row = index // per_row
        col = index % per_row
        count_in_row = min(per_row, len(icons) - row * per_row)
        row_width = (count_in_row - 1) * gap_x
        start_x = width / 2 - row_width / 2
        x = start_x + col * gap_x
        y = first_y + row * gap_y
        placed.append(place_icon(path, index, x, y, size))
        placed.append(serif.draw(stack_label(path), x, y + size / 2 + 15, 13, "#d9cbe0", "middle")[0])
    word = "stack"
    word_size = 34
    word_width = script.measure(word, word_size, tracking=-0.4)
    # The short letters' middle lands on the same line as the star.
    word_drop = script.line_rise(word, word_size)
    left_star_x = 78
    right_star_x = width - 78
    left_word_x = left_star_x + 40
    right_word_x = right_star_x - 40 - word_width
    drifting = f'''
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0; 10 -14; 0 0" dur="12s" repeatCount="indefinite"/>
      {star_field(width, height, 8, 11, margin=80)}
    </g>'''
    body = f'''
    {night(width, height)}
    {star_field(width, height, 42 + rows * 4, 5)}
    {drifting}
    {yellow_star(left_star_x, top, 2.8)}
    {script.draw(word, left_word_x, top + word_drop, word_size, CREAM, tracking=-0.4)[0]}
    {gold_rule(left_word_x + word_width + 18, width - 36, top)}
    {''.join(placed)}
    {gold_rule(36, right_word_x - 18, bottom_rule)}
    {script.draw(word, right_word_x, bottom_rule + word_drop, word_size, CREAM, tracking=-0.4)[0]}
    {yellow_star(right_star_x, bottom_rule, 2.8)}
    '''
    return document(width, height, "", body, "stack", "A star field for stack icons. Drop files in assets/stacks and rebuild.")


def rose(x: float, y: float, flip: bool = False) -> str:
    turn = f"translate({x + 72},{y}) scale(-1,1)" if flip else f"translate({x},{y})"
    return f'''
    <g transform="{turn}">
      <g>
        <animateTransform attributeName="transform" type="rotate" values="-2.5 30 40; 2.5 30 40; -2.5 30 40" dur="6.5s" repeatCount="indefinite"/>
        <path d="M34 86 C30 66 36 52 30 38" fill="none" stroke="#6b5344" stroke-width="3.2" stroke-linecap="round"/>
        <path d="M32 64 C16 58 8 48 6 36 C22 44 28 54 32 62" fill="#3f6b52"/>
        <path d="M34 72 C50 64 60 52 64 40 C50 50 42 60 34 70" fill="#2f5340"/>
        <g transform="translate(30,36) scale(0.46)">
          <g fill="#7a2434">
            <path d="M0 10 C26-4 30-48 0-74 C-30-48 -26-4 0 10Z"/>
            <path d="M0 10 C26-4 30-48 0-74 C-30-48 -26-4 0 10Z" transform="rotate(60)"/>
            <path d="M0 10 C26-4 30-48 0-74 C-30-48 -26-4 0 10Z" transform="rotate(120)"/>
          </g>
          <g fill="#a33d4d">
            <path d="M0 8 C20-2 24-38 0-58 C-24-38 -20-2 0 8Z" transform="rotate(30)"/>
            <path d="M0 8 C20-2 24-38 0-58 C-24-38 -20-2 0 8Z" transform="rotate(90)"/>
            <path d="M0 8 C20-2 24-38 0-58 C-24-38 -20-2 0 8Z" transform="rotate(150)"/>
          </g>
          <g fill="#d36a74">
            <path d="M0 6 C14 0 16-26 0-40 C-16-26 -14 0 0 6Z" transform="rotate(10)"/>
            <path d="M0 6 C14 0 16-26 0-40 C-16-26 -14 0 0 6Z" transform="rotate(70)"/>
            <path d="M0 6 C14 0 16-26 0-40 C-16-26 -14 0 0 6Z" transform="rotate(130)"/>
            <path d="M0 6 C14 0 16-26 0-40 C-16-26 -14 0 0 6Z" transform="rotate(190)"/>
          </g>
          <path d="M0 2 C8-6 6-16 0-18 C-6-16 -8-6 0 2 C4 8 8 10 0 14 C-8 10 -4 8 0 2Z" fill="#f3c4c6"/>
          <circle r="5" fill="#f8e4dc"/>
        </g>
      </g>
    </g>
    '''


def build_projects_label(script: Font) -> str:
    width, height = 920, 168
    size = 68
    word = "projects"
    drifting = f'''
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0; 16 -8; 0 0" dur="11s" repeatCount="indefinite"/>
      {star_field(width, height, 14, 21, margin=30)}
    </g>
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0; -12 10; 0 0" dur="15s" repeatCount="indefinite"/>
      {star_field(width, height, 10, 27, margin=40)}
    </g>'''
    body = f'''
    {night(width, height)}
    {star_field(width, height, 22, 9)}
    {drifting}
    {rose(28, 28)}
    {script.draw(word, 118, 108, size, CREAM, tracking=-0.4)[0]}
    {rose(width - 150, 28, flip=True)}
    '''
    return document(width, height, "", body, "projects", "The projects label.")


def leet_bar(x: float, y: float, width: float, stats: dict) -> str:
    easy = stats.get("leetcode_easy")
    medium = stats.get("leetcode_medium")
    hard = stats.get("leetcode_hard")
    if easy is None and medium is None and hard is None:
        parts = (0.34, 0.40, 0.26)
    else:
        total = max((easy or 0) + (medium or 0) + (hard or 0), 1)
        parts = ((easy or 0) / total, (medium or 0) / total, (hard or 0) / total)
    colors = ("#2db55d", "#ffc01e", "#ef4743")
    cursor = x
    shapes = []
    for fraction, color in zip(parts, colors):
        segment = max(width * fraction - 3, 2)
        shapes.append(f'<rect x="{cursor:.1f}" y="{y}" width="{segment:.1f}" height="7" rx="3" fill="{color}"/>')
        cursor += segment + 3
    return "\n".join(shapes)


def build_card(project: dict, serif: Font, italic: Font) -> str:
    side = project.get("imageSide", "left")
    badge = (project.get("badge") or "").strip()
    title = project["title"]
    description = project.get("description") or ""
    detail = project.get("detail") or ""
    tags = project.get("tags") or []
    text_x = 210 if side == "left" else 36
    text_width = 640 if side == "left" else 500
    title_size = 28
    while serif.measure(title, title_size) > text_width - (120 if badge else 0) and title_size > 18:
        title_size -= 1
    desc_lines = wrap(italic, description, 16, text_width)
    detail_lines = wrap(italic, detail, 14, text_width) if detail else []
    cursor_y = 96
    desc_svg = draw_lines(italic, desc_lines, text_x, cursor_y, 16, MUTED, 22)
    cursor_y += 22 * len(desc_lines) + 6
    detail_svg = draw_lines(italic, detail_lines, text_x, cursor_y, 14, DIM, 20)
    cursor_y += 20 * max(len(detail_lines), 1)
    bar_y = max(168, cursor_y + 10)
    card_h = bar_y + 46
    height = card_h + 20
    width = 920
    planet_size = 150
    planet_x = 28 if side == "left" else 742
    planet_y = 22
    glow_cx = planet_x + planet_size / 2
    glow_cy = planet_y + planet_size / 2
    badge_svg = ""
    if badge:
        badge_size = 11
        badge_w = serif.measure(badge, badge_size, tracking=1.6) + 18
        badge_x = (planet_x - badge_w - 18) if side == "right" else (width - 36 - badge_w)
        badge_svg = f'''
        <rect x="{badge_x}" y="36" width="{badge_w}" height="20" rx="10" fill="none" stroke="{PINK}" stroke-width="1"/>
        {serif.draw(badge, badge_x + 9, 50, badge_size, PINK, tracking=1.6)[0]}
        '''
    tag_svg = []
    tag_cursor = 36
    for tag in tags:
        tag_svg.append(f'<g transform="translate({tag_cursor + 6},188) scale(0.55)"><path d="{STAR}" fill="{GOLD}"/></g>')
        # y is replaced after bar_y is known
        drawn, tag_width = serif.draw(tag, tag_cursor + 20, bar_y + 28, 14, GOLD)
        tag_svg.append(drawn)
        tag_cursor += 20 + tag_width + 18
    # The star y above used a placeholder. Rebuild tags now that bar_y is final.
    tag_svg = []
    tag_cursor = 36
    for tag in tags:
        tag_svg.append(
            f'<g transform="translate({tag_cursor + 7},{bar_y + 24}) scale(0.62)">'
            f'<path d="{STAR}" fill="{GOLD}"/></g>'
        )
        drawn, tag_width = serif.draw(tag, tag_cursor + 22, bar_y + 28, 15, GOLD)
        tag_svg.append(drawn)
        tag_cursor += 22 + tag_width + 16
    image = ROOT / project["image"]
    picture = inline_svg(image, project["id"].replace("-", "") + "p", planet_x, planet_y, planet_size, planet_size)
    orbit = f'''
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0 {glow_cx} {glow_cy}" to="360 {glow_cx} {glow_cy}" dur="16s" repeatCount="indefinite"/>
      <ellipse cx="{glow_cx}" cy="{glow_cy}" rx="78" ry="30" fill="none" stroke="{GOLD}" stroke-width="1.1" stroke-dasharray="3 7" opacity="0.7" transform="rotate(-16 {glow_cx} {glow_cy})"/>
      <circle cx="{glow_cx + 78}" cy="{glow_cy}" r="2.4" fill="#fff6d8"/>
    </g>'''
    body = f'''
    <clipPath id="cardClip"><rect x="16" y="8" width="888" height="{card_h}" rx="22"/></clipPath>
    <g clip-path="url(#cardClip)">
      <rect x="16" y="8" width="888" height="{card_h}" fill="{CARD}"/>
      <rect x="16" y="{bar_y}" width="888" height="{card_h - (bar_y - 8)}" fill="{CARD_BAR}"/>
      <circle cx="{glow_cx}" cy="{glow_cy}" r="54" fill="{PURPLE}" opacity="0.22">
        <animate attributeName="opacity" values="0.1;0.32;0.1" dur="4.8s" repeatCount="indefinite"/>
      </circle>
      {picture}
      {orbit}
    </g>
    <rect x="16" y="8" width="888" height="{card_h}" rx="22" fill="none" stroke="#f0d7a2" stroke-opacity="0.28" stroke-width="1.2"/>
    {serif.draw(title, text_x, 64, title_size, CREAM)[0]}
    {badge_svg}
    {desc_svg}
    {detail_svg}
    {''.join(tag_svg)}
    '''
    return document(
        width,
        height,
        "",
        body,
        title,
        description,
        fade=True,
        side=0.028,
        vert=0.04,
    )


def github_mark(x: float, y: float, size: float) -> str:
    return (
        f'<g transform="translate({x},{y}) scale({size / 24})">'
        f'<circle cx="12" cy="12" r="12" fill="#f4f1ea"/>'
        f'<path d="{GITHUB_MARK}" fill="#16141f" transform="translate(2.6,2.6) scale(0.78)"/>'
        f"</g>"
    )


def leetcode_mark(x: float, y: float, size: float) -> str:
    return f'''
    <g transform="translate({x},{y}) scale({size / 36})">
      <path d="M22 2 L8 16 L22 30" fill="none" stroke="#FFA116" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M16 30 H32" fill="none" stroke="#b8b8b8" stroke-width="5" stroke-linecap="round"/>
    </g>'''


def duo_mark(x: float, y: float, size: float) -> str:
    return f'''
    <g transform="translate({x},{y})">
      <rect width="{size}" height="{size}" rx="{size * 0.22}" fill="#58cc02"/>
      <circle cx="{size * 0.38}" cy="{size * 0.42}" r="{size * 0.16}" fill="#fff"/>
      <circle cx="{size * 0.66}" cy="{size * 0.42}" r="{size * 0.16}" fill="#fff"/>
      <circle cx="{size * 0.4}" cy="{size * 0.44}" r="{size * 0.06}" fill="#3c2a12"/>
      <circle cx="{size * 0.68}" cy="{size * 0.44}" r="{size * 0.06}" fill="#3c2a12"/>
      <path d="M{size * 0.42} {size * 0.62} L{size * 0.62} {size * 0.6} L{size * 0.5} {size * 0.74} Z" fill="#ffb100"/>
    </g>'''


def fox(x: float, y: float) -> str:
    return f'''
    <g transform="translate({x},{y})">
      <g>
        <animateTransform attributeName="transform" type="rotate" values="-3 42 48; 3 42 48; -3 42 48" dur="4.6s" repeatCount="indefinite"/>
        <path d="M22 40 L6 6 L36 28 Z" fill="#e07a2f"/>
        <path d="M24 34 L14 14 L32 28 Z" fill="#6a3820"/>
        <path d="M62 40 L78 6 L48 28 Z" fill="#e07a2f"/>
        <path d="M60 34 L70 14 L52 28 Z" fill="#6a3820"/>
        <ellipse cx="42" cy="52" rx="30" ry="26" fill="#f0a04a"/>
        <ellipse cx="42" cy="64" rx="16" ry="13" fill="#fff6ea"/>
        <ellipse cx="31" cy="50" rx="3.4" ry="4.2" fill="#24160f"/>
        <ellipse cx="53" cy="50" rx="3.4" ry="4.2" fill="#24160f"/>
        <ellipse cx="32.2" cy="48.6" rx="1.1" ry="1.3" fill="#fff6ea"/>
        <ellipse cx="54.2" cy="48.6" rx="1.1" ry="1.3" fill="#fff6ea"/>
        <ellipse cx="42" cy="60" rx="3.6" ry="2.6" fill="#24160f"/>
        <path d="M36 66 Q42 71 48 66" fill="none" stroke="#c45a28" stroke-width="1.3" stroke-linecap="round"/>
      </g>
    </g>'''


def activity_number(stats: dict) -> int:
    if (stats.get("duolingo_username") or "").strip() and stats.get("duolingo_streak") is not None:
        return int(stats["duolingo_streak"])
    return int(stats.get("counting_number") or 0)


def contribution_grid(stats: dict, x: float, y: float, serif: Font) -> str:
    """Fifty-three weeks of GitHub's day boxes. Columns are weeks, rows are Sunday to Saturday."""
    calendar = {item["date"]: item for item in stats.get("github_calendar") or []}
    end = today().date()
    days_since_sunday = (end.weekday() + 1) % 7
    start = end - timedelta(days=days_since_sunday + 52 * 7)
    cell, gap = 8.0, 2.2
    step = cell + gap
    parts = []
    for week in range(53):
        week_start = start + timedelta(days=week * 7)
        for row in range(7):
            day = week_start + timedelta(days=row)
            if day > end:
                continue
            if day.day == 1:
                parts.append(serif.draw(MONTHS[day.month - 1], x + week * step, y - 2, 10, DIM)[0])
            item = calendar.get(day.isoformat(), {})
            count = int(item.get("count") or 0)
            level = int(item.get("level") or 0)
            if level == 0 and count:
                level = 1 if count < 3 else 2 if count < 6 else 3 if count < 10 else 4
            level = max(0, min(4, level))
            parts.append(
                f'<rect x="{x + week * step:.2f}" y="{y + 4 + row * step:.2f}" '
                f'width="{cell}" height="{cell}" rx="1.6" fill="{CONTRIBUTION_LEVELS[level]}"/>'
            )
    return "\n".join(parts)


def build_activity(stats: dict, script: Font, serif: Font, italic: Font) -> str:
    width, height = 620, 560
    body = f'''
    {night(width, height)}
    {star_field(width, height, 18, 13, margin=16)}
    {fox(4, 0)}
    {script.draw("activity", 128, 78, 42, CREAM, tracking=-0.3)[0]}
    {github_mark(24, 148, 40)}
    {italic.draw("contributions", 78, 162, 16, PINK)[0]}
    {serif.draw(digits(stats.get("github_contributions")), 78, 208, 32, CREAM, tracking=1.2)[0]}
    {italic.draw("streak", 78, 234, 15, GOLD)[0]}
    {serif.draw(digits(stats.get("github_streak")), 132, 234, 15, GOLD, tracking=0.8)[0]}
    {leetcode_mark(330, 146, 40)}
    {italic.draw("problems solved", 380, 162, 16, PINK)[0]}
    {serif.draw(digits(stats.get("leetcode_solved")), 380, 208, 32, CREAM, tracking=1.2)[0]}
    {leet_bar(380, 224, 170, stats)}
    {duo_mark(24, 292, 42)}
    {serif.draw(digits(activity_number(stats)), 80, 328, 32, CREAM, tracking=1.2)[0]}
    {italic.draw("streak", 80, 356, 15, GOLD)[0]}
    {contribution_grid(stats, 32, 400, serif)}
    '''
    return document(width, height, "", body, "activity", "GitHub, LeetCode, and the counting streak.", side=0.02, vert=0.02)


def quote_corners(width: float, height: float) -> str:
    inset = 28
    arm = 46
    corners = [
        (inset, inset, 1, 1),
        (width - inset, inset, -1, 1),
        (inset, height - inset, 1, -1),
        (width - inset, height - inset, -1, -1),
    ]
    parts = []
    for x, y, sx, sy in corners:
        parts.append(
            f'''<g fill="none" stroke="{GOLD}" stroke-width="1.35" stroke-linejoin="round">
              <path d="M{x} {y + sy * arm} V{y} H{x + sx * arm}"/>
              <path d="M{x + sx * 8} {y + sy * (arm + 8)} V{y + sy * 8} H{x + sx * (arm + 8)}"/>
              <animate attributeName="stroke-opacity" values="0.55;1;0.55" dur="5s" repeatCount="indefinite"/>
            </g>'''
        )
    return "\n".join(parts)


def build_quote(text: str, script: Font) -> str:
    width, height = 460, 460
    lines = [text]
    size = 34
    for candidate in (36, 32, 28, 24, 20, 17):
        wrapped = wrap(script, text, candidate, 300, tracking=-0.3)
        if len(wrapped) * candidate * 1.15 <= 220:
            lines = wrapped
            size = candidate
            break
    else:
        lines = wrap(script, text, 17, 300, tracking=-0.3)
        size = 17
    block = len(lines) * size * 1.15
    start = height / 2 - block / 2 + size * 0.8
    body = f'''
    {night(width, height)}
    {star_field(width, height, 12, 17)}
    {quote_corners(width, height)}
    {draw_lines(script, lines, width / 2, start, size, CREAM, size * 1.15, "middle", tracking=-0.3)}
    '''
    return document(width, height, "", body, text, "The quote for today.")


def stamp(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]


def write_readme(profile: dict, projects: list[dict], quote: str, stats: dict) -> None:
    cards = "\n".join(
        "\n".join(
            [
                "<p align=\"center\">",
                f'  <img src="assets/profile/cards/{project["id"]}.svg" alt="{xml(project["title"])}" width="100%">',
                "</p>",
            ]
        )
        for project in projects
    )
    text = f'''<!--
The pictures are built from the files in content/.

name and the lines under the name: content/profile.json
  name and bio. They are drawn into assets/profile/header-words.svg only.
account links under the portrait: content/profile.json, the links list
  label is the words beside the icon. url is where a click goes.
  Type the account there. The icon files in assets/profile/icons stay as they are.
  Facebook, GitHub, and LinkedIn are separate pictures, so a click opens url
  instead of opening the picture file.
one project per object, in order: content/projects.json
  image is a planet file already in assets/, or a new one
  imageSide is "left" or "right"
  badge is "PRIVATE" or ""
  description, detail, and tags are the words on the card
stack icons: drop an .svg or .png into assets/stacks, then rebuild.
  name them 01-something.svg, 02-something.svg to set the order
quotes, one per line: content/quotes.txt
  a credit after an em dash is kept in the file and left off the picture
usernames: content/stats.json
  github_username is already set
  leetcode_username and duolingo_username stay empty until you fill them
  with no Duolingo username, the lower number counts up by one each day

Pushing a change in content/ redraws the pictures on GitHub.
The picture address changes with the words, so the page does not keep the old drawing.
-->

{header_block(profile)}

<br>

<p align="center">
  <img src="assets/profile/tagline.svg" alt="code that tells a story" width="100%">
</p>

<p align="center">
  <img src="assets/profile/stack-field.svg" alt="stack" width="100%">
</p>

<p align="center">
  <img src="assets/profile/projects-label.svg" alt="projects" width="100%">
</p>

{cards}

<table>
<tr>
<td width="58%" valign="top">
<img src="assets/profile/activity.svg?v={stamp(json.dumps([stats.get('github_contributions'), stats.get('github_streak'), stats.get('leetcode_solved'), activity_number(stats)], default=str))}" alt="activity" width="100%">
</td>
<td width="42%" valign="top">
<img src="assets/profile/quote.svg?v={stamp(quote)}" alt="A quote that changes every day" width="100%">
</td>
</tr>
</table>
'''
    save(ROOT / "README.md", text)


def write_preview(profile: dict, projects: list[dict]) -> None:
    cards = "\n".join(
        f'    <img src="assets/profile/cards/{project["id"]}.svg" alt="" width="100%">' for project in projects
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Profile preview</title>
  <style>
    body {{ margin: 0; background: #05040a; color: #f6efe4; font-family: Georgia, serif; }}
    main {{ width: min(920px, 100%); margin: 0 auto; padding: 28px 0 80px; }}
    img[width="100%"] {{ display: block; width: 100%; height: auto; }}
    img[height="32"] {{ display: inline-block; width: auto; height: 32px; vertical-align: middle; }}
    a {{ color: #f7f1e6; text-decoration: none; }}
    .gap {{ height: 36px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    td {{ vertical-align: top; padding: 0; }}
  </style>
</head>
<body>
  <main>
    {header_block(profile)}
    <div class="gap"></div>
    <img src="assets/profile/tagline.svg" alt="" width="100%">
    <img src="assets/profile/stack-field.svg" alt="" width="100%">
    <img src="assets/profile/projects-label.svg" alt="" width="100%">
{cards}
    <table>
      <tr>
        <td width="58%"><img src="assets/profile/activity.svg" alt="" width="100%"></td>
        <td width="42%"><img src="assets/profile/quote.svg" alt="" width="100%"></td>
      </tr>
    </table>
  </main>
</body>
</html>
"""
    save(ROOT / "preview.html", html)


def build_all(advance_counter: bool = False) -> None:
    script, serif, italic = load_fonts()
    profile = load_json(ROOT / "content" / "profile.json")
    projects = load_json(ROOT / "content" / "projects.json")
    stats_path = ROOT / "content" / "stats.json"
    stats = load_json(stats_path)
    stats = refresh_stats(stats, advance_counter=advance_counter)
    save(stats_path, json.dumps(stats, indent=2) + "\n")
    save(ROOT / "assets" / "profile" / "header-portrait.svg", build_portrait_panel())
    save(ROOT / "assets" / "profile" / "header-words.svg", build_words_panel(profile, script, italic))
    write_social_icons()
    write_link_labels(profile, serif)
    old_header = ROOT / "assets" / "profile" / "header.svg"
    if old_header.exists():
        old_header.unlink()
    save(ROOT / "assets" / "profile" / "tagline.svg", build_tagline(profile, script, italic))
    save(ROOT / "assets" / "profile" / "stack-field.svg", build_stack(script, serif))
    save(ROOT / "assets" / "profile" / "projects-label.svg", build_projects_label(script))
    for project in projects:
        save(ROOT / "assets" / "profile" / "cards" / f"{project['id']}.svg", build_card(project, serif, italic))
    save(ROOT / "assets" / "profile" / "activity.svg", build_activity(stats, script, serif, italic))
    quote = quote_for()
    save(ROOT / "assets" / "profile" / "quote.svg", build_quote(quote, script))
    write_readme(profile, projects, quote, stats)
    write_preview(profile, projects)


def refresh_daily() -> None:
    """Used by the daily workflow. Rewrites the quote and the activity picture only."""
    script, serif, italic = load_fonts()
    stats_path = ROOT / "content" / "stats.json"
    stats = refresh_stats(load_json(stats_path), advance_counter=True)
    save(stats_path, json.dumps(stats, indent=2) + "\n")
    save(ROOT / "assets" / "profile" / "activity.svg", build_activity(stats, script, serif, italic))
    quote = quote_for()
    save(ROOT / "assets" / "profile" / "quote.svg", build_quote(quote, script))
    profile = load_json(ROOT / "content" / "profile.json")
    projects = load_json(ROOT / "content" / "projects.json")
    write_link_labels(profile, serif)
    write_readme(profile, projects, quote, stats)


if __name__ == "__main__":
    build_all(advance_counter=False)
