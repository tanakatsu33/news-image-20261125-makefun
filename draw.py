"""Draw an original, compact newspaper using Pillow and installed Noto fonts."""
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PAPER, INK, ACCENT, MUTED = '#f6f2e8', '#17252c', '#ab342b', '#677175'
page = Image.new('RGB', (1024, 1024), PAPER)
pen = ImageDraw.Draw(page)
WARNINGS = []
FONT_HOME = Path('/usr/share/fonts/truetype/noto')

@lru_cache(None)
def font(size, bold=False):
    name = 'NotoSans-ExtraCondensedBold.ttf' if bold else 'NotoSans-ExtraCondensed.ttf'
    return ImageFont.truetype(str(FONT_HOME / name), size)

@lru_cache(None)
def missing(character, size, bold):
    face = font(size, bold)
    mask = face.getmask(character)
    absent = face.getmask('\U0010ffff')
    return mask.size == absent.size and bytes(mask) == bytes(absent)

def warning(message):
    WARNINGS.append(message)
    print('WARNING:', message)

def words_into_lines(value, width, size, bold=False):
    lines, current = [], ''
    for word in value.split():
        candidate = (current + ' ' + word).strip()
        if current and pen.textlength(candidate, font=font(size, bold)) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines

def text(value, x, y, width, size=14, bold=False, color=INK):
    for char in set(value):
        if not char.isspace() and missing(char, size, bold):
            warning(f'Missing glyph {char!r} in {value!r}')
    face = font(size, bold)
    bounds = face.getbbox(value)
    natural = max(1, int(pen.textlength(value, font=face) + 2))
    # A single newspaper line may be optically condensed; no words are removed.
    tile = Image.new('RGBA', (natural, size + 7))
    ImageDraw.Draw(tile).text((0, -bounds[1]), value, font=face, fill=color)
    if natural > width:
        tile = tile.resize((int(width), size + 7), Image.Resampling.LANCZOS)
    if x < 0 or y < 0 or x + tile.width > 1024 or y + tile.height > 1024:
        warning(f'Canvas overflow: {value}')
    page.paste(tile, (int(x), int(y)), tile)

def paragraph(value, x, y, width, size, height, bold=False, leading=None):
    step = leading or size + 2
    lines = words_into_lines(value, width, size, bold)
    if len(lines) * step > height:
        warning(f'Text box overflow ({len(lines) * step}>{height}): {value}')
    for index, line in enumerate(lines):
        text(line, x, y + index * step, width, size, bold)
    return len(lines) * step

def rule(y, x=24, right=1000, color=INK, weight=1):
    pen.line((x, y, right, y), fill=color, width=weight)

def badge(label, x, y, width=81):
    fill = ACCENT if label == 'CONFIRMED' else '#deded8' if label == 'REPORTED' else PAPER
    pen.rounded_rectangle((x, y, x + width, y + 17), radius=2, fill=fill,
                          outline=ACCENT if label == 'OFFICIAL' else fill)
    text(label, x + 5, y + 2, width - 10, 12, True,
         'white' if label == 'CONFIRMED' else INK)

# Masthead and full-width lead.
text('THE WORLD IN ONE PICTURE', 24, 12, 976, 28, True)
text('WEDNESDAY 25 NOVEMBER 2026', 24, 43, 976, 56, True)
text('35 STORIES · EVERY STORY SOURCED AND BADGED', 25, 100, 975, 14, True, ACCENT)
rule(120, weight=3)
text('LEAD · SPACE — JIUQUAN, CHINA', 24, 130, 976, 14, True, ACCENT)
text('SHENZHOU-24 FLIES FIRST PAKISTANI INTO SPACE', 24, 151, 976, 38, True)
paragraph("China's Shenzhou-24 crew ship lifts off from Jiuquan for the Tiangong station with Zeeshan Ali aboard — the first Pakistani national in space.",
          24, 198, 976, 17, 40)
