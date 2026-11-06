"""Build the portrait galaxy and its standalone portfolio assets.

Python draws one tall SVG in a painted, storybook style. Motion lives in the
SVG itself: drifting dust, a turning ring, an orbiting moon, a glowing lamp,
swaying sprout, floating pages, and petals that fall. A still copy is built too.
The edges fade to transparent so the picture melts into GitHub's dark page.
Each world is also exported as an independent SVG for flexible layouts.
"""

from pathlib import Path
import random

W, H = 760, 1520
SERIF = "Palatino, Georgia, serif"


def a(still: bool, xml: str) -> str:
    """Return animation markup only when the scene is moving."""
    return "" if still else xml


# ---------------------------------------------------------------- defs
DEFS = """
  <defs>
    <radialGradient id="space" cx="50%" cy="42%" r="85%">
      <stop offset="0%" stop-color="#2a2142"/><stop offset="45%" stop-color="#151029"/><stop offset="100%" stop-color="#0d1117"/>
    </radialGradient>
    <radialGradient id="cloudPink" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#e7b4c4" stop-opacity="0.30"/><stop offset="100%" stop-color="#e7b4c4" stop-opacity="0"/></radialGradient>
    <radialGradient id="cloudViolet" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#7d6bb8" stop-opacity="0.42"/><stop offset="100%" stop-color="#7d6bb8" stop-opacity="0"/></radialGradient>
    <radialGradient id="cloudBlue" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#5b7fd0" stop-opacity="0.28"/><stop offset="100%" stop-color="#5b7fd0" stop-opacity="0"/></radialGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#fff1c2" stop-opacity="0.55"/><stop offset="100%" stop-color="#fff1c2" stop-opacity="0"/></radialGradient>
    <radialGradient id="lampglow" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#ffd978" stop-opacity="0.85"/><stop offset="45%" stop-color="#ffb94a" stop-opacity="0.28"/><stop offset="100%" stop-color="#ffb94a" stop-opacity="0"/></radialGradient>
    <radialGradient id="rock" cx="32%" cy="26%" r="80%"><stop offset="0%" stop-color="#e6cfa8"/><stop offset="45%" stop-color="#a47f5d"/><stop offset="100%" stop-color="#4a3226"/></radialGradient>
    <linearGradient id="shade" x1="0.15" y1="0.05" x2="0.9" y2="1"><stop offset="0.35" stop-color="#140c1c" stop-opacity="0"/><stop offset="1" stop-color="#140c1c" stop-opacity="0.6"/></linearGradient>
    <radialGradient id="sea" cx="34%" cy="30%" r="78%"><stop offset="0%" stop-color="#bfe9ff"/><stop offset="40%" stop-color="#2f7fb0"/><stop offset="100%" stop-color="#102a4a"/></radialGradient>
    <radialGradient id="atmo" cx="50%" cy="50%" r="50%"><stop offset="80%" stop-color="#7cc4ff" stop-opacity="0"/><stop offset="93%" stop-color="#7cc4ff" stop-opacity="0.35"/><stop offset="100%" stop-color="#7cc4ff" stop-opacity="0"/></radialGradient>
    <linearGradient id="mtn" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9a8a8a"/><stop offset="1" stop-color="#4d4048"/></linearGradient>
    <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c4895a"/><stop offset="1" stop-color="#7a4a30"/></linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e6f3ff" stop-opacity="0.18"/><stop offset="1" stop-color="#e6f3ff" stop-opacity="0.03"/></linearGradient>

    <!-- edge fades: white = visible, black = transparent -->
    <linearGradient id="gx" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000"/><stop offset="0.02" stop-color="#2a2a2a"/><stop offset="0.045" stop-color="#8c8c8c"/><stop offset="0.08" stop-color="#fff"/>
      <stop offset="0.92" stop-color="#fff"/><stop offset="0.955" stop-color="#8c8c8c"/><stop offset="0.98" stop-color="#2a2a2a"/><stop offset="1" stop-color="#000"/>
    </linearGradient>
    <linearGradient id="gy" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000"/><stop offset="0.012" stop-color="#2a2a2a"/><stop offset="0.028" stop-color="#8c8c8c"/><stop offset="0.05" stop-color="#fff"/>
      <stop offset="0.95" stop-color="#fff"/><stop offset="0.972" stop-color="#8c8c8c"/><stop offset="0.988" stop-color="#2a2a2a"/><stop offset="1" stop-color="#000"/>
    </linearGradient>
    <mask id="mx" maskUnits="userSpaceOnUse" x="0" y="0" width="760" height="1520"><rect width="760" height="1520" fill="url(#gx)"/></mask>
    <mask id="my" maskUnits="userSpaceOnUse" x="0" y="0" width="760" height="1520"><rect width="760" height="1520" fill="url(#gy)"/></mask>

    <filter id="haze" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="26"/></filter>
    <filter id="rough" x="-15%" y="-15%" width="130%" height="130%">
      <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="3" seed="4" result="n"/>
      <feDisplacementMap in="SourceGraphic" in2="n" scale="4" xChannelSelector="R" yChannelSelector="G" result="d"/>
      <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="9" result="g"/>
      <feColorMatrix in="g" type="matrix" values="0 0 0 0 .1  0 0 0 0 .06  0 0 0 0 .06  1.3 0 0 0 -.5" result="ga"/>
      <feComposite in="ga" in2="d" operator="in" result="gg"/>
      <feMerge><feMergeNode in="d"/><feMergeNode in="gg"/></feMerge>
    </filter>

    <path id="blob" transform="translate(-10 -7)" d="M-34 8c2-28 22-46 48-42 20 3 36 16 40 36 4 22-8 40-28 46-24 8-52 2-60-18-6-14-4-16 0-22z"/>
    <g id="body" filter="url(#rough)">
      <use href="#blob" fill="url(#rock)" stroke="#2b1d22" stroke-width="1.3" stroke-linejoin="round"/>
      <ellipse cx="-14" cy="-8" rx="9" ry="5.5" fill="#5b4333" opacity="0.5"/>
      <path d="M-22 -5a9 5.5 0 0 0 17 3" fill="none" stroke="#f0dcb8" stroke-width="1.1" opacity="0.5"/>
      <ellipse cx="16" cy="18" rx="11" ry="6.5" fill="#4a3426" opacity="0.45"/>
      <path d="M6 21a11 6.5 0 0 0 20-2" fill="none" stroke="#f0dcb8" stroke-width="1.1" opacity="0.4"/>
      <ellipse cx="-22" cy="22" rx="5" ry="3" fill="#5b4333" opacity="0.45"/>
      <ellipse cx="22" cy="-18" rx="4" ry="2.6" fill="#5b4333" opacity="0.4"/>
      <use href="#blob" fill="url(#shade)"/>
    </g>
  </defs>
"""


