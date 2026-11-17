"""Builds The Profit & Cash Flow Cycle model as standalone SVGs.

Run:  python3 build.py   (writes cycle-16x9.svg, cycle-square.svg and cycle-embed.svg next to this file)
Then export PNG/PDF with export.sh.

The three circles sit on one big ring. The arrows run along that ring, clockwise,
so together they read as one continuous circular motion around the model.
"""
import base64, math, pathlib

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[1]
BRAND = ROOT / "my-skills/pdf-forge/brands/the-profit-analyst"

NAVY, BLUE, GREEN = "#002B4E", "#02A3FF", "#12C870"
INK = "#002B4E"
MUTED = "#4A6378"

# Order matters: clockwise from the top
CIRCLES = [
    dict(key="pl", angle=-90, head="PROFITABILITY", sub="(P&amp;L)", ring=NAVY, fill="#EDF2F7",
         q1=["What is our", "current profit?"],
         q2=["What is our target", "profit formula?"]),
    dict(key="bs", angle=30, head="CAPITAL", sub="(Balance Sheet)", ring=BLUE, fill="#E8F6FF",
         q1=["What is our", "financial position?"],
         q2=["Where did our", "profit go?"]),
    dict(key="cf", angle=150, head="CASH FLOW", sub=None, ring=GREEN, fill="#E7F9F0",
         q1=["When is our next", "cash low point,", "and are we safe?"],
         q2=["What cash is", "available to", "fund growth?"]),
]
# Arrow i runs from circle i to circle i+1, in the colour of the circle it leaves
ARROW_LABELS = [
    ["Where did our", "profit go?"],
    ["How do we turn more", "profit into cash?"],
    ["How much cash can we", "invest to grow profit?"],
]
CENTRE = ["Make profit.", "Turn it into cash.", "Fund future growth."]


def font_face():
    out = []
    for fam, file, w, style in [("Poppins", "Poppins-SemiBold.ttf", 600, "normal"),
                                ("Poppins", "Poppins-Bold.ttf", 700, "normal"),
                                ("Lato", "Lato-Regular.ttf", 400, "normal"),
                                ("Lato", "Lato-Bold.ttf", 700, "normal"),
                                ("Lato", "Lato-Italic.ttf", 400, "italic")]:
        b64 = base64.b64encode((BRAND / "fonts" / file).read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{style};"
                   f"src:url(data:font/ttf;base64,{b64}) format('truetype');}}")
    return "".join(out)


def logo_href():
    return "data:image/svg+xml;base64," + base64.b64encode((BRAND / "logo.svg").read_bytes()).decode()


def text_block(x, y, lines, size, lh, cls, anchor="middle"):
    s = f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" font-size="{size}">'
    for i, ln in enumerate(lines):
        s += f'<tspan x="{x:.1f}" dy="{0 if i == 0 else lh}">{ln}</tspan>'
    return s + "</text>"


def circle(cx, cy, c, L):
    r, qs, hs, ss = L["r"], L["q_size"], L["head_size"], L["sub_size"]
    lh = qs * 1.25
    gap = qs * 1.1
    sub_h = ss * 1.35 if c["sub"] else 0
    # total height of the text stack, used to centre it in the circle
    head_h = hs * 0.75 + sub_h + 16 + 5
    body_h = gap + (len(c["q1"]) - 1) * lh + 2 * gap * 0.95 + (len(c["q2"]) - 1) * lh + qs * 0.7
    y = cy - (head_h + body_h) / 2 + hs * 0.75
    g = f'<g filter="url(#lift)"><circle cx="{cx}" cy="{cy}" r="{r}" fill="#FFFFFF"/></g>'
    g += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c["fill"]}"/>'
    g += f'<circle cx="{cx}" cy="{cy}" r="{r - L["ring"]/2}" fill="none" stroke="{c["ring"]}" stroke-width="{L["ring"]}"/>'
    g += text_block(cx, y, [c["head"]], hs, 0, "head")
    if c["sub"]:
        y += sub_h
        g += text_block(cx, y, [c["sub"]], ss, 0, "subh")
    bar_y = y + 16
    g += f'<rect x="{cx-28}" y="{bar_y:.1f}" width="56" height="5" rx="2.5" fill="{c["ring"]}"/>'
    y1 = bar_y + 5 + gap + qs * 0.35
    g += text_block(cx, y1, c["q1"], qs, lh, "q")
    div_y = y1 + (len(c["q1"]) - 1) * lh + gap * 0.95 - qs * 0.35
    g += (f'<line x1="{cx-70}" x2="{cx+70}" y1="{div_y:.1f}" y2="{div_y:.1f}" stroke="{c["ring"]}" '
          f'stroke-opacity=".45" stroke-width="2" stroke-dasharray="2 7" stroke-linecap="round"/>')
    y2 = div_y + gap * 0.95 + qs * 0.35
    g += text_block(cx, y2, c["q2"], qs, lh, "q")
    return g


