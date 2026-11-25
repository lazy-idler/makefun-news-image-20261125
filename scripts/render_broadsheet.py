"""Deterministic 1024x1024 world news broadsheet renderer for Wednesday, 25 November 2026."""

from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSET_OUT = ROOT / "assets" / "entry.png"
SCRATCH_DIR = Path(r"C:\Users\82103\.gemini\antigravity\brain\c8bbd2ac-e3a5-415b-8afb-bf347f8e20ad\scratch")
PREVIEW_300 = SCRATCH_DIR / "preview_300_v13.png"


def proj(lon: float, lat: float) -> tuple[float, float]:
    """Project (lon, lat) onto 464x146 equirectangular SVG canvas."""
    x = (lon + 180.0) / 360.0 * 464.0
    y = (75.0 - lat) / 133.0 * 146.0
    return round(x, 1), round(y, 1)


def poly_pts(coords: list[tuple[float, float]]) -> str:
    return " ".join(f"{proj(lon, lat)[0]},{proj(lon, lat)[1]}" for lon, lat in coords)


CONTINENTS = [
    # North & Central America
    [(-168, 65), (-140, 70), (-110, 70), (-82, 65), (-62, 52), (-54, 47), (-67, 45),
     (-75, 36), (-81, 25), (-83, 30), (-90, 29), (-97, 26), (-96, 19), (-88, 21),
     (-84, 10), (-78, 8), (-85, 11), (-92, 15), (-105, 20), (-112, 28), (-117, 32),
     (-124, 41), (-125, 49), (-136, 58), (-152, 60), (-165, 55)],
    # Greenland
    [(-52, 60), (-43, 60), (-20, 71), (-25, 74), (-55, 74), (-60, 68)],
    # South America
    [(-78, 9), (-72, 12), (-61, 10), (-50, 1), (-35, -6), (-38, -14), (-41, -22),
     (-49, -28), (-55, -35), (-63, -41), (-68, -54), (-74, -52), (-73, -42),
     (-71, -30), (-70, -18), (-77, -12), (-81, -5), (-79, 2)],
    # Africa
    [(-17, 15), (-13, 28), (-6, 36), (10, 37), (12, 33), (25, 32), (32, 31),
     (39, 22), (43, 12), (51, 12), (49, 4), (41, -2), (40, -11), (35, -20),
     (32, -26), (26, -34), (18, -35), (14, -22), (12, -12), (9, 4), (2, 6),
     (-8, 5), (-16, 11)],
    # Madagascar
    [(44, -25), (47, -25), (50, -15), (49, -12), (45, -18)],
    # Europe
    [(-9, 37), (-9, 43), (-2, 44), (-5, 48), (2, 51), (8, 54), (10, 58), (5, 61),
     (16, 69), (28, 71), (42, 68), (60, 68), (55, 55), (44, 47), (36, 46), (29, 41),
     (24, 38), (18, 40), (15, 38), (12, 42), (7, 44), (3, 42), (-5, 36)],
    # UK & Ireland
    [(-6, 50), (1, 51), (1, 53), (-2, 58), (-6, 58), (-5, 54)],
    [(-10, 52), (-6, 52), (-6, 55), (-10, 54)],
    # Asia
    [(27, 41), (36, 37), (35, 30), (39, 21), (44, 13), (54, 17), (59, 22), (56, 26),
     (50, 29), (57, 25), (67, 24), (72, 20), (77, 8), (82, 16), (88, 22), (92, 21),
     (97, 16), (100, 13), (104, 2), (105, 9), (109, 13), (108, 21), (114, 22),
     (121, 25), (122, 31), (119, 35), (122, 38), (126, 35), (129, 35), (129, 40),
     (135, 44), (141, 52), (138, 58), (150, 60), (162, 60), (174, 65), (160, 70),
     (130, 72), (104, 74), (75, 72), (60, 68), (55, 55), (44, 47), (39, 45), (29, 41)],
    # Japan
    [(130, 32), (135, 34), (140, 36), (141, 41), (145, 44), (141, 45), (139, 39), (134, 35)],
    # SE Asia / New Guinea
    [(95, 5), (105, -6), (114, -8), (112, -6), (101, 0)],
    [(109, 1), (118, 5), (117, -3), (110, -3)],
    [(132, -2), (141, -3), (150, -9), (145, -9), (136, -5)],
    # Australia & NZ
    [(114, -22), (122, -17), (131, -12), (137, -15), (142, -11), (146, -18),
     (153, -27), (150, -37), (141, -38), (136, -34), (129, -32), (115, -34), (114, -27)],
    [(167, -46), (173, -41), (178, -37), (175, -35), (172, -41), (166, -45)],
]