def body(transform: str) -> str:
    return f'<use href="#body" transform="{transform}"/>'


# ---------------------------------------------------------------- sky
def clouds(still: bool) -> str:
    return f"""
    <g filter="url(#haze)">
      <ellipse cx="380" cy="760" rx="420" ry="90" fill="url(#cloudViolet)" transform="rotate(54 380 760)"/>
      <ellipse cx="180" cy="240" rx="180" ry="70" fill="url(#cloudViolet)">{a(still, '<animate attributeName="cx" values="180;230;180" dur="18s" repeatCount="indefinite"/>')}</ellipse>
      <ellipse cx="540" cy="760" rx="200" ry="80" fill="url(#cloudPink)">{a(still, '<animate attributeName="cx" values="540;490;540" dur="22s" repeatCount="indefinite"/>')}</ellipse>
      <ellipse cx="300" cy="1180" rx="160" ry="56" fill="url(#cloudBlue)">{a(still, '<animate attributeName="cy" values="1180;1140;1180" dur="16s" repeatCount="indefinite"/>')}</ellipse>
      <ellipse cx="600" cy="520" rx="140" ry="50" fill="url(#cloudBlue)"/>
    </g>"""


def band() -> str:
    """Fine, still stardust along a diagonal Milky Way."""
    rng = random.Random(5)
    cols = ("#fff6d8", "#cdbcf5", "#f4c9d6", "#b9c7ff")
    bits = []
    for _ in range(240):
        t = rng.random()
        x = 720 - 680 * t + rng.gauss(0, 60)
        y = 300 + 1000 * t + rng.gauss(0, 45)
        bits.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rng.uniform(0.5, 1.2):.1f}" '
            f'fill="{rng.choice(cols)}" opacity="{rng.uniform(0.25, 0.75):.2f}"/>'
        )
    return "\n".join(bits)


