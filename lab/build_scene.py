"""Build the portrait galaxy.

Python draws one tall SVG. Motion lives in the SVG itself:
drifting dust, a turning ring, an orbiting moon, a glowing lamp,
and petals that fall.
"""

from pathlib import Path
import random

W, H = 760, 1520


def dust(still: bool) -> str:
    rng = random.Random(11)
    bits = []
    for _ in range(110):
        x = rng.uniform(6, W - 6)
        y = rng.uniform(6, H - 6)
        r = rng.choice((1.1, 1.5, 1.9, 2.4, 3.0))
        opacity = rng.uniform(0.35, 1)
        if still:
            bits.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff6d8" opacity="{opacity:.2f}"/>'
            )
            continue
        dx = rng.uniform(-70, 90)
        dy = rng.uniform(-50, 80)
        drift = rng.uniform(6, 14)
        twinkle = rng.uniform(2.4, 5.5)
        bits.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff6d8" opacity="{opacity:.2f}">'
            f'<animate attributeName="cx" values="{x:.1f};{x + dx:.1f};{x:.1f}" dur="{drift:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{y:.1f};{y + dy:.1f};{y:.1f}" dur="{drift * 1.15:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{max(opacity * 0.15, 0.05):.2f};{opacity:.2f};{max(opacity * 0.15, 0.05):.2f}" dur="{twinkle:.1f}s" repeatCount="indefinite"/>'
            f"</circle>"
        )
    return "\n".join(bits)


def spark(x, y, scale=1, still=True):
    star = 'd="M0-8 1.6-2.3 8-2 2.6 1.4 4.4 7.4 0 3.6-4.4 7.4-2.6 1.4-8-2-1.6-2.3Z"'
    if still:
        inner = f'<path transform="scale({scale})" fill="#fff1c2" {star}/>'
    else:
        inner = (
            "<g>"
            f'<animateTransform attributeName="transform" type="scale" values="{scale};{scale * 1.35};{scale}" dur="3.2s" repeatCount="indefinite"/>'
            f'<path fill="#fff1c2" {star}/>'
            "</g>"
        )
    return f'<g transform="translate({x} {y})">{inner}</g>'


def rock(scale=1):
    return (
        f'<path transform="scale({scale})" fill="url(#rock)" '
        f'd="M-34 8c2-28 22-46 48-42 20 3 36 16 40 36 4 22-8 40-28 46-24 8-52 2-60-18-6-14-4-16 0-22z"/>'
    )


def peak():
    return """
    <g transform="translate(230 500)">
      <ellipse cx="0" cy="10" rx="120" ry="42" fill="#7d6bb8" opacity="0.2"/>
      <ellipse cx="6" cy="86" rx="78" ry="14" fill="#000" opacity="0.28"/>
      <path d="M-78 16c4-58 40-96 96-90 40 4 74 24 86 64 12 44-8 86-52 100-50 16-108 6-128-30-14-26-12-32-2-44z" fill="url(#rock)"/>
      <path d="M-50 28 L10-118 L38-22 L70-58 L100 34 Z" fill="url(#snow)"/>
      <path d="M10-118 L34-24 L-2-40 Z" fill="#b7c7d8"/>
      <ellipse cx="-28" cy="-6" rx="14" ry="9" fill="#6d4e3a" opacity="0.35"/>
      <ellipse cx="40" cy="28" rx="18" ry="11" fill="#5a4032" opacity="0.28"/>
      <text x="0" y="128" fill="#f3e6d4" font-family="Palatino, Georgia, serif" font-size="16" text-anchor="middle">Peak Hunter</text>
    </g>
    """


def route(still: bool):
    spin = "" if still else '<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="16s" repeatCount="indefinite"/>'
    return f"""
    <g transform="translate(250 860)">
      <ellipse cx="4" cy="92" rx="74" ry="12" fill="#000" opacity="0.25"/>
      <g>{spin}<ellipse rx="108" ry="36" fill="none" stroke="#f0d7a2" stroke-width="1.6"/></g>
      <g fill="#fff1c2">
        <circle cx="-96" cy="-6" r="3.4"/>
        <circle cx="-40" cy="-30" r="2.6"/>
        <circle cx="48" cy="-28" r="2.8"/>
        <circle cx="100" cy="8" r="3.2"/>
      </g>
      <circle r="64" fill="url(#sea)"/>
      <path d="M-28-8c12-10 30-8 40 2 6 8-2 16-16 16-16 0-30-6-24-18z" fill="#1f6d58" opacity="0.55"/>
      <path d="M6 16c10-4 22-2 28 6-8 6-20 8-28 2z" fill="#d7f3ef" opacity="0.35"/>
      <text x="0" y="118" fill="#f3e6d4" font-family="Palatino, Georgia, serif" font-size="16" text-anchor="middle">Jeepney Router</text>
    </g>
    """


