"""Dense one-page front for Wednesday 25 November 2026: 35 sourced, badged stories.

Flat shapes + type only. Every text block is measured with textlength and
wrapped programmatically; anything that would leave its box (or a glyph the
font lacks, or overlapping map pins) is reported as a warning instead of
silently spilling.
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (246, 240, 226)
PANEL = (238, 230, 212)
INK = (28, 26, 24)
SOFT = (92, 86, 78)
RULE = (150, 140, 126)
ACCENT = (160, 28, 28)
GREY = (118, 112, 104)
LAND = (196, 184, 162)
WHITE = (255, 255, 255)

FD = "/usr/share/fonts/truetype/noto/"
BOLD = FD + "NotoSans-Bold.ttf"
SC = FD + "NotoSans-SemiCondensed.ttf"
SCB = FD + "NotoSans-SemiCondensedBold.ttf"
SCSB = FD + "NotoSans-SemiCondensedSemiBold.ttf"
SCM = FD + "NotoSans-SemiCondensedMedium.ttf"
CM = FD + "NotoSans-CondensedMedium.ttf"
CBD = FD + "NotoSans-CondensedBold.ttf"
CB = FD + "NotoSansDisplay-CondensedBold.ttf"
SERIF_BLACK = FD + "NotoSerif-Black.ttf"

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
M = 24
warnings = []
_fc = {}

# Glyph guard: warn whenever a string uses a character its font lacks (no tofu boxes).
try:
    from fontTools.ttLib import TTFont
    _cmaps = {}

    def _missing(s, f):
        path = f.path
        if path not in _cmaps:
            _cmaps[path] = TTFont(path).getBestCmap()
        return {ch for ch in s if not ch.isspace() and ord(ch) not in _cmaps[path]}
except ImportError:  # pragma: no cover
    def _missing(s, f):
        return set()

_raw_text = d.text


def _checked_text(xy, s, *a, **kw):
    miss = _missing(s, kw["font"])
    if miss:
        warnings.append(f"missing glyphs {sorted(miss)} in {kw['font'].path.split('/')[-1]}: {s!r}")
    return _raw_text(xy, s, *a, **kw)


d.text = _checked_text


def font(path, size):
    key = (path, size)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(path, size)
    return _fc[key]


def tw(s, f):
    return d.textlength(s, font=f)


def wrap(s, f, width):
    lines, cur = [], ""
    for w in (p for p in s.split(" ") if p):  # split on plain spaces only: NBSP keeps dates together
        trial = (cur + " " + w).strip()
        if tw(trial, f) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(x, y, s, f, width, lh, fill, max_lines=None, tag=""):
    lines = wrap(s, f, width)
    if max_lines and len(lines) > max_lines:
        warnings.append(f"{tag}: {len(lines)} lines > {max_lines}: {s!r}")
    for ln in lines:
        if tw(ln, f) > width:
            warnings.append(f"{tag}: line too wide: {ln!r}")
        d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def check_bottom(y, limit, tag):
    if y > limit:
        warnings.append(f"{tag}: content bottom {y:.0f} > box bottom {limit:.0f}")


def centered(y, s, f, fill):
    d.text(((W - tw(s, f)) / 2, y), s, font=f, fill=fill)


def chip(x, y, label, size=10):
    """Verification badge. One system, three fills."""
    f = font(SCB, size)
    pad = 4
    w = tw(label, f) + 2 * pad
    h = size + 5
    if label == "CONFIRMED":
        d.rectangle([x, y, x + w, y + h], fill=ACCENT)
        col = WHITE
    elif label == "OFFICIAL":
        d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=ACCENT, width=1)
        col = ACCENT
    elif label == "REPORTED":
        d.rectangle([x, y, x + w, y + h], fill=GREY)
        col = WHITE
    else:
        raise ValueError(f"unknown badge {label!r}")
    d.text((x + pad, y + h / 2), label, font=f, fill=col, anchor="lm")
    return w


def chip_w(label, size):
    return tw(label, font(SCB, size)) + 8


def source_line(x, y, source, badge, width, size=12, tag=""):
    f = font(SCSB, size)
    d.text((x, y), source, font=f, fill=SOFT)
    sx = x + tw(source, f) + 6
    cw = chip(sx, y + 2, badge, size=size - 2)
    if sx + cw - x > width:
        warnings.append(f"{tag}: source+badge too wide")


# ======================= 1. MASTHEAD =======================
y = 12
centered(y, "THE WORLD IN ONE PICTURE", font(BOLD, 15), ACCENT)
y += 18
date = "WEDNESDAY 25 NOVEMBER 2026"
for ds in range(64, 55, -1):  # largest size that fits, never below 56px
    f_date = font(SERIF_BLACK, ds)
    if tw(date, f_date) <= W - 2 * M:
        break
else:
    warnings.append("date too wide even at 56px")
centered(y - 6, date, f_date, INK)
y += 78
centered(y, "35 STORIES · EVERY STORY SOURCED AND BADGED", font(SCB, 14), SOFT)
y += 22
d.line([M, y, W - M, y], fill=INK, width=3)
d.line([M, y + 5, W - M, y + 5], fill=INK, width=1)
y += 12

# ======================= 2. LEAD BAND =======================
f_kick = font(SCB, 13)
d.text((M, y), "LEAD · SPACE — JIUQUAN, CHINA", font=f_kick, fill=ACCENT)
# source + badge right-aligned on the kicker line
lead_src, lead_badge = "Japan Times / Reuters", "CONFIRMED"
f_ls = font(SCSB, 14)
cw = chip_w(lead_badge, 12)
sx = W - M - cw - 8 - tw(lead_src, f_ls)
d.text((sx, y - 1), lead_src, font=f_ls, fill=SOFT)
chip(W - M - cw, y, lead_badge, size=12)
y += 18
lead_head = "SHENZHOU-24 FLIES FIRST PAKISTANI INTO SPACE"
f_lead = font(BOLD, 38)
if tw(lead_head, f_lead) > W - 2 * M:
    warnings.append(f"lead headline too wide: {tw(lead_head, f_lead):.0f}px")
d.text((M, y - 4), lead_head, font=f_lead, fill=INK)
y += 46
y = block(M, y, "China's Shenzhou-24 crew ship lifts off from Jiuquan for the Tiangong station "
          "with Zeeshan Ali aboard — the first Pakistani national in space.",
          font(SC, 16), W - 2 * M, 20, INK, max_lines=2, tag="lead summary")
y += 6
d.line([M, y, W - M, y], fill=RULE, width=1)
y += 6

# ======================= 3. NUMBERS STRIP =======================
nums = [
    ("25", "hostages in Cartagena supermarket siege"),
    ("7,000", "landmine casualties in 2025, a 5-year high"),
    ("36%", "pay rise ends Bangladesh garment strike"),
    ("$100m", "Shein settlement with the FTC"),
    ("103.3", "US consumer confidence in November"),
    ("5", "killed in Turkish helicopter crash"),
]
SH = 44
d.rectangle([M, y, W - M, y + SH], fill=INK)
f_lab = font(SCB, 12)
f_num = font(CB, 16)
f_txt = font(SC, 13)
d.text((M + 8, y + 6), "THE DAY", font=f_lab, fill=(240, 196, 120))
d.text((M + 8, y + 22), "IN NUMBERS", font=f_lab, fill=(240, 196, 120))
nx0 = M + 90
sep = " · "
rows = [nums[:3], nums[3:]]
for ri, row in enumerate(rows):
    x = nx0
    ry = y + 4 + ri * 19
    for i, (n, t) in enumerate(row):
        if i:
            d.text((x, ry + 1), sep, font=f_txt, fill=(200, 190, 170))
            x += tw(sep, f_txt)
        d.text((x, ry - 1), n, font=f_num, fill=WHITE)
        x += tw(n, f_num) + 4
        d.text((x, ry + 1), t, font=f_txt, fill=(225, 218, 205))
        x += tw(t, f_txt)
    if x > W - M - 4:
        warnings.append(f"numbers row {ri}: overflows by {x - (W - M - 4):.0f}px")
y += SH + 8

# ======================= 4. FEATURED GRID =======================
featured = [
    ("UKRAINE WAR", "US shelves business-deal plan to end war",
     "Washington quietly drops energy and aviation offers after the Kremlin shows little interest, FT reports",
     "Reuters", "REPORTED"),
    ("UKRAINE WAR", "Russian strike kills two in Odesa region",
     "Cars and homes hit near the Black Sea port; drones also set a Kyiv tower block ablaze",
     "Reuters", "OFFICIAL"),
    ("CYBER", "CIA unclassified system breached",
     "Hackers hit an unclassified CIA system; officials say no classified data was compromised",
     "Telegraph India", "REPORTED"),
    ("TECH TRIAL", "Huawei convicted in US Iran-business trial",
     "A US jury convicts the Chinese tech giant in a sprawling criminal case over trade secrets and Iran deals",
     "Japan Times", "CONFIRMED"),
    ("CHINA", "Xi probes Shanghai party chief Chen Jining",
     "The Politburo member falls under investigation in the biggest party shakeup in decades",
     "Japan Times", "CONFIRMED"),
    ("PACIFIC", "Australia–Solomons pact shuts out China",
     "Canberra becomes Honiara's top security partner in a sweeping deal signed in Honiara",
     "Reuters", "CONFIRMED"),
    ("MIDDLE EAST", "Riyadh tower hit again; 11 injured",
     "Saudi Arabia strikes Houthi-run Hodeidah port as the Red Sea war flares again",
     "SCMP / Inshorts", "CONFIRMED"),
    ("COLOMBIA", "Gunmen hold 25 hostage in supermarket",
     "Troops surround a Cartagena store after a failed armoured-car raid; a bomb attack wounds 23 elsewhere",
     "SCMP", "REPORTED"),
]
GAP = 10
PW = (W - 2 * M - 3 * GAP) / 4
PH = 140
f_k = font(SCB, 12)
f_h = font(SCB, 19)
f_s = font(SC, 14)
for i, (reg, head, summ, src, badge) in enumerate(featured):
    c, r = i % 4, i // 4
    x0 = M + c * (PW + GAP)
    y0 = y + r * (PH + GAP)
    d.rectangle([x0, y0, x0 + PW, y0 + PH], fill=PANEL)
    d.rectangle([x0, y0, x0 + PW, y0 + 3], fill=ACCENT)
    ix, iw = x0 + 8, PW - 16
    yy = y0 + 8
    d.text((ix, yy), f"{i + 1} · {reg}", font=f_k, fill=ACCENT)
    yy += 16
    yy = block(ix, yy, head, f_h, iw, 22, INK, max_lines=2, tag=f"panel {i + 1} head")
    yy += 3
    yy = block(ix, yy, summ, f_s, iw, 16, SOFT, max_lines=4, tag=f"panel {i + 1} summary")
    foot_y = y0 + PH - 20
    check_bottom(yy, foot_y + 2, f"panel {i + 1}")
    source_line(ix, foot_y, src, badge, iw, size=12, tag=f"panel {i + 1}")
y += 2 * PH + GAP + 10

# ======================= 5. MAP + TIMELINE + DATE CHECK =======================
band_top = y
BH = 172
MAPW = 340
TLW = 330
DCW = W - 2 * M - MAPW - TLW - 2 * 14
mx0, tx0 = M, M + MAPW + 14
dx0 = tx0 + TLW + 14

# --- world map: coarse dot grid from rough continent polygons (lon, lat) ---
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-95, 72), (-80, 64), (-60, 55), (-66, 45), (-81, 31), (-80, 25),
     (-97, 26), (-97, 18), (-87, 21), (-83, 9), (-78, 8), (-105, 22), (-117, 32), (-125, 42),
     (-124, 49), (-140, 60), (-165, 60)],
    # Greenland
    [(-55, 60), (-42, 60), (-20, 70), (-22, 81), (-60, 82), (-70, 76)],
    # South America
    [(-78, 8), (-72, 12), (-60, 10), (-50, 0), (-35, -6), (-40, -22), (-58, -38), (-68, -55),
     (-75, -50), (-72, -30), (-80, -6)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (-5, 48), (2, 51), (8, 54), (5, 58), (12, 66), (25, 71),
     (40, 68), (45, 55), (40, 45), (28, 41), (20, 40), (12, 44), (10, 38), (0, 39)],
    # Britain
    [(-6, 50), (2, 51), (0, 55), (-3, 59), (-6, 57)],
    # Africa
    [(-17, 21), (-10, 32), (10, 37), (32, 31), (34, 28), (43, 12), (51, 12), (40, -4), (40, -16),
     (32, -28), (20, -35), (13, -18), (9, 0), (-8, 4), (-17, 14)],
    # Asia (incl. Middle East, India, SE Asia mainland)
    [(28, 41), (36, 36), (34, 28), (43, 12), (57, 22), (60, 25), (68, 24), (73, 16), (78, 8),
     (82, 16), (90, 22), (95, 16), (99, 7), (104, 1), (109, 12), (108, 21), (121, 30), (122, 40),
     (128, 35), (130, 43), (142, 47), (142, 60), (162, 62), (180, 66), (180, 70), (140, 73),
     (110, 77), (70, 73), (60, 68), (45, 68), (40, 45)],
    # Japan
    [(130, 31), (136, 34), (141, 36), (142, 43), (145, 44), (140, 41), (135, 36), (130, 34)],
    # Indonesia / Borneo (coarse)
    [(95, 5), (106, -6), (115, -8), (120, -9), (118, 0), (117, 7), (109, 2), (104, 0)],
    # New Guinea
    [(131, -1), (141, -3), (150, -6), (147, -10), (138, -8)],
    # Australia
    [(114, -22), (122, -18), (131, -12), (137, -12), (142, -11), (146, -19), (153, -26),
     (150, -37), (140, -38), (131, -31), (115, -34)],
]
LAT_TOP, LAT_BOT = 76, -42  # crop polar/southern ocean so the pinned band gets more height
map_title_h = 18
map_cap_h = 16
my0 = band_top + map_title_h
mh = BH - map_title_h - map_cap_h
d.text((mx0, band_top), "WHERE THE DAY HAPPENED", font=font(SCB, 13), fill=ACCENT)


def proj(lon, lat):
    px = mx0 + (lon + 170) / 360 * MAPW
    py = my0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * mh
    return px, py


def inside(pt, poly):
    x, yv = pt
    res = False
    n = len(poly)
    for k in range(n):
        x1, y1 = poly[k]
        x2, y2 = poly[(k + 1) % n]
        if (y1 > yv) != (y2 > yv):
            xi = x1 + (yv - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                res = not res
    return res


STEP = 5
for lat in range(LAT_TOP - 2, LAT_BOT, -STEP):
    for lon in range(-170, 190, STEP):
        ln = lon if lon <= 180 else lon - 360
        if any(inside((ln, lat), p) for p in CONTINENTS):
            px, py = proj(lon, lat)
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=LAND)

# (label, lon, lat): story number -> where it happened
PINS = [
    ("L", 100.3, 41.0),   # Jiuquan launch centre
    (2, 30.7, 46.5),      # Odesa
    (4, -74.0, 40.7),     # US court, New York
    (5, 121.5, 31.2, -4, 5),  # Shanghai (nudged off Seoul, leader line)
    (6, 160.0, -9.4),     # Honiara
    (7, 46.7, 24.7),      # Riyadh
    (8, -75.5, 10.4),     # Cartagena
    (14, 51.4, 35.7),     # Tehran
    (15, 34.4, 31.4),     # Gaza
    (17, 90.4, 23.8),     # Dhaka
    (21, 127.0, 37.5),    # Seoul
    (23, 139.7, 35.7),    # Tokyo
    (26, -0.1, 51.5),     # London
    (28, 12.6, 55.7),     # Copenhagen
    (29, -3.7, 40.4),     # Madrid
    (30, 25.0, -8.0),     # DR Congo
    (33, 105.8, 21.0),    # Hanoi
]
f_pin = font(SCB, 9)
R = 6
placed = []
for lab, lon, lat, *off in PINS:
    px, py = proj(lon, lat)
    if off:
        d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=INK)
        d.line([px, py, px + off[0], py + off[1]], fill=INK, width=1)
        px, py = px + off[0], py + off[1]
    for ql, qx, qy in placed:
        if (px - qx) ** 2 + (py - qy) ** 2 < (2 * R - 1) ** 2:
            warnings.append(f"map pins {ql} and {lab} overlap")
    placed.append((lab, px, py))
    fill = INK if lab == "L" else ACCENT
    d.ellipse([px - R, py - R, px + R, py + R], fill=fill, outline=PAPER, width=1)
    d.text((px, py), str(lab), font=f_pin, fill=WHITE, anchor="mm")
cap = "35 stories · 20+ countries  ·  L = lead, numbers = stories"
f_cap = font(SC, 12)
d.text((mx0, band_top + BH - map_cap_h + 2), cap, font=f_cap, fill=SOFT)
if tw(cap, f_cap) > MAPW:
    warnings.append("map caption too wide")

# --- timeline ---
d.rectangle([tx0, band_top, tx0 + TLW, band_top + BH], fill=PANEL)
d.text((tx0 + 10, band_top + 8), "THE DAY IN UTC — AS REPORTED", font=font(SCB, 13), fill=ACCENT)
TL = [
    ("Early", "Shenzhou-24 lifts off from Jiuquan"),
    ("Morning", "Huawei verdict lands in US court"),
    ("Midday", "Riyadh counts 11 hurt in tower hit"),
    ("Later", "Cartagena supermarket siege unfolds"),
    ("All day", "Odesa mourns strike dead"),
]
f_tt = font(CB, 16)
f_tl = font(SC, 14)
ty = band_top + 34
line_x = tx0 + 74
d.line([line_x, ty + 6, line_x, ty + 4 * 26 + 8], fill=RULE, width=2)
for t, s in TL:
    d.text((line_x - 10 - tw(t, f_tt), ty - 1), t, font=f_tt, fill=INK)
    d.ellipse([line_x - 4, ty + 6, line_x + 4, ty + 14], fill=ACCENT)
    d.text((line_x + 12, ty), s, font=f_tl, fill=INK)
    if line_x + 12 + tw(s, f_tl) > tx0 + TLW - 6:
        warnings.append(f"timeline row too wide: {s!r}")
    if line_x - 10 - tw(t, f_tt) < tx0 + 6:
        warnings.append(f"timeline label too wide: {t!r}")
    ty += 26
check_bottom(ty, band_top + BH, "timeline")

# --- date check ---
d.rectangle([dx0, band_top, dx0 + DCW, band_top + BH], outline=ACCENT, width=2)
d.text((dx0 + 10, band_top + 8), "DATE CHECK", font=font(SCB, 13), fill=ACCENT)
dc = ("Every story here happened or was first reported on Wednesday 25 Nov 2026 in some time "
      "zone. Left out as earlier days' news: the sinking of the Russian corvette Merkury off "
      "Benghazi (22\u00a0Nov), the Banten factory fire (24\u00a0Nov), and COP31's collapse in Antalya "
      "(24\u00a0Nov).")
yy = block(dx0 + 10, band_top + 30, dc, font(SC, 13), DCW - 20, 17, INK, tag="date check")
check_bottom(yy, band_top + BH - 4, "date check")
y = band_top + BH + 10

# ======================= 6. MORE OF THE DAY =======================
d.line([M, y, W - M, y], fill=INK, width=2)
d.text((M, y + 4), "MORE OF THE DAY", font=font(SCB, 14), fill=ACCENT)
y += 24
more = [
    (9, "US", "Soldier admits selling military secrets to China buyers"),
    (10, "US", "Trump awards Giuliani highest US civilian honour"),
    (11, "US", "Washington to unveil new tariffs on 16 countries"),
    (12, "US", "Consumer confidence jumps to 103.3"),
    (13, "US", "Pentagon in talks with GM, Ford on drone output"),
    (14, "IRAN", "Tehran rules out US talks until 7 conditions met"),
    (15, "GAZA", "Hamas security chief killed in Israeli strike"),
    (16, "ISRAEL", "Eisenkot clinches first coalition pact"),
    (17, "BANGLADESH", "Garment workers win 36% pay hike"),
    (18, "MYANMAR", "Landmine toll worst in world, monitor says"),
    (19, "UN", "Five women killed each hour by relatives in 2025"),
    (20, "TÜRKIYE", "Five killed as army helicopter crashes on training"),
    (21, "KOREA", "Seoul subway strike called off in wage deal"),
    (22, "KOREA", "Russian planes enter Seoul air defence zone"),
    (23, "JAPAN", "Rakuten Securities breach leaked client asset data"),
    (24, "JAPAN", "Labour federation to seek ¥17,000 pay-scale hike"),
    (25, "JAPAN", "NPB stars Sato and Taira agree MLB deals"),
    (26, "BRITAIN", "Met Police still institutionally racist — report"),
    (27, "BRITAIN", "Two held after break-in at Prince William's home"),
    (28, "DENMARK", "Top court upholds 'ghetto' evictions"),
    (29, "SPAIN", "Polls put People's Party first for Nov 29 snap vote"),
    (30, "CONGO", "Chinese cobalt firms race DR Congo export ban"),
    (31, "BUSINESS", "Shein to pay $100m in FTC settlement"),
    (32, "INDIA", "Two Indians hurt in Riyadh tower attack"),
    (33, "VIETNAM", "Hanoi hot-pot restaurant blast kills six"),
    (34, "HONG KONG", "Fire survivors return a year after 168 died"),
]
assert len(more) == 26 and 1 + len(featured) + len(more) == 35
COLS = 3
CGAP = 8
CW = (W - 2 * M - (COLS - 1) * CGAP) / COLS
per_col = (len(more) + COLS - 1) // COLS
LH = 19
f_mr = font(CBD, 10.5)
# ONE headline font for the whole list (largest candidate where every line fits),
# so the list reads as one system instead of a patchwork of sizes
HEAD_FONTS = [font(SCM, 14), font(CM, 14), font(CM, 13.5), font(CM, 13)]


def list_fits(f_mh):
    return all(tw(f"{n} · {reg} — ", f_mr) + tw(head, f_mh) <= CW for n, reg, head in more)


f_mh = next((f for f in HEAD_FONTS if list_fits(f)), HEAD_FONTS[-1])
print(f"more list font: {f_mh.path.split('/')[-1]} {f_mh.size}")
for i, (n, reg, head) in enumerate(more):
    c, r = i // per_col, i % per_col
    x = M + c * (CW + CGAP)
    yy = y + r * LH
    pre = f"{n} · {reg} — "
    d.text((x, yy + 3), pre, font=f_mr, fill=ACCENT)
    hx = x + tw(pre, f_mr)
    if hx + tw(head, f_mh) - x > CW:
        warnings.append(f"more {n}: overflows column by {hx + tw(head, f_mh) - x - CW:.0f}px")
    d.text((hx, yy), head, font=f_mh, fill=INK)
for c in range(1, COLS):
    lx = M + c * (CW + CGAP) - CGAP / 2
    d.line([lx, y, lx, y + per_col * LH - 2], fill=RULE, width=1)
y += per_col * LH + 6

# ======================= 7. FOOTER =======================
d.line([M, y, W - M, y], fill=INK, width=1)
foot = ("Sources: Reuters · The Japan Times · South China Morning Post · Telegraph India · "
        "Inshorts — Badges: CONFIRMED = several sources · OFFICIAL = primary source · "
        "REPORTED = single source, as attributed.")
yy = block(M, y + 4, foot, font(SC, 12), W - 2 * M, 15, SOFT, max_lines=2, tag="footer")
check_bottom(yy, H - 6, "page")

img.save("entry.png", optimize=True)
for w in warnings:
    print("WARNING:", w)
print(f"saved entry.png, date {f_date.size}px, bottom y={yy:.0f}, warnings={len(warnings)}")