def dust(still: bool) -> str:
    rng = random.Random(11)
    bits = []
    for _ in range(110):
        x = rng.uniform(6, W - 6)
        y = rng.uniform(6, H - 6)
        r = rng.choice((1.1, 1.5, 1.9, 2.4, 3.0)) * 0.7
        opacity = rng.uniform(0.35, 1)
        if still:
            bits.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="#fff6d8" opacity="{opacity:.2f}"/>')
            continue
        dx = rng.uniform(-70, 90)
        dy = rng.uniform(-50, 80)
        drift = rng.uniform(6, 14)
        twinkle = rng.uniform(2.4, 5.5)
        lo = max(opacity * 0.15, 0.05)
        bits.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="#fff6d8" opacity="{opacity:.2f}">'
            f'<animate attributeName="cx" values="{x:.1f};{x + dx:.1f};{x:.1f}" dur="{drift:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{y:.1f};{y + dy:.1f};{y:.1f}" dur="{drift * 1.15:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{lo:.2f};{opacity:.2f};{lo:.2f}" dur="{twinkle:.1f}s" repeatCount="indefinite"/>'
            "</circle>"
        )
    return "\n".join(bits)


def spark(x, y, scale=1, still=True):
    star = 'd="M0-10C1.5-3 3-1.5 10 0 3 1.5 1.5 3 0 10-1.5 3-3 1.5-10 0-3-1.5-1.5-3 0-10Z"'
    if still:
        inner = f'<path transform="scale({scale})" fill="#fff6d8" {star}/>'
    else:
        inner = (
            "<g>"
            f'<animateTransform attributeName="transform" type="scale" values="{scale};{scale * 1.35};{scale}" dur="3.2s" repeatCount="indefinite"/>'
            f'<path fill="#fff6d8" {star}/>'
            "</g>"
        )
    return f'<g transform="translate({x} {y})"><circle r="18" fill="url(#glow)"/>{inner}</g>'


def stars(still: bool) -> str:
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
            f'<text x="{x}" y="{y + 18}" fill="#f3e6d4" font-family="{SERIF}" font-size="14" text-anchor="middle">{label}</text>'
        )
    return "\n".join(bits)


def rocks() -> str:
    return "\n".join(
        [
            # big cropped rocks at the edges
            body("translate(-30 600) rotate(8) scale(1.5 2.3)"),
            body("translate(705 1505) rotate(-8) scale(3 2.2)"),
            # small drifting ones
            body("translate(352 346) scale(.22)"),
            body("translate(436 640) rotate(40) scale(.16)"),
            body("translate(140 1130) scale(.2)"),
            body("translate(410 1040) rotate(-30) scale(.14)"),
            body("translate(700 1190) rotate(20) scale(.24)"),
        ]
    )


# ---------------------------------------------------------------- worlds
def ring_world(still: bool) -> str:
    spin = a(still, '<animateTransform attributeName="transform" type="rotate" from="-20" to="340" dur="18s" repeatCount="indefinite"/>')
    return f"""
    <g transform="translate(170 170)">
      <g>{spin}<ellipse rx="78" ry="21" fill="none" stroke="#f0d7a2" stroke-width="1.6" opacity="0.9"/></g>
      {body("scale(1.05)")}
      <g transform="translate(-4 -40) rotate(-6)">
        <ellipse cx="0" cy="2" rx="17" ry="4" fill="#7d3b52"/>
        <rect x="-10" y="-17" width="20" height="19" rx="2" fill="#7d3b52"/>
        <rect x="-10" y="-6" width="20" height="4" fill="#e7b4c4"/>
      </g>
    </g>"""


def moon(still: bool) -> str:
    spin = a(still, '<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="12s" repeatCount="indefinite"/>')
    return f"""
    <g transform="translate(170 170)">
      <g>{spin}<circle cx="86" cy="0" r="5" fill="#fff6d8"/></g>
    </g>"""


