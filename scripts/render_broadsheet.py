"""Deterministic 1024x1024 world news broadsheet renderer for Wednesday, 25 November 2026."""

from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSET_OUT = ROOT / "assets" / "entry.png"
SCRATCH_DIR = Path(r"C:\Users\82103\.gemini\antigravity\brain\c8bbd2ac-e3a5-415b-8afb-bf347f8e20ad\scratch")
PREVIEW_300 = SCRATCH_DIR / "preview_300_v6.png"


def proj(lon: float, lat: float) -> tuple[float, float]:
    """Project (lon, lat) onto 460x154 equirectangular SVG canvas."""
    x = (lon + 180.0) / 360.0 * 460.0
    y = (75.0 - lat) / 133.0 * 154.0
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
    # SE Asia / New Guinea / Solomon Is.
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
        f'<polygon points="{poly_pts(c)}" fill="#EAE1CE" stroke="#6E7C91" stroke-width="0.9" stroke-linejoin="round"/>'
        for c in CONTINENTS
    )
    # 10 pins covering every inhabited continent without overlap
    pins = [
        (1, 99.0, 40.9, "#1E3A8A", -8, -14),    # China Space
        (2, 127.0, 37.5, "#DC2626", 13, -2),    # Korea / Asia Markets
        (3, 56.3, 26.6, "#EA580C", -3, 3),      # Hormuz
        (4, 155.5, -16.5, "#0F766E", 10, -4),   # Australia-Solomons
        (5, 90.4, 23.8, "#B45309", -4, 13),     # Bangladesh
        (6, 30.5, 50.4, "#4338CA", 5, -2),      # Ukraine / US talks
        (7, 22.0, 12.0, "#0E7490", -2, 8),      # Africa (Libya/DRC/Sudan)
        (8, -66.9, 6.5, "#9D174D", 4, 12),      # Venezuela Debt
        (9, -0.1, 51.5, "#334155", -12, -10),   # London UK
        (10, -87.6, 41.8, "#1D4ED8", -10, -4),  # US Trade / Chicago
    ]
    wx, wy = proj(-77.0, 38.9)
    kx, ky = proj(30.5, 50.4)
    ax, ay = proj(149.1, -35.3)
    sx, sy = proj(160.0, -9.4)

    arc_us_eu = (
        f'<path d="M {wx} {wy} Q {(wx+kx)/2} {min(wy,ky)-26} {kx} {ky}" '
        f'fill="none" stroke="#4338CA" stroke-width="1.6" stroke-dasharray="3,2"/>'
    )
    arc_aus_sol = (
        f'<path d="M {ax} {ay} Q {ax+11} {(ay+sy)/2} {sx} {sy}" '
        f'fill="none" stroke="#0F766E" stroke-width="2"/>'
        f'<circle cx="{sx}" cy="{sy}" r="2.8" fill="#0F766E" stroke="#FFF" stroke-width="0.9"/>'
    )

    markers = []
    for num, lon, lat, color, dx, dy in pins:
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        leader = ""
        if dx != 0 or dy != 0:
            leader = f'<line x1="{px}" y1="{py}" x2="{cx}" y2="{cy}" stroke="{color}" stroke-width="1.3"/>'
        markers.append(
            f'{leader}'
            f'<circle cx="{cx}" cy="{cy}" r="9.2" fill="{color}" stroke="#FFFFFF" stroke-width="1.8"/>'
            f'<text x="{cx}" y="{cy+3.3}" text-anchor="middle" fill="#FFFFFF" font-family="Segoe UI, Arial, sans-serif" font-size="9.8" font-weight="900">{num}</text>'
        )

    return f"""
    <svg viewBox="0 0 460 154" width="460" height="154" xmlns="http://www.w3.org/2000/svg" style="display:block;border-radius:6px;background:#D8E8F2;border:1px solid #B8CAD8;">
      <g opacity="0.35" stroke="#92AFC4" stroke-width="0.6">
        <line x1="0" y1="77" x2="460" y2="77" stroke-dasharray="4,4"/>
        <line x1="230" y1="0" x2="230" y2="154" stroke-dasharray="4,4"/>
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
    background: #F6F1E6;
    color: #0F172A;
    font-family: "Segoe UI", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .page {{
    width: 1024px;
    height: 1024px;
    padding: 14px 18px 14px 18px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}
  .masthead {{
    border-top: 4px solid #0F172A;
    border-bottom: 3px double #0F172A;
    padding: 4px 0 5px 0;
    text-align: center;
  }}
  .mast-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13.5px;
    font-weight: 800;
    letter-spacing: 1.2px;
    color: #334155;
    text-transform: uppercase;
    margin-bottom: 1px;
  }}
  .mast-date {{
    font-family: Georgia, "Times New Roman", serif;
    font-size: 44px;
    font-weight: 900;
    letter-spacing: 0.7px;
    line-height: 1.02;
    color: #0B1320;
  }}
  .mast-sub {{
    margin-top: 2px;
    font-size: 13.5px;
    font-weight: 800;
    letter-spacing: 0.8px;
    color: #475569;
    text-transform: uppercase;
  }}
  .row-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }}
  .row-3 {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
  }}
  .row-4 {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 10px;
    flex: 1;
  }}
  .card {{
    background: #FFFDF9;
    border: 1.5px solid #CBD5E1;
    border-radius: 9px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 4px rgba(15, 23, 42, 0.06);
  }}
  .card-bar {{
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 5px 10px;
    color: #FFFFFF;
    font-size: 13.5px;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }}
  .num-pill {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(255,255,255,0.24);
    border: 1.5px solid #FFFFFF;
    font-size: 12px;
    font-weight: 900;
    flex-shrink: 0;
  }}
  .card-body {{
    padding: 8px 11px 8px 11px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
  }}
  .hl-lg {{
    font-size: 23.5px;
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: -0.25px;
    color: #0F172A;
  }}
  .hl-sm {{
    font-size: 19.5px;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.25px;
    color: #0F172A;
  }}
  .hl-xs {{
    font-size: 16.5px;
    font-weight: 900;
    line-height: 1.12;
    letter-spacing: -0.2px;
    color: #0F172A;
  }}
  .facts {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 16.5px;
    line-height: 1.22;
    color: #1E293B;
    font-weight: 600;
  }}
  .facts li::before {{
    content: "▸ ";
    font-weight: 900;
  }}
  .facts strong {{
    color: #0B1320;
    font-weight: 800;
  }}
  .split-h {{
    display: grid;
    grid-template-columns: 184px 1fr;
    gap: 10px;
    align-items: center;
    flex: 1;
  }}
  .map-legend {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 4px 4px;
    font-size: 11.5px;
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
    font-size: 9px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
  }}
  .art-box {{
    width: 100%;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #D5DEE8;
  }}
  .bars {{
    display: flex;
    flex-direction: column;
    gap: 4.5px;
  }}
  .bar-row {{
    display: grid;
    grid-template-columns: 92px 1fr 62px;
    align-items: center;
    gap: 6px;
    font-size: 15px;
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
    line-height: 1.2;
    font-weight: 700;
    color: #1E293B;
  }}
</style>
</head>
<body>
<div class="page">

  <header class="masthead">
    <div class="mast-top">
      <span>ALL-CONTINENT VISUAL EDITION</span>
      <span>10 STORIES &middot; 6 CONTINENTS &middot; ONE DAY</span>
    </div>
    <div class="mast-date">WEDNESDAY &middot; 25 NOVEMBER 2026</div>
    <div class="mast-sub">VERIFIED WORLD NEWS DISPATCHES AS REPORTED ON 25 NOV 2026</div>
  </header>

  <!-- ROW 1: GLOBAL MAP (10 PINS) + STORY 1 (SPACE) -->
  <section class="row-2" style="height: 244px;">
    <div class="card">
      <div class="card-bar" style="background:#0F172A;">
        <span>GLOBAL DISPATCH MAP &middot; 10 STORIES</span>
      </div>
      <div class="card-body" style="padding: 6px 9px 6px 9px; gap: 4px;">
        {MAP_SVG}
        <div class="map-legend">
          <span class="leg-item"><span class="dot" style="background:#1E3A8A;">1</span>SPACE</span>
          <span class="leg-item"><span class="dot" style="background:#DC2626;">2</span>CHIPS</span>
          <span class="leg-item"><span class="dot" style="background:#EA580C;">3</span>HORMUZ</span>
          <span class="leg-item"><span class="dot" style="background:#0F766E;">4</span>PACIFIC</span>
          <span class="leg-item"><span class="dot" style="background:#B45309;">5</span>DHAKA</span>
          <span class="leg-item"><span class="dot" style="background:#4338CA;">6</span>UKRAINE</span>
          <span class="leg-item"><span class="dot" style="background:#0E7490;">7</span>AFRICA</span>
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
          <div class="art-box" style="height: 148px;">
            <svg viewBox="0 0 184 148" width="184" height="148" xmlns="http://www.w3.org/2000/svg" style="display:block;background:linear-gradient(180deg,#0A1633 0%,#1B3568 100%);">
              <circle cx="22" cy="22" r="1.5" fill="#FFF" opacity="0.8"/>
              <circle cx="48" cy="14" r="1.2" fill="#FFF" opacity="0.7"/>
              <circle cx="155" cy="18" r="1.5" fill="#FFF" opacity="0.8"/>
              <ellipse cx="92" cy="166" rx="130" ry="32" fill="#1D4ED8" stroke="#60A5FA" stroke-width="2"/>
              <g transform="translate(115,25)">
                <rect x="-26" y="6" width="52" height="7" rx="2" fill="#E2E8F0"/>
                <rect x="-4" y="-12" width="8" height="34" rx="2" fill="#CBD5E1"/>
                <rect x="-32" y="-8" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="12" y="-8" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="-32" y="16" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="12" y="16" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <text x="0" y="38" text-anchor="middle" fill="#93C5FD" font-size="8.5" font-weight="900">TIANGONG</text>
              </g>
              <g transform="translate(50,76) rotate(-25)">
                <path d="M-9,26 L0,54 L9,26 Z" fill="#F97316"/>
                <path d="M-4.5,26 L0,43 L4.5,26 Z" fill="#FDE047"/>
                <rect x="-7" y="-24" width="14" height="50" rx="3" fill="#F8FAFC"/>
                <polygon points="-7,-24 0,-42 7,-24" fill="#EF4444"/>
                <rect x="-12" y="6" width="5" height="20" rx="1.5" fill="#E2E8F0"/>
                <rect x="7" y="6" width="5" height="20" rx="1.5" fill="#E2E8F0"/>
              </g>
              <rect x="106" y="82" width="32" height="21" rx="2" fill="#DE2910" stroke="#FFF" stroke-width="1"/>
              <polygon points="114,87 115.5,91 119.5,91 116.2,93.5 117.5,97.5 114,95 110.5,97.5 111.8,93.5 108.5,91 112.5,91" fill="#FFDE00"/>
              <rect x="144" y="82" width="32" height="21" rx="2" fill="#01411C" stroke="#FFF" stroke-width="1"/>
              <rect x="144" y="82" width="8" height="21" fill="#FFF"/>
              <circle cx="162" cy="92.5" r="5" fill="#FFF"/>
              <circle cx="164" cy="91" r="4" fill="#01411C"/>
              <text x="141" y="119" text-anchor="middle" fill="#F8FAFC" font-size="11" font-weight="900">CN + PK CREW</text>
            </svg>
          </div>
          <ul class="facts">
            <li><strong>First foreign astronaut</strong> on Tiangong station</li>
            <li>Pakistan's <strong>M. Zeeshan Ali</strong> + 2 taikonauts</li>
            <li>Liftoff <strong>08:18 BJT (00:18 UTC)</strong>, Jiuquan</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- ROW 2: MARKETS + HORMUZ -->
  <section class="row-2" style="height: 238px;">
    <div class="card">
      <div class="card-bar" style="background:#DC2626;">
        <span class="num-pill">2</span>
        <span>GLOBAL MARKETS &middot; AI &amp; TECH</span>
      </div>
      <div class="card-body">
        <div class="hl-lg">ASIAN AI &amp; CHIP STOCKS PLUNGE</div>
        <div class="split-h">
          <div class="art-box" style="height: 150px;">
            <svg viewBox="0 0 184 150" width="184" height="150" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#FFF5F5;">
              <line x1="14" y1="34" x2="170" y2="34" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <line x1="14" y1="72" x2="170" y2="72" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <line x1="14" y1="110" x2="170" y2="110" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <polyline points="14,36 46,40 74,56 100,52 126,90 160,118" fill="none" stroke="#DC2626" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
              <polygon points="164,122 148,120 158,108" fill="#DC2626"/>
              <rect x="14" y="10" width="110" height="25" rx="5" fill="#991B1B"/>
              <text x="69" y="28" text-anchor="middle" fill="#FFF" font-size="14" font-weight="900">KOSPI -6.2%</text>
              <!-- AI Chip icon top-right -->
              <g transform="translate(136,10)">
                <rect x="4" y="4" width="24" height="24" rx="3" fill="#1E293B" stroke="#DC2626" stroke-width="1.5"/>
                <text x="16" y="19" text-anchor="middle" fill="#FECACA" font-size="9" font-weight="900">AI</text>
                <line x1="10" y1="0" x2="10" y2="4" stroke="#64748B" stroke-width="2"/>
                <line x1="22" y1="0" x2="22" y2="4" stroke="#64748B" stroke-width="2"/>
                <line x1="10" y1="28" x2="10" y2="32" stroke="#64748B" stroke-width="2"/>
                <line x1="22" y1="28" x2="22" y2="32" stroke="#64748B" stroke-width="2"/>
                <line x1="0" y1="10" x2="4" y2="10" stroke="#64748B" stroke-width="2"/>
                <line x1="0" y1="22" x2="4" y2="22" stroke="#64748B" stroke-width="2"/>
                <line x1="28" y1="10" x2="32" y2="10" stroke="#64748B" stroke-width="2"/>
                <line x1="28" y1="22" x2="32" y2="22" stroke="#64748B" stroke-width="2"/>
              </g>
              <rect x="14" y="122" width="142" height="21" rx="4" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.3"/>
              <text x="85" y="137" text-anchor="middle" fill="#991B1B" font-size="11" font-weight="900">SIDECAR TRIGGERED</text>
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
            <div style="font-size:15.5px;font-weight:700;color:#1E293B;border-top:1px solid #E2E8F0;padding-top:4px;">
              Seoul hits <strong>4,697.51</strong> (-308.5 pts), 10-mo low.
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
          <div class="art-box" style="height: 150px;">
            <svg viewBox="0 0 184 150" width="184" height="150" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#1A365D;">
              <polygon points="0,0 184,0 184,48 134,38 106,30 78,42 0,40" fill="#D6C7A9" stroke="#78716C" stroke-width="1"/>
              <polygon points="0,104 60,92 94,104 106,74 122,88 140,134 184,150 0,150" fill="#E7D8B9" stroke="#78716C" stroke-width="1"/>
              <text x="12" y="21" fill="#44403C" font-size="11" font-weight="900">IRAN</text>
              <text x="10" y="142" fill="#44403C" font-size="10.5" font-weight="900">SAUDI / UAE</text>
              <text x="142" y="54" text-anchor="middle" fill="#BAE6FD" font-size="8.5" font-weight="800" font-style="italic">HORMUZ</text>
              <g transform="translate(86,60)">
                <circle cx="8" cy="-18" r="5" fill="#64748B" opacity="0.65"/>
                <circle cx="13" cy="-24" r="6" fill="#94A3B8" opacity="0.5"/>
                <polygon points="-21,6 21,6 26,0 -19,0" fill="#0F172A"/>
                <rect x="-13" y="-6" width="8" height="6" fill="#F8FAFC"/>
                <path d="M1,0 Q8,-15 15,0 Q10,-21 1,-14 Z" fill="#F97316"/>
                <path d="M4,0 Q9,-9 13,0 Z" fill="#FDE047"/>
              </g>
              <g transform="translate(142,76)">
                <circle cx="7" cy="-16" r="4.5" fill="#64748B" opacity="0.65"/>
                <circle cx="11" cy="-22" r="5.5" fill="#94A3B8" opacity="0.5"/>
                <polygon points="-18,6 18,6 23,0 -16,0" fill="#0F172A"/>
                <rect x="-11" y="-5" width="7" height="5" fill="#F8FAFC"/>
                <path d="M0,0 Q7,-13 13,0 Q9,-19 0,-12 Z" fill="#EF4444"/>
                <path d="M3,0 Q7,-8 11,0 Z" fill="#FDE047"/>
              </g>
              <circle cx="45" cy="70" r="8" fill="#111827" stroke="#F8FAFC" stroke-width="1.2"/>
              <line x1="45" y1="57" x2="45" y2="83" stroke="#111827" stroke-width="2"/>
              <line x1="32" y1="70" x2="58" y2="70" stroke="#111827" stroke-width="2"/>
              <line x1="36" y1="61" x2="54" y2="79" stroke="#111827" stroke-width="2"/>
              <line x1="36" y1="79" x2="54" y2="61" stroke="#111827" stroke-width="2"/>
              <path d="M 14 122 A 21 21 0 0 1 53 113" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="3,2"/>
              <g stroke="#DC2626" stroke-width="2" stroke-linecap="round">
                <line x1="18" y1="106" x2="24" y2="112"/><line x1="24" y1="106" x2="18" y2="112"/>
                <line x1="29" y1="102" x2="35" y2="108"/><line x1="35" y1="102" x2="29" y2="108"/>
                <line x1="41" y1="105" x2="47" y2="111"/><line x1="47" y1="105" x2="41" y2="111"/>
              </g>
              <text x="58" y="112" fill="#991B1B" font-size="10" font-weight="900">4 DRONES</text>
              <text x="58" y="122" fill="#991B1B" font-size="9.5" font-weight="800">DOWNED</text>
            </svg>
          </div>
          <ul class="facts">
            <li><strong>2 oil tankers catch fire</strong> after hitting mines</li>
            <li>Saudi downs <strong>4 drones</strong> over Ras Tanura</li>
            <li><strong>Houthis threaten</strong> Jeddah &amp; Red Sea ports</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- ROW 3: OCEANIA, SOUTH ASIA, US-EUROPE -->
  <section class="row-3" style="height: 214px;">
    <div class="card">
      <div class="card-bar" style="background:#0F766E;">
        <span class="num-pill">4</span>
        <span>OCEANIA &middot; GEOPOLITICS</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 76px;">
          <svg viewBox="0 0 296 76" width="296" height="76" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#E6F4F1;">
            <polygon points="16,32 38,20 58,18 72,28 74,48 60,60 40,56 18,54" fill="#0F766E" opacity="0.9"/>
            <text x="45" y="43" text-anchor="middle" fill="#FFF" font-size="11" font-weight="900">AUS</text>
            <circle cx="110" cy="18" r="4.5" fill="#0F766E"/>
            <circle cx="121" cy="22" r="4" fill="#0F766E"/>
            <path d="M 66 28 Q 88 12 106 18" fill="none" stroke="#0F766E" stroke-width="2.2" stroke-dasharray="4,3"/>
            <text x="117" y="40" text-anchor="middle" fill="#0F766E" font-size="9.5" font-weight="900">SOLOMON IS.</text>
            <rect x="168" y="8" width="118" height="27" rx="4" fill="#0F766E"/>
            <text x="227" y="26" text-anchor="middle" fill="#FFF" font-size="12.5" font-weight="900">AU$740M / 10Y</text>
            <rect x="168" y="40" width="118" height="28" rx="4" fill="#FFF" stroke="#DC2626" stroke-width="1.8"/>
            <text x="227" y="58" text-anchor="middle" fill="#B91C1C" font-size="10.5" font-weight="900">NO FOREIGN BASES</text>
          </svg>
        </div>
        <div class="hl-sm">AUSTRALIA&ndash;SOLOMON SECURITY TREATY</div>
        <div class="wire-fact">PMs <strong>Albanese &amp; Wale</strong> sign pact barring foreign bases; AU$740M aid.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#B45309;">
        <span class="num-pill">5</span>
        <span>SOUTH ASIA &middot; LABOR</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 76px;">
          <svg viewBox="0 0 296 76" width="296" height="76" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#FEF3C7;">
            <polygon points="16,66 16,26 38,14 38,26 60,14 60,26 82,14 82,66" fill="#78350F"/>
            <line x1="22" y1="22" x2="76" y2="60" stroke="#DC2626" stroke-width="5" stroke-linecap="round"/>
            <line x1="76" y1="22" x2="22" y2="60" stroke="#DC2626" stroke-width="5" stroke-linecap="round"/>
            <rect x="104" y="8" width="180" height="27" rx="4" fill="#92400E"/>
            <text x="194" y="26" text-anchor="middle" fill="#FFF" font-size="13" font-weight="900">PAY VOTE: &#x09F3;17,000</text>
            <rect x="104" y="40" width="180" height="28" rx="4" fill="#DC2626"/>
            <text x="194" y="58" text-anchor="middle" fill="#FFF" font-size="12.5" font-weight="900">UNIONS SEEK &#x09F3;18K+</text>
          </svg>
        </div>
        <div class="hl-sm">BANGLADESH GARMENT STRIKE SHUTS PLANTS</div>
        <div class="wire-fact"><strong>87+ factories close</strong> after &#x09F3;17K pay vote; <strong>108 BGB units</strong> deployed.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#4338CA;">
        <span class="num-pill">6</span>
        <span>WAR &amp; DIPLOMACY</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 76px;">
          <svg viewBox="0 0 296 76" width="296" height="76" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#EEF2FF;">
            <rect x="14" y="6" width="106" height="64" rx="4" fill="#FFF" stroke="#4338CA" stroke-width="1.8"/>
            <text x="67" y="20" text-anchor="middle" fill="#312E81" font-size="10.5" font-weight="900">US&ndash;RUSSIA</text>
            <text x="67" y="32" text-anchor="middle" fill="#4338CA" font-size="9.2" font-weight="800">CORPORATE LURES</text>
            <g transform="translate(67,52) rotate(-7)">
              <rect x="-38" y="-10" width="76" height="20" rx="3" fill="#FFF1F2" stroke="#DC2626" stroke-width="2"/>
              <text x="0" y="4" text-anchor="middle" fill="#DC2626" font-size="12" font-weight="900">SHELVED</text>
            </g>
            <polygon points="128,34 148,34 148,28 162,38 148,48 148,42 128,42" fill="#4338CA"/>
            <defs>
              <clipPath id="shieldClip4">
                <path d="M172,8 L282,8 L282,50 Q282,64 227,69 Q172,64 172,50 Z"/>
              </clipPath>
            </defs>
            <g clip-path="url(#shieldClip4)">
              <rect x="172" y="8" width="110" height="30" fill="#1E3A8A"/>
              <rect x="172" y="38" width="110" height="32" fill="#FACC15"/>
            </g>
            <path d="M172,8 L282,8 L282,50 Q282,64 227,69 Q172,64 172,50 Z" fill="none" stroke="#0F172A" stroke-width="1.8"/>
            <text x="227" y="28" text-anchor="middle" fill="#FFF" font-size="12" font-weight="900">UKRAINE</text>
            <text x="227" y="54" text-anchor="middle" fill="#0F172A" font-size="10" font-weight="900">SECURITY FOCUS</text>
          </svg>
        </div>
        <div class="hl-sm">U.S. SHELVES RUSSIA BUSINESS PITCH</div>
        <div class="wire-fact">Envoys tell Europe Moscow lures dropped; talks shift to security (FT).</div>
      </div>
    </div>
  </section>

  <!-- ROW 4: 4 CONTINENTAL WIRE DISPATCHES WITH FULL MINI-SCENES -->
  <section class="row-4">
    <div class="card">
      <div class="card-bar" style="background:#0E7490;">
        <span class="num-pill">7</span>
        <span>AFRICA &middot; SECURITY</span>
      </div>
      <div class="card-body" style="gap: 4px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 44px;">
          <svg viewBox="0 0 218 44" width="218" height="44" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#ECFEFF;">
            <polygon points="16,6 32,6 39,17 33,26 27,39 20,26 12,17" fill="#0E7490"/>
            <circle cx="29" cy="11" r="4" fill="#DC2626" stroke="#FFF" stroke-width="1.2"/>
            <circle cx="30" cy="24" r="4" fill="#F97316" stroke="#FFF" stroke-width="1.2"/>
            <rect x="52" y="7" width="76" height="30" rx="4" fill="#0E7490"/>
            <text x="90" y="20" text-anchor="middle" fill="#FFF" font-size="9.5" font-weight="900">BENGHAZI</text>
            <text x="90" y="31" text-anchor="middle" fill="#CFFAFE" font-size="8.5" font-weight="800">2 OFFICERS DIE</text>
            <rect x="134" y="7" width="76" height="30" rx="4" fill="#FFF" stroke="#DC2626" stroke-width="1.5"/>
            <text x="172" y="20" text-anchor="middle" fill="#B91C1C" font-size="9.5" font-weight="900">E. CONGO</text>
            <text x="172" y="31" text-anchor="middle" fill="#991B1B" font-size="8.5" font-weight="800">M23 / ADF</text>
          </svg>
        </div>
        <div class="hl-xs">BENGHAZI TOLL &amp; DRC CLASHES</div>
        <div class="wire-fact">2 Libyan officers die after ship strike; clashes flare in E. Congo.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#9D174D;">
        <span class="num-pill">8</span>
        <span>S. AMERICA &middot; DEBT</span>
      </div>
      <div class="card-body" style="gap: 4px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 44px;">
          <svg viewBox="0 0 218 44" width="218" height="44" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#FDF2F8;">
            <rect x="12" y="25" width="9" height="13" rx="1" fill="#F472B6"/>
            <rect x="25" y="18" width="9" height="20" rx="1" fill="#DB2777"/>
            <rect x="38" y="8" width="11" height="30" rx="1" fill="#9D174D"/>
            <rect x="60" y="7" width="146" height="30" rx="4" fill="#9D174D"/>
            <text x="133" y="21" text-anchor="middle" fill="#FFF" font-size="11.5" font-weight="900">$237.5B DEBT</text>
            <text x="133" y="32" text-anchor="middle" fill="#FCE7F3" font-size="9" font-weight="800">242% OF GDP</text>
          </svg>
        </div>
        <div class="hl-xs">VENEZUELA REVEALS $237.5B DEBT</div>
        <div class="wire-fact">Official tally hits <strong>242% of GDP</strong> ahead of restructuring.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#334155;">
        <span class="num-pill">9</span>
        <span>UK &amp; EUROPE &middot; JUSTICE</span>
      </div>
      <div class="card-body" style="gap: 4px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 44px;">
          <svg viewBox="0 0 218 44" width="218" height="44" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#F1F5F9;">
            <rect x="14" y="6" width="28" height="32" rx="2" fill="#FFF" stroke="#334155" stroke-width="1.6"/>
            <line x1="19" y1="14" x2="37" y2="14" stroke="#334155" stroke-width="2"/>
            <line x1="19" y1="21" x2="37" y2="21" stroke="#DC2626" stroke-width="2"/>
            <line x1="19" y1="28" x2="32" y2="28" stroke="#334155" stroke-width="2"/>
            <rect x="54" y="7" width="152" height="30" rx="4" fill="#FFF" stroke="#DC2626" stroke-width="1.6"/>
            <text x="130" y="20" text-anchor="middle" fill="#334155" font-size="9.5" font-weight="900">FAIRFIELD REVIEW</text>
            <text x="130" y="31" text-anchor="middle" fill="#DC2626" font-size="9" font-weight="900">INSTITUTIONAL BIAS</text>
          </svg>
        </div>
        <div class="hl-xs">MET POLICE STILL 'BIASED': REVIEW</div>
        <div class="wire-fact">Report finds London force still racist &amp; misogynistic.</div>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#1D4ED8;">
        <span class="num-pill">10</span>
        <span>N. AMERICA &middot; TRADE</span>
      </div>
      <div class="card-body" style="gap: 4px; padding: 6px 9px 7px 9px;">
        <div class="art-box" style="height: 44px;">
          <svg viewBox="0 0 218 44" width="218" height="44" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#EFF6FF;">
            <rect x="12" y="7" width="96" height="30" rx="4" fill="#1D4ED8"/>
            <text x="60" y="20" text-anchor="middle" fill="#FFF" font-size="9.5" font-weight="900">TARIFF PROBE</text>
            <text x="60" y="31" text-anchor="middle" fill="#DBEAFE" font-size="8.8" font-weight="800">16 PARTNERS</text>
            <rect x="114" y="7" width="94" height="30" rx="4" fill="#FFF" stroke="#DC2626" stroke-width="1.5"/>
            <text x="161" y="20" text-anchor="middle" fill="#1E293B" font-size="9.5" font-weight="900">O'HARE STOP</text>
            <text x="161" y="31" text-anchor="middle" fill="#DC2626" font-size="8.5" font-weight="900">FAA RADAR OUT</text>
          </svg>
        </div>
        <div class="hl-xs">U.S. EYES TARIFFS; O'HARE DELAY</div>
        <div class="wire-fact">Overcapacity duties drafted; FAA outage slows Chicago hub.</div>
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
