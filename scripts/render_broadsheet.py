"""Deterministic 1024x1024 editorial world news front page for Wednesday, 25 November 2026."""

from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSET_OUT = ROOT / "assets" / "entry.png"
SCRATCH_DIR = Path(r"C:\Users\82103\.gemini\antigravity\brain\c8bbd2ac-e3a5-415b-8afb-bf347f8e20ad\scratch")
PREVIEW_300 = SCRATCH_DIR / "preview_300_v12.png"


def proj(lon: float, lat: float) -> tuple[float, float]:
    """Project (lon, lat) onto 470x172 equirectangular SVG canvas."""
    x = (lon + 180.0) / 360.0 * 470.0
    y = (75.0 - lat) / 133.0 * 172.0
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
        f'<polygon points="{poly_pts(c)}" fill="#EAE0CA" stroke="#5B6B7D" stroke-width="1" stroke-linejoin="round"/>'
        for c in CONTINENTS
    )
    # 10 verified locations across all 6 inhabited continents cleanly separated for 300px clarity
    pins = [
        (1, 99.0, 40.9, "#1E3A8A", -9, -13),    # Jiuquan Space
        (2, 127.0, 37.5, "#DC2626", 15, -2),    # Seoul / Asia Chips
        (3, 56.3, 26.6, "#EA580C", 3, 2),       # Hormuz
        (4, 158.0, -10.5, "#0F766E", 8, -2),    # Australia-Solomons
        (5, 90.4, 23.8, "#B45309", -2, 13),     # Dhaka
        (6, 30.5, 50.4, "#4338CA", 9, -5),      # Ukraine Diplomacy
        (7, 20.1, 32.1, "#0E7490", -2, 8),      # Benghazi, Libya
        (8, -66.9, 8.0, "#9D174D", 4, 12),      # Venezuela Debt
        (9, -0.1, 51.5, "#334155", -15, -3),    # London UK
        (10, -77.0, 38.9, "#1D4ED8", -12, 4),   # Washington D.C. Tariffs
    ]
    wx, wy = proj(-77.0, 38.9)
    kx, ky = proj(30.5, 50.4)
    ax, ay = proj(149.1, -35.3)
    sx, sy = proj(160.0, -9.4)

    arc_us_eu = (
        f'<path d="M {wx} {wy} Q {(wx+kx)/2} {min(wy,ky)-24} {kx} {ky}" '
        f'fill="none" stroke="#4338CA" stroke-width="1.9" stroke-dasharray="4,3"/>'
    )
    arc_aus_sol = (
        f'<path d="M {ax} {ay} Q {ax+12} {(ay+sy)/2} {sx} {sy}" '
        f'fill="none" stroke="#0F766E" stroke-width="2.3"/>'
        f'<circle cx="{sx}" cy="{sy}" r="3.2" fill="#0F766E" stroke="#FFF" stroke-width="1.1"/>'
    )

    markers = []
    for num, lon, lat, color, dx, dy in pins:
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        leader = ""
        if dx != 0 or dy != 0:
            leader = f'<line x1="{px}" y1="{py}" x2="{cx}" y2="{cy}" stroke="{color}" stroke-width="1.6"/>'
        markers.append(
            f'{leader}'
            f'<circle cx="{cx}" cy="{cy}" r="11.5" fill="{color}" stroke="#FFFFFF" stroke-width="2.1"/>'
            f'<text x="{cx}" y="{cy+4.2}" text-anchor="middle" fill="#FFFFFF" font-family="Segoe UI, Arial, sans-serif" font-size="12.5" font-weight="900">{num}</text>'
        )

    return f"""
    <svg viewBox="0 0 470 172" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;border-radius:6px;border:1px solid #B5C8D8;">
      <defs>
        <radialGradient id="oceanGrad" cx="52%" cy="48%" r="65%">
          <stop offset="0%" stop-color="#DFEEF8"/>
          <stop offset="100%" stop-color="#C6DEEE"/>
        </radialGradient>
      </defs>
      <rect x="0" y="0" width="470" height="172" fill="url(#oceanGrad)"/>
      <g opacity="0.35" stroke="#8FADBE" stroke-width="0.7">
        <line x1="0" y1="86" x2="470" y2="86" stroke-dasharray="4,4"/>
        <line x1="235" y1="0" x2="235" y2="172" stroke-dasharray="4,4"/>
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
    background: #F3EDE0;
    color: #0B1320;
    font-family: "Segoe UI", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .page {{
    width: 1024px;
    height: 1024px;
    padding: 10px 15px 10px 15px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .masthead {{
    background: #FAF6EC;
    border-bottom: 3.5px double #0B1320;
    border-radius: 6px 6px 0 0;
    overflow: hidden;
    text-align: center;
  }}
  .mast-top {{
    background: #0B1320;
    color: #F8FAFC;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 3px 12px;
    font-size: 13.5px;
    font-weight: 800;
    letter-spacing: 0.9px;
    text-transform: uppercase;
  }}
  .mast-date {{
    font-family: Georgia, "Times New Roman", serif;
    font-size: 48px;
    font-weight: 900;
    letter-spacing: 0.4px;
    line-height: 1.04;
    padding: 3px 0 4px 0;
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
    border: 1.5px solid #C6D1DE;
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.07);
  }}
  .card-bar {{
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 4px 10px;
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.4px;
    text-transform: uppercase;
  }}
  .num-pill {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(255,255,255,0.25);
    border: 1.6px solid #FFFFFF;
    font-size: 12.5px;
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
    font-size: 24px;
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -0.3px;
    color: #0B1320;
  }}
  .hl-sm {{
    font-size: 20px;
    font-weight: 900;
    line-height: 1.06;
    letter-spacing: -0.3px;
    color: #0B1320;
  }}
  .hl-xs {{
    font-size: 17.5px;
    font-weight: 900;
    line-height: 1.06;
    letter-spacing: -0.25px;
    color: #0B1320;
  }}
  .facts {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 17.5px;
    line-height: 1.15;
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
    grid-template-columns: 196px 1fr;
    gap: 10px;
    align-items: center;
    flex: 1;
  }}
  .art-box {{
    width: 100%;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #CAD6E2;
  }}
  .bars {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .bar-row {{
    display: grid;
    grid-template-columns: 92px 1fr 66px;
    align-items: center;
    gap: 6px;
    font-size: 16px;
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
    font-size: 15.2px;
    line-height: 1.14;
    font-weight: 700;
    color: #334155;
  }}
</style>
</head>
<body>
<div class="page">

  <header class="masthead">
    <div class="mast-top">
      <span>ALL-CONTINENT WORLD NEWS EDITION</span>
      <span>10 STORIES &middot; 6 CONTINENTS &middot; ONE DAY</span>
    </div>
    <div class="mast-date">WEDNESDAY &middot; 25 NOVEMBER 2026</div>
  </header>

  <!-- ROW 1: LARGE GLOBAL MAP (10 PINS) + STORY 1 (SPACE) -->
  <section class="row-2" style="height: 222px;">
    <div class="card">
      <div class="card-bar" style="background:#0F172A;">
        <span>GLOBAL DISPATCH MAP &middot; LOCATIONS 1&ndash;10</span>
      </div>
      <div class="card-body" style="padding: 6px 8px 6px 8px;">
        <div style="flex:1;height:100%;">
          {MAP_SVG}
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
          <div class="art-box" style="height: 144px;">
            <svg viewBox="0 0 196 144" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(180deg,#061128 0%,#16346B 100%);">
              <circle cx="18" cy="18" r="1.6" fill="#FFF" opacity="0.85"/>
              <circle cx="52" cy="13" r="1.3" fill="#FFF" opacity="0.7"/>
              <circle cx="176" cy="16" r="1.6" fill="#FFF" opacity="0.85"/>
              <circle cx="88" cy="36" r="1.2" fill="#BAE6FD" opacity="0.75"/>
              <path d="M 48 64 Q 76 26 122 25" fill="none" stroke="#93C5FD" stroke-width="1.8" stroke-dasharray="3.5,3"/>
              <ellipse cx="98" cy="163" rx="140" ry="32" fill="#1D4ED8" stroke="#60A5FA" stroke-width="2.2"/>
              <g transform="translate(128,25)">
                <rect x="-28" y="6" width="56" height="7" rx="2" fill="#E2E8F0"/>
                <rect x="-4.5" y="-11" width="9" height="32" rx="2" fill="#CBD5E1"/>
                <rect x="-34" y="-8" width="21" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="13" y="-8" width="21" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="-34" y="15" width="21" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="13" y="15" width="21" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <text x="0" y="37" text-anchor="middle" fill="#BAE6FD" font-size="9.5" font-weight="900">TIANGONG</text>
              </g>
              <g transform="translate(46,74) rotate(-26)">
                <path d="M-9,25 L0,54 L9,25 Z" fill="#F97316"/>
                <path d="M-4.5,25 L0,42 L4.5,25 Z" fill="#FDE047"/>
                <rect x="-7" y="-22" width="14" height="47" rx="3" fill="#F8FAFC"/>
                <polygon points="-7,-22 0,-40 7,-22" fill="#EF4444"/>
                <rect x="-12" y="6" width="5" height="19" rx="1.5" fill="#E2E8F0"/>
                <rect x="7" y="6" width="5" height="19" rx="1.5" fill="#E2E8F0"/>
              </g>
              <rect x="108" y="76" width="36" height="23" rx="2" fill="#DE2910" stroke="#FFF" stroke-width="1.2"/>
              <polygon points="116,81 117.5,85 121.5,85 118.2,87.5 119.5,91.5 116,89 112.5,91.5 113.8,87.5 110.5,85 114.5,85" fill="#FFDE00"/>
              <rect x="150" y="76" width="36" height="23" rx="2" fill="#01411C" stroke="#FFF" stroke-width="1.2"/>
              <rect x="150" y="76" width="8.5" height="23" fill="#FFF"/>
              <circle cx="170" cy="87.5" r="5.2" fill="#FFF"/>
              <circle cx="172" cy="86" r="4.2" fill="#01411C"/>
              <text x="147" y="116" text-anchor="middle" fill="#F8FAFC" font-size="12.5" font-weight="900">CN + PK CREW</text>
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
  <section class="row-2" style="height: 228px;">
    <div class="card">
      <div class="card-bar" style="background:#DC2626;">
        <span class="num-pill">2</span>
        <span>GLOBAL MARKETS &middot; AI &amp; TECH</span>
      </div>
      <div class="card-body">
        <div class="hl-lg">ASIAN AI &amp; CHIP STOCKS PLUNGE</div>
        <div class="split-h">
          <div class="art-box" style="height: 144px;">
            <svg viewBox="0 0 196 144" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#FFF5F5;">
              <defs>
                <linearGradient id="crashArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#DC2626" stop-opacity="0.30"/>
                  <stop offset="100%" stop-color="#DC2626" stop-opacity="0.03"/>
                </linearGradient>
              </defs>
              <line x1="12" y1="38" x2="184" y2="38" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <line x1="12" y1="76" x2="184" y2="76" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <polygon points="14,44 48,48 78,62 106,58 136,92 172,110 172,116 14,116" fill="url(#crashArea)"/>
              <polyline points="14,44 48,48 78,62 106,58 136,92 172,110" fill="none" stroke="#DC2626" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
              <polygon points="178,114 160,113 170,101" fill="#DC2626"/>
              <rect x="12" y="8" width="122" height="26" rx="5" fill="#991B1B"/>
              <text x="73" y="26" text-anchor="middle" fill="#FFF" font-size="14.5" font-weight="900">KOSPI -6.2%</text>
              <g transform="translate(148,7)">
                <rect x="4" y="4" width="26" height="26" rx="3" fill="#1E293B" stroke="#DC2626" stroke-width="1.6"/>
                <text x="17" y="21" text-anchor="middle" fill="#FECACA" font-size="10.5" font-weight="900">AI</text>
                <line x1="11" y1="0" x2="11" y2="4" stroke="#64748B" stroke-width="2"/>
                <line x1="23" y1="0" x2="23" y2="4" stroke="#64748B" stroke-width="2"/>
                <line x1="11" y1="30" x2="11" y2="34" stroke="#64748B" stroke-width="2"/>
                <line x1="23" y1="30" x2="23" y2="34" stroke="#64748B" stroke-width="2"/>
                <line x1="0" y1="11" x2="4" y2="11" stroke="#64748B" stroke-width="2"/>
                <line x1="0" y1="23" x2="4" y2="23" stroke="#64748B" stroke-width="2"/>
                <line x1="30" y1="11" x2="34" y2="11" stroke="#64748B" stroke-width="2"/>
                <line x1="30" y1="23" x2="34" y2="23" stroke="#64748B" stroke-width="2"/>
              </g>
              <rect x="12" y="118" width="172" height="20" rx="4" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.4"/>
              <text x="98" y="132" text-anchor="middle" fill="#991B1B" font-size="11.5" font-weight="900">SIDECAR TRIGGERED</text>
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
            <div style="font-size:15px;font-weight:800;color:#1E293B;border-top:1px solid #E2E8F0;padding-top:3px;white-space:nowrap;">
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
          <div class="art-box" style="height: 144px;">
            <svg viewBox="0 0 196 144" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#18345C;">
              <polygon points="0,0 196,0 196,44 140,34 110,27 80,39 0,37" fill="#D8C8AA" stroke="#78716C" stroke-width="1"/>
              <polygon points="0,98 64,86 98,98 114,68 130,82 148,128 196,144 0,144" fill="#E9DABC" stroke="#78716C" stroke-width="1"/>
              <text x="10" y="19" fill="#44403C" font-size="12" font-weight="900">IRAN</text>
              <text x="9" y="137" fill="#44403C" font-size="11" font-weight="900">SAUDI / UAE</text>
              <text x="150" y="48" text-anchor="middle" fill="#BAE6FD" font-size="9.5" font-weight="900" font-style="italic">HORMUZ</text>
              <g transform="translate(92,57)">
                <circle cx="9" cy="-17" r="5.5" fill="#64748B" opacity="0.65"/>
                <circle cx="14" cy="-24" r="6.5" fill="#94A3B8" opacity="0.5"/>
                <polygon points="-22,6 22,6 27,0 -20,0" fill="#0F172A"/>
                <rect x="-14" y="-6" width="8" height="6" fill="#F8FAFC"/>
                <path d="M1,0 Q9,-16 16,0 Q11,-22 1,-14 Z" fill="#F97316"/>
                <path d="M4,0 Q9,-10 13,0 Z" fill="#FDE047"/>
              </g>
              <g transform="translate(152,73)">
                <circle cx="7" cy="-16" r="5" fill="#64748B" opacity="0.65"/>
                <circle cx="12" cy="-22" r="6" fill="#94A3B8" opacity="0.5"/>
                <polygon points="-19,6 19,6 24,0 -17,0" fill="#0F172A"/>
                <rect x="-12" y="-5" width="7" height="5" fill="#F8FAFC"/>
                <path d="M0,0 Q7,-14 14,0 Q9,-20 0,-12 Z" fill="#EF4444"/>
                <path d="M3,0 Q7,-8 11,0 Z" fill="#FDE047"/>
              </g>
              <circle cx="46" cy="66" r="9" fill="#0F172A" stroke="#F8FAFC" stroke-width="1.6"/>
              <line x1="46" y1="51" x2="46" y2="81" stroke="#F8FAFC" stroke-width="2.1"/>
              <line x1="31" y1="66" x2="61" y2="66" stroke="#F8FAFC" stroke-width="2.1"/>
              <line x1="35" y1="55" x2="57" y2="77" stroke="#F8FAFC" stroke-width="2.1"/>
              <line x1="35" y1="77" x2="57" y2="55" stroke="#F8FAFC" stroke-width="2.1"/>
              <path d="M 12 116 A 21 21 0 0 1 52 106" fill="none" stroke="#DC2626" stroke-width="2" stroke-dasharray="3,2"/>
              <g stroke="#DC2626" stroke-width="2.2" stroke-linecap="round">
                <line x1="16" y1="99" x2="22" y2="105"/><line x1="22" y1="99" x2="16" y2="105"/>
                <line x1="28" y1="95" x2="34" y2="101"/><line x1="34" y1="95" x2="28" y2="101"/>
                <line x1="40" y1="98" x2="46" y2="104"/><line x1="46" y1="98" x2="40" y2="104"/>
              </g>
              <rect x="54" y="96" width="64" height="23" rx="3" fill="#991B1B"/>
              <text x="86" y="106.5" text-anchor="middle" fill="#FFF" font-size="9.5" font-weight="900">4 DRONES</text>
              <text x="86" y="116" text-anchor="middle" fill="#FECACA" font-size="8.5" font-weight="800">DOWNED</text>
            </svg>
          </div>
          <ul class="facts">
            <li><strong>2 oil tankers burn</strong> after hitting mines</li>
            <li>Saudi downs <strong>4 drones</strong> at Ras Tanura</li>
            <li><strong>Houthis threaten</strong> Red Sea ports</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- ROW 3: OCEANIA, SOUTH ASIA, US-EUROPE (TALL 96PX EDITORIAL ART) -->
  <section class="row-3" style="height: 222px;">
    <div class="card">
      <div class="card-bar" style="background:#0F766E;">
        <span class="num-pill">4</span>
        <span>OCEANIA &middot; GEOPOLITICS</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 96px;">
          <svg viewBox="0 0 296 96" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(135deg,#E6F4F1 0%,#CCFBF1 100%);">
            <polygon points="12,42 35,23 58,21 72,33 74,60 58,76 38,72 14,70" fill="#0F766E"/>
            <text x="43" y="54" text-anchor="middle" fill="#FFF" font-size="13.5" font-weight="900">AUS</text>
            <circle cx="102" cy="21" r="5" fill="#0F766E"/>
            <circle cx="115" cy="27" r="4.5" fill="#0F766E"/>
            <path d="M 64 33 Q 83 11 98 20" fill="none" stroke="#0F766E" stroke-width="2.6" stroke-dasharray="4,3"/>
            <text x="112" y="48" text-anchor="middle" fill="#0F766E" font-size="10.5" font-weight="900">SOLOMON IS.</text>
            <rect x="150" y="11" width="76" height="74" rx="4" fill="#FFFBEB" stroke="#B45309" stroke-width="2"/>
            <line x1="160" y1="25" x2="216" y2="25" stroke="#92400E" stroke-width="2.8"/>
            <line x1="160" y1="35" x2="212" y2="35" stroke="#CBD5E1" stroke-width="2.4"/>
            <line x1="160" y1="44" x2="204" y2="44" stroke="#CBD5E1" stroke-width="2.4"/>
            <circle cx="212" cy="69" r="7.5" fill="#DC2626" stroke="#991B1B" stroke-width="1.6"/>
            <text x="179" y="73" text-anchor="middle" fill="#0F766E" font-size="14" font-weight="900">$740M</text>
            <g transform="translate(234,11)">
              <rect x="0" y="0" width="54" height="74" rx="5" fill="#FFF" stroke="#DC2626" stroke-width="2"/>
              <polygon points="8,38 46,38 42,48 12,48" fill="#475569"/>
              <rect x="20" y="24" width="14" height="14" fill="#64748B"/>
              <line x1="27" y1="14" x2="27" y2="24" stroke="#475569" stroke-width="2.5"/>
              <circle cx="27" cy="31" r="18" fill="none" stroke="#DC2626" stroke-width="3.6"/>
              <line x1="14" y1="44" x2="40" y2="18" stroke="#DC2626" stroke-width="3.6"/>
              <text x="27" y="66" text-anchor="middle" fill="#991B1B" font-size="9.5" font-weight="900">NO BASES</text>
            </g>
          </svg>
        </div>
        <div class="hl-sm">AUSTRALIA&ndash;SOLOMON PACT</div>
        <div class="wire-fact">Bars foreign bases &middot; <strong>AU$740M</strong> package.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#B45309;">
        <span class="num-pill">5</span>
        <span>SOUTH ASIA &middot; LABOR</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 96px;">
          <svg viewBox="0 0 296 96" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(135deg,#FEF3C7 0%,#FDE68A 100%);">
            <polygon points="12,82 12,32 32,18 32,32 52,18 52,32 72,18 72,82" fill="#78350F"/>
            <rect x="22" y="46" width="13" height="14" fill="#FDE68A"/>
            <rect x="46" y="46" width="13" height="14" fill="#FDE68A"/>
            <line x1="16" y1="24" x2="68" y2="74" stroke="#DC2626" stroke-width="6.5" stroke-linecap="round"/>
            <line x1="68" y1="24" x2="16" y2="74" stroke="#DC2626" stroke-width="6.5" stroke-linecap="round"/>
            <!-- Textile spool -->
            <g transform="translate(86,18)">
              <rect x="6" y="10" width="32" height="44" rx="3" fill="#B45309" stroke="#78350F" stroke-width="1.6"/>
              <line x1="6" y1="20" x2="38" y2="20" stroke="#FEF3C7" stroke-width="2"/>
              <line x1="6" y1="30" x2="38" y2="30" stroke="#FEF3C7" stroke-width="2"/>
              <line x1="6" y1="40" x2="38" y2="40" stroke="#FEF3C7" stroke-width="2"/>
              <rect x="1" y="4" width="42" height="6" rx="2" fill="#78350F"/>
              <rect x="1" y="54" width="42" height="6" rx="2" fill="#78350F"/>
            </g>
            <rect x="140" y="12" width="144" height="32" rx="5" fill="#92400E"/>
            <text x="212" y="33.5" text-anchor="middle" fill="#FFF" font-size="14.5" font-weight="900">BOARD: &#x09F3;17,000</text>
            <rect x="140" y="50" width="144" height="34" rx="5" fill="#DC2626"/>
            <text x="212" y="72.5" text-anchor="middle" fill="#FFF" font-size="14.5" font-weight="900">UNION: &#x09F3;18,000+</text>
          </svg>
        </div>
        <div class="hl-sm">BANGLADESH GARMENT STRIKE</div>
        <div class="wire-fact"><strong>87+ plants shut</strong> &middot; <strong>108 BGB</strong> units deployed.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#4338CA;">
        <span class="num-pill">6</span>
        <span>WAR &amp; DIPLOMACY</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 96px;">
          <svg viewBox="0 0 296 96" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(135deg,#EEF2FF 0%,#E0E7FF 100%);">
            <!-- Russian energy/business deal briefcase crossed/shelved -->
            <g transform="translate(12,10)">
              <rect x="0" y="0" width="114" height="76" rx="5" fill="#FFF" stroke="#4338CA" stroke-width="2"/>
              <!-- Kremlin onion-dome & oil barrel icon cleanly separated on left -->
              <rect x="9" y="24" width="16" height="23" rx="2" fill="#94A3B8" stroke="#475569" stroke-width="1.3"/>
              <line x1="9" y1="31" x2="25" y2="31" stroke="#475569" stroke-width="1.5"/>
              <line x1="9" y1="39" x2="25" y2="39" stroke="#475569" stroke-width="1.5"/>
              <path d="M35,25 Q41,11 47,25 Z" fill="#D97706"/>
              <rect x="34" y="25" width="14" height="22" fill="#475569"/>
              <text x="82" y="28" text-anchor="middle" fill="#312E81" font-size="11" font-weight="900">MOSCOW</text>
              <text x="82" y="42" text-anchor="middle" fill="#4338CA" font-size="10.5" font-weight="800">DEALS</text>
              <g transform="translate(57,59) rotate(-6)">
                <rect x="-46" y="-11" width="92" height="22" rx="3" fill="#FFF1F2" stroke="#DC2626" stroke-width="2.5"/>
                <text x="0" y="4.5" text-anchor="middle" fill="#DC2626" font-size="13.5" font-weight="900">SHELVED</text>
              </g>
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
            <path d="M174,10 L284,10 L284,62 Q284,80 229,87 Q174,80 174,62 Z" fill="none" stroke="#0F172A" stroke-width="2.2"/>
            <text x="229" y="34" text-anchor="middle" fill="#FFF" font-size="14" font-weight="900">UKRAINE</text>
            <text x="229" y="66" text-anchor="middle" fill="#0F172A" font-size="12.5" font-weight="900">SECURITY</text>
          </svg>
        </div>
        <div class="hl-sm">U.S. DROPS RUSSIA DEAL LURES</div>
        <div class="wire-fact">Talks pivot back to Ukraine security (FT).</div>
      </div>
    </div>
  </section>

  <!-- ROW 4: 4 CONTINENTAL DISPATCHES (TALL 96PX SCENES, CRISP 300PX TYPOGRAPHY) -->
  <section class="row-4">
    <div class="card">
      <div class="card-bar" style="background:#0E7490;">
        <span class="num-pill">7</span>
        <span>AFRICA &middot; LIBYA</span>
      </div>
      <div class="card-body" style="gap: 5px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 94px;">
          <svg viewBox="0 0 218 88" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(180deg,#E0F2FE 0%,#BAE6FD 54%,#0369A1 54%,#075985 100%);">
            <polygon points="10,8 48,12 46,42 28,44 12,34" fill="#0E7490" stroke="#FFF" stroke-width="1"/>
            <circle cx="42" cy="18" r="4.5" fill="#DC2626" stroke="#FFF" stroke-width="1.2"/>
            <text x="27" y="29" text-anchor="middle" fill="#FFF" font-size="8.5" font-weight="900">LIBYA</text>
            <!-- Port crane silhouette on Benghazi pier -->
            <line x1="184" y1="47" x2="184" y2="18" stroke="#475569" stroke-width="2.5"/>
            <line x1="166" y1="22" x2="196" y2="14" stroke="#475569" stroke-width="2"/>
            <g transform="translate(124,49)">
              <circle cx="14" cy="-26" r="8" fill="#64748B" opacity="0.6"/>
              <circle cx="23" cy="-35" r="9" fill="#94A3B8" opacity="0.45"/>
              <polygon points="-44,12 44,12 52,-1 -39,-1" fill="#0F172A"/>
              <rect x="-28" y="-12" width="16" height="11" fill="#F8FAFC"/>
              <path d="M2,-1 Q14,-25 26,-1 Q17,-34 2,-22 Z" fill="#F97316"/>
              <path d="M7,-1 Q15,-14 21,-1 Z" fill="#FDE047"/>
            </g>
            <rect x="142" y="65" width="68" height="18" rx="3" fill="#DC2626"/>
            <text x="176" y="78" text-anchor="middle" fill="#FFF" font-size="11" font-weight="900">2 DEAD</text>
            <text x="72" y="78" text-anchor="middle" fill="#E0F2FE" font-size="12" font-weight="900">BENGHAZI</text>
          </svg>
        </div>
        <div class="hl-xs">LIBYA WARNS ON PORT STRIKE</div>
        <div class="wire-fact">Benghazi vessel hit kills 2 naval officers.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#9D174D;">
        <span class="num-pill">8</span>
        <span>S. AMERICA &middot; DEBT</span>
      </div>
      <div class="card-body" style="gap: 5px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 94px;">
          <svg viewBox="0 0 218 88" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#FDF2F8;">
            <polygon points="14,12 36,16 48,34 40,56 30,78 22,68 18,42 10,26" fill="#9D174D"/>
            <circle cx="24" cy="19" r="4.5" fill="#FACC15" stroke="#FFF" stroke-width="1.2"/>
            <line x1="56" y1="49" x2="132" y2="49" stroke="#BE185D" stroke-width="1.5" stroke-dasharray="4,2"/>
            <rect x="60" y="57" width="13" height="22" rx="2" fill="#F472B6"/>
            <rect x="78" y="46" width="13" height="33" rx="2" fill="#EC4899"/>
            <rect x="96" y="29" width="13" height="50" rx="2" fill="#DB2777"/>
            <rect x="114" y="12" width="15" height="67" rx="2" fill="#9D174D"/>
            <rect x="55" y="30" width="46" height="14" rx="2" fill="#FDF2F8" opacity="0.95"/>
            <text x="78" y="40" text-anchor="middle" fill="#9D174D" font-size="8.8" font-weight="900">100% GDP</text>
            <text x="174" y="39" text-anchor="middle" fill="#831843" font-size="20" font-weight="900">$237.5B</text>
            <rect x="137" y="47" width="74" height="23" rx="4" fill="#9D174D"/>
            <text x="174" y="63" text-anchor="middle" fill="#FFF" font-size="12" font-weight="900">242% GDP</text>
          </svg>
        </div>
        <div class="hl-xs">VENEZUELA REVEALS DEBT</div>
        <div class="wire-fact">Official debt hits <strong>$237.5B</strong> (242% GDP).</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#334155;">
        <span class="num-pill">9</span>
        <span>UK &middot; JUSTICE</span>
      </div>
      <div class="card-body" style="gap: 5px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 94px;">
          <svg viewBox="0 0 218 88" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:#F1F5F9;">
            <!-- Subtle Big Ben clock tower silhouette left edge for instant London cue -->
            <rect x="8" y="22" width="16" height="58" fill="#CBD5E1"/>
            <polygon points="8,22 16,6 24,22" fill="#94A3B8"/>
            <circle cx="16" cy="32" r="5" fill="#F8FAFC" stroke="#64748B" stroke-width="1"/>
            <!-- London Bobby Helmet w/ Sillitoe Tartan band -->
            <g transform="translate(50,47)">
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
            <line x1="102" y1="15" x2="102" y2="74" stroke="#334155" stroke-width="3"/>
            <line x1="87" y1="74" x2="117" y2="74" stroke="#334155" stroke-width="3"/>
            <line x1="82" y1="36" x2="122" y2="21" stroke="#0F172A" stroke-width="2.8"/>
            <polygon points="82,36 75,54 89,54" fill="#DC2626"/>
            <polygon points="122,21 115,39 129,39" fill="#475569"/>
            <!-- Bold stamp -->
            <rect x="136" y="16" width="74" height="56" rx="5" fill="#FFF" stroke="#334155" stroke-width="1.8"/>
            <text x="173" y="34" text-anchor="middle" fill="#0F172A" font-size="11.5" font-weight="900">LONDON</text>
            <rect x="142" y="42" width="62" height="23" rx="3" fill="#DC2626"/>
            <text x="173" y="57.5" text-anchor="middle" fill="#FFF" font-size="12" font-weight="900">BIASED</text>
          </svg>
        </div>
        <div class="hl-xs">MET POLICE 'STILL BIASED'</div>
        <div class="wire-fact">Fairfield Review cites racism &amp; misogyny.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#1D4ED8;">
        <span class="num-pill">10</span>
        <span>N. AMERICA &middot; TRADE</span>
      </div>
      <div class="card-body" style="gap: 5px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 94px;">
          <svg viewBox="0 0 218 88" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:100%;background:linear-gradient(180deg,#EFF6FF 0%,#DBEAFE 65%,#1E3A8A 65%,#1E40AF 100%);">
            <!-- Cargo ship loaded with containers approaching tall U.S. tariff barrier -->
            <g transform="translate(56,52)">
              <rect x="-36" y="-20" width="32" height="16" rx="1.5" fill="#0284C7" stroke="#FFF" stroke-width="0.9"/>
              <rect x="-2" y="-20" width="32" height="16" rx="1.5" fill="#2563EB" stroke="#FFF" stroke-width="0.9"/>
              <rect x="-30" y="-37" width="54" height="16" rx="1.5" fill="#1D4ED8" stroke="#FFF" stroke-width="0.9"/>
              <polygon points="-44,12 36,12 46,-2 -40,-2" fill="#0F172A"/>
              <rect x="-34" y="-12" width="10" height="10" fill="#F8FAFC"/>
              <text x="-3" y="-25.5" text-anchor="middle" fill="#FFF" font-size="9.5" font-weight="900">IMPORTS</text>
            </g>
            <!-- Red Section 301 Tariff Wall -->
            <rect x="114" y="10" width="94" height="68" rx="6" fill="#DC2626" stroke="#FFF" stroke-width="1.5"/>
            <text x="161" y="29" text-anchor="middle" fill="#FECACA" font-size="11" font-weight="900">SEC. 301</text>
            <text x="161" y="50" text-anchor="middle" fill="#FFF" font-size="16.5" font-weight="900">TARIFFS</text>
            <text x="161" y="67" text-anchor="middle" fill="#FEF2F2" font-size="10.5" font-weight="900">16 NATIONS</text>
          </svg>
        </div>
        <div class="hl-xs">U.S. EYES 16-NATION TARIFFS</div>
        <div class="wire-fact">USTR targets excess factory capacity.</div>
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