def lantern(still: bool) -> str:
    glow = a(still, '<animate attributeName="opacity" values="0.35;1;0.35" dur="2.2s" repeatCount="indefinite"/>')
    return f"""
    <g transform="translate(560 300)">
      <circle cy="-54" r="46" fill="url(#lampglow)">{glow}</circle>
      {body("scale(.55)")}
      <path d="M0 -20V-60" stroke="#3b2c30" stroke-width="3.2" stroke-linecap="round"/>
      <path d="M-9 -64H9L6 -76H-6Z" fill="#2f2428"/>
      <path d="M-7 -64H7L5 -50H-5Z" fill="#ffe29a" stroke="#2f2428" stroke-width="1.2">{glow}</path>
      <path d="M-5 -50H5L7 -46H-7Z" fill="#2f2428"/>
    </g>"""


def peak() -> str:
    return f"""
    <g transform="translate(230 500)">
      <ellipse cx="0" cy="10" rx="130" ry="46" fill="#7d6bb8" opacity="0.18"/>
      <path d="M-52 -20L-24 -108L-8 -94L26 -152L52 -98L66 -108L76 -20Z" fill="url(#mtn)" stroke="#2b1d22" stroke-width="1.4" stroke-linejoin="round"/>
      <path d="M26 -152L52 -98L66 -108L76 -20L40 -20Z" fill="#140c1c" opacity="0.25"/>
      <path d="M26 -152L44 -112L35 -116L27 -104L18 -117L8 -110Z" fill="#fffaf2" stroke="#2b1d22" stroke-width="1" stroke-linejoin="round"/>
      <path d="M-24 -108L-12 -90L-17 -94L-23 -88L-31 -97Z" fill="#fffaf2" stroke="#2b1d22" stroke-width="1" stroke-linejoin="round"/>
      <path d="M26 -152V-174" stroke="#3b2c30" stroke-width="2" stroke-linecap="round"/>
      <path d="M26 -174L42 -169L26 -164Z" fill="#c8453f"/>
      {body("scale(2 1.95)")}
      <g fill="#3f6b52" stroke="#1f3a2c" stroke-width="1">
        <path d="M-58 -52L-50 -76L-42 -52Z"/><path d="M-46 -54L-39 -72L-32 -54Z"/><path d="M52 -66L59 -86L66 -66Z"/>
      </g>
      <text x="0" y="120" fill="#f3e6d4" font-family="{SERIF}" font-size="16" text-anchor="middle">Peak Hunter</text>
    </g>"""


def books() -> str:
    return f"""
    <g transform="translate(560 660)">
      {body("scale(1.3)")}
      <g stroke="#2b1d22" stroke-width="1">
        <rect x="-44" y="-30" width="42" height="9" rx="1" fill="#8e3d4a"/>
        <rect x="-40" y="-39" width="36" height="9" rx="1" fill="#3f6b52"/>
        <rect x="-42" y="-48" width="38" height="9" rx="1" fill="#c4895a"/>
        <rect x="-38" y="-56" width="32" height="8" rx="1" fill="#4a5f8e"/>
      </g>
      <path d="M-6 -26H-2M-6 -35H-4M-6 -44H-4" stroke="#efe2c4" stroke-width="1.4" opacity="0.8"/>
      <g transform="translate(24 -42)">
        <path d="M-12 22H12" stroke="#5c3828" stroke-width="3" stroke-linecap="round"/>
        <path d="M-14 4A15 15 0 0 0 14 4" fill="none" stroke="#5c3828" stroke-width="1.6"/>
        <circle r="13" fill="url(#sea)" stroke="#2b1d22" stroke-width="1"/>
        <path d="M-8-3c4-4 8-3 10 0s-3 5-6 4-6-1-4-4z" fill="#3f8f6a" opacity="0.85"/>
        <path d="M-13 0H13" stroke="#e7fbff" stroke-width="0.6" opacity="0.5"/>
      </g>
      <path d="M-4 -6L36 -10L46 6L2 12Z" fill="#efe2c4" stroke="#2b1d22" stroke-width="1" stroke-linejoin="round"/>
      <path d="M14 -8L18 8M28 -9L30 4" stroke="#b7a07a" stroke-width="1"/>
      <path d="M32 -2L38 4M38 -2L32 4" stroke="#c8453f" stroke-width="1.6" stroke-linecap="round"/>
    </g>"""