def build_map_svg() -> str:
    polys = "\n".join(
        f'<polygon points="{poly_pts(c)}" fill="#EDE3CE" stroke="#64748B" stroke-width="0.95" stroke-linejoin="round"/>'
        for c in CONTINENTS
    )
    pins = [
        (1, 99.0, 40.9, "#1E3A8A", -8, -12),    # Jiuquan Space
        (2, 127.0, 37.5, "#DC2626", 14, -2),    # Seoul / Asia Chips
        (3, 56.3, 26.6, "#EA580C", 2, 2),       # Hormuz
        (4, 158.0, -10.5, "#0F766E", 8, -2),    # Australia-Solomons
        (5, 90.4, 23.8, "#B45309", -2, 11),     # Dhaka
        (6, 30.5, 50.4, "#4338CA", 8, -4),      # Ukraine Diplomacy
        (7, 20.1, 32.1, "#0E7490", -2, 6),      # Benghazi, Libya
        (8, -66.9, 8.0, "#9D174D", 4, 10),      # Venezuela Debt
        (9, -0.1, 51.5, "#334155", -14, -3),    # London UK
        (10, -77.0, 38.9, "#1D4ED8", -10, 4),   # Washington D.C. Tariffs
    ]
    wx, wy = proj(-77.0, 38.9)
    kx, ky = proj(30.5, 50.4)
    ax, ay = proj(149.1, -35.3)
    sx, sy = proj(160.0, -9.4)

    arc_us_eu = (
        f'<path d="M {wx} {wy} Q {(wx+kx)/2} {min(wy,ky)-22} {kx} {ky}" '
        f'fill="none" stroke="#4338CA" stroke-width="1.7" stroke-dasharray="3.5,2.5"/>'
    )
    arc_aus_sol = (
        f'<path d="M {ax} {ay} Q {ax+11} {(ay+sy)/2} {sx} {sy}" '
        f'fill="none" stroke="#0F766E" stroke-width="2.1"/>'
        f'<circle cx="{sx}" cy="{sy}" r="3" fill="#0F766E" stroke="#FFF" stroke-width="1"/>'
    )

    markers = []
    for num, lon, lat, color, dx, dy in pins:
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        leader = ""
        if dx != 0 or dy != 0:
            leader = f'<line x1="{px}" y1="{py}" x2="{cx}" y2="{cy}" stroke="{color}" stroke-width="1.4"/>'
        markers.append(
            f'{leader}'
            f'<circle cx="{cx}" cy="{cy}" r="10.2" fill="{color}" stroke="#FFFFFF" stroke-width="1.9"/>'
            f'<text x="{cx}" y="{cy+3.7}" text-anchor="middle" fill="#FFFFFF" font-family="Segoe UI, Arial, sans-serif" font-size="11" font-weight="900">{num}</text>'
        )

    return f"""
    <svg viewBox="0 0 464 146" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:146px;border-radius:6px;border:1px solid #B5C8D8;">
      <defs>
        <radialGradient id="oceanGrad" cx="50%" cy="50%" r="65%">
          <stop offset="0%" stop-color="#DFEEF7"/>
          <stop offset="100%" stop-color="#C8DFEE"/>
        </radialGradient>
      </defs>
      <rect x="0" y="0" width="464" height="146" fill="url(#oceanGrad)"/>
      <g opacity="0.35" stroke="#8FADBE" stroke-width="0.6">
        <line x1="0" y1="73" x2="464" y2="73" stroke-dasharray="4,4"/>
        <line x1="232" y1="0" x2="232" y2="146" stroke-dasharray="4,4"/>
      </g>
      {polys}
      {arc_us_eu}
      {arc_aus_sol}
      {''.join(markers)}
    </svg>
    """


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 1024px;
    height: 1024px;
    overflow: hidden;
    background: #F4EFE3;
    color: #0F172A;
    font-family: "Segoe UI", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .page {{
    width: 1024px;
    height: 1024px;
    padding: 11px 16px 11px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .masthead {{
    border-top: 4px solid #0B1320;
    border-bottom: 3px double #0B1320;
    padding: 3px 0 4px 0;
    text-align: center;
  }}
  .mast-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #334155;
    text-transform: uppercase;
    margin-bottom: 1px;
  }}
  .mast-date {{
    font-family: Georgia, "Times New Roman", serif;
    font-size: 47px;
    font-weight: 900;
    letter-spacing: 0.4px;
    line-height: 1.02;
    color: #0B1320;
  }}
  .row-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }}
  .row-3 {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
  }}
  .row-4 {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 9px;
    flex: 1;
  }}
  .card {{
    background: #FFFDF9;
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 4px rgba(15, 23, 42, 0.06);
  }}
  .card-bar {{
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 4px 10px;
    color: #FFFFFF;
    font-size: 13.5px;
    font-weight: 800;
    letter-spacing: 0.45px;
    text-transform: uppercase;
  }}
  .num-pill {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 19px;
    height: 19px;
    border-radius: 50%;
    background: rgba(255,255,255,0.25);
    border: 1.5px solid #FFFFFF;
    font-size: 12px;
    font-weight: 900;
    flex-shrink: 0;
  }}
  .card-body {{
    padding: 7px 10px 7px 10px;
    display: flex;
    flex-direction: column;
    gap: 5px;
    flex: 1;
  }}
  .hl-lg {{
    font-size: 23.5px;
    font-weight: 900;
    line-height: 1.06;
    letter-spacing: -0.25px;
    color: #0B1320;
  }}
  .hl-sm {{
    font-size: 19.5px;
    font-weight: 900;
    line-height: 1.07;
    letter-spacing: -0.25px;
    color: #0B1320;
  }}
  .hl-xs {{
    font-size: 17px;
    font-weight: 900;
    line-height: 1.07;
    letter-spacing: -0.25px;
    color: #0B1320;
  }}
  .facts {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 5px;
    font-size: 17px;
    line-height: 1.18;
    color: #1E293B;
    font-weight: 700;
  }}
  .facts li::before {{
    content: "▸ ";
    font-weight: 900;
  }}
  .facts strong {{
    color: #0B1320;
    font-weight: 900;
  }}
  .split-h {{
    display: grid;
    grid-template-columns: 186px 1fr;
    gap: 10px;
    align-items: center;
    flex: 1;
  }}
  .map-legend {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 3px 4px;
    font-size: 12.2px;
    font-weight: 800;
    color: #1E293B;
    padding-top: 2px;
  }}
  .leg-item {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
  }}
  .dot {{
    width: 14px;
    height: 14px;
    border-radius: 50%;
    color: #FFF;
    font-size: 9.5px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    flex-shrink: 0;
  }}
  .art-box {{
    width: 100%;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #CFD9E3;
  }}
  .bars {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .bar-row {{
    display: grid;
    grid-template-columns: 92px 1fr 64px;
    align-items: center;
    gap: 6px;
    font-size: 15.5px;
    font-weight: 800;
    color: #1E293B;
  }}
  .bar-track {{
    height: 14px;
    background: #FEE2E2;
    border-radius: 4px;
    overflow: hidden;
  }}
  .bar-fill {{
    height: 100%;
    background: #DC2626;
    border-radius: 4px;
  }}
  .bar-val {{
    text-align: right;
    color: #B91C1C;
    font-weight: 900;
  }}
  .wire-fact {{
    font-size: 14.8px;
    line-height: 1.16;
    font-weight: 700;
    color: #1E293B;
  }}
</style>
</head>
<body>
<div class="page">

  <header class="masthead">
    <div class="mast-top">
      <span>ALL-CONTINENT WORLD BRIEF &middot; 25 NOV 2026</span>
      <span>10 STORIES &middot; 6 CONTINENTS &middot; VERIFIED</span>
    </div>
    <div class="mast-date">WEDNESDAY &middot; 25 NOVEMBER 2026</div>
  </header>

  <!-- ROW 1: GLOBAL MAP (10 PINS + LEGEND) + STORY 1 (SPACE) -->
  <section class="row-2" style="height: 222px;">
    <div class="card">
      <div class="card-bar" style="background:#0F172A;">
        <span>GLOBAL DISPATCH MAP &middot; 10 STORIES</span>
      </div>
      <div class="card-body" style="padding: 6px 9px 5px 9px; gap: 4px;">
        {MAP_SVG}
        <div class="map-legend">
          <span class="leg-item"><span class="dot" style="background:#1E3A8A;">1</span>SPACE</span>
          <span class="leg-item"><span class="dot" style="background:#DC2626;">2</span>CHIPS</span>
          <span class="leg-item"><span class="dot" style="background:#EA580C;">3</span>HORMUZ</span>
          <span class="leg-item"><span class="dot" style="background:#0F766E;">4</span>PACIFIC</span>
          <span class="leg-item"><span class="dot" style="background:#B45309;">5</span>DHAKA</span>
          <span class="leg-item"><span class="dot" style="background:#4338CA;">6</span>UKRAINE</span>
          <span class="leg-item"><span class="dot" style="background:#0E7490;">7</span>LIBYA</span>
          <span class="leg-item"><span class="dot" style="background:#9D174D;">8</span>DEBT</span>
          <span class="leg-item"><span class="dot" style="background:#334155;">9</span>UK</span>
          <span class="leg-item"><span class="dot" style="background:#1D4ED8;">10</span>U.S.</span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#1E3A8A;">
        <span class="num-pill">1</span>
        <span>EAST ASIA &middot; SPACE &amp; SCIENCE</span>
      </div>
      <div class="card-body">
        <div class="hl-lg">CHINA LAUNCHES SHENZHOU-24</div>
        <div class="split-h">
          <div class="art-box" style="height: 142px;">
            <svg viewBox="0 0 186 142" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(180deg,#08142E 0%,#1A366E 100%);">
              <circle cx="20" cy="18" r="1.6" fill="#FFF" opacity="0.85"/>
              <circle cx="52" cy="13" r="1.2" fill="#FFF" opacity="0.7"/>
              <circle cx="164" cy="14" r="1.5" fill="#FFF" opacity="0.85"/>
              <path d="M 46 66 Q 70 28 112 24" fill="none" stroke="#93C5FD" stroke-width="1.6" stroke-dasharray="3,3" opacity="0.8"/>
              <ellipse cx="93" cy="160" rx="132" ry="30" fill="#1D4ED8" stroke="#60A5FA" stroke-width="2"/>
              <g transform="translate(122,24)">
                <rect x="-26" y="6" width="52" height="7" rx="2" fill="#E2E8F0"/>
                <rect x="-4" y="-11" width="8" height="32" rx="2" fill="#CBD5E1"/>
                <rect x="-32" y="-8" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="12" y="-8" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="-32" y="15" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="12" y="15" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <text x="0" y="37" text-anchor="middle" fill="#BAE6FD" font-size="9" font-weight="900">TIANGONG</text>
              </g>
              <g transform="translate(46,74) rotate(-25)">
                <path d="M-9,25 L0,52 L9,25 Z" fill="#F97316"/>
                <path d="M-4.5,25 L0,41 L4.5,25 Z" fill="#FDE047"/>
                <rect x="-7" y="-22" width="14" height="47" rx="3" fill="#F8FAFC"/>
                <polygon points="-7,-22 0,-39 7,-22" fill="#EF4444"/>
                <rect x="-12" y="6" width="5" height="19" rx="1.5" fill="#E2E8F0"/>
                <rect x="7" y="6" width="5" height="19" rx="1.5" fill="#E2E8F0"/>
              </g>
              <rect x="102" y="76" width="34" height="22" rx="2" fill="#DE2910" stroke="#FFF" stroke-width="1.1"/>
              <polygon points="110,81 111.5,85 115.5,85 112.2,87.5 113.5,91.5 110,89 106.5,91.5 107.8,87.5 104.5,85 108.5,85" fill="#FFDE00"/>
              <rect x="142" y="76" width="34" height="22" rx="2" fill="#01411C" stroke="#FFF" stroke-width="1.1"/>
              <rect x="142" y="76" width="8" height="22" fill="#FFF"/>
              <circle cx="161" cy="87" r="5" fill="#FFF"/>
              <circle cx="163" cy="85.5" r="4" fill="#01411C"/>
              <text x="139" y="115" text-anchor="middle" fill="#F8FAFC" font-size="12" font-weight="900">CN + PK CREW</text>
            </svg>
          </div>
          <ul class="facts">
            <li><strong>First foreign astronaut</strong> reaches Tiangong</li>
            <li>Pakistan's <strong>M. Zeeshan Ali</strong> + 2 crew</li>
            <li><strong>08:18 BJT</strong> (00:18 UTC) &middot; Jiuquan</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- ROW 2: MARKETS + HORMUZ -->
  <section class="row-2" style="height: 232px;">
    <div class="card">
      <div class="card-bar" style="background:#DC2626;">
        <span class="num-pill">2</span>
        <span>GLOBAL MARKETS &middot; AI &amp; TECH</span>
      </div>
      <div class="card-body">
        <div class="hl-lg">ASIAN AI &amp; CHIP STOCKS PLUNGE</div>
        <div class="split-h">
          <div class="art-box" style="height: 146px;">
            <svg viewBox="0 0 186 146" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#FFF5F5;">
              <defs>
                <linearGradient id="crashArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#DC2626" stop-opacity="0.28"/>
                  <stop offset="100%" stop-color="#DC2626" stop-opacity="0.03"/>
                </linearGradient>
              </defs>
              <line x1="12" y1="38" x2="174" y2="38" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <line x1="12" y1="76" x2="174" y2="76" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <polygon points="14,44 46,48 74,62 100,58 128,92 162,112 162,118 14,118" fill="url(#crashArea)"/>
              <polyline points="14,44 46,48 74,62 100,58 128,92 162,112" fill="none" stroke="#DC2626" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
              <polygon points="168,116 150,115 160,103" fill="#DC2626"/>
              <rect x="12" y="8" width="114" height="25" rx="5" fill="#991B1B"/>
              <text x="69" y="25.5" text-anchor="middle" fill="#FFF" font-size="14" font-weight="900">KOSPI -6.2%</text>
              <g transform="translate(140,7)">
                <rect x="4" y="4" width="24" height="24" rx="3" fill="#1E293B" stroke="#DC2626" stroke-width="1.6"/>
                <text x="16" y="19.5" text-anchor="middle" fill="#FECACA" font-size="9.5" font-weight="900">AI</text>
                <line x1="10" y1="0" x2="10" y2="4" stroke="#64748B" stroke-width="2"/>
                <line x1="22" y1="0" x2="22" y2="4" stroke="#64748B" stroke-width="2"/>
                <line x1="10" y1="28" x2="10" y2="32" stroke="#64748B" stroke-width="2"/>
                <line x1="22" y1="28" x2="22" y2="32" stroke="#64748B" stroke-width="2"/>
                <line x1="0" y1="10" x2="4" y2="10" stroke="#64748B" stroke-width="2"/>
                <line x1="0" y1="22" x2="4" y2="22" stroke="#64748B" stroke-width="2"/>
                <line x1="28" y1="10" x2="32" y2="10" stroke="#64748B" stroke-width="2"/>
                <line x1="28" y1="22" x2="32" y2="22" stroke="#64748B" stroke-width="2"/>
              </g>
              <rect x="12" y="119" width="162" height="20" rx="4" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.4"/>
              <text x="93" y="133" text-anchor="middle" fill="#991B1B" font-size="11.5" font-weight="900">SIDECAR TRIGGERED</text>
            </svg>
          </div>
          <div style="display:flex;flex-direction:column;justify-content:space-between;height:100%;">
            <div class="bars">
              <div class="bar-row"><span>SK HYNIX</span><div class="bar-track"><div class="bar-fill" style="width:100%;"></div></div><span class="bar-val">-11.1%</span></div>
              <div class="bar-row"><span>SAMSUNG</span><div class="bar-track"><div class="bar-fill" style="width:89%;"></div></div><span class="bar-val">-9.9%</span></div>
              <div class="bar-row"><span>KOSPI</span><div class="bar-track"><div class="bar-fill" style="width:56%;"></div></div><span class="bar-val">-6.2%</span></div>
              <div class="bar-row"><span>TAIEX</span><div class="bar-track"><div class="bar-fill" style="width:45%;"></div></div><span class="bar-val">-5.0%</span></div>
              <div class="bar-row"><span>NIKKEI</span><div class="bar-track"><div class="bar-fill" style="width:26%;"></div></div><span class="bar-val">-2.8%</span></div>
            </div>
            <div style="font-size:14.8px;font-weight:700;color:#1E293B;border-top:1px solid #E2E8F0;padding-top:4px;white-space:nowrap;">
              Seoul: <strong>4,697.51</strong> (-308.5), 10-mo low
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#EA580C;">
        <span class="num-pill">3</span>
        <span>MIDDLE EAST &middot; ENERGY &amp; CONFLICT</span>
      </div>
      <div class="card-body">
        <div class="hl-lg">2 TANKERS HIT MINES IN HORMUZ</div>
        <div class="split-h">
          <div class="art-box" style="height: 146px;">
            <svg viewBox="0 0 186 142" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#1A365D;">
              <polygon points="0,0 186,0 186,44 134,34 106,27 78,39 0,37" fill="#D6C7A9" stroke="#78716C" stroke-width="1"/>
              <polygon points="0,96 60,84 94,96 108,68 124,82 142,126 186,142 0,142" fill="#E7D8B9" stroke="#78716C" stroke-width="1"/>
              <text x="10" y="19" fill="#44403C" font-size="11.5" font-weight="900">IRAN</text>
              <text x="9" y="135" fill="#44403C" font-size="10.5" font-weight="900">SAUDI / UAE</text>
              <text x="144" y="48" text-anchor="middle" fill="#BAE6FD" font-size="9" font-weight="900" font-style="italic">HORMUZ</text>
              <g transform="translate(88,56)">
                <circle cx="8" cy="-16" r="5" fill="#64748B" opacity="0.65"/>
                <circle cx="13" cy="-22" r="6" fill="#94A3B8" opacity="0.5"/>
                <polygon points="-21,6 21,6 26,0 -19,0" fill="#0F172A"/>
                <rect x="-13" y="-6" width="8" height="6" fill="#F8FAFC"/>
                <path d="M1,0 Q8,-15 15,0 Q10,-21 1,-14 Z" fill="#F97316"/>
                <path d="M4,0 Q9,-9 13,0 Z" fill="#FDE047"/>
              </g>
              <g transform="translate(144,72)">
                <circle cx="7" cy="-15" r="4.5" fill="#64748B" opacity="0.65"/>
                <circle cx="11" cy="-21" r="5.5" fill="#94A3B8" opacity="0.5"/>
                <polygon points="-18,6 18,6 23,0 -16,0" fill="#0F172A"/>
                <rect x="-11" y="-5" width="7" height="5" fill="#F8FAFC"/>
                <path d="M0,0 Q7,-13 13,0 Q9,-19 0,-12 Z" fill="#EF4444"/>
                <path d="M3,0 Q7,-8 11,0 Z" fill="#FDE047"/>
              </g>
              <circle cx="44" cy="65" r="8.5" fill="#0F172A" stroke="#F8FAFC" stroke-width="1.6"/>
              <line x1="44" y1="51" x2="44" y2="79" stroke="#F8FAFC" stroke-width="2"/>
              <line x1="30" y1="65" x2="58" y2="65" stroke="#F8FAFC" stroke-width="2"/>
              <line x1="34" y1="55" x2="54" y2="75" stroke="#F8FAFC" stroke-width="2"/>
              <line x1="34" y1="75" x2="54" y2="55" stroke="#F8FAFC" stroke-width="2"/>
              <path d="M 12 114 A 21 21 0 0 1 51 105" fill="none" stroke="#DC2626" stroke-width="1.9" stroke-dasharray="3,2"/>
              <g stroke="#DC2626" stroke-width="2.1" stroke-linecap="round">
                <line x1="16" y1="98" x2="22" y2="104"/><line x1="22" y1="98" x2="16" y2="104"/>
                <line x1="27" y1="94" x2="33" y2="100"/><line x1="33" y1="94" x2="27" y2="100"/>
                <line x1="39" y1="97" x2="45" y2="103"/><line x1="45" y1="97" x2="39" y2="103"/>
              </g>
              <rect x="52" y="96" width="60" height="22" rx="3" fill="#991B1B"/>
              <text x="82" y="106" text-anchor="middle" fill="#FFF" font-size="9.2" font-weight="900">4 DRONES</text>
              <text x="82" y="115" text-anchor="middle" fill="#FECACA" font-size="8.2" font-weight="800">DOWNED</text>
            </svg>
          </div>
          <ul class="facts">
            <li><strong>2 oil tankers burn</strong> after hitting mines</li>
            <li>Saudi downs <strong>4 drones</strong> over Ras Tanura</li>
            <li><strong>Houthis threaten</strong> Red Sea ports</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- ROW 3: OCEANIA, SOUTH ASIA, US-EUROPE -->
  <section class="row-3" style="height: 218px;">
    <div class="card">
      <div class="card-bar" style="background:#0F766E;">
        <span class="num-pill">4</span>
        <span>OCEANIA &middot; GEOPOLITICS</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 94px;">
          <svg viewBox="0 0 296 96" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(135deg,#E6F4F1 0%,#CCFBF1 100%);">
            <polygon points="14,42 36,24 58,22 72,33 74,60 58,76 38,72 16,70" fill="#0F766E"/>
            <text x="44" y="54" text-anchor="middle" fill="#FFF" font-size="13" font-weight="900">AUS</text>
            <circle cx="104" cy="22" r="5" fill="#0F766E"/>
            <circle cx="116" cy="28" r="4.5" fill="#0F766E"/>
            <path d="M 64 34 Q 84 12 100 21" fill="none" stroke="#0F766E" stroke-width="2.6" stroke-dasharray="4,3"/>
            <text x="114" y="48" text-anchor="middle" fill="#0F766E" font-size="10.5" font-weight="900">SOLOMON IS.</text>
            <rect x="152" y="12" width="74" height="72" rx="4" fill="#FFFBEB" stroke="#B45309" stroke-width="2"/>
            <line x1="162" y1="26" x2="216" y2="26" stroke="#92400E" stroke-width="2.6"/>
            <line x1="162" y1="36" x2="212" y2="36" stroke="#CBD5E1" stroke-width="2.2"/>
            <line x1="162" y1="45" x2="204" y2="45" stroke="#CBD5E1" stroke-width="2.2"/>
            <circle cx="212" cy="68" r="7.5" fill="#DC2626" stroke="#991B1B" stroke-width="1.6"/>
            <text x="180" y="72" text-anchor="middle" fill="#0F766E" font-size="13.5" font-weight="900">$740M</text>
            <g transform="translate(234,12)">
              <rect x="0" y="0" width="54" height="72" rx="5" fill="#FFF" stroke="#DC2626" stroke-width="2"/>
              <polygon points="8,38 46,38 42,48 12,48" fill="#475569"/>
              <rect x="20" y="24" width="14" height="14" fill="#64748B"/>
              <line x1="27" y1="14" x2="27" y2="24" stroke="#475569" stroke-width="2.5"/>
              <circle cx="27" cy="31" r="18" fill="none" stroke="#DC2626" stroke-width="3.5"/>
              <line x1="14" y1="44" x2="40" y2="18" stroke="#DC2626" stroke-width="3.5"/>
              <text x="27" y="65" text-anchor="middle" fill="#991B1B" font-size="9.2" font-weight="900">NO BASES</text>
            </g>
          </svg>
        </div>
        <div class="hl-sm">AUSTRALIA&ndash;SOLOMON SECURITY PACT</div>
        <div class="wire-fact">Albanese &amp; Wale bar foreign bases; <strong>AU$740M</strong> aid.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#B45309;">
        <span class="num-pill">5</span>
        <span>SOUTH ASIA &middot; LABOR</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 94px;">
          <svg viewBox="0 0 296 96" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(135deg,#FEF3C7 0%,#FDE68A 100%);">
            <polygon points="14,82 14,32 34,18 34,32 54,18 54,32 74,18 74,82" fill="#78350F"/>
            <rect x="24" y="46" width="13" height="14" fill="#FDE68A"/>
            <rect x="48" y="46" width="13" height="14" fill="#FDE68A"/>
            <line x1="18" y1="24" x2="70" y2="74" stroke="#DC2626" stroke-width="6" stroke-linecap="round"/>
            <line x1="70" y1="24" x2="18" y2="74" stroke="#DC2626" stroke-width="6" stroke-linecap="round"/>
            <g transform="translate(86,18)">
              <rect x="6" y="10" width="32" height="44" rx="3" fill="#B45309" stroke="#78350F" stroke-width="1.6"/>
              <line x1="6" y1="20" x2="38" y2="20" stroke="#FEF3C7" stroke-width="2"/>
              <line x1="6" y1="30" x2="38" y2="30" stroke="#FEF3C7" stroke-width="2"/>
              <line x1="6" y1="40" x2="38" y2="40" stroke="#FEF3C7" stroke-width="2"/>
              <rect x="1" y="4" width="42" height="6" rx="2" fill="#78350F"/>
              <rect x="1" y="54" width="42" height="6" rx="2" fill="#78350F"/>
            </g>
            <rect x="140" y="12" width="144" height="32" rx="5" fill="#92400E"/>
            <text x="212" y="33" text-anchor="middle" fill="#FFF" font-size="14" font-weight="900">BOARD: &#x09F3;17,000</text>
            <rect x="140" y="50" width="144" height="34" rx="5" fill="#DC2626"/>
            <text x="212" y="72" text-anchor="middle" fill="#FFF" font-size="14" font-weight="900">UNION: &#x09F3;18,000+</text>
          </svg>
        </div>
        <div class="hl-sm">BANGLADESH GARMENT STRIKE</div>
        <div class="wire-fact"><strong>87+ factories closed</strong> after pay vote; <strong>108 BGB</strong> units.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#4338CA;">
        <span class="num-pill">6</span>
        <span>WAR &amp; DIPLOMACY</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 94px;">
          <svg viewBox="0 0 296 96" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#EEF2FF;">
            <rect x="12" y="8" width="114" height="80" rx="5" fill="#FFF" stroke="#4338CA" stroke-width="2"/>
            <!-- Clean oil barrel & Kremlin gold dome left of RUSSIA DEAL LURES -->
            <rect x="19" y="21" width="14" height="22" rx="2" fill="#94A3B8" stroke="#475569" stroke-width="1.3"/>
            <line x1="19" y1="28" x2="33" y2="28" stroke="#475569" stroke-width="1.5"/>
            <line x1="19" y1="36" x2="33" y2="36" stroke="#475569" stroke-width="1.5"/>
            <path d="M37,22 Q41,12 45,22 Z" fill="#D97706"/>
            <rect x="37" y="22" width="8" height="21" fill="#475569"/>
            <text x="84" y="29" text-anchor="middle" fill="#312E81" font-size="11.5" font-weight="900">RUSSIA</text>
            <text x="84" y="42" text-anchor="middle" fill="#4338CA" font-size="10.5" font-weight="800">DEAL LURES</text>
            <g transform="translate(69,67) rotate(-6)">
              <rect x="-46" y="-12" width="92" height="24" rx="3" fill="#FFF1F2" stroke="#DC2626" stroke-width="2.5"/>
              <text x="0" y="5" text-anchor="middle" fill="#DC2626" font-size="14" font-weight="900">SHELVED</text>
            </g>
            <polygon points="133,42 152,42 152,34 168,48 152,62 152,54 133,54" fill="#4338CA"/>
            <defs>
              <clipPath id="shieldClip4">
                <path d="M174,10 L284,10 L284,62 Q284,80 229,87 Q174,80 174,62 Z"/>
              </clipPath>
            </defs>
            <g clip-path="url(#shieldClip4)">
              <rect x="174" y="10" width="110" height="38" fill="#1E3A8A"/>
              <rect x="174" y="48" width="110" height="40" fill="#FACC15"/>
            </g>
            <path d="M174,10 L284,10 L284,62 Q284,80 229,87 Q174,80 174,62 Z" fill="none" stroke="#0F172A" stroke-width="2"/>
            <text x="229" y="34" text-anchor="middle" fill="#FFF" font-size="13.5" font-weight="900">UKRAINE</text>
            <text x="229" y="66" text-anchor="middle" fill="#0F172A" font-size="12" font-weight="900">SECURITY</text>
          </svg>
        </div>
        <div class="hl-sm">U.S. DROPS RUSSIA DEAL LURES</div>
        <div class="wire-fact">Envoys shift Ukraine talks back to security (FT).</div>
      </div>
    </div>
  </section>

  <!-- ROW 4: 4 CONTINENTAL DISPATCHES (CRISP COHESIVE PASTEL PALETTE + 90PX SCENES) -->
  <section class="row-4">
    <div class="card">
      <div class="card-bar" style="background:#0E7490;">
        <span class="num-pill">7</span>
        <span>AFRICA &middot; LIBYA</span>
      </div>
      <div class="card-body" style="gap: 5px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 90px;">
          <svg viewBox="0 0 218 86" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(180deg,#E0F2FE 0%,#BAE6FD 54%,#0369A1 54%,#075985 100%);">
            <polygon points="10,8 48,12 46,42 28,44 12,34" fill="#0E7490" stroke="#FFF" stroke-width="1"/>
            <circle cx="42" cy="18" r="4.5" fill="#DC2626" stroke="#FFF" stroke-width="1.2"/>
            <text x="27" y="29" text-anchor="middle" fill="#FFF" font-size="8.5" font-weight="900">LIBYA</text>
            <line x1="184" y1="47" x2="184" y2="18" stroke="#475569" stroke-width="2.5"/>
            <line x1="166" y1="22" x2="196" y2="14" stroke="#475569" stroke-width="2"/>
            <g transform="translate(124,48)">
              <circle cx="14" cy="-26" r="8" fill="#64748B" opacity="0.6"/>
              <circle cx="23" cy="-35" r="9" fill="#94A3B8" opacity="0.45"/>
              <polygon points="-44,12 44,12 52,-1 -39,-1" fill="#0F172A"/>
              <rect x="-28" y="-12" width="16" height="11" fill="#F8FAFC"/>
              <path d="M2,-1 Q14,-25 26,-1 Q17,-34 2,-22 Z" fill="#F97316"/>
              <path d="M7,-1 Q15,-14 21,-1 Z" fill="#FDE047"/>
            </g>
            <rect x="142" y="64" width="68" height="17" rx="3" fill="#DC2626"/>
            <text x="176" y="76" text-anchor="middle" fill="#FFF" font-size="10.5" font-weight="900">2 DEAD</text>
            <text x="70" y="76" text-anchor="middle" fill="#E0F2FE" font-size="11.5" font-weight="900">BENGHAZI</text>
          </svg>
        </div>
        <div class="hl-xs">LIBYA WARNS ON PORT STRIKE</div>
        <div class="wire-fact">Benghazi vessel hit kills 2 Libyan officers.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#9D174D;">
        <span class="num-pill">8</span>
        <span>S. AMERICA &middot; DEBT</span>
      </div>
      <div class="card-body" style="gap: 5px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 90px;">
          <svg viewBox="0 0 218 86" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#FDF2F8;">
            <polygon points="14,12 36,16 48,34 40,56 30,78 22,68 18,42 10,26" fill="#9D174D"/>
            <circle cx="24" cy="19" r="4.5" fill="#FACC15" stroke="#FFF" stroke-width="1.2"/>
            <line x1="56" y1="48" x2="132" y2="48" stroke="#BE185D" stroke-width="1.4" stroke-dasharray="4,2"/>
            <rect x="60" y="56" width="13" height="22" rx="2" fill="#F472B6"/>
            <rect x="78" y="45" width="13" height="33" rx="2" fill="#EC4899"/>
            <rect x="96" y="28" width="13" height="50" rx="2" fill="#DB2777"/>
            <rect x="114" y="12" width="15" height="66" rx="2" fill="#9D174D"/>
            <rect x="56" y="29" width="44" height="14" rx="2" fill="#FDF2F8" opacity="0.95"/>
            <text x="78" y="39" text-anchor="middle" fill="#9D174D" font-size="8.5" font-weight="900">100% GDP</text>
            <text x="174" y="38" text-anchor="middle" fill="#831843" font-size="18.5" font-weight="900">$237.5B</text>
            <rect x="138" y="46" width="72" height="22" rx="4" fill="#9D174D"/>
            <text x="174" y="61" text-anchor="middle" fill="#FFF" font-size="11.5" font-weight="900">242% GDP</text>
          </svg>
        </div>
        <div class="hl-xs">VENEZUELA REVEALS DEBT</div>
        <div class="wire-fact">Official tally hits <strong>$237.5B</strong> (242% of GDP).</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#334155;">
        <span class="num-pill">9</span>
        <span>UK &middot; JUSTICE</span>
      </div>
      <div class="card-body" style="gap: 5px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 90px;">
          <svg viewBox="0 0 218 86" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#F1F5F9;">
            <!-- Subtle Big Ben clock tower silhouette -->
            <rect x="7" y="22" width="14" height="56" fill="#CBD5E1"/>
            <polygon points="7,22 14,7 21,22" fill="#94A3B8"/>
            <circle cx="14" cy="31" r="4.5" fill="#F8FAFC" stroke="#64748B" stroke-width="1"/>
            <!-- London Bobby Helmet w/ Sillitoe Tartan band -->
            <g transform="translate(47,45)">
              <path d="M-16,12 L16,12 L12,-14 Q12,-28 0,-28 Q-12,-28 -12,-14 Z" fill="#1E293B"/>
              <rect x="-15" y="4" width="30" height="5" fill="#FFF"/>
              <rect x="-15" y="4" width="6" height="5" fill="#0F172A"/>
              <rect x="-3" y="4" width="6" height="5" fill="#0F172A"/>
              <rect x="9" y="4" width="6" height="5" fill="#0F172A"/>
              <rect x="-19" y="10" width="38" height="6" rx="2" fill="#0F172A"/>
              <circle cx="0" cy="-9" r="7" fill="#E2E8F0"/>
              <text x="0" y="-6" text-anchor="middle" fill="#0F172A" font-size="8" font-weight="900">MET</text>
            </g>
            <!-- Tilted justice scales -->
            <line x1="99" y1="14" x2="99" y2="72" stroke="#334155" stroke-width="3"/>
            <line x1="84" y1="72" x2="114" y2="72" stroke="#334155" stroke-width="3"/>
            <line x1="78" y1="36" x2="120" y2="20" stroke="#0F172A" stroke-width="2.8"/>
            <polygon points="78,36 71,54 85,54" fill="#DC2626"/>
            <polygon points="120,20 113,38 127,38" fill="#475569"/>
            <!-- Bold stamp -->
            <rect x="134" y="16" width="76" height="54" rx="5" fill="#FFF" stroke="#334155" stroke-width="1.8"/>
            <text x="172" y="34" text-anchor="middle" fill="#0F172A" font-size="11" font-weight="900">FAIRFIELD</text>
            <rect x="140" y="42" width="64" height="22" rx="3" fill="#DC2626"/>
            <text x="172" y="57" text-anchor="middle" fill="#FFF" font-size="11.5" font-weight="900">BIASED</text>
          </svg>
        </div>
        <div class="hl-xs">MET POLICE 'STILL BIASED'</div>
        <div class="wire-fact">UK review cites racism &amp; misogyny.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#1D4ED8;">
        <span class="num-pill">10</span>
        <span>N. AMERICA &middot; TRADE</span>
      </div>
      <div class="card-body" style="gap: 5px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 90px;">
          <svg viewBox="0 0 218 86" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#EFF6FF;">
            <!-- Crisp shipping containers with corner ribs clear of centered labels -->
            <rect x="12" y="14" width="92" height="28" rx="3" fill="#2563EB"/>
            <line x1="21" y1="18" x2="21" y2="38" stroke="#93C5FD" stroke-width="2"/>
            <line x1="95" y1="18" x2="95" y2="38" stroke="#93C5FD" stroke-width="2"/>
            <text x="58" y="32" text-anchor="middle" fill="#FFF" font-size="11.5" font-weight="900">IMPORTS</text>
            <rect x="12" y="46" width="92" height="28" rx="3" fill="#1E40AF"/>
            <line x1="21" y1="50" x2="21" y2="70" stroke="#60A5FA" stroke-width="2"/>
            <line x1="95" y1="50" x2="95" y2="70" stroke="#60A5FA" stroke-width="2"/>
            <text x="58" y="64" text-anchor="middle" fill="#DBEAFE" font-size="11" font-weight="900">16 NATIONS</text>
            <rect x="114" y="14" width="94" height="60" rx="6" fill="#DC2626"/>
            <text x="161" y="34" text-anchor="middle" fill="#FECACA" font-size="11" font-weight="900">SEC. 301</text>
            <text x="161" y="54" text-anchor="middle" fill="#FFF" font-size="16" font-weight="900">TARIFFS</text>
            <text x="161" y="68" text-anchor="middle" fill="#FEF2F2" font-size="9.5" font-weight="800">U.S. DRAFT</text>
          </svg>
        </div>
        <div class="hl-xs">U.S. READIES 16-NATION TARIFFS</div>
        <div class="wire-fact">USTR targets excess capacity under Sec. 301.</div>
      </div>
    </div>
  </section>

</div>
</body>
</html>
"""


def render() -> None:
    ASSET_OUT.parent.mkdir(parents=True, exist_ok=True)
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    html = HTML_TEMPLATE.format(MAP_SVG=build_map_svg())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1024, "height": 1024}, device_scale_factor=1)
        page.set_content(html, wait_until="load")
        page.screenshot(path=str(ASSET_OUT), type="png")
        browser.close()

    with Image.open(ASSET_OUT) as im:
        im_rgb = im.convert("RGB")
        im_rgb.save(ASSET_OUT, format="PNG", optimize=True)
        preview = im_rgb.resize((300, 300), Image.Resampling.LANCZOS)
        preview.save(PREVIEW_300, format="PNG", optimize=True)

    size_bytes = ASSET_OUT.stat().st_size
    print(f"Rendered {ASSET_OUT} ({size_bytes:,} bytes)")
    print(f"Preview  {PREVIEW_300} ({PREVIEW_300.stat().st_size:,} bytes)")


if __name__ == "__main__":
    render()