def rose(still: bool):
    fall = ""
    if not still:
        fall = """
        <ellipse cx="-54" cy="-20" rx="6" ry="3.5" fill="#e7a0a8">
          <animate attributeName="cy" values="-20;40;-20" dur="9s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="1;0.2;1" dur="9s" repeatCount="indefinite"/>
        </ellipse>
        <ellipse cx="36" cy="-70" rx="7" ry="4" fill="#e7a0a8">
          <animate attributeName="cy" values="-70;10;-70" dur="11s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.3;1;0.3" dur="11s" repeatCount="indefinite"/>
        </ellipse>
        """
    else:
        fall = """
        <ellipse cx="-54" cy="-20" rx="6" ry="3.5" fill="#e7a0a8"/>
        <ellipse cx="36" cy="-70" rx="7" ry="4" fill="#e7a0a8"/>
        """
    return f"""
    <g transform="translate(230 1260)">
      <ellipse cx="0" cy="70" rx="42" ry="11" fill="#000" opacity="0.25"/>
      <path d="M-32 56c4-18 16-28 32-26 14 2 26 12 30 28 1 6-6 11-14 12-18 3-40 1-48-14z" fill="url(#rock)"/>
      <path d="M-2 42 C-6-6 6-62-10-108" fill="none" stroke="#6b5344" stroke-width="4.5" stroke-linecap="round"/>
      <path d="M-6-16 C-32-28 -46-44 -54-62 C-30-52 -16-36 -6-18" fill="#3f6b52"/>
      <g transform="translate(-8 -118)">
        <path d="M0 7 C16-2 20-32 0-50 C-20-32 -16-2 0 7Z" fill="#7a2434"/>
        <path d="M0 7 C16-2 20-32 0-50 C-20-32 -16-2 0 7Z" fill="#7a2434" transform="rotate(60)"/>
        <path d="M0 7 C16-2 20-32 0-50 C-20-32 -16-2 0 7Z" fill="#7a2434" transform="rotate(120)"/>
        <path d="M0 5 C12 0 14-22 0-36 C-14-22 -12 0 0 5Z" fill="#d36a74" transform="rotate(30)"/>
        <path d="M0 5 C12 0 14-22 0-36 C-14-22 -12 0 0 5Z" fill="#d36a74" transform="rotate(90)"/>
        <path d="M0 5 C12 0 14-22 0-36 C-14-22 -12 0 0 5Z" fill="#d36a74" transform="rotate(150)"/>
        <circle r="5" fill="#f8e4dc"/>
      </g>
      {fall}
    </g>
    """


def drawer():
    return """
    <g transform="translate(540 1390)">
      <ellipse cx="0" cy="52" rx="36" ry="9" fill="#000" opacity="0.25"/>
      <path d="M-30 32c3-20 18-30 32-28 14 2 26 12 28 26 1 7-7 14-16 14-16 2-38 0-44-12z" fill="url(#rock)"/>
      <path d="M-20-6 h40 l-4 9 h-32 z" fill="#5c3828"/>
      <path d="M-16 3 h32 v7 h-32 z" fill="#3a241c"/>
      <path d="M-24 10 h48 l5 14 h-58 z" fill="url(#wood)"/>
      <rect x="-7" y="15" width="14" height="3.5" rx="1.4" fill="#fff1c2"/>
      <path d="M-8-1 h16 l3 4 h-18 z" fill="#fffaf2"/>
    </g>
    """


def ring_world(still: bool):
    spin = "" if still else '<animateTransform attributeName="transform" type="rotate" from="-20" to="340" dur="18s" repeatCount="indefinite"/>'
    return f"""
    <g transform="translate(170 170)">
      <g>{spin}<ellipse rx="74" ry="22" fill="none" stroke="#f0d7a2" stroke-width="1.5"/></g>
      {rock(1.05)}
      <ellipse cx="-8" cy="-10" rx="9" ry="6" fill="#6d4e3a" opacity="0.35"/>
    </g>
    """


def moon(still: bool):
    spin = "" if still else '<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="12s" repeatCount="indefinite"/>'
    return f"""
    <g transform="translate(170 170)">
      <g>{spin}<circle cx="86" cy="0" r="5" fill="#fff6d8"/></g>
    </g>
    """


def lantern(still: bool):
    glow = "" if still else '<animate attributeName="opacity" values="0.35;1;0.35" dur="2.2s" repeatCount="indefinite"/>'
    return f"""
    <g transform="translate(560 300)">
      {rock(0.92)}
      <path d="M0-4 v-46" stroke="#6b5344" stroke-width="3.4" stroke-linecap="round"/>
      <path d="M-10-58 h20 l-3 16 h-14 z" fill="#f0d7a2"/>
      <rect x="-7" y="-56" width="14" height="12" fill="#fff6d8" opacity="0.95">{glow}</rect>
    </g>
    """


def books():
    return """
    <g transform="translate(560 660)">
      """ + rock(1) + """
      <g transform="translate(-22 -36)">
        <rect x="0" y="0" width="18" height="24" rx="1" fill="#8e3d4a"/>
        <rect x="16" y="-6" width="16" height="30" rx="1" fill="#3f6b52"/>
        <rect x="30" y="2" width="15" height="22" rx="1" fill="#c4895a"/>
        <path d="M2 28 h40 l6 12 h-50 z" fill="#efe2c4"/>
        <path d="M12 33 h22 M12 37 h16" stroke="#b7a07a" stroke-width="1.2"/>
      </g>
    </g>
    """