def route(still: bool) -> str:
    spin = a(still, '<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="16s" repeatCount="indefinite"/>')
    return f"""
    <g transform="translate(250 860)">
      <circle r="86" fill="#5b9bd5" opacity="0.12"/>
      <g>{spin}<ellipse rx="108" ry="36" fill="none" stroke="#f0d7a2" stroke-width="1.6"/></g>
      <g fill="#fff1c2">
        <circle cx="-96" cy="-6" r="3.4"/><circle cx="-40" cy="-30" r="2.6"/>
        <circle cx="48" cy="-28" r="2.8"/><circle cx="100" cy="8" r="3.2"/>
      </g>
      <circle r="64" fill="url(#sea)" stroke="#102a4a" stroke-width="1.2"/>
      <path d="M-34-12c8-16 26-18 36-8 4 8-4 14-14 14-12 0-24 0-22-6z" fill="#3f8f6a"/>
      <path d="M10 14c8-8 26-8 32 2-4 14-22 18-32 8z" fill="#3f8f6a"/>
      <path d="M-20 30c8-4 16-3 20 3-8 5-16 5-20-3z" fill="#4e9f78"/>
      <g fill="#fff" opacity="0.8">
        <path d="M-62 -4c10-14 24-14 36-6-10 2-14 6-18 12-8 0-14-2-18-6z"/>
        <path d="M12 -44c14-6 30 0 36 10-12 0-20 2-26 8-6-4-10-10-10-18z" opacity="0.9"/>
        <path d="M-4 34c14-4 30 2 40-6-2 10-14 22-30 22-6-2-10-8-10-16z" opacity="0.7"/>
      </g>
      <circle r="64" fill="url(#atmo)"/>
      <circle r="64" fill="url(#shade)"/>
      <text x="0" y="116" fill="#f3e6d4" font-family="{SERIF}" font-size="16" text-anchor="middle">Jeepney Router</text>
    </g>"""


def sprout(still: bool) -> str:
    sway = a(still, '<animateTransform attributeName="transform" type="rotate" values="-3 0 -34;3 0 -34;-3 0 -34" dur="5s" repeatCount="indefinite"/>')
    return f"""
    <g transform="translate(560 980)">
      {body("scale(.9)")}
      <g>{sway}
        <path d="M0 -33C1 -46 -1 -58 0 -72" fill="none" stroke="#3f6b52" stroke-width="3" stroke-linecap="round"/>
        <path d="M0 -62C-14 -78 -30 -74 -32 -58C-18 -56 -6 -56 0 -62Z" fill="#6fae78" stroke="#1f3a2c" stroke-width="1.2" stroke-linejoin="round"/>
        <path d="M0 -70C14 -88 32 -82 32 -66C18 -64 6 -64 0 -70Z" fill="#8fd08f" stroke="#1f3a2c" stroke-width="1.2" stroke-linejoin="round"/>
        <path d="M-4 -62C-14 -68 -22 -68 -26 -62M4 -70C14 -76 22 -76 26 -72" fill="none" stroke="#2f5a42" stroke-width="1"/>
      </g>
    </g>"""