def build(L):
    W, H, r, R = L["W"], L["H"], L["r"], L["R"]
    ox, oy = L["centre"]
    P = lambda ang, rad=R: (ox + rad * math.cos(math.radians(ang)), oy + rad * math.sin(math.radians(ang)))
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           '<title>The Profit &amp; Cash Flow Cycle</title>',
           '<defs><style>', font_face(),
           f'.title{{font-family:Poppins;font-weight:700;fill:{INK};letter-spacing:-.5px}}'
           f'.sub{{font-family:Lato;font-weight:400;fill:{MUTED}}}'
           f'.head{{font-family:Poppins;font-weight:700;fill:{INK};letter-spacing:1px}}'
           f'.subh{{font-family:Lato;font-weight:400;fill:{MUTED}}}'
           f'.q{{font-family:Lato;font-weight:700;fill:{INK}}}'
           f'.lab{{font-family:Lato;font-weight:400;font-style:italic;fill:{INK}}}'
           f'.centre{{font-family:Poppins;font-weight:600;fill:{MUTED}}}',
           '</style>',
           '<filter id="lift" x="-20%" y="-20%" width="140%" height="150%">'
           '<feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#002B4E" flood-opacity=".12"/></filter>']
    for c in CIRCLES:
        col = c["ring"][1:]
        svg.append(f'<marker id="head-{col}" viewBox="0 0 12 12" refX="7" refY="6" markerWidth="{L["head"]}" '
                   f'markerHeight="{L["head"]}" orient="auto" markerUnits="userSpaceOnUse">'
                   f'<path d="M1,1 L11,6 L1,11 L3.5,6 Z" fill="#{col}"/></marker>')
    svg.append('</defs>')
    svg.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

    t = L.get("title")
    if t:
        svg.append(text_block(t["x"], t["y"], t["lines"], t["size"], t["size"] * 1.1, "title", t["anchor"]))
        svg.append(text_block(t["x"], t["sub_y"], t["sub"], t["sub_size"], t["sub_size"] * 1.3, "sub", t["anchor"]))
    lg = L.get("logo")
    if lg:
        svg.append(f'<image href="{logo_href()}" x="{lg[0]}" y="{lg[1]}" width="{lg[2]}" height="{lg[2]*0.948:.1f}"/>')

    # Arrows: arcs of the big ring between neighbouring circles, clockwise
    gap_deg = math.degrees(2 * math.asin((r + L["arrow_gap"]) / (2 * R)))
    labels = []
    for i, c in enumerate(CIRCLES):
        a0 = c["angle"] + gap_deg
        a1 = CIRCLES[(i + 1) % 3]["angle"] % 360
        a1 = a1 if a1 > c["angle"] else a1 + 360
        a1 -= gap_deg + L["head_deg"]
        p0, p1 = P(a0), P(a1)
        svg.append(f'<path d="M{p0[0]:.1f},{p0[1]:.1f} A{R},{R} 0 0 1 {p1[0]:.1f},{p1[1]:.1f}" fill="none" '
                   f'stroke="{c["ring"]}" stroke-width="{L["arrow_w"]}" stroke-linecap="round" '
                   f'marker-end="url(#head-{c["ring"][1:]})"/>')
        mid = (a0 + a1 + L["head_deg"]) / 2
        lx, ly = P(mid, R + L["lab_off"])
        lines = L.get("lab_lines", {}).get(i, ARROW_LABELS[i])
        cosm = math.cos(math.radians(mid))
        anchor = "start" if cosm > 0.3 else "end" if cosm < -0.3 else "middle"
        n = len(lines)
        ls = L["lab_size"]
        if anchor == "middle":  # below the bottom arc
            y0 = ly + ls * 0.8
        else:  # beside the arc, vertically centred
            y0 = ly - (n - 1) * ls * 1.25 / 2 + ls * 0.35
        labels.append(text_block(lx, y0, lines, ls, ls * 1.25, "lab", anchor))

    for c in CIRCLES:
        x, y = P(c["angle"])
        svg.append(circle(x, y, c, L))
    svg.extend(labels)

    cs = L["centre_size"]
    svg.append(text_block(ox, oy + L.get("centre_dy", 0) - cs * 1.3 + cs * 0.35, CENTRE, cs, cs * 1.3, "centre"))
    svg.append('</svg>')
    return "".join(svg)


WIDE = dict(
    W=1920, H=1080, r=205, R=356, centre=(960, 598),
    ring=9, head_size=27, sub_size=21, q_size=26, lab_size=26, centre_size=24,
    arrow_w=7, head=30, head_deg=2.5, arrow_gap=18, lab_off=34,
    title=dict(x=96, y=118, lines=["The Profit &amp;", "Cash Flow Cycle"], size=54, anchor="start",
               sub_y=268, sub=["Six strategic questions.", "One connected financial picture."], sub_size=26),
    logo=(1704, 72, 120),
)

SQUARE = dict(
    W=1080, H=1080, r=176, R=306, centre=(540, 652),
    ring=8, head_size=22.5, sub_size=18, q_size=21.5, lab_size=21, centre_size=19,
    arrow_w=6, head=26, head_deg=2.8, arrow_gap=15, lab_off=26,
    lab_lines={2: ["How much cash", "can we invest to", "grow profit?"]},
    title=dict(x=60, y=88, lines=["The Profit &amp; Cash Flow Cycle"], size=40, anchor="start",
               sub_y=130, sub=["Six strategic questions. One connected financial picture."], sub_size=21),
    logo=(948, 52, 76),
)

# Model only (no title or logo), for placing inside documents such as the offer doc
EMBED = dict(WIDE, W=1340, H=1030, centre=(670, 580), title=None, logo=None)

if __name__ == "__main__":
    for name, L in [("cycle-16x9", WIDE), ("cycle-square", SQUARE), ("cycle-embed", EMBED)]:
        (HERE / f"{name}.svg").write_text(build(L))
        print("wrote", name)
