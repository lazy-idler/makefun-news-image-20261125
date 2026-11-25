"""Deterministic 1024x1024 world news broadsheet renderer for Wednesday, 25 November 2026."""

from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSET_OUT = ROOT / "assets" / "entry.png"
SCRATCH_DIR = Path(r"C:\Users\82103\.gemini\antigravity\brain\c8bbd2ac-e3a5-415b-8afb-bf347f8e20ad\scratch")
PREVIEW_300 = SCRATCH_DIR / "preview_300_v3.png"


def proj(lon: float, lat: float) -> tuple[float, float]:
    """Project (lon, lat) onto 460x188 equirectangular SVG canvas."""
    x = (lon + 180.0) / 360.0 * 460.0
    y = (75.0 - lat) / 133.0 * 188.0
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
        f'<polygon points="{poly_pts(c)}" fill="#EAE1CE" stroke="#6E7C91" stroke-width="0.95" stroke-linejoin="round"/>'
        for c in CONTINENTS
    )
    pins = [
        (1, 99.0, 40.9, "#1E3A8A", -10, -14),   # Jiuquan, China
        (2, 127.0, 37.5, "#DC2626", 13, -3),    # Seoul, South Korea
        (3, 56.3, 26.6, "#EA580C", -5, 4),      # Strait of Hormuz
        (4, 155.5, -16.5, "#0F766E", 10, -4),   # Australia-Solomon Is. pact
        (5, 90.4, 23.8, "#B45309", -4, 13),     # Dhaka, Bangladesh
        (6, 30.5, 50.4, "#4338CA", 2, -2),      # Ukraine / Europe
    ]
    wx, wy = proj(-77.0, 38.9)
    kx, ky = proj(30.5, 50.4)
    ax, ay = proj(149.1, -35.3)
    sx, sy = proj(160.0, -9.4)

    arc_us_eu = (
        f'<path d="M {wx} {wy} Q {(wx+kx)/2} {min(wy,ky)-30} {kx} {ky}" '
        f'fill="none" stroke="#4338CA" stroke-width="2" stroke-dasharray="4,2.5"/>'
    )
    arc_aus_sol = (
        f'<path d="M {ax} {ay} Q {ax+11} {(ay+sy)/2} {sx} {sy}" '
        f'fill="none" stroke="#0F766E" stroke-width="2.2"/>'
        f'<circle cx="{sx}" cy="{sy}" r="3" fill="#0F766E" stroke="#FFF" stroke-width="1"/>'
    )

    markers = []
    for num, lon, lat, color, dx, dy in pins:
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        leader = ""
        if dx != 0 or dy != 0:
            leader = f'<line x1="{px}" y1="{py}" x2="{cx}" y2="{cy}" stroke="{color}" stroke-width="1.5"/>'
        markers.append(
            f'{leader}'
            f'<circle cx="{cx}" cy="{cy}" r="10.5" fill="{color}" stroke="#FFFFFF" stroke-width="2"/>'
            f'<text x="{cx}" y="{cy+4}" text-anchor="middle" fill="#FFFFFF" font-family="Segoe UI, Arial, sans-serif" font-size="11.5" font-weight="900">{num}</text>'
        )

    us_pin = (
        f'<circle cx="{wx}" cy="{wy}" r="9" fill="#4338CA" stroke="#FFFFFF" stroke-width="1.8"/>'
        f'<text x="{wx}" y="{wy+3.3}" text-anchor="middle" fill="#FFFFFF" font-family="Segoe UI, Arial, sans-serif" font-size="8.8" font-weight="900">US</text>'
    )

    return f"""
    <svg viewBox="0 0 460 188" width="460" height="188" xmlns="http://www.w3.org/2000/svg" style="display:block;border-radius:6px;background:#D8E8F2;border:1px solid #B8CAD8;">
      <g opacity="0.38" stroke="#92AFC4" stroke-width="0.6">
        <line x1="0" y1="94" x2="460" y2="94" stroke-dasharray="4,4"/>
        <line x1="230" y1="0" x2="230" y2="188" stroke-dasharray="4,4"/>
      </g>
      {polys}
      {arc_us_eu}
      {arc_aus_sol}
      {us_pin}
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
    padding: 16px 20px 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .masthead {{
    border-top: 4px solid #0F172A;
    border-bottom: 3px double #0F172A;
    padding: 5px 0 7px 0;
    text-align: center;
  }}
  .mast-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 1.4px;
    color: #334155;
    text-transform: uppercase;
    margin-bottom: 2px;
  }}
  .mast-date {{
    font-family: Georgia, "Times New Roman", serif;
    font-size: 46px;
    font-weight: 900;
    letter-spacing: 0.8px;
    line-height: 1.03;
    color: #0B1320;
  }}
  .mast-sub {{
    margin-top: 3px;
    font-size: 14.5px;
    font-weight: 700;
    letter-spacing: 0.9px;
    color: #475569;
    text-transform: uppercase;
  }}
  .row-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }}
  .row-3 {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 14px;
    flex: 1;
  }}
  .card {{
    background: #FFFDF9;
    border: 1.5px solid #CBD5E1;
    border-radius: 10px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.06);
  }}
  .card-bar {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 11px;
    color: #FFFFFF;
    font-size: 14.5px;
    font-weight: 800;
    letter-spacing: 0.6px;
    text-transform: uppercase;
  }}
  .num-pill {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: rgba(255,255,255,0.24);
    border: 1.5px solid #FFFFFF;
    font-size: 13.5px;
    font-weight: 900;
    flex-shrink: 0;
  }}
  .card-body {{
    padding: 9px 12px 10px 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1;
  }}
  .hl-lg {{
    font-size: 25px;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.2px;
    color: #0F172A;
  }}
  .hl-sm {{
    font-size: 22px;
    font-weight: 900;
    line-height: 1.12;
    letter-spacing: -0.25px;
    color: #0F172A;
  }}
  .facts {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 5px;
    font-size: 17.5px;
    line-height: 1.24;
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
    grid-template-columns: 188px 1fr;
    gap: 11px;
    align-items: center;
    flex: 1;
  }}
  .map-legend {{
    display: flex;
    flex-wrap: nowrap;
    justify-content: space-between;
    gap: 4px;
    font-size: 13px;
    font-weight: 800;
    color: #1E293B;
    padding-top: 2px;
  }}
  .leg-item {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }}
  .dot {{
    width: 15px;
    height: 15px;
    border-radius: 50%;
    color: #FFF;
    font-size: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
  }}
  .art-box {{
    width: 100%;
    border-radius: 7px;
    overflow: hidden;
    border: 1px solid #D5DEE8;
  }}
  .bars {{
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .bar-row {{
    display: grid;
    grid-template-columns: 98px 1fr 66px;
    align-items: center;
    gap: 7px;
    font-size: 15.5px;
    font-weight: 800;
    color: #1E293B;
  }}
  .bar-track {{
    height: 16px;
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
</style>
</head>
<body>
<div class="page">

  <header class="masthead">
    <div class="mast-top">
      <span>WORLD NEWS VISUAL SUMMARY</span>
      <span>6 CONTINENTS &amp; BEATS &middot; ONE DAY</span>
    </div>
    <div class="mast-date">WEDNESDAY &middot; 25 NOVEMBER 2026</div>
    <div class="mast-sub">VERIFIED GLOBAL DISPATCHES AS REPORTED ON 25 NOV 2026</div>
  </header>

  <section class="row-2" style="height: 256px;">
    <div class="card">
      <div class="card-bar" style="background:#0F172A;">
        <span>GLOBAL DISPATCH MAP &middot; 25 NOV 2026</span>
      </div>
      <div class="card-body" style="padding: 8px 10px 8px 10px; gap: 5px;">
        {MAP_SVG}
        <div class="map-legend">
          <span class="leg-item"><span class="dot" style="background:#1E3A8A;">1</span>SPACE</span>
          <span class="leg-item"><span class="dot" style="background:#DC2626;">2</span>MARKETS</span>
          <span class="leg-item"><span class="dot" style="background:#EA580C;">3</span>HORMUZ</span>
          <span class="leg-item"><span class="dot" style="background:#0F766E;">4</span>PACIFIC</span>
          <span class="leg-item"><span class="dot" style="background:#B45309;">5</span>DHAKA</span>
          <span class="leg-item"><span class="dot" style="background:#4338CA;">6</span>US-EU</span>
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
          <div class="art-box" style="height: 162px;">
            <svg viewBox="0 0 188 162" width="188" height="162" xmlns="http://www.w3.org/2000/svg" style="display:block;background:linear-gradient(180deg,#0A1633 0%,#1B3568 100%);">
              <circle cx="22" cy="24" r="1.5" fill="#FFF" opacity="0.8"/>
              <circle cx="48" cy="14" r="1.2" fill="#FFF" opacity="0.7"/>
              <circle cx="158" cy="20" r="1.5" fill="#FFF" opacity="0.8"/>
              <circle cx="170" cy="48" r="1.2" fill="#FFF" opacity="0.7"/>
              <ellipse cx="94" cy="180" rx="132" ry="34" fill="#1D4ED8" stroke="#60A5FA" stroke-width="2"/>
              <g transform="translate(115,26)">
                <rect x="-26" y="6" width="52" height="7" rx="2" fill="#E2E8F0"/>
                <rect x="-4" y="-12" width="8" height="34" rx="2" fill="#CBD5E1"/>
                <rect x="-32" y="-8" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="12" y="-8" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="-32" y="16" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
                <rect x="12" y="16" width="20" height="10" fill="#3B82F6" stroke="#93C5FD" stroke-width="1"/>
              </g>
              <g transform="translate(52,82) rotate(-25)">
                <path d="M-9,28 L0,58 L9,28 Z" fill="#F97316"/>
                <path d="M-4.5,28 L0,46 L4.5,28 Z" fill="#FDE047"/>
                <rect x="-7" y="-26" width="14" height="54" rx="3" fill="#F8FAFC"/>
                <polygon points="-7,-26 0,-45 7,-26" fill="#EF4444"/>
                <rect x="-12" y="6" width="5" height="22" rx="1.5" fill="#E2E8F0"/>
                <rect x="7" y="6" width="5" height="22" rx="1.5" fill="#E2E8F0"/>
              </g>
              <rect x="108" y="88" width="32" height="21" rx="2" fill="#DE2910" stroke="#FFF" stroke-width="1"/>
              <polygon points="116,93 117.5,97 121.5,97 118.2,99.5 119.5,103.5 116,101 112.5,103.5 113.8,99.5 110.5,97 114.5,97" fill="#FFDE00"/>
              <rect x="146" y="88" width="32" height="21" rx="2" fill="#01411C" stroke="#FFF" stroke-width="1"/>
              <rect x="146" y="88" width="8" height="21" fill="#FFF"/>
              <circle cx="164" cy="98.5" r="5" fill="#FFF"/>
              <circle cx="166" cy="97" r="4" fill="#01411C"/>
              <text x="143" y="126" text-anchor="middle" fill="#F8FAFC" font-size="11.5" font-weight="900">CN + PK CREW</text>
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

  <section class="row-2" style="height: 280px;">
    <div class="card">
      <div class="card-bar" style="background:#DC2626;">
        <span class="num-pill">2</span>
        <span>GLOBAL MARKETS &middot; AI &amp; TECH</span>
      </div>
      <div class="card-body">
        <div class="hl-lg">ASIAN AI &amp; CHIP STOCKS PLUNGE</div>
        <div class="split-h">
          <div class="art-box" style="height: 166px;">
            <svg viewBox="0 0 188 166" width="188" height="166" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#FFF5F5;">
              <line x1="14" y1="36" x2="174" y2="36" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <line x1="14" y1="78" x2="174" y2="78" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <line x1="14" y1="120" x2="174" y2="120" stroke="#FECACA" stroke-width="1" stroke-dasharray="3,3"/>
              <polyline points="14,38 46,42 74,60 100,56 128,98 164,132" fill="none" stroke="#DC2626" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
              <polygon points="168,136 151,134 162,121" fill="#DC2626"/>
              <rect x="14" y="10" width="112" height="27" rx="5" fill="#991B1B"/>
              <text x="70" y="29" text-anchor="middle" fill="#FFF" font-size="14.5" font-weight="900">KOSPI -6.2%</text>
              <rect x="14" y="135" width="144" height="22" rx="4" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.3"/>
              <text x="86" y="150" text-anchor="middle" fill="#991B1B" font-size="11.5" font-weight="900">SIDECAR TRIGGERED</text>
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
            <div style="font-size:17px;font-weight:700;color:#1E293B;border-top:1px solid #E2E8F0;padding-top:6px;">
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
        <div class="hl-lg" style="font-size:23.5px;">2 TANKERS HIT MINES IN HORMUZ</div>
        <div class="split-h">
          <div class="art-box" style="height: 166px;">
            <svg viewBox="0 0 188 166" width="188" height="166" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#1A365D;">
              <polygon points="0,0 188,0 188,52 136,42 108,32 80,46 0,44" fill="#D6C7A9" stroke="#78716C" stroke-width="1"/>
              <polygon points="0,114 62,102 96,114 108,82 124,96 142,146 188,166 0,166" fill="#E7D8B9" stroke="#78716C" stroke-width="1"/>
              <text x="12" y="23" fill="#44403C" font-size="11.5" font-weight="900">IRAN</text>
              <text x="10" y="156" fill="#44403C" font-size="11" font-weight="900">SAUDI / UAE</text>
              <!-- Burning Tanker 1 -->
              <g transform="translate(88,65)">
                <polygon points="-22,7 22,7 27,0 -20,0" fill="#0F172A"/>
                <rect x="-14" y="-6" width="8" height="6" fill="#F8FAFC"/>
                <path d="M1,0 Q8,-16 15,0 Q10,-22 1,-15 Z" fill="#F97316"/>
                <path d="M4,0 Q9,-10 13,0 Z" fill="#FDE047"/>
              </g>
              <!-- Burning Tanker 2 -->
              <g transform="translate(145,82)">
                <polygon points="-19,7 19,7 24,0 -17,0" fill="#0F172A"/>
                <rect x="-12" y="-5" width="7" height="5" fill="#F8FAFC"/>
                <path d="M0,0 Q7,-14 13,0 Q9,-20 0,-13 Z" fill="#EF4444"/>
                <path d="M3,0 Q7,-9 11,0 Z" fill="#FDE047"/>
              </g>
              <!-- Naval mine -->
              <circle cx="46" cy="76" r="8.5" fill="#111827" stroke="#F8FAFC" stroke-width="1.3"/>
              <line x1="46" y1="62" x2="46" y2="90" stroke="#111827" stroke-width="2.2"/>
              <line x1="32" y1="76" x2="60" y2="76" stroke="#111827" stroke-width="2.2"/>
              <line x1="36" y1="66" x2="56" y2="86" stroke="#111827" stroke-width="2.2"/>
              <line x1="36" y1="86" x2="56" y2="66" stroke="#111827" stroke-width="2.2"/>
              <!-- Radar arc + 4 intercepted drones -->
              <path d="M 14 134 A 22 22 0 0 1 54 124" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="3,2"/>
              <g stroke="#DC2626" stroke-width="2" stroke-linecap="round">
                <line x1="18" y1="117" x2="24" y2="123"/><line x1="24" y1="117" x2="18" y2="123"/>
                <line x1="29" y1="112" x2="35" y2="118"/><line x1="35" y1="112" x2="29" y2="118"/>
                <line x1="41" y1="115" x2="47" y2="121"/><line x1="47" y1="115" x2="41" y2="121"/>
              </g>
              <text x="58" y="122" fill="#991B1B" font-size="10.5" font-weight="900">4 DRONES</text>
              <text x="58" y="133" fill="#991B1B" font-size="9.5" font-weight="800">DOWNED</text>
            </svg>
          </div>
          <ul class="facts">
            <li><strong>2 oil tankers catch fire</strong> after hitting mines</li>
            <li>Saudi coalition downs <strong>4 drones</strong> over Ras Tanura</li>
            <li><strong>Houthis threaten</strong> Jeddah &amp; Red Sea ports</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="row-3">
    <div class="card">
      <div class="card-bar" style="background:#0F766E;">
        <span class="num-pill">4</span>
        <span>OCEANIA &middot; GEOPOLITICS</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 106px;">
          <svg viewBox="0 0 290 106" width="290" height="106" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#E6F4F1;">
            <polygon points="14,46 38,32 60,30 76,42 78,68 62,84 40,78 16,76" fill="#0F766E" opacity="0.9"/>
            <text x="46" y="61" text-anchor="middle" fill="#FFF" font-size="11.5" font-weight="900">AUS</text>
            <circle cx="112" cy="26" r="5.5" fill="#0F766E"/>
            <circle cx="124" cy="31" r="4.5" fill="#0F766E"/>
            <circle cx="135" cy="36" r="4" fill="#0F766E"/>
            <path d="M 68 42 Q 90 20 108 26" fill="none" stroke="#0F766E" stroke-width="2.5" stroke-dasharray="4,3"/>
            <text x="122" y="54" text-anchor="middle" fill="#0F766E" font-size="10" font-weight="900">SOLOMON IS.</text>
            <rect x="168" y="13" width="112" height="33" rx="5" fill="#0F766E"/>
            <text x="224" y="34" text-anchor="middle" fill="#FFF" font-size="14" font-weight="900">AU$740M / 10Y</text>
            <rect x="168" y="55" width="112" height="38" rx="5" fill="#FFF" stroke="#DC2626" stroke-width="2"/>
            <text x="224" y="72" text-anchor="middle" fill="#B91C1C" font-size="11" font-weight="900">NO FOREIGN</text>
            <text x="224" y="86" text-anchor="middle" fill="#B91C1C" font-size="11" font-weight="900">MILITARY BASES</text>
          </svg>
        </div>
        <div class="hl-sm">AUSTRALIA&ndash;SOLOMON SECURITY TREATY</div>
        <ul class="facts" style="font-size:16.5px;">
          <li>PMs <strong>Albanese &amp; Wale</strong> sign Canberra pact</li>
          <li><strong>Bars foreign bases</strong> &middot; AU$740M deal</li>
        </ul>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#B45309;">
        <span class="num-pill">5</span>
        <span>SOUTH ASIA &middot; LABOR</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 106px;">
          <svg viewBox="0 0 290 106" width="290" height="106" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#FEF3C7;">
            <polygon points="16,88 16,40 40,26 40,40 64,26 64,40 88,26 88,88" fill="#78350F"/>
            <rect x="28" y="55" width="16" height="14" fill="#FDE68A"/>
            <rect x="56" y="55" width="16" height="14" fill="#FDE68A"/>
            <line x1="24" y1="34" x2="80" y2="82" stroke="#DC2626" stroke-width="6" stroke-linecap="round"/>
            <line x1="80" y1="34" x2="24" y2="82" stroke="#DC2626" stroke-width="6" stroke-linecap="round"/>
            <rect x="104" y="13" width="174" height="35" rx="5" fill="#92400E"/>
            <text x="191" y="36" text-anchor="middle" fill="#FFF" font-size="14" font-weight="900">PAY VOTE: &#x09F3;17,000</text>
            <rect x="104" y="56" width="174" height="36" rx="5" fill="#DC2626"/>
            <text x="191" y="79" text-anchor="middle" fill="#FFF" font-size="13.5" font-weight="900">UNION DEMAND: &#x09F3;18K+</text>
          </svg>
        </div>
        <div class="hl-sm">BANGLADESH GARMENT STRIKE SHUTS PLANTS</div>
        <ul class="facts" style="font-size:16.5px;">
          <li><strong>87+ factories shut</strong> after &#x09F3;17,000 vote</li>
          <li><strong>108 BGB units</strong> deployed near Dhaka</li>
        </ul>
      </div>
    </div>

    <div class="card">
      <div class="card-bar" style="background:#4338CA;">
        <span class="num-pill">6</span>
        <span>AMERICAS &amp; EUROPE</span>
      </div>
      <div class="card-body">
        <div class="art-box" style="height: 106px;">
          <svg viewBox="0 0 290 106" width="290" height="106" xmlns="http://www.w3.org/2000/svg" style="display:block;background:#EEF2FF;">
            <rect x="14" y="12" width="102" height="82" rx="4" fill="#FFF" stroke="#4338CA" stroke-width="2"/>
            <text x="65" y="30" text-anchor="middle" fill="#312E81" font-size="11" font-weight="900">US&ndash;RUSSIA</text>
            <text x="65" y="44" text-anchor="middle" fill="#4338CA" font-size="10" font-weight="800">ENERGY &amp; AVIATION</text>
            <line x1="24" y1="54" x2="106" y2="54" stroke="#CBD5E1" stroke-width="2"/>
            <line x1="24" y1="64" x2="94" y2="64" stroke="#CBD5E1" stroke-width="2"/>
            <g transform="translate(65,67) rotate(-12)">
              <rect x="-40" y="-12" width="80" height="24" rx="3" fill="#FFF1F2" stroke="#DC2626" stroke-width="2.5"/>
              <text x="0" y="5" text-anchor="middle" fill="#DC2626" font-size="13.5" font-weight="900">SHELVED</text>
            </g>
            <polygon points="124,48 144,48 144,41 158,53 144,65 144,58 124,58" fill="#4338CA"/>
            <defs>
              <clipPath id="shieldClip">
                <path d="M168,12 L278,12 L278,70 Q278,88 223,95 Q168,88 168,70 Z"/>
              </clipPath>
            </defs>
            <g clip-path="url(#shieldClip)">
              <rect x="168" y="12" width="110" height="40" fill="#1E3A8A"/>
              <rect x="168" y="52" width="110" height="45" fill="#FACC15"/>
            </g>
            <path d="M168,12 L278,12 L278,70 Q278,88 223,95 Q168,88 168,70 Z" fill="none" stroke="#0F172A" stroke-width="2"/>
            <text x="223" y="38" text-anchor="middle" fill="#FFF" font-size="13" font-weight="900">UKRAINE</text>
            <text x="223" y="70" text-anchor="middle" fill="#0F172A" font-size="10.5" font-weight="900">SECURITY TALKS</text>
          </svg>
        </div>
        <div class="hl-sm">U.S. SHELVES RUSSIA BUSINESS PITCH</div>
        <ul class="facts" style="font-size:16.5px;">
          <li>Envoys drop Moscow corporate lures (FT)</li>
          <li><strong>Ukraine talks</strong> refocus on security</li>
        </ul>
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