def rose(still: bool) -> str:
    fall1 = a(still, '<animate attributeName="cy" values="-20;40;-20" dur="9s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0.2;1" dur="9s" repeatCount="indefinite"/>')
    fall2 = a(still, '<animate attributeName="cy" values="-70;10;-70" dur="11s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.3;1;0.3" dur="11s" repeatCount="indefinite"/>')
    petal = 'd="M0 7C16-2 20-32 0-50 -20-32 -16-2 0 7Z"'
    inner = 'd="M0 5C12 0 14-22 0-36 -14-22 -12 0 0 5Z"'
    return f"""
    <g transform="translate(230 1260)">
      <ellipse cx="0" cy="72" rx="48" ry="9" fill="#000" opacity="0.22"/>
      {body("translate(0 66) scale(.85)")}
      <g transform="translate(0 34) scale(.72) translate(0 -34)">
        <path d="M-2 42C-6 -6 6 -62 -10 -108" fill="none" stroke="#4f7a52" stroke-width="4.5" stroke-linecap="round"/>
        <path d="M-6 -16C-32 -28 -46 -44 -54 -62C-30 -52 -16 -36 -6 -18" fill="#3f6b52" stroke="#1f3a2c" stroke-width="1"/>
        <g transform="translate(-8 -118)">
          <path {petal} fill="#7a2434"/>
          <path {petal} fill="#7a2434" transform="rotate(60)"/>
          <path {petal} fill="#7a2434" transform="rotate(120)"/>
          <path {inner} fill="#d36a74" transform="rotate(30)"/>
          <path {inner} fill="#d36a74" transform="rotate(90)"/>
          <path {inner} fill="#d36a74" transform="rotate(150)"/>
          <circle r="5" fill="#f8e4dc"/>
        </g>
        <ellipse cx="-54" cy="-20" rx="6" ry="3.5" fill="#e7a0a8">{fall1}</ellipse>
        <ellipse cx="36" cy="-70" rx="7" ry="4" fill="#e7a0a8">{fall2}</ellipse>
      </g>
      <ellipse cx="0" cy="34" rx="42" ry="7" fill="none" stroke="#d5e8ff" stroke-opacity="0.4" stroke-width="1.2"/>
      <path d="M-42 34C-46 -40 -24 -128 0 -128 24 -128 46 -40 42 34Z" fill="url(#glass)" stroke="#d5e8ff" stroke-opacity="0.4" stroke-width="1.4"/>
      <path d="M-33 -10C-35 -56 -22 -104 -8 -116" fill="none" stroke="#fff" stroke-opacity="0.45" stroke-width="2" stroke-linecap="round"/>
    </g>"""


def drawer(still: bool) -> str:
    p1 = a(still, '<animate attributeName="y" values="-30;-62;-30" dur="7s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.9;0.15;0.9" dur="7s" repeatCount="indefinite"/>')
    p2 = a(still, '<animate attributeName="y" values="-24;-58;-24" dur="9s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.8;0.1;0.8" dur="9s" repeatCount="indefinite"/>')
    return f"""
    <g transform="translate(540 1380) scale(1.3)">
      <rect x="-10" y="-30" width="8" height="11" fill="#fffaf2" opacity="0.9" transform="rotate(-14)">{p1}</rect>
      <rect x="14" y="-24" width="7" height="10" fill="#fffaf2" opacity="0.8" transform="rotate(18)">{p2}</rect>
      {body("translate(0 50) scale(.9)")}
      <g stroke="#2b1d22" stroke-width="1.1" stroke-linejoin="round">
        <rect x="-26" y="-9" width="52" height="6" rx="1" fill="#c4895a"/>
        <rect x="-22" y="-3" width="44" height="14" fill="url(#wood)"/>
        <rect x="-17" y="2" width="34" height="6" fill="#ffe29a"/>
        <rect x="-4" y="4" width="8" height="2" fill="#fff" stroke="none"/>
        <rect x="-24" y="11" width="4" height="9" fill="#7a4a30"/><rect x="20" y="11" width="4" height="9" fill="#7a4a30"/>
      </g>
      <ellipse cx="0" cy="9" rx="24" ry="8" fill="url(#glow)"/>
      <rect x="34" y="6" width="10" height="3" rx="1" fill="#7a4a30" stroke="#2b1d22" stroke-width="1"/>
      <path d="M36 9V20M42 9V20" stroke="#2b1d22" stroke-width="1.6"/>
    </g>"""


# ---------------------------------------------------------------- build
def build(still: bool) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="sceneTitle sceneDesc">
  <title id="sceneTitle">A portrait sky</title>
  <desc id="sceneDesc">A tall storybook galaxy. Peak Hunter and Jeepney Router share the sky with a glass-domed rose, a desk with a drawer, and unnamed worlds holding a ring, a lantern, books, and a sprout. Stars and dust move through the same background.</desc>
{DEFS}
  <g mask="url(#my)"><g mask="url(#mx)">
  <rect width="{W}" height="{H}" fill="url(#space)"/>
  {clouds(still)}
  {band()}
  {dust(still)}
  {stars(still)}
  {rocks()}
  {ring_world(still)}
  {moon(still)}
  {lantern(still)}
  {peak()}
  {books()}
  {route(still)}
  {sprout(still)}
  {rose(still)}
  {drawer(still)}
  </g></g>
