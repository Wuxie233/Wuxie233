"""Generate the profile's illustrated SVGs.

Run from the repository root:
    uv run --with fonttools python scripts/art/build.py

Text is converted to outlines so every viewer sees the same type; the
rolling-year stats card reads the Chinese labels from scripts/art/glyphs.json.
"""

import json
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTCollection, TTFont

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
ART = ROOT / "scripts" / "art"

NIGHT = "#0E0D16"
LINE = "#26233A"
TEXT = "#EEEAF6"
DIM = "#A29DB8"
ORANGE = "#F0883E"
GREEN = "#3FB68B"
VIOLET = "#8B6CFF"

CUBE = {
    "impulse": ("#F7A15A", "#D9772B", "#AE5B1B"),
    "chain": ("#5BD3A6", "#3FB68B", "#2A8A67"),
    "repeat": ("#A891FF", "#8B6CFF", "#6A4EDB"),
    "stone": ("#4A4760", "#38354C", "#2A2839"),
    "wall": ("#E4DFEF", "#C3BDD3", "#9C96AE"),
    "roof": ("#F7A15A", "#D9772B", "#AE5B1B"),
}

SERIF_BOLD = ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", 2)
SERIF = ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", 2)
MONO = ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", None)


def num(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Outline:
    def __init__(self, spec):
        path, index = spec
        self.font = TTCollection(path).fonts[index] if index is not None else TTFont(path)
        self.upem = self.font["head"].unitsPerEm
        self.cmap = self.font.getBestCmap()
        self.glyphs = self.font.getGlyphSet()
        self.hmtx = self.font["hmtx"]

    def glyph(self, ch, size, x, y):
        name = self.cmap[ord(ch)]
        s = size / self.upem
        pen = SVGPathPen(self.glyphs, ntos=num)
        self.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        return pen.getCommands(), self.hmtx[name][0] * s

    def width(self, text, size):
        return sum(self.hmtx[self.cmap[ord(c)]][0] for c in text) * size / self.upem

    def run(self, text, size, x, y, fill, cls="", start=0):
        """One <path> per character so characters can animate individually."""
        out = []
        for i, ch in enumerate(text):
            d, adv = self.glyph(ch, size, x, y)
            if d:
                style = f' style="--i:{start + i}"' if cls else ""
                klass = f' class="{cls}"' if cls else ""
                out.append(f'<path{klass}{style} fill="{fill}" d="{d}"/>')
            x += adv
        return "".join(out), x

    def spans(self, spans, size, x, y, cls="", start=0):
        out, i = [], start
        for text, fill in spans:
            svg, x = self.run(text, size, x, y, fill, cls, i)
            out.append(svg)
            i += len(text)
        return "".join(out), x, i


serif_bold = Outline(SERIF_BOLD)
serif = Outline(SERIF)
mono = Outline(MONO)
pixel_font = json.loads((ART / "pixel-font.json").read_text())["glyphs"]


def pixel_text(text, x, y, p, gap, fill, cls=""):
    """Pixel letters built from square blocks; --c is the column for sweeps."""
    cell = p + gap
    out, col = [], 0
    for ch in text:
        rows = pixel_font[ch]
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    klass = f' class="{cls}" style="--c:{col + c}"' if cls else ""
                    out.append(f'<rect{klass} x="{num(x + (col + c) * cell)}" y="{num(y + r * cell)}" width="{p}" height="{p}" fill="{fill}"/>')
        col += len(rows[0]) + 1
    return "".join(out), (col - 1) * cell


def iso(ox, oy, s):
    def project(x, y, z):
        return ox + (x - y) * s * 0.866, oy + (x + y) * s * 0.5 - z * s
    return project


def poly(points, fill, extra=""):
    pts = " ".join(f"{num(px)},{num(py)}" for px, py in points)
    return f'<polygon{extra} points="{pts}" fill="{fill}"/>'


def inset(points, t):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    return [(px + (cx - px) * t, py + (cy - py) * t) for px, py in points]


def cube(project, x, y, z, kind, cls="", style="", glow=False, screen=True):
    top_c, left_c, right_c = CUBE[kind]
    top = [project(x, y, z + 1), project(x + 1, y, z + 1), project(x + 1, y + 1, z + 1), project(x, y + 1, z + 1)]
    left = [project(x, y + 1, z), project(x + 1, y + 1, z), project(x + 1, y + 1, z + 1), project(x, y + 1, z + 1)]
    right = [project(x + 1, y, z), project(x + 1, y + 1, z), project(x + 1, y + 1, z + 1), project(x + 1, y, z + 1)]
    parts = [poly(top, top_c), poly(left, left_c), poly(right, right_c)]
    if screen:
        parts.append(poly(inset(left, 0.42), right_c))
        parts.append(poly(inset(right, 0.42), "#00000033"))
    if glow:
        parts.append(poly(top, "#FFFFFF", ' class="glow"'))
    klass = f' class="{cls}"' if cls else ""
    st = f' style="{style}"' if style else ""
    return f"<g{klass}{st}>{''.join(parts)}</g>"


def svg(w, h, title, desc, style, body, rx=20):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{title}</title>
<desc id="desc">{desc}</desc>
<style>
{style.strip()}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<rect width="{w}" height="{h}" rx="{rx}" fill="{NIGHT}"/>
{body}
</svg>
"""


def stars(rng, count, x0, y0, x1, y1):
    out = []
    for i in range(count):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.choice([1, 1.2, 1.6])
        o = rng.choice([0.25, 0.4, 0.6])
        twinkle = ' class="tw"' if i % 3 == 0 else ""
        out.append(f'<circle{twinkle} style="--d:{num(rng.uniform(0, 4))}s" cx="{num(x)}" cy="{num(y)}" r="{r}" fill="{TEXT}" opacity="{o}"/>')
    return "".join(out)


HERO_STYLE = f"""
.px {{ animation: sweep 7s calc(var(--c) * 0.035s) infinite; }}
@keyframes sweep {{ 0%, 9%, 100% {{ fill: {TEXT}; }} 4% {{ fill: {ORANGE}; }} }}
.ch {{ animation: type 0.01s calc(0.6s + var(--i) * 0.07s) backwards; }}
@keyframes type {{ from {{ opacity: 0; }} }}
.caret {{ animation: blink 1.1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.glow {{ opacity: 0; animation: pulse 4.8s calc(1.2s + var(--i) * 0.22s) infinite; }}
@keyframes pulse {{ 0% {{ opacity: 0; }} 5% {{ opacity: .55; }} 16%, 100% {{ opacity: 0; }} }}
.pt {{ opacity: 0; animation: rise 3.6s calc(var(--i) * 0.45s) infinite cubic-bezier(.16,1,.3,1); }}
@keyframes rise {{ 0% {{ opacity: 0; transform: translate(0, 0); }} 20% {{ opacity: .9; }} 100% {{ opacity: 0; transform: translate(var(--dx), -130px); }} }}
.tw {{ animation: twinkle 4s var(--d) infinite; }}
@keyframes twinkle {{ 50% {{ opacity: .9; }} }}
"""

# A staircase of command blocks: impulse at the foot, repeating at the top.
CHAIN = [(0, 0, "impulse"), (-1, 0, "chain"), (-1, 1, "chain"), (-2, 1, "chain"), (-2, 2, "chain"), (-3, 2, "chain"), (-3, 3, "chain"), (-4, 3, "repeat")]


def chain_art(ox, oy, s, rng):
    project = iso(ox, oy, s)
    # Signal order follows the chain, not the paint order.
    # Steps climb away from the viewer (-y) and upward; paint far cubes first.
    order = {(y, z): i for i, (y, z, _) in enumerate(CHAIN)}
    cubes = "".join(
        cube(project, 0, y, z, kind, style=f"--i:{order[(y, z)]}", glow=True)
        for y, z, kind in sorted(CHAIN, key=lambda c: (c[0], c[1]))
    )
    tx, ty = project(0.5, -3.5, 4)
    particles = "".join(
        f'<rect class="pt" style="--i:{i};--dx:{rng.randint(-50, 50)}px" x="{num(tx - 3 + rng.uniform(-10, 10))}" y="{num(ty - 6)}" width="{rng.choice([4, 5, 6])}" height="{rng.choice([4, 5, 6])}" fill="{rng.choice([VIOLET, TEXT, VIOLET])}"/>'
        for i in range(8)
    )
    return cubes + particles


LINE_1 = "人应该诗一般栖居在大地上，"
LINE_2 = "而不是变成灰色的铁鸟。"


def hero():
    rng = random.Random(7)
    n = len(LINE_1 + LINE_2)
    desc = "Pixel lettering WUXIE above the line: 人应该诗一般栖居在大地上，而不是变成灰色的铁鸟。A staircase of command blocks passes a signal upward and releases light toward the stars."
    word, _ = pixel_text("WUXIE", 72, 70, 13, 2, TEXT, "px")
    l1, _ = serif_bold.run(LINE_1, 38, 72, 248, TEXT, "ch")
    l2, end = serif_bold.run(LINE_2, 38, 72, 304, TEXT, "ch", start=len(LINE_1))
    caret = f'<rect class="caret" x="{num(end + 8)}" y="270" width="16" height="38" fill="{ORANGE}" style="animation-delay:{num(0.6 + n * 0.07)}s"/>'
    body = (
        stars(rng, 34, 820, 24, 1250, 200)
        + word + l1 + l2 + caret
        + f'<path d="M72 352H560" stroke="{LINE}" stroke-width="2"/>'
        + chain_art(990, 325, 40, rng)
    )
    (ASSETS / "hero.svg").write_text(svg(1280, 400, "Wuxie", desc, HERO_STYLE, body))

    rng = random.Random(7)
    word, _ = pixel_text("WUXIE", 48, 64, 14, 2, TEXT, "px")
    l1, _ = serif_bold.run(LINE_1, 42, 48, 262, TEXT, "ch")
    l2, end = serif_bold.run(LINE_2, 42, 48, 320, TEXT, "ch", start=len(LINE_1))
    caret = f'<rect class="caret" x="{num(end + 8)}" y="282" width="18" height="42" fill="{ORANGE}" style="animation-delay:{num(0.6 + n * 0.07)}s"/>'
    body = (
        stars(rng, 30, 360, 470, 690, 620)
        + word + l1 + l2 + caret
        + chain_art(265, 800, 56, rng)
    )
    (ASSETS / "hero-mobile.svg").write_text(svg(720, 880, "Wuxie", desc, HERO_STYLE, body))


MC_STYLE = f"""
.on {{ opacity: 0; animation: run 7s var(--d) infinite; }}
@keyframes run {{ 0% {{ opacity: 0; }} 3%, 16% {{ opacity: 1; }} 26%, 100% {{ opacity: 0; }} }}
"""


def works_minecraft():
    rng = random.Random(116)
    cells, cols = [], 29
    for i in range(116):
        cx, cy = 628 + (i % cols) * 20, 48 + (i // cols) * 80
        length = rng.randint(2, 7)
        active = rng.random() < 0.24
        start = rng.uniform(0, 6.4)
        cells.append(f'<rect x="{cx}" y="{cy}" width="12" height="12" fill="#4A3424"/>')
        if active:
            cells.append(f'<rect class="on" style="--d:{num(start)}s" x="{cx}" y="{cy}" width="12" height="12" fill="{ORANGE}"/>')
        for k in range(length):
            by = cy + 16 + k * 9
            cells.append(f'<rect x="{cx + 2}" y="{by}" width="8" height="7" fill="#1F3A31"/>')
            if active:
                cells.append(f'<rect class="on" style="--d:{num(start + 0.08 * (k + 1))}s" x="{cx + 2}" y="{by}" width="8" height="7" fill="{GREEN}"/>')
    l1, _, _ = serif_bold.spans([("7295", ORANGE), (" 个命令方块，", TEXT)], 36, 64, 152)
    l2, _ = serif_bold.run("没人触发时，", 36, 64, 204, TEXT)
    l3, _ = serif_bold.run("每 tick 只醒来三百来个。", 36, 64, 256, TEXT)
    note, _ = serif.run("最新一代空岛一条龙 · 116 条命令链", 22, 64, 322, DIM)
    desc = "116 command chains drawn as small columns; only a few light up at a time. 7295 command blocks, and with nobody triggering a feature only about three hundred run each tick."
    (ASSETS / "work-commands.svg").write_text(svg(1280, 400, "Minecraft command systems", desc, MC_STYLE, "".join(cells) + l1 + l2 + l3 + note))


NEO_STYLE = f"""
.ev {{ animation: ev 3.2s var(--d) infinite linear; opacity: 0; }}
@keyframes ev {{ 0% {{ opacity: 0; transform: translate(0, 0); }} 8%, 92% {{ opacity: 1; }} 100% {{ opacity: 0; transform: translate(var(--tx), var(--ty)); }} }}
.live {{ animation: live 2s infinite; }}
@keyframes live {{ 50% {{ opacity: .25; }} }}
"""


def works_neomega():
    parts = []
    srv = iso(610, 214, 30)
    server = [(x, y, z) for z in range(2) for x in range(2) for y in range(2)]
    for x, y, z in sorted(server, key=lambda c: (c[0] + c[1], c[2])):
        parts.append(cube(srv, x, y, z, "stone", screen=False))
    host = iso(874, 196, 54)
    parts.append(cube(host, 0, 0, 0, "chain"))
    plug_y = [112, 210, 308]
    for py in plug_y:
        parts.append(cube(iso(1112, py - 20, 30), 0, 0, 0, "repeat"))
    lines = [f'<path d="M660 210H860" stroke="{LINE}" stroke-width="2"/>']
    for py in plug_y:
        lines.append(f'<path d="M940 210L1100 {py}" stroke="{LINE}" stroke-width="2"/>')
    packets = []
    for i in range(3):
        packets.append(f'<rect class="ev" style="--d:{i * 1.05}s;--tx:190px;--ty:0px" x="664" y="200" width="8" height="8" fill="{GREEN}"/>')
    for i, py in enumerate(plug_y):
        packets.append(f'<rect class="ev" style="--d:{0.5 + i * 0.9}s;--tx:150px;--ty:{py - 210}px" x="944" y="200" width="8" height="8" fill="{GREEN}"/>')
        packets.append(f'<rect class="ev" style="--d:{1.6 + i * 0.9}s;--tx:-150px;--ty:{210 - py}px" x="1096" y="{py - 10}" width="8" height="8" fill="{ORANGE}"/>')
    labels = []
    for text, x, size in [("网易租赁服", 556, 22), ("Host", 878, 22), ("插件", 1170, 22)]:
        t, _ = serif.run(text, size, x, 370 if text != "插件" else 218, DIM)
        labels.append(t)
    tag, _ = serif.run("正在做", 22, 88, 104, GREEN)
    l1, _ = serif_bold.run("连接、协议、崩溃恢复", 36, 64, 186, TEXT)
    l2, _ = serif_bold.run("交给框架；", 36, 64, 238, TEXT)
    l3, _ = serif_bold.run("你只写玩法。", 36, 64, 290, TEXT)
    body = (
        f'<rect class="live" x="64" y="88" width="14" height="14" fill="{GREEN}"/>' + tag
        + l1 + l2 + l3 + "".join(lines) + "".join(parts) + "".join(packets) + "".join(labels)
    )
    desc = "Neomega: a NetEase rental server on the left, the Host in the middle, Python plugins on the right; events flow to plugins and actions flow back. Connection, protocol and crash recovery go to the framework; you only write gameplay."
    (ASSETS / "work-neomega.svg").write_text(svg(1280, 400, "Neomega", desc, NEO_STYLE, body))


BDX_STYLE = f"""
.cmd {{ animation: cmd 6s var(--d) infinite; }}
@keyframes cmd {{ 0%, 14%, 100% {{ fill: {DIM}; }} 3%, 8% {{ fill: {ORANGE}; }} }}
.flow {{ animation: flow 1.2s linear infinite; }}
@keyframes flow {{ to {{ stroke-dashoffset: -32; }} }}
.blk {{ animation: drop 6s var(--d) infinite cubic-bezier(.16,1,.3,1); }}
@keyframes drop {{ 0% {{ opacity: 0; transform: translateY(-18px); }} 6%, 86% {{ opacity: 1; transform: none; }} 96%, 100% {{ opacity: 0; }} }}
"""

COMMANDS = [
    "scoreboard players add @a online 1",
    "testfor @a[scores={gate=1}]",
    "tp @a[tag=home] 0 120 0",
    "execute @a[tag=menu] ~ ~ ~ function ui",
    "setblock ~ ~1 ~ chain_command_block",
]


def works_bdx():
    title, _ = serif_bold.run("几千个命令方块，不再手搬。", 36, 64, 96, TEXT)
    label_l, _ = mono.run(".mcfunction", 18, 64, 152, ORANGE)
    lines = []
    for i, cmd in enumerate(COMMANDS):
        t, _ = mono.run(cmd, 19, 64, 196 + i * 38, DIM)
        lines.append(f'<g class="cmd" style="--d:{num(i * 0.55)}s">{t}</g>')
    arrow = f'<path class="flow" d="M560 236H800" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="3 13" stroke-linecap="round"/>'
    label_r, _ = mono.run(".bdx", 18, 932, 356, ORANGE)
    project = iso(950, 190, 38)
    blocks = []
    cells = [(x, y, 0) for x in range(3) for y in range(3)] + [(x, y, 1) for x in range(2) for y in range(2)] + [(0, 0, 2)]
    for k, (x, y, z) in enumerate(sorted(cells, key=lambda c: (c[2], c[0] + c[1]))):
        kind = "impulse" if (x, y, z) == (0, 0, 0) else ("repeat" if z == 2 else "chain")
        delay = 0.4 + k * 0.2
        blocks.append(cube(project, x, y, z, kind, cls="blk", style=f"--d:{num(delay)}s"))
    desc = "Bedrock commands on the left light up one by one and become command blocks stacked on the right: thousands of command blocks, no more moving them by hand."
    (ASSETS / "work-bdx.svg").write_text(svg(1280, 400, "BDXSuperTool", desc, BDX_STYLE, title + label_l + "".join(lines) + arrow + label_r + "".join(blocks)))


FLY_STYLE = f"""
.bld {{ animation: build 0.7s var(--d) cubic-bezier(.16,1,.3,1) backwards; }}
@keyframes build {{ from {{ opacity: 0; transform: translateY(-16px); }} }}
.win {{ animation: dusk 9s 3s infinite; }}
@keyframes dusk {{ 0%, 40% {{ opacity: 1; }} 55%, 85% {{ opacity: .15; }} 100% {{ opacity: 1; }} }}
"""


def works_flybuild():
    project = iso(985, 205, 30)
    blocks = []
    cells = []
    for x in range(5):
        for y in range(4):
            cells.append((x, y, 0, "stone"))
    for z in (1, 2):
        for x in range(5):
            for y in range(4):
                if x in (0, 4) or y in (0, 3):
                    cells.append((x, y, z, "wall"))
    for x in range(5):
        for y in range(4):
            cells.append((x, y, 3, "roof"))
    for x in range(1, 4):
        for y in range(1, 3):
            cells.append((x, y, 4, "roof"))
    cells.sort(key=lambda c: (c[2], c[0] + c[1]))
    for k, (x, y, z, kind) in enumerate(cells):
        blocks.append(cube(project, x, y, z, kind, cls="bld", style=f"--d:{num(0.2 + k * 0.035)}s", screen=False))
    windows = []
    for x in (1, 3):
        a, b, c, d = project(x, 4, 1.25), project(x + 1, 4, 1.25), project(x + 1, 4, 2.1), project(x, 4, 2.1)
        windows.append(poly(inset([a, b, c, d], 0.22), ORANGE, ' class="win"'))
    for y in (1,):
        a, b, c, d = project(5, y, 1.25), project(5, y + 2, 1.25), project(5, y + 2, 2.1), project(5, y, 2.1)
        windows.append(poly(inset([a, b, c, d], 0.2), ORANGE, ' class="win"'))
    title, _ = serif_bold.run("六种建筑格式，一个工作台。", 36, 64, 110, TEXT)
    tags = []
    x, y = 64, 180
    for i, fmt in enumerate([".bdx", ".mcstructure", ".schem", ".schematic", ".litematic", ".mcworld"]):
        w = mono.width(fmt, 22) + 28
        if x + w > 700:
            x, y = 64, y + 52
        t, _ = mono.run(fmt, 22, x + 14, y + 26, TEXT)
        tags.append(f'<rect x="{num(x)}" y="{y}" width="{num(w)}" height="38" rx="6" fill="none" stroke="{LINE}" stroke-width="2"/>{t}')
        x += w + 12
    end, _ = serif.run("社群曾有 500 多人，现已结束运营。", 22, 64, 336, DIM)
    desc = "An isometric house assembles block by block; its windows glow and dim. Six build formats, one workbench: .bdx, .mcstructure, .schem, .schematic, .litematic, .mcworld. The community once had more than 500 members; FlyBuild has ended operation."
    (ASSETS / "work-flybuild.svg").write_text(svg(1280, 400, "FlyBuild", desc, FLY_STYLE, title + "".join(tags) + end + "".join(blocks) + "".join(windows)))


def stats_glyphs():
    """Unit-size outlines (1em = 1) for the Node stats generator."""
    out = {}
    for key, font in [("次贡献", serif_bold), ("最近一年", serif), ("次提交", serif), ("个仓库", serif), ("·", serif)]:
        out[key] = {"svg": font.run(key, 100, 0, 0, "currentColor")[0], "advance": font.width(key, 100) / 100}
    (ART / "glyphs.json").write_text(json.dumps(out, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    hero()
    works_minecraft()
    works_neomega()
    works_bdx()
    works_flybuild()
    stats_glyphs()
    print("built:", ", ".join(sorted(p.name for p in ASSETS.glob("*.svg"))))