text('Japan Times / Reuters —', 24, 231, 165, 13)
badge('CONFIRMED', 198, 228)
rule(257)
text('THE DAY IN NUMBERS', 24, 264, 976, 14, True, ACCENT)
numbers = [
    '25 hostages in Cartagena supermarket siege',
    '7,000 landmine casualties in 2025, a 5-year high',
    '36% pay rise ends Bangladesh garment strike',
    '$100m Shein settlement with the FTC',
    '103.3 US consumer confidence in November',
    '5 killed in Turkish helicopter crash',
]
for i, item in enumerate(numbers):
    text(item, 24 + (i % 3) * 329, 285 + (i // 3) * 19, 315, 14, True)
rule(326, weight=2)

features = [
    ('UKRAINE WAR', 'US shelves business-deal plan to end war', 'Washington quietly drops energy and aviation offers after the Kremlin shows little interest, FT reports', 'Reuters', 'REPORTED'),
    ('UKRAINE WAR', 'Russian strike kills two in Odesa region', 'Cars and homes hit near the Black Sea port; drones also set a Kyiv tower block ablaze', 'Reuters', 'OFFICIAL'),
    ('CYBER', 'CIA unclassified system breached', 'Hackers hit an unclassified CIA system; officials say no classified data was compromised', 'Telegraph India', 'REPORTED'),
    ('TECH TRIAL', 'Huawei convicted in US Iran-business trial', 'A US jury convicts the Chinese tech giant in a sprawling criminal case over trade secrets and Iran deals', 'Japan Times', 'CONFIRMED'),
    ('CHINA', 'Xi probes Shanghai party chief Chen Jining', 'The Politburo member falls under investigation in the biggest party shakeup in decades', 'Japan Times', 'CONFIRMED'),
    ('PACIFIC', 'Australia–Solomons pact shuts out China', "Canberra becomes Honiara's top security partner in a sweeping deal signed in Honiara", 'Reuters', 'CONFIRMED'),
    ('MIDDLE EAST', 'Riyadh tower hit again; 11 injured', 'Saudi Arabia strikes Houthi-run Hodeidah port as the Red Sea war flares again', 'SCMP / Inshorts', 'CONFIRMED'),
    ('COLOMBIA', 'Gunmen hold 25 hostage in supermarket', 'Troops surround a Cartagena store after a failed armoured-car raid; a bomb attack wounds 23 elsewhere', 'SCMP', 'REPORTED'),
]
pen.line((510, 335, 510, 648), fill='#d6d2c8', width=1)
for i, (region, headline, summary, source, status) in enumerate(features):
    x, y = 24 + (i % 2) * 496, 335 + (i // 2) * 79
    text(f'{i + 1} · {region}', x, y, 476, 12, True, ACCENT)
    text(headline, x, y + 16, 476, 19, True)
    text(summary, x, y + 39, 476, 14)
    text(source + ' —', x, y + 60, 168, 12)
    badge(status, x + 170, y + 56)
    rule(y + 76, x, x + 476, '#c3c1b8')

# Geographic context: stylized continent polygons in longitude/latitude space.
band_y = 658
text('WHERE THE DAY HAPPENED', 24, band_y, 310, 15, True)
def geo(lon, lat):
    return (29 + (lon + 180) / 360 * 298, 687 + (80 - lat) / 150 * 84)
continents = [
    [(-168,70),(-125,73),(-55,48),(-83,10),(-106,24),(-125,48)],
    [(-80,10),(-40,-7),(-52,-35),(-70,-55),(-77,-15)],
    [(-17,35),(13,37),(49,10),(33,-35),(15,-34),(-12,5)],
    [(-10,36),(-10,60),(30,72),(100,75),(170,58),(140,35),(110,0),(70,8),(40,35)],
    [(113,-12),(153,-10),(155,-38),(118,-35)],
    [(-53,60),(-25,73),(-42,82),(-60,76)],
]
for polygon in continents:
    pen.polygon([geo(*point) for point in polygon], fill='#c7cfc7')
# Offset labels keep nearby European and Asian locations distinct.
# Pin 35 denotes the unnumbered lead; 1–34 match the story list.
pins = [(35,100,41,6,-19), (1,30,49,5,-16),
        (7,47,24,8,8), (8,-75,10,0,9),
        (9,-100,40,-8,-9), (17,90,24,-8,15),
        (20,35,39,-4,3), (23,139,36,10,-7),
        (26,-2,54,-10,-12), (29,-4,40,-13,5),
        (30,23,-4,0,14), (6,160,-9,6,10)]
for number, lon, lat, dx, dy in pins:
    px, py = geo(lon, lat)
    lx, ly = px + dx, py + dy
    pen.ellipse((px-2, py-2, px+2, py+2), fill=ACCENT)
    pen.line((px, py, lx, ly), fill=ACCENT, width=1)
    pen.rounded_rectangle((lx-6, ly-5, lx+6, ly+6), radius=2, fill=ACCENT)
    text(str(number), lx-5, ly-4, 11, 9, True, 'white')
text('35 stories · 20+ countries', 24, 782, 310, 12, True)
text('THE DAY IN UTC — AS REPORTED', 354, band_y, 318, 15, True)
for i, event in enumerate([
    'Early — Shenzhou-24 lifts off from Jiuquan',
    'Morning — Huawei verdict lands in US court',
    'Midday — Riyadh counts 11 hurt in tower hit',
    'Later — Cartagena supermarket siege unfolds',
    'All day — Odesa mourns strike dead',
]):
    text(event, 354, 686 + 20*i, 318, 14)
pen.rectangle((694, 654, 1000, 798), outline=ACCENT)
text('DATE CHECK', 704, 663, 286, 15, True, ACCENT)
paragraph("Every story here happened or was first reported on Wednesday 25 Nov 2026 in some time zone. Left out as earlier days' news: the sinking of the Russian corvette Merkury off Benghazi (22 Nov), the Banten factory fire (24 Nov), and COP31's collapse in Antalya (24 Nov).",
          704, 690, 286, 14, 101, leading=16)
rule(806, weight=2)
text('MORE OF THE DAY', 24, 813, 976, 16, True, ACCENT)
more = [
    ('US', 'Soldier admits selling military secrets to China buyers'),
    ('US', 'Trump awards Giuliani highest US civilian honour'),
    ('US', 'Washington to unveil new tariffs on 16 countries'),
    ('US', 'Consumer confidence jumps to 103.3'),
    ('US', 'Pentagon in talks with GM, Ford on drone output'),
    ('IRAN', 'Tehran rules out US talks until 7 conditions met'),
    ('GAZA', 'Hamas security chief killed in Israeli strike'),
    ('ISRAEL', 'Eisenkot clinches first coalition pact'),
    ('BANGLADESH', 'Garment workers win 36% pay hike'),
    ('MYANMAR', 'Landmine toll worst in world, monitor says'),
    ('UN', 'Five women killed each hour by relatives in 2025'),
    ('TÜRKIYE', 'Five killed as army helicopter crashes on training'),
    ('KOREA', 'Seoul subway strike called off in wage deal'),
    ('KOREA', 'Russian planes enter Seoul air defence zone'),
    ('JAPAN', 'Rakuten Securities breach leaked client asset data'),
    ('JAPAN', 'Labour federation to seek ¥17,000 pay-scale hike'),
    ('JAPAN', 'NPB stars Sato and Taira agree MLB deals'),
    ('BRITAIN', 'Met Police still institutionally racist — report'),
    ('BRITAIN', "Two held after break-in at Prince William's home"),
    ('DENMARK', "Top court upholds 'ghetto' evictions"),
    ('SPAIN', "Polls put People's Party first for Nov 29 snap vote"),
    ('CONGO', 'Chinese cobalt firms race DR Congo export ban'),
    ('BUSINESS', 'Shein to pay $100m in FTC settlement'),
    ('INDIA', 'Two Indians hurt in Riyadh tower attack'),
    ('VIETNAM', 'Hanoi hot-pot restaurant blast kills six'),
    ('HONG KONG', 'Fire survivors return a year after 168 died'),
]
for i, (region, headline) in enumerate(more):
    column, row = divmod(i, 9)
    text(f'{i+9} · {region} — {headline}', 24 + column*329, 837 + row*16, 315, 14)
rule(985)
paragraph('Sources: Reuters · The Japan Times · South China Morning Post · Telegraph India · Inshorts — Badges: CONFIRMED = several sources · OFFICIAL = primary source · REPORTED = single source, as attributed.',
          24, 992, 976, 11, 28, leading=13)
output = ROOT / 'entry.png'
page.save(output, optimize=True)
size = output.stat().st_size
if size > 1024 * 1024:
    warning(f'PNG exceeds 1 MiB: {size} bytes')
print(f'entry.png: {page.width}x{page.height}, {size} bytes; {len(WARNINGS)} warnings')
if WARNINGS:
    raise SystemExit(1)