</svg>
"""


def standalone(
    title: str,
    description: str,
    view_box: tuple[int, int, int, int],
    content: str,
) -> str:
    """Wrap one scene element in its own self-contained SVG card."""
    x, y, width, height = view_box
    blur = round(min(width, height) * 0.035, 1)
    inset = round(blur * 3, 1)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {width} {height}" role="img" aria-labelledby="assetTitle assetDesc">
  <title id="assetTitle">{title}</title>
  <desc id="assetDesc">{description}</desc>
{DEFS}
  <defs>
    <filter id="assetEdgeBlur" x="{x}" y="{y}" width="{width}" height="{height}" filterUnits="userSpaceOnUse">
      <feGaussianBlur stdDeviation="{blur}"/>
    </filter>
    <mask id="assetEdgeFade" x="{x}" y="{y}" width="{width}" height="{height}" maskUnits="userSpaceOnUse">
      <rect x="{x + inset}" y="{y + inset}" width="{width - inset * 2}" height="{height - inset * 2}" rx="18" fill="#fff" filter="url(#assetEdgeBlur)"/>
    </mask>
  </defs>
  <g mask="url(#assetEdgeFade)">
  <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="url(#space)"/>
  <ellipse cx="{x + width * 0.28}" cy="{y + height * 0.25}" rx="{width * 0.42}" ry="{height * 0.2}" fill="url(#cloudViolet)"/>
  <ellipse cx="{x + width * 0.78}" cy="{y + height * 0.72}" rx="{width * 0.45}" ry="{height * 0.2}" fill="url(#cloudPink)"/>
  {content}
  </g>
</svg>
"""


def write_individual_assets(assets: Path) -> None:
    """Export the scene's missing worlds as reusable animated SVG files."""
    specs = (
        (
            "ring-world",
            "The ringed world",
            "A tiny rocky world with a turning ring, an orbiting moon, and a small hat.",
            (58, 48, 224, 224),
            lambda still: ring_world(still) + moon(still),
        ),
        (
            "lantern-world",
            "The lantern world",
            "A tiny rocky world carrying a softly glowing lantern.",
            (462, 174, 196, 196),
            lantern,
        ),
        (
            "books-world",
            "The books world",
            "A tiny rocky world with a stack of books, a globe, and an open map.",
            (458, 550, 204, 196),
            lambda _still: books(),
        ),
        (
            "sprout-world",
            "The sprout world",
            "A tiny rocky world with a gently swaying green sprout.",
            (472, 864, 176, 190),
            sprout,
        ),
    )

    for filename, title, description, view_box, render in specs:
        (assets / f"{filename}.svg").write_text(
            standalone(title, description, view_box, render(False)),
            encoding="utf-8",
        )
        (assets / f"{filename}-still.svg").write_text(
            standalone(title, description, view_box, render(True)),
            encoding="utf-8",
        )