def sprout():
    return """
    <g transform="translate(560 980)">
      """ + rock(0.85) + """
      <path d="M2-8 v-28" stroke="#3f6b52" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M2-28 C-10-40 -18-36 -16-26 C-8-28 -2-30 2-24" fill="#6fae78"/>
      <path d="M2-22 C14-34 22-30 20-20 C12-22 6-24 2-18" fill="#3f6b52"/>
    </g>
    """


def stars(still: bool):
    labels = [
        (78, 90, "[tool]", 1.05),
        (400, 70, "[certificate]", 0.95),
        (660, 210, "[language]", 1),
        (70, 390, "[surprise]", 0.85),
        (430, 400, "[skill]", 1),
        (90, 700, "[framework]", 0.9),
        (560, 790, "[language]", 0.9),
        (80, 1000, "[tool]", 0.95),
    ]
    bits = []
    for index, (x, y, label, scale) in enumerate(labels):
        bits.append(spark(x, y - 14, scale, still or index % 2 == 0))
        bits.append(
            f'<text x="{x}" y="{y + 16}" fill="#f3e6d4" font-family="Palatino, Georgia, serif" font-size="14" text-anchor="middle">{label}</text>'
        )
    return "\n".join(bits)


def clouds(still: bool) -> str:
    if still:
        return """
        <ellipse cx="180" cy="240" rx="180" ry="70" fill="url(#cloudViolet)"/>
        <ellipse cx="540" cy="760" rx="200" ry="80" fill="url(#cloudPink)"/>
        <ellipse cx="300" cy="1180" rx="160" ry="56" fill="url(#cloudGold)"/>
        """
    return """
    <ellipse cx="180" cy="240" rx="180" ry="70" fill="url(#cloudViolet)">
      <animate attributeName="cx" values="180;230;180" dur="18s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="540" cy="760" rx="200" ry="80" fill="url(#cloudPink)">
      <animate attributeName="cx" values="540;490;540" dur="22s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="300" cy="1180" rx="160" ry="56" fill="url(#cloudGold)">
      <animate attributeName="cy" values="1180;1140;1180" dur="16s" repeatCount="indefinite"/>
    </ellipse>
    """


def build(still: bool) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="sceneTitle sceneDesc">
  <title id="sceneTitle">A portrait sky</title>
  <desc id="sceneDesc">A tall galaxy. Peak Hunter and Jeepney Router share the sky with a rose, a drawer, and unnamed worlds holding a ring, a lantern, books, and a sprout. Stars and dust move through the same background.</desc>
  <defs>
    <radialGradient id="space" cx="50%" cy="40%" r="80%">
      <stop offset="0%" stop-color="#322848"/>
      <stop offset="48%" stop-color="#141028"/>
      <stop offset="100%" stop-color="#090712"/>
    </radialGradient>
    <radialGradient id="cloudPink" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#e7b4c4" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="#e7b4c4" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="cloudViolet" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#7d6bb8" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#7d6bb8" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="cloudGold" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#f0d7a2" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#f0d7a2" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="rock" cx="32%" cy="28%" r="78%">
      <stop offset="0%" stop-color="#edd8b6"/>
      <stop offset="48%" stop-color="#a78462"/>
      <stop offset="100%" stop-color="#4e3428"/>
    </radialGradient>
    <radialGradient id="sea" cx="34%" cy="30%" r="75%">
      <stop offset="0%" stop-color="#e7fbff"/>
      <stop offset="40%" stop-color="#3e8ea4"/>
      <stop offset="100%" stop-color="#163848"/>
    </radialGradient>
    <linearGradient id="snow" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fffaf2"/>
      <stop offset="100%" stop-color="#d5e4f2"/>
    </linearGradient>
    <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#c4895a"/>
      <stop offset="100%" stop-color="#7a4a30"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#space)"/>
  {clouds(still)}
  {dust(still)}
  {stars(still)}
  {ring_world(still)}
  {moon(still)}
  {lantern(still)}
  {peak()}
  {books()}
  {route(still)}
  {sprout()}
  {rose(still)}
  {drawer()}
</svg>
"""


def main():
    root = Path(__file__).resolve().parents[1]
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    moving = build(False)
    (assets / "scene.svg").write_text(moving, encoding="utf-8")
    (assets / "scene-still.svg").write_text(build(True), encoding="utf-8")
    preview = root / "preview.html"
    preview.write_text(
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Portrait sky</title>
  <style>
    html, body { margin: 0; background: #090712; }
    body { display: flex; justify-content: center; }
    object { width: min(460px, 100vw); height: auto; }
  </style>
</head>
<body>
  <object data="assets/scene.svg" type="image/svg+xml" width="460" aria-label="Portrait galaxy with moving stardust, a turning ring, an orbiting moon, a glowing lantern, and falling petals."></object>
</body>
</html>
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