PREVIEW_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Worlds in the portrait sky</title>
  <style>
    :root { color-scheme: dark; font-family: Palatino, Georgia, serif; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: #f3e6d4;
      background:
        radial-gradient(circle at 50% 0%, #2a2142 0, #151029 34rem, #090712 72rem);
    }
    main { width: min(1040px, calc(100% - 32px)); margin: 0 auto; padding: 72px 0 96px; }
    header { max-width: 680px; margin-bottom: 42px; }
    .eyebrow { color: #e7b4c4; font-size: 0.78rem; letter-spacing: 0.18em; text-transform: uppercase; }
    h1 { margin: 10px 0 14px; font-size: clamp(2.6rem, 8vw, 5.8rem); font-weight: 400; line-height: 0.94; }
    header p { max-width: 58ch; color: #cdbfd2; font-size: 1.06rem; line-height: 1.7; }
    .gallery { display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }
    figure {
      grid-column: span 4;
      margin: 0;
      overflow: hidden;
      border: 1px solid rgba(231, 180, 196, 0.16);
      border-radius: 22px;
      background: rgba(20, 16, 40, 0.72);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
    }
    figure.wide { grid-column: span 8; }
    figure img { display: block; width: 100%; aspect-ratio: 1.15; object-fit: cover; }
    figure.wide img { aspect-ratio: 2.2; }
    figcaption { padding: 15px 17px 18px; color: #d9ccdc; }
    figcaption strong { display: block; margin-bottom: 5px; color: #fff6d8; font-weight: 400; font-size: 1.08rem; }
    figcaption span { color: #998da2; font-size: 0.83rem; }
    details { margin-top: 34px; color: #a99cad; }
    summary { cursor: pointer; width: fit-content; }
    details img { display: block; width: min(460px, 100%); margin: 20px auto 0; }
    @media (max-width: 760px) {
      main { padding-top: 48px; }
      figure, figure.wide { grid-column: span 6; }
      figure.wide img { aspect-ratio: 1.35; }
    }
    @media (max-width: 500px) {
      figure, figure.wide { grid-column: 1 / -1; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="eyebrow">A portfolio in orbit</div>
      <h1>Worlds from one sky</h1>
      <p>Each illustration now lives as its own reusable asset—small worlds that can move, change, and find their own place without being locked into one scene.</p>
    </header>
    <section class="gallery" aria-label="Individual portfolio illustrations">
      <figure class="wide">
        <picture><source media="(prefers-reduced-motion: reduce)" srcset="assets/sky-still.svg"><img src="assets/sky.svg" alt="A painted galaxy filled with labeled stars."></picture>
        <figcaption><strong>Constellation</strong><span>Tools, skills, and discoveries</span></figcaption>
      </figure>
      <figure>
        <picture><source media="(prefers-reduced-motion: reduce)" srcset="assets/ring-world-still.svg"><img src="assets/ring-world.svg" alt="A tiny ringed world with an orbiting moon."></picture>
        <figcaption><strong>The ringed world</strong><span>Still unnamed</span></figcaption>
      </figure>
      <figure>
        <picture><source media="(prefers-reduced-motion: reduce)" srcset="assets/lantern-world-still.svg"><img src="assets/lantern-world.svg" alt="A rocky world carrying a glowing lantern."></picture>
        <figcaption><strong>The lantern world</strong><span>Still unnamed</span></figcaption>
      </figure>
      <figure>
        <img src="assets/planet-peak.svg" alt="A small rocky world with a snowy mountain.">
        <figcaption><strong>Peak Hunter</strong><span>Private project</span></figcaption>
      </figure>
      <figure>
        <picture><source media="(prefers-reduced-motion: reduce)" srcset="assets/books-world-still.svg"><img src="assets/books-world.svg" alt="A rocky world with books, a globe, and an open map."></picture>
        <figcaption><strong>The books world</strong><span>Still unnamed</span></figcaption>
      </figure>
      <figure>
        <img src="assets/planet-route.svg" alt="A blue world circled by a route of warm lights.">
        <figcaption><strong>Jeepney Router</strong><span>Private project</span></figcaption>
      </figure>
      <figure>
        <picture><source media="(prefers-reduced-motion: reduce)" srcset="assets/sprout-world-still.svg"><img src="assets/sprout-world.svg" alt="A rocky world with a gently swaying sprout."></picture>
        <figcaption><strong>The sprout world</strong><span>Still unnamed</span></figcaption>
      </figure>
      <figure>
        <img src="assets/rose.svg" alt="A rose growing from a tiny asteroid.">
        <figcaption><strong>The rose</strong><span>What is cared for</span></figcaption>
      </figure>
      <figure>
        <img src="assets/drawer.svg" alt="A tiny world with an open wooden drawer.">
        <figcaption><strong>The drawer</strong><span>A note waiting to be found</span></figcaption>
      </figure>
      <figure class="wide">
        <img src="assets/path.svg" alt="A trail of warm stars crossing the galaxy.">
        <figcaption><strong>The path</strong><span>What comes next</span></figcaption>
      </figure>
    </section>
    <details>
      <summary>View the original composed scene</summary>
      <picture><source media="(prefers-reduced-motion: reduce)" srcset="assets/scene-still.svg"><img src="assets/scene.svg" alt="The original tall portrait galaxy combining all the worlds."></picture>
    </details>
  </main>
</body>
</html>
"""


def main():
    root = Path(__file__).resolve().parents[1]
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "scene.svg").write_text(build(False), encoding="utf-8")
    (assets / "scene-still.svg").write_text(build(True), encoding="utf-8")
    write_individual_assets(assets)
    preview = root / "preview.html"
    preview.write_text(PREVIEW_HTML, encoding="utf-8")


if __name__ == "__main__":
    main()
