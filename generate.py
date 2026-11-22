#!/usr/bin/env python3
"""Blattwerk · reproduzierbarer SVG/PNG/Asset-Export für `Normal/` und `Beta/`.

Aufruf:  python generate.py             beide Bereiche neu erzeugen
         python generate.py normal      nur Normal/ (G01…G16)
         python generate.py beta        nur Beta/   (B01…B02)

Regeln:  AGENTS.md    → Stern-Codes (*1 *2 *3 *S), Beta-Policy, Freigabe
         STILGUIDE.md → Geometrie, Paletten, Abnahme

Alles wird aus diesem Skript erzeugt; `SVG/`, `PNG/`, `*.xcassets/` und
`Vorschau.html` sind Artefakte. Dateien zu Motiven, die nicht mehr in den
Gruppentabellen stehen, werden beim Lauf entfernt (prune).
"""
from pathlib import Path
import base64, html, io, json, math, shutil, sys

from PIL import Image

ROOT = Path(__file__).resolve().parent
GROESSEN = (32, 64, 96, 256)

# ── Renderer ────────────────────────────────────────────────────────────────
# Kanonisch ist CairoSVG (System-Cairo nötig). Fehlt libcairo, springt resvg-py
# ein — reine Wheels, gleiche Geometrie, Abweichung < 1/255 pro Pixel.
def _renderer():
    try:
        import cairosvg
        return lambda b, w, h: cairosvg.svg2png(bytestring=b, output_width=w, output_height=h)
    except Exception:
        pass
    try:
        import resvg_py
        return lambda b, w, h: resvg_py.svg_to_bytes(svg_string=b.decode(), width=w, height=h)
    except Exception:
        pass
    sys.exit('Kein Renderer gefunden:  python -m pip install cairosvg   (Fallback: resvg-py)')
raster = _renderer()

# ── Farbrollen ──────────────────────────────────────────────────────────────
# I Kontur, B Körper, L Papier/hell, M Schatten, H Licht, A Akzent, D Detail
PAL = {
 'fern':    ('#174c40', '#58bd8b', '#d5f2cf', '#328862', '#f5fff0', '#dbec79', '#255e49'),
 'cobalt':  ('#29476a', '#609cde', '#d7eaff', '#477cb6', '#f4faff', '#f6c770', '#345978'),
 'iris':    ('#493d70', '#ac92d8', '#e8ddf8', '#8269b5', '#fcf6ff', '#ffd589', '#63508b'),
 'coral':   ('#703e4a', '#ed98a0', '#ffe0d4', '#cf7685', '#fff5e9', '#ffc979', '#965660'),
 'honey':   ('#624d2d', '#eac365', '#fff0bc', '#cc9845', '#fffae3', '#f39c71', '#876936'),
 'sea':     ('#28555c', '#63bcb6', '#d1eeeb', '#418f94', '#f3fffb', '#f4c775', '#346d74'),
 'ember':   ('#743d34', '#ee876a', '#ffdfb9', '#c46552', '#fff5d8', '#ffcf62', '#94503e'),
 # Sonderpalette, nur für *S (destruktive Aktionen wie Löschen). Nie für reguläre Motive.
 'rot':     ('#6b1f22', '#de4a4a', '#ffdfda', '#b03a3a', '#fff5f3', '#f2c57c', '#8a2e2e'),
}
KEYS = 'IBLMHAD'
MONO = dict(zip(KEYS, ['white', 'white', 'black', 'white', 'black', 'black', 'white']))

# ── Stern-Codes (siehe AGENTS.md) ───────────────────────────────────────────
# *1 = nur Grün in mehreren Grüntönen   *2 = Schwarz + Weiß   *3 = farbig
# *S = Sonderfarbe (aktuell Rot)        Kombinationen: *12, *23, *123 …
STERN = {'1': ['gruen'], '2': ['schwarz', 'weiss'], '3': ['farbe'], 'S': ['rot']}
REIHE = ['farbe', 'gruen', 'rot', 'schwarz', 'weiss']
def varianten(code):
    out = []
    for z in str(code).upper():
        if z not in STERN:
            sys.exit(f'Unbekannter Stern-Code {z!r} in {code!r} — erlaubt: 1 2 3 S')
        out += [v for v in STERN[z] if v not in out]
    return sorted(out, key=REIHE.index)

# ── Geometrie-Bausteine (Palette-Tokens, keine festen Farben) ───────────────
colors = {}
def col(k): return colors.get(k, k)
def attrs(f, s, w): return f'fill="{col(f)}" stroke="{col(s)}" stroke-width="{w}"'
def p(d, f='none', s='I', w=2.6, extra=''): return f'<path d="{d}" {attrs(f,s,w)} {extra}/>'
def r(x, y, w, h, rr, f='B', s='I', sw=2.6): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rr}" {attrs(f,s,sw)}/>'
def c(x, y, rad, f='B', s='I', w=2.6): return f'<circle cx="{x}" cy="{y}" r="{rad}" {attrs(f,s,w)}/>'
def line(d, s='I', w=2): return p(d, 'none', s, w)
def group(content, t): return f'<g transform="{t}">{content}</g>'
def tilt(z, a=38): return group(z, f'rotate({a} 32 32)')

# ── Normal: freigegebene Motive (G01…G16; G08–G16 aus Beta übernommen) ──────────────────────────────────
def nibpen(): return tilt(r(26,5,12,31,4,'B')+r(26,10,12,5,1,'A','I',1.8)+line('M29 19v12','H')+p('M26 35h12l3 8-9 16-9-16Z','L')+line('M32 56V46')+c(32,44,2,'I','none'))
def standard(): return tilt(r(18,17,28,33,5,'B')+p('M18 34h28v11q0 5-5 5H23q-5 0-5-5Z','L')+line('M23 23h12','H',2.6)+line('M22 39h20','M'),42)
def shapes(): return r(8,12,27,29,5,'B')+p('m40 9 15 26H25Z','A')+c(38,43,13,'L')+line('M30 43q0-6 6-8','M')
def page(): return p('M17 8h22l10 10v34q0 4-4 4H17q-4 0-4-4V12q0-4 4-4Z','L')+p('M38 8v11h11Z','B','I',2)
def _pt(cx, cy, R, a):
    t = math.radians(a); return cx + R*math.cos(t), cy + R*math.sin(t)
def arc(cx, cy, R, a0, a1):
    """Kreisbogen von a0 nach a1 (Grad, Bildschirmkoordinaten: 90 = unten)."""
    x0, y0 = _pt(cx, cy, R, a0); x1, y1 = _pt(cx, cy, R, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return f'M{x0:.2f} {y0:.2f}A{R} {R} 0 {large} {sweep} {x1:.2f} {y1:.2f}'
def _star_pts(cx, cy, R, ri):
    pts_out, pts_in = [], []
    for i in range(5):
        ao = math.radians(-90 + i * 72)
        ai = math.radians(-90 + i * 72 + 36)
        pts_out.append((cx + R * math.cos(ao), cy + R * math.sin(ao)))
        pts_in.append((cx + ri * math.cos(ai), cy + ri * math.sin(ai)))
    return pts_out, pts_in
def star_round(cx, cy, R, ri):
    """Weich gerundeter 5-zackiger Blattwerk-Stern."""
    pts_out, pts_in = _star_pts(cx, cy, R, ri)
    d = []
    for i in range(5):
        ox, oy = pts_out[i]
        ix_prev, iy_prev = pts_in[(i - 1) % 5]
        ix_next, iy_next = pts_in[i]
        t = 0.20
        b1x, b1y = ox + (ix_prev - ox) * t, oy + (iy_prev - oy) * t
        b2x, b2y = ox + (ix_next - ox) * t, oy + (iy_next - oy) * t
        v1x, v1y = ix_next + (ox - ix_next) * 0.15, iy_next + (oy - iy_next) * 0.15
        ox_n, oy_n = pts_out[(i + 1) % 5]
        v2x, v2y = ix_next + (ox_n - ix_next) * 0.15, iy_next + (oy_n - iy_next) * 0.15
        d.append(f'M{b1x:.2f} {b1y:.2f}' if i == 0 else f'L{b1x:.2f} {b1y:.2f}')
        d.append(f'Q{ox:.2f} {oy:.2f} {b2x:.2f} {b2y:.2f}')
        d.append(f'L{v1x:.2f} {v1y:.2f}')
        d.append(f'Q{ix_next:.2f} {iy_next:.2f} {v2x:.2f} {v2y:.2f}')
    d.append('Z')
    return ''.join(d)
def gear_round(cx, cy, ro, ri, n=8):
    """Zahnrad mit weich abgerundeten Zahnspitzen und -füßen."""
    def xy(ang_deg, rad):
        a = math.radians(ang_deg)
        return cx + rad * math.cos(a), cy + rad * math.sin(a)
    d = []
    for i in range(n):
        t = i * 360 / n
        v0 = xy(t - 18, ri)
        v1 = xy(t - 13, ri)
        fl_in = xy(t - 11.2, ri + (ro - ri) * 0.45)
        t_c1 = xy(t - 5.2, ro)
        t_c2 = xy(t + 5.2, ro)
        fl_out = xy(t + 11.2, ri + (ro - ri) * 0.45)
        v2 = xy(t + 13, ri)
        v3 = xy(t + 18, ri)
        k_in, k_tip1 = xy(t - 12.2, ri), xy(t - 9.5, ro)
        k_tip2, k_out = xy(t + 9.5, ro), xy(t + 12.2, ri)
        if i == 0:
            d.append(f'M{v0[0]:.2f} {v0[1]:.2f}')
        d.append(f'L{v1[0]:.2f} {v1[1]:.2f}')
        d.append(f'Q{k_in[0]:.2f} {k_in[1]:.2f} {fl_in[0]:.2f} {fl_in[1]:.2f}')
        d.append(f'Q{k_tip1[0]:.2f} {k_tip1[1]:.2f} {t_c1[0]:.2f} {t_c1[1]:.2f}')
        d.append(f'L{t_c2[0]:.2f} {t_c2[1]:.2f}')
        d.append(f'Q{k_tip2[0]:.2f} {k_tip2[1]:.2f} {fl_out[0]:.2f} {fl_out[1]:.2f}')
        d.append(f'Q{k_out[0]:.2f} {k_out[1]:.2f} {v2[0]:.2f} {v2[1]:.2f}')
        d.append(f'L{v3[0]:.2f} {v3[1]:.2f}')
    d.append('Z')
    return ''.join(d)
def curved_arrow(cx, cy, r_in, r_out, a_start, a_end, cw=True, head_extra=3.8, head_ang=22):
    """Kräftiger geschwungener Bandpfeil von a_start nach a_end."""
    r_mid = 0.5 * (r_in + r_out)
    a_shaft = a_end - head_ang if cw else a_end + head_ang
    def pt(ang, rad):
        t = math.radians(ang)
        return cx + rad * math.cos(t), cy + rad * math.sin(t)
    s_out, e_out = pt(a_start, r_out), pt(a_shaft, r_out)
    wing_out, tip = pt(a_shaft, r_out + head_extra), pt(a_end, r_mid)
    wing_in, e_in = pt(a_shaft, r_in - head_extra), pt(a_shaft, r_in)
    s_in = pt(a_start, r_in)
    sweep_out, sweep_in = (1, 0) if cw else (0, 1)
    large = 1 if abs(a_shaft - a_start) > 180 else 0
    return (f'M{s_out[0]:.2f} {s_out[1]:.2f}'
            f'A{r_out} {r_out} 0 {large} {sweep_out} {e_out[0]:.2f} {e_out[1]:.2f}'
            f'L{wing_out[0]:.2f} {wing_out[1]:.2f}L{tip[0]:.2f} {tip[1]:.2f}'
            f'L{wing_in[0]:.2f} {wing_in[1]:.2f}L{e_in[0]:.2f} {e_in[1]:.2f}'
            f'A{r_in} {r_in} 0 {large} {sweep_in} {s_in[0]:.2f} {s_in[1]:.2f}Z')
def doc_page(x=13, y=8, w=36, h=48, fold=10, rr=4, f='L'):
    """Dokumentseite mit sauberem Eselsohr-Falz."""
    rx, by, fx, fy = x + w, y + h, x + w - fold, y + fold
    main = f'M{x+rr} {y}H{fx}L{rx} {fy}V{by-rr}q0 {rr}-{rr} {rr}H{x+rr}q-{rr} 0-{rr}-{rr}V{y+rr}q0-{rr} {rr}-{rr}Z'
    return p(main, f) + p(f'M{fx} {y}V{fy}H{rx}Z', 'B', 'I', 2)

def icon(k):
    if k=='stift': return tilt(r(26,7,12,36,4,'B')+p('M26 37h12v7l-6 13-6-13Z','L')+p('m29 51 3 7 3-7Z','I','I',1.5)+r(26,14,12,4,0.7,'A','I',1.6)+line('M29.5 21v12','H',2))
    if k=='freihandlasso': return p('M19 42C6 36 9 19 22 13c13-7 31-1 32 12 1 14-15 22-29 18','none','I',6)+p('M19 42C6 36 9 19 22 13c13-7 31-1 32 12 1 14-15 22-29 18','none','B',2.8)+line('M23 43c10 11 18 17 23 8 3-6-4-9-6-5','I',3.2)+c(22,42,4.8,'A')
    if k=='boxlasso': return r(12,14,40,34,3,'L','none')+p('M14 14h36q2 0 2 2v30q0 2-2 2H14q-2 0-2-2V16q0-2 2-2Z','none','I',2.8,'stroke-dasharray="4 5"')+''.join(r(x-3.3,y-3.3,6.6,6.6,1.5,'B') for x,y in [(12,14),(52,14),(12,48),(52,48)])
    if k=='radiergummi': return tilt(r(20,9,24,44,5,'B')+p('M20 30h24v18q0 5-5 5H25q-5 0-5-5Z','L')+line('M24 16v9','H',2.5)+line('M24 35h16','M'),43)+line('M32 55h19','I',2.4)
    if k=='textfeld': return r(9,12,46,40,4,'L')+p('M21 23h22v6h-3l-1-2h-4v15h4v3H25v-3h4V27h-4l-1 2h-3Z','I','none')+r(6,9,7,7,1.5,'B','I',2)+r(51,48,7,7,1.5,'B','I',2)
    if k=='formen': return shapes()
    if k=='sticker': return p('M11 23q0-8 8-9l24-4q8-1 9 7l3 18q0 4-3 8L40 54q-2 2-6 2l-15 1q-6 0-7-7Z','B')+p('M37 55q4-7 3-14 7 2 14-3Z','L')+c(24,29,2.5,'F','none')+c(39,26,2.5,'F','none')+line('M25 37q7 6 13-2','F',2.8)+line('m17 22 7-1','H')
    if k=='bilder': return group(r(9,16,42,34,4,'M'),'rotate(-9 30 33)')+r(14,14,42,34,4,'L')+c(45,23,3.8,'A','I',1.6)+p('m17 43 11-15 9 10 5-6 11 11v2H17Z','B','I',1.9)
    if k=='notizzettel': return group(r(13,11,39,44,4,'M'),'rotate(-6 32 32)')+p('M14 10h36q2 0 2 3v27L38 53H15q-3 0-3-3V13q0-3 2-3Z','L')+p('M38 53V40h14Z','B')+r(22,7,20,7,1,'A','I',1.8)+line('M19 24h25m-25 7h19m-19 7h10','D',2.3)
    if k=='laserpointer': return tilt(r(26,23,12,34,4,'B')+r(26,23,12,7,2,'L','I',2)+r(30,34,4,8,2,'F','none')+line('M32 18v-9m-6 10-3-4m15 4 3-4','I',2.8)+c(32,5,2,'A','I',1.5))
    if k=='seitenleiste': return r(7,13,50,38,5,'L')+p('M12 13h13v38H12q-5 0-5-5V18q0-5 5-5Z','B')+line('M12 22h8m-8 7h6m-6 7h6','H',2.2)+line('M32 22h17m-17 7h12','D',2)
    if k=='suche': return p('m38 40 4-4 13 13q3 3 0 6t-6 0Z','B')+c(27,27,18,'B')+c(27,27,12,'L','I',2)+line('M19 27q0-7 7-8','M',2.3)
    if k=='weltkugel': return c(32,32,23,'B')+p('M32 9c-16 11-16 35 0 46 16-11 16-35 0-46Z','L','I',2)+line('M10 32h44M15 18q17 10 34 0M15 46q17-10 34 0M32 10v44','I',2)
    if k=='lesemodus': return page()+line('M20 23h12m-12 7h14','D')+p('M22 43q16-22 36 0-18 22-36 0Z','B')+c(40,43,6,'L','I',2)+c(40,43,2.6,'I','none')
    if k=='seite-hinzufuegen': return page()+line('M20 24h12m-12 7h13','D')+c(47,46,12,'B')+line('M41 46h12m-6-6v12','H',3)
    if k=='seiten': return r(9,16,33,40,4,'M')+r(16,11,33,40,4,'B')+r(23,7,32,40,4,'L')+r(29,14,20,8,1.5,'B','I',1.7)+line('M29 29h19m-19 6h13','D')
    if k=='mehr': return r(6,19,52,26,13,'B')+''.join(c(x,32,2.8,'I','none') for x in [19,32,45])+line('M17 23h15','H',1.7)
    if k=='fueller': return nibpen()
    if k=='kugelschreiber': return tilt(r(29,4,6,7,1,'L','I',2)+r(27,10,10,34,3,'B')+p('M27 39h10l-1 8-4 10-4-10Z','L')+line('M32 54v4','I',2.6)+line('M36 13h5v14','I',2.7)+line('M30 18v15','H'))
    if k=='pinsel': return tilt(p('M29 31 30 9q0-5 3-5t3 5l-1 23Z','B')+p('m26 31 11 1-1 10-12-1Z','L')+p('M24 40q-6 4-4 11t-5 9q18 1 21-12 1-4-1-7Z','M')+line('M30 44q0 7-6 11','H',2)+line('m26 36 9 1','D',1.8),29)
    if k=='textmarker': return tilt(r(23,7,18,34,4,'B')+p('M23 35h18l-3 11H26Z','L')+p('M27 46h10v7l-10 5Z','A')+line('M27 14v15','H',3)+line('M24 11h16','I',1.7))
    if k=='bleistift': return tilt(r(26,6,12,41,2,'B')+r(26,5,12,8,2,'A','I',2)+r(26,13,12,4,0,'L','I',1.6)+line('M30 18v26','F',1.8)+p('m26 45 6 14 6-14-3 2-3-2-3 2Z','L','I',1.9)+p('m30 53 2 6 2-6Z','I','I',1.3))
    if k=='tape': return p('M27 21h14v12q1 6 7 8l11 3-4 3 2 5-16-4q-14-3-14-15Z','L')+p('M26 12q20-2 20 17t-17 20l-8-1Z','M')+f'<ellipse cx="24" cy="30" rx="16" ry="18" {attrs("B","I",2.6)}/>'+f'<ellipse cx="24" cy="30" rx="7" ry="8.5" {attrs("L","I",2.3)}/>'+line('m46 42-3 5m8-4-3 5','D',1.6)+line('M13 25q2-6 7-8','H')
    if k=='formen-werkzeug': return p('M31 7 56 53H7Z','B')+p('m31 24 10 19H21Z','L','I',2)+line('m17 44 3 2m0-9 3 2m1-9 3 2','I',1.8)+c(46,18,9,'A')
    if k=='praezisionsradierer': return tilt(r(27,7,10,35,3,'B')+p('M27 36h10l-1 10h-8Z','L')+p('M29 46h6v8q-1 4-5 3l-1-2Z','A')+line('M30 15v15','H'))+line('M35 51h4m4 0h3m4 0h2','D',2)
    if k=='standardradierer': return standard()
    if k=='strichradierer': return line('M7 49q4-7 9-2t11 4','D',3.6)+p('M30 51q9 1 13-7t12-7','none','M',2.5,'stroke-dasharray="3 5"')+group(standard(),'translate(2 -5) scale(.91)')
    if k in ('rueckgaengig','vorgaengig'):
        a=p('M8 28 25 12q2-2 2 1v8h7c16 0 23 12 22 28q0 4-2 1c-5-11-12-17-22-17h-5v9q0 2-2 0L8 30q-1-1 0-2Z','I','I',1.6)
        return a if k=='rueckgaengig' else group(a,'translate(64 0) scale(-1 1)')
    if k=='haus': return p('M7 30 30 10q2-2 4 0l23 20q2 2 0 4l-2 2q-1 1-3 0l-3-3v19q0 3-3 3h-9V39H27v16h-9q-3 0-3-3V33l-3 3q-2 1-3 0l-2-2q-2-2 0-4Z','I','none')
    if k=='schliessen': return line('m17 17 30 30m0-30L17 47','I',7)
    if k=='groesse-aendern':
        return (r(13,13,38,38,3,'L','I',2.2)
                +line('M21 19h20','M',2)+line('M21 45h13','M',2)
                +r(8,8,10,10,2.5,'B')+r(46,8,10,10,2.5,'A')
                +r(8,46,10,10,2.5,'L')+r(46,46,10,10,2.5,'M')
                +line('M10.5 11h4','H',1.8))
    if k=='ausschneiden':
        return (p('M30 32 15 8q-1-2 2-1 10 4 17 20Z','L')
                +line('M20 13 31 29','M',1.8)
                +p('M34 32 49 8q1-2-2-1-10 4-17 20Z','L')
                +line('M44 13 33 29','M',1.8)
                +p('M30 30q-3 4-6 8l4 3 6-8Z','M')
                +p('M34 30q3 4 6 8l-4 3-6-8Z','B')
                +c(22,46,8,'B')+c(22,46,4,'L','I',1.8)
                +c(42,46,8,'B')+c(42,46,4,'L','I',1.8)
                +c(32,30,2.8,'A','I',1.7)+line('M17 43q1-2 3-3','H',1.8))
    if k=='duplizieren':
        return (r(22,7,30,34,4,'M')+line('M28 14h14','H',2)
                +r(10,15,30,34,4,'L')+line('M16 26h18m-18 6h12','D',2.2)
                +c(44,44,11,'B')+line('M38 44h12m-6-6v12','H',3))
    if k=='loeschen':
        return (p('M26 15v-3q0-4 4-4h4q4 0 4 4v3','none','I',2.6)
                +p('M16 22h32l-3 30q-.4 4-4 4H23q-3.6 0-4-4Z','B')
                +p('M20 25h24l-2 25q-.2 2-2 2H24q-2 0-2-2Z','L','I',1.8)
                +line('M27 30v16m5-16v16m5-16v16','D',2.1)
                +r(11,15,42,7,3,'M')+line('M16 17.5h12','H',2))
    if k=='kopieren':
        return (p('M28 7h16l10 10v26q0 4-4 4H28q-4 0-4-4V11q0-4 4-4Z','M')
                +p('M44 7v10h10Z','B','I',2)
                +p('M14 17h16l10 10v26q0 4-4 4H14q-4 0-4-4V21q0-4 4-4Z','L')
                +p('M30 17v10h10Z','B','I',2)
                +line('M16 33h18m-18 7h16m-16 7h10','D',2.2))
    if k=='einfuegen':
        return (r(10,10,44,46,5,'M')+r(15,15,34,36,3,'L')
                +line('M21 28h22m-22 7h18m-18 7h12','D',2.2)
                +p('M23 12q0-3 3-3h2q0-4 4-4t4 4h2q3 0 3 3v6H23Z','B')
                +c(32,10,1.5,'F','none')+line('M26 14h5','H',1.8))
    if k=='farbe-aendern':
        blatt=lambda a,f: group(r(25.5,10,13,42,5,f,'I',2.4),f'rotate({a} 32 52)')
        return (blatt(-24,'L')+blatt(-8,'A')+blatt(8,'B')+blatt(24,'M')
                +line('M41 16l-2 8','H',2)+c(32,52,3.4,'L','I',2.2))
    if k=='bild-zuschneiden':
        return (r(14,14,36,36,3,'L')+c(40,23,3,'A','I',1.6)
                +p('M18 44 27 31l7 8 4-4 8 9Z','B','I',1.8)
                +p('M11 9h7v36h37v7H15q-4 0-4-4Z','M')
                +p('M9 12h36q4 0 4 4v39h-7V19H9Z','B')
                +line('M12 15h12','H',2))
    if k in ('ebene-nach-vorne','ebene-nach-hinten'):
        hinten = r(9,10,34,34,4,'M')+line('M15 16h12','H',2)
        vorne = r(20,20,34,34,4,'L')+line('M26 27h20m-20 6h14','D',2)
        badge = c(44,44,10,'B')
        arrow = (line('M44 49V39m-4 4 4-4 4 4','H',2.8) if k=='ebene-nach-vorne'
                 else line('M44 39v10m-4-4 4 4 4-4','H',2.8))
        if k=='ebene-nach-hinten':
            hinten = r(20,20,34,34,4,'M')+line('M26 26h12','H',2)
            vorne = r(9,10,34,34,4,'L')+line('M15 17h20m-20 6h14','D',2)
            badge = c(44,44,10,'B')
        return hinten+vorne+badge+arrow
    if k=='umwandeln' or k.startswith('umwandeln-in-'):
        # Die gemeinsame handschriftliche Quelle bleibt in allen drei Motiven gleich.
        quelle = (r(7,9,24,34,3,'L')
                  +line('M11 20c3-5 4 4 7-1s4 3 8-1M11 29c3-5 4 4 7-1s4 3 8-1','D',2))
        ziel = r(33,9,24,34,3,'B')+line('M37 13h8','H',1.8)
        if k=='umwandeln-in-text':
            ziel += line('M39 34 45 19l6 15m-10-5h8','F',2.5)
        elif k=='umwandeln-in-mathe':
            ziel += line('M51 20H39l6 7-6 7h12','F',2.7)
        else:
            ziel += line('M39 23h12m-12 5h9m-9 5h12','F',2.2)
        if k=='umwandeln':
            pfeil = line('M18 51h28','I',3)+p('M12 51l8-5v10Z','B')+p('M52 51l-8-5v10Z','B')
        else:
            pfeil = line('M17 51h25','I',3)+p('M51 51l-9-6v12Z','B')
        return quelle+ziel+pfeil
    if k=='objekt-erstellen':
        return (p('M10 22q0-7 7-8l22-4q8-1 9 7l2 15q0 4-3 7L37 49q-2 2-6 2l-14 1q-6 0-7-7Z','B')
                +p('M35 50q4-6 3-12 6 2 11-2Z','L')
                +c(22,27,2.2,'F','none')+c(36,25,2.2,'F','none')
                +line('M23 34q6 5 12-2','F',2.4)+line('M16 21l6-1','H',2)
                +c(49,49,9,'B')+line('M44 49h10m-5-5v10','H',2.7))
    if k=='bildschirmfoto':
        return (p('M21 19l4-7h14l4 7Z','M')+r(8,18,48,35,6,'B')
                +p('M9 27h46v19q0 7-6 7H15q-6 0-6-7Z','M','I',2)
                +c(32,35,12,'L')+c(32,35,7,'B','I',2)
                +line('M28 34q0-3 3-4','H',2)+c(48,24,2.5,'A','I',1.7))
    if k == 'lineal':
        ticks = ''.join(line(f'M{43-w} {y}h{w}', 'I', 2.0)
                        for y, w in [(12, 6.5), (19, 4.2), (26, 6.5), (33, 4.2), (40, 6.5), (47, 4.2), (54, 6.5)])
        return tilt(r(21, 5, 22, 54, 3.5, 'B')
                    + p('M33 5h6.5a3.5 3.5 0 0 1 3.5 3.5v47a3.5 3.5 0 0 1-3.5 3.5H33Z', 'L', 'I', 2.0)
                    + ticks + c(27, 11.5, 2.3, 'L', 'I', 1.8) + line('M25 19v29', 'H', 2.1)
                    + r(21, 5, 22, 54, 3.5, 'none', 'I', 2.6))
    if k == 'zoom-ansicht':
        return (p('m37 40 4-4 14 14q3 3 0 6t-6 0Z', 'B')
                + p('m39 42 4-4 3.5 3.5-4 4Z', 'A', 'I', 1.7)
                + line('M47 47l5.5 5.5', 'H', 2.0)
                + c(26, 26, 18.5, 'B') + line(arc(26, 26, 15.3, 200, 245), 'H', 2.0)
                + c(26, 26, 12.5, 'L', 'I', 2.2)
                + line('M26 19.5v13m-6.5-6.5h13', 'I', 3.0))
    if k == 'stoppuhr':
        return (group(r(29.5, 11.8, 5, 6.5, 1.5, 'M', 'I', 2.2), 'rotate(44 32 36)')
                + r(29, 11, 6, 7, 1, 'M', 'I', 2.2) + r(25, 5.5, 14, 5.5, 2.5, 'A', 'I', 2.4)
                + c(32, 36, 19, 'B') + line(arc(32, 36, 16, 200, 245), 'H', 2.0)
                + c(32, 36, 13.5, 'L', 'I', 2.2)
                + p('M32 36V24A12 12 0 0 1 43.2 31.8Z', 'A', 'none')
                + line('M32 24.2v2.4m0 18.8v2.4M20.2 36h2.4m18.8 0h2.4', 'D', 2.0)
                + line('M32 36V27', 'I', 2.7) + line('M32 36l6 3.5', 'I', 2.6)
                + c(32, 36, 2.5, 'B', 'I', 1.8))
    if k == 'scrollrichtung-vertikal':
        return (r(10, 11, 36, 45, 5, 'M') + r(15, 7, 38, 49, 5, 'L')
                + r(46.2, 21, 3.2, 21, 1.6, 'M', 'none')
                + p('M32.5 13l9 9.5H36v18h5.5L32.5 50l-9-9.5H29v-18h-5.5Z', 'B', 'I', 2.4)
                + line('M31.3 25v13', 'H', 1.9))
    if k == 'scrollrichtung-horizontal':
        return (r(11, 10, 45, 36, 5, 'M') + r(7, 15, 49, 38, 5, 'L')
                + r(21, 46.2, 21, 3.2, 1.6, 'M', 'none')
                + p('M13 32.5l9.5-9V29h18v-5.5L50 32.5l-9.5 9V36h-18v5.5Z', 'B', 'I', 2.4)
                + line('M25 31.3h13', 'H', 1.9))
    if k == 'seitenleiste-links':
        return (r(7, 12, 50, 40, 5.5, 'L')
                + p('M12.5 12H26v40H12.5q-5.5 0-5.5-5.5V17.5q0-5.5 5.5-5.5Z', 'B')
                + r(10.5, 19, 12, 5, 2, 'A', 'I', 1.6) + line('M11.5 29.5h10m-10 7h8', 'H', 2.2)
                + r(31, 19, 15, 5, 1.8, 'M', 'none') + line('M31 30h20m-20 7h14', 'D', 2.2))
    if k == 'seitenleiste-rechts':
        return (r(7, 12, 50, 40, 5.5, 'L')
                + p('M38 12h13.5q5.5 0 5.5 5.5v29q0 5.5-5.5 5.5H38Z', 'B')
                + r(41.5, 19, 12, 5, 2, 'A', 'I', 1.6) + line('M42.5 29.5h10m-10 7h8', 'H', 2.2)
                + r(13, 19, 15, 5, 1.8, 'M', 'none') + line('M13 30h20m-20 7h14', 'D', 2.2))
    if k == 'seite-drehen':
        cx, cy, R, a_end = 45, 45, 6.4, 338
        t = math.radians(a_end)
        px, py = cx + R*math.cos(t), cy + R*math.sin(t)
        tx, ty, nx, ny = -math.sin(t), math.cos(t), math.cos(t), math.sin(t)
        tip = (px + tx*4.0, py + ty*4.0)
        w1 = (px - tx*1.8 + nx*3.8, py - ty*1.8 + ny*3.8)
        w2 = (px - tx*1.8 - nx*3.8, py - ty*1.8 - ny*3.8)
        tri = f'M{tip[0]:.2f} {tip[1]:.2f}L{w1[0]:.2f} {w1[1]:.2f}L{w2[0]:.2f} {w2[1]:.2f}Z'
        return (r(9, 23, 42, 31, 4, 'M') + doc_page(14, 8, 32, 43, 9, 4, 'L')
                + line('M19 23h13m-13 6h10m-10 6h7', 'D', 2.0)
                + c(45, 45, 12, 'B') + line(arc(cx, cy, R, 125, a_end), 'H', 2.6) + p(tri, 'H', 'none'))
    if k == 'seite-nach-rechts-drehen':
        return (doc_page(10, 15, 30, 41, 8.5, 4, 'L') + line('M15 29.5h13m-13 6.5h17m-17 6.5h11', 'D', 2.1)
                + p(curved_arrow(34, 30, 15.5, 21.5, -108, 6, cw=True), 'B', 'I', 2.4)
                + line(arc(34, 30, 18.5, -94, -36), 'H', 1.8))
    if k == 'seite-nach-links-drehen':
        return (doc_page(24, 15, 30, 41, 8.5, 4, 'L') + line('M29 29.5h13m-13 6.5h17m-17 6.5h11', 'D', 2.1)
                + p(curved_arrow(30, 30, 15.5, 21.5, -72, -186, cw=False), 'B', 'I', 2.4)
                + line(arc(30, 30, 18.5, -144, -86), 'H', 1.8))
    if k == 'seite-180-drehen':
        return (r(21, 16, 22, 32, 3.5, 'L')
                + p('M21 19.5q0-3.5 3.5-3.5h15q3.5 0 3.5 3.5v3.5H21Z', 'A', 'I', 2.0)
                + line('M25.5 29.5h13m-13 6h9m-9 6h11', 'D', 2.0)
                + p(curved_arrow(32, 32, 18.5, 24, -88, 16, cw=True, head_extra=3.4, head_ang=24), 'B', 'I', 2.3)
                + p(curved_arrow(32, 32, 18.5, 24, 92, 196, cw=True, head_extra=3.4, head_ang=24), 'B', 'I', 2.3))
    if k == 'gehe-zu-seite':
        return (r(50, 22, 6, 12, 2.2, 'A', 'I', 1.8) + doc_page(22, 9, 31, 46, 9, 4, 'L')
                + line('M28 24h13m-13 7h18m-18 7h14m-14 7h10', 'D', 2.1)
                + p('M7 28.5h13.5v-6L33 33 20.5 43.5v-6H7Z', 'B', 'I', 2.5) + line('M10 31.6h9', 'H', 1.8))
    if k == 'seite-leeren':
        eraser = group(r(30, 26, 18, 25, 4, 'B', 'I', 2.4)
                       + p('M30 40h18v7q0 4-4 4H34q-4 0-4-4Z', 'L', 'I', 2.0)
                       + line('M33.5 30v7', 'H', 2.0) + line('M33.5 44.5h11', 'M', 1.8), 'rotate(42 39 38.5)')
        return (doc_page(13, 8, 35, 47, 10, 4, 'L') + line('M18 22h15', 'D', 2.1)
                + p('M18 29h16', 'none', 'M', 2.1, 'stroke-dasharray="3.5 3.5"')
                + line('M18 37q5 2.5 9.5 0', 'M', 2.0) + eraser)
    if k == 'gliederung':
        return (r(12, 11, 35, 46, 4, 'M') + doc_page(16, 7, 36, 48, 10, 4, 'L')
                + r(21, 16, 6.5, 6.5, 2, 'B', 'I', 1.8) + line('M31 19.2h9', 'I', 2.6)
                + line('M24.2 22.5v17M24.2 29h4.5M24.2 37h4.5', 'M', 2.0)
                + c(31, 29, 2.3, 'A', 'I', 1.6) + line('M36 29h10', 'D', 2.1)
                + c(31, 37, 2.3, 'A', 'I', 1.6) + line('M36 37h8', 'D', 2.1)
                + r(21, 43.5, 6.5, 6.5, 2, 'B', 'I', 1.8) + line('M31 46.7h14', 'I', 2.6))
    if k == 'favorit':
        cx, cy, R, ri = 32, 33, 24.5, 12.2
        sd = star_round(cx, cy, R, ri)
        po, pi = _star_pts(cx, cy, R, ri)
        shade = (f'M{cx} {cy}L{po[0][0]:.2f} {po[0][1]:.2f}L{pi[0][0]:.2f} {pi[0][1]:.2f}'
                 f'L{po[1][0]:.2f} {po[1][1]:.2f}L{pi[1][0]:.2f} {pi[1][1]:.2f}'
                 f'L{po[2][0]:.2f} {po[2][1]:.2f}L{pi[2][0]:.2f} {pi[2][1]:.2f}Z')
        return (p(sd, 'B') + p(shade, 'M', 'none') + p(sd, 'none', 'I', 2.6)
                + p(star_round(32, 33.5, 8.6, 4.3), 'A', 'I', 1.8) + line('M20 26l6-1.5', 'H', 2.2))
    if k == 'lesezeichen':
        return (r(11, 13, 39, 41, 4.5, 'L') + line('M17 24h9m-9 7h9m-9 7h8', 'D', 2.2)
                + p('M27.5 13v-3q0-3 3-3h4v6Z', 'M')
                + p('M30.5 10q0-3 3-3h10q2.5 0 2.5 2.5V56.5l-7.75-6-7.75 6Z', 'B')
                + line('M34 15v23', 'H', 2.1) + p(star_round(38.5, 27, 5.8, 2.9), 'A', 'I', 1.7))
    if k == 'vorlage-wechseln':
        pal_path = 'M33 17C19 17 10 26 10 37c0 9.5 7 17 16 17 3.8 0 5-2 4.2-4.8-.7-2.6 1.2-4.7 4.8-4.7h5c7 0 13-5 13-11.5C53 23 44 17 33 17Z'
        return (group(r(11, 9, 31, 36, 4, 'L') + line('M16 16.5h14', 'D', 2.1), 'rotate(-7 26 27)')
                + p(pal_path, 'B') + line('M16 28q3-5 10-7', 'H', 2.2)
                + c(20.5, 31, 3.8, 'L', 'I', 1.9) + c(30, 24.5, 3.8, 'A', 'I', 1.9)
                + c(41.5, 28, 3.8, 'H', 'I', 1.9) + c(19.5, 42, 3.8, 'A', 'I', 1.9)
                + c(39, 44, 3.8, 'L', 'I', 2.0))
    if k == 'bestimmte-objekte-loeschen':
        return (r(9, 9, 36, 36, 4, 'L', 'none')
                + p('M13 9h28q4 0 4 4v28q0 4-4 4H13q-4 0-4-4V13q0-4 4-4Z', 'none', 'I', 2.4, 'stroke-dasharray="4.2 4.5"')
                + ''.join(r(x-3.1, y-3.1, 6.2, 6.2, 1.5, 'B', 'I', 2.2) for x, y in [(9, 9), (45, 9), (9, 45)])
                + r(15, 16, 13.5, 13.5, 3, 'B') + line('M18 19.5h5', 'H', 1.8)
                + c(33, 28.5, 7, 'A', 'I', 2.2) + c(45.5, 45.5, 11.5, 'B') + line('M39.5 45.5h12', 'H', 3.2))
    if k == 'einstellungen':
        return (p(gear_round(32, 32, 25.5, 19.5, 8), 'B') + line(arc(32, 32, 16.5, 205, 245), 'H', 2.1)
                + c(32, 32, 14, 'L', 'I', 2.1) + c(32, 32, 8.2, 'B', 'I', 2.0) + c(32, 32, 3.5, 'L', 'I', 1.8))
    if k == 'alles-exportieren':
        return (r(16, 13, 32, 22, 3.5, 'M') + r(12, 18, 40, 24, 3.5, 'L')
                + p('M9 35h13l3 5h14l3-5h13v14q0 5-5 5H14q-5 0-5-5Z', 'B')
                + p('M9.5 45h45v4q0 5-5 5H14.5q-5 0-5-5Z', 'M', 'I', 2.0) + line('M14 40h6', 'H', 2.0)
                + p('M32 7l10.5 11H36v16h-8V18h-6.5Z', 'B', 'I', 2.5) + line('M30.5 21v9', 'H', 1.8))
    if k == 'seite-exportieren':
        return (doc_page(11, 9, 33, 46, 9.5, 4, 'L') + line('M16 24h14m-14 7h12m-12 7h7', 'D', 2.1)
                + p('M28 42Q33 25 46 21l-3-5.5 14 2.5-6 13-3-5.5Q38 29 34 44Z', 'B', 'I', 2.4)
                + line('M34 35q4-7 11-10', 'H', 1.8))
    if k == 'pdf':
        return (r(11, 11, 36, 46, 4, 'M') + doc_page(16, 7, 36, 48, 10, 4, 'L')
                + line('M22 18h12m-12 30h19', 'D', 2.1) + p('M11.2 40.5L16 44.5V41Z', 'M', 'I', 2.0)
                + r(10, 26, 44, 15, 3, 'B', 'I', 2.4) + line('M14 29h6', 'H', 1.6)
                + p('M18 38V30h3.4a2.1 2.1 0 0 1 0 4.2H18', 'none', 'L', 2.4)
                + p('M27.3 30h2.8a4 4 0 0 1 0 8h-2.8Z', 'none', 'L', 2.4)
                + line('M38.8 38V30h6.2M38.8 34h4.8', 'L', 2.4))
    if k == 'bezier-kurve-anpassen':
        arch = 'M11 47C12 24 21 19 32 19C43 19 52 24 53 47'
        return (p(arch, 'none', 'I', 6.4) + p(arch, 'none', 'B', 2.8) + line('M12 19h40', 'D', 2.4)
                + r(7, 43, 8.5, 8.5, 2, 'L', 'I', 2.4) + r(48.5, 43, 8.5, 8.5, 2, 'L', 'I', 2.4)
                + r(27.5, 14.5, 9, 9, 2.2, 'L', 'I', 2.4)
                + c(11, 19, 4.4, 'A', 'I', 2.2) + c(53, 19, 4.4, 'A', 'I', 2.2))
    if k == 'bezier-punkte-verschieben':
        zig = 'M9.5 47L20 21.5L33.5 44L45 18.5L54.5 34'
        return (p(zig, 'none', 'I', 6.4) + p(zig, 'none', 'B', 2.8)
                + r(15.5, 17, 9, 9, 2.2, 'L', 'I', 2.4)
                + r(29, 39.5, 9, 9, 2.2, 'A', 'I', 2.4)
                + r(40.5, 14, 9, 9, 2.2, 'L', 'I', 2.4))
    if k == 'dicken':
        return (line('M11 15q10.5-4.5 21 0t21 0', 'I', 3.4)
                + p('M11 29q10.5-4.5 21 0t21 0', 'none', 'I', 7.6) + p('M11 29q10.5-4.5 21 0t21 0', 'none', 'M', 3.0)
                + p('M11 46q10.5-4.5 21 0t21 0', 'none', 'I', 13.0) + p('M11 46q10.5-4.5 21 0t21 0', 'none', 'B', 7.8)
                + line('M15 43.0q6.5-2.1 11.5-0.4', 'H', 1.8))
    raise KeyError(k)

# ── Beta: neue Motive (B01…B02) ─────────────────────────────────────────────
# Gleiche Regeln wie Normal: Handgeräte +38° gekippt, Bedienelemente gerade.
def bicon(k):
    if k == 'duplizieren':
        return (r(8.5, 8.5, 31, 31, 4.5, 'L') + line('M14 14h10', 'H', 2.0)
                + r(24.5, 24.5, 31, 31, 4.5, 'B')
                + line('M40 32.5v15m-7.5-7.5h15', 'H', 4.5))
    if k == 'verschieben':
        body = 'M32 6.5l10 10.5H36v11h11v-6L57.5 32 47 42v-6H36v11h6L32 57.5 22 47h6V36H17v6L6.5 32 17 22v6h11V17h-6Z'
        return p(body, 'B', 'I', 2.6) + c(32, 32, 5.8, 'A', 'I', 2.3)
    if k == 'einklappen-pfeile':
        top = p('M32 28L43.2 15H36.5V0H27.5V15H20.8Z', 'B', 'I', 2.6) + line('M30.1 4.8v8.0', 'H', 1.9)
        bot = p('M32 36L43.2 49H36.5V64H27.5V49H20.8Z', 'B', 'I', 2.6) + line('M30.1 51.2v8.0', 'H', 1.9)
        return group(top + bot, 'rotate(45 32 32)')
    if k == 'ausklappen-pfeile':
        top = p('M32 -2.2L43.2 11.8H36.5V26.8H27.5V11.8H20.8Z', 'B', 'I', 2.6) + line('M30.1 14v8.0', 'H', 1.9)
        bot = p('M32 66.2L43.2 52.2H36.5V37.2H27.5V52.2H20.8Z', 'B', 'I', 2.6) + line('M30.1 42v8.0', 'H', 1.9)
        return group(top + bot, 'rotate(45 32 32)')
    if k == 'einklappen':
        return (r(9, 13.5, 46, 21.5, 5, 'L')
                + p('M9 18.5q0-5 5-5h36q5 0 5 5v7.5H9Z', 'B')
                + line('M14.5 19.5h15', 'H', 2.0) + r(40.5, 17.5, 9, 4.5, 1.8, 'A', 'I', 1.7)
                + p('M21.5 49.5L32 39 42.5 49.5l-3.8 3.8-6.7-6.7-6.7 6.7Z', 'B', 'I', 2.4))
    if k == 'ausklappen':
        return (r(9, 9, 46, 39, 5, 'L')
                + p('M9 14q0-5 5-5h36q5 0 5 5v7.5H9Z', 'B')
                + line('M14.5 15h15', 'H', 2.0) + r(40.5, 13, 9, 4.5, 1.8, 'A', 'I', 1.7)
                + line('M16 28.5h24m-24 7h17', 'D', 2.2)
                + p('M21.5 44.5L32 55l10.5-10.5-3.8-3.8-6.7 6.7-6.7-6.7Z', 'B', 'I', 2.4))
    raise KeyError(k)

# ── Gruppentabellen: (Gruppe, [(slug, Anzeigename, Palette, Stern-Code)]) ───
GROUPS = [
 ('Werkzeugleiste', [('stift','Stift','fern','23'),('freihandlasso','Freihandlasso','fern','23'),('boxlasso','Boxlasso','sea','23'),('radiergummi','Radiergummi','coral','23'),('textfeld','Textfeld','fern','23'),('formen','Formen','iris','23'),('sticker','Objekte · Sticker','honey','23'),('bilder','Bilder','cobalt','23'),('notizzettel','Notizzettel','honey','23'),('laserpointer','Laserpointer','ember','23')]),
 ('Navigation & Seiten', [('seitenleiste','Seitenleiste','fern','1'),('suche','Suche','fern','1'),('weltkugel','Weltkugel · Internet','fern','1'),('lesemodus','Nur Lesemodus','fern','1'),('seite-hinzufuegen','Seite hinzufügen','fern','1'),('seiten','Seiten','fern','1'),('mehr','Mehr','fern','1')]),
 ('Schreibspitzen', [('fueller','Füller','fern','23'),('kugelschreiber','Kugelschreiber','cobalt','23'),('pinsel','Pinsel','ember','23')]),
 ('Zeichenwerkzeuge', [('textmarker','Textmarker','fern','23'),('bleistift','Bleistift','honey','23'),('tape','Tape','sea','23'),('formen-werkzeug','Formen','iris','23')]),
 ('Radierer', [('praezisionsradierer','Präzisionsradierer','sea','3'),('standardradierer','Standardradierer','coral','3'),('strichradierer','Strichradierer','iris','3')]),
 ('Verlauf', [('rueckgaengig','Rückgängig','fern','2'),('vorgaengig','Vorgängig','fern','2')]),
 ('App-Navigation', [('haus','Haus · Startseite','fern','2'),('schliessen','Kreuz · Schließen','fern','2')]),
 ('Bearbeiten', [('groesse-aendern','Größe ändern','fern','1'),('ausschneiden','Ausschneiden','fern','1'),('duplizieren','Duplizieren','fern','1'),('loeschen','Löschen','rot','S'),('kopieren','Kopieren','fern','1'),('einfuegen','Einfügen','fern','1'),('farbe-aendern','Farbe ändern','fern','1'),('bild-zuschneiden','Bild zuschneiden','fern','1')]),
 ('Ebenen', [('ebene-nach-vorne','Ebene nach vorne','fern','1'),('ebene-nach-hinten','Ebene nach hinten','fern','1')]),
 ('Umwandeln', [('umwandeln','Umwandeln','fern','1'),('umwandeln-in-text','In Text umwandeln','fern','1'),('umwandeln-in-mathe','In Mathe umwandeln','fern','1')]),
 ('Objekte & Aufnahme', [('objekt-erstellen','Objekt erstellen','fern','1'),('bildschirmfoto','Bildschirmfoto','fern','1')]),
 ('Ansicht & Werkzeuge', [('lineal','Lineal','honey','23'),('zoom-ansicht','Zoom Ansicht','cobalt','23'),('stoppuhr','Stoppuhr','ember','23'),('scrollrichtung-vertikal','Scrollrichtung vertikal','fern','1'),('scrollrichtung-horizontal','Scrollrichtung horizontal','fern','1'),('seitenleiste-links','Seitenleiste links','fern','1'),('seitenleiste-rechts','Seitenleiste rechts','fern','1')]),
 ('Seiten', [('seite-drehen','Seite drehen','fern','1'),('seite-nach-rechts-drehen','Seite nach rechts drehen','fern','1'),('seite-nach-links-drehen','Seite nach links drehen','fern','1'),('seite-180-drehen','180 Grad drehen','fern','1'),('gehe-zu-seite','Gehe zu Seite','fern','1'),('seite-leeren','Seite leeren','rot','S'),('gliederung','Gliederung','fern','1')]),
 ('Organisation', [('favorit','Favorit','fern','1'),('lesezeichen','Lesezeichen','fern','1'),('vorlage-wechseln','Vorlage wechseln (Farbpalette)','fern','1'),('bestimmte-objekte-loeschen','Bestimmte Objekte löschen','fern','1')]),
 ('Einstellungen & Export', [('einstellungen','Einstellungen (Zahnrad)','fern','12'),('alles-exportieren','Alles exportieren','fern','1'),('seite-exportieren','Seite exportieren','fern','1'),('pdf','PDF','fern','12')]),
 ('Zeichnen', [('bezier-kurve-anpassen','Bezier Kurve anpassen','fern','1'),('bezier-punkte-verschieben','Bezier Punkte verschieben','fern','1'),('dicken','Dicken','fern','1')]),
]
BETA_GROUPS = [
 ('Bearbeiten', [('duplizieren','Duplizieren','fern','1'),('verschieben','Verschieben','fern','1')]),
 ('Ansicht', [('einklappen-pfeile','Einklappen (Pfeile)','fern','1'),('ausklappen-pfeile','Ausklappen (Pfeile)','fern','1'),('einklappen','Einklappen','fern','1'),('ausklappen','Ausklappen','fern','1')]),
]

AREAS = {
 'Normal': dict(tag='G', groups=GROUPS, glyph=icon, cat='Blattwerk.xcassets',
                hinweis='Freigegeben'),
 'Beta':   dict(tag='B', groups=BETA_GROUPS, glyph=bicon, cat='Blattwerk-Beta.xcassets',
                hinweis='Nicht freigegeben'),
}

HEADER = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
def paint(raw): return '<g stroke-linecap="round" stroke-linejoin="round">'+raw+'</g>'

def build(area, tag, glyph, k, label, palette, v):
    """Ein Export: schreibt SVG + PNG(32/64/96/256) + Asset, liefert Daten-URI."""
    global colors
    root = ROOT / area
    key = f'{tag.lower()}-{k}-{v}'
    ism = v in ('schwarz', 'weiss')
    colors = MONO.copy() if ism else dict(zip(KEYS, PAL[palette]))
    colors['F'] = 'black' if ism else colors['I']
    layers = paint(glyph(k))
    body = layers
    if ism:
        ink = '#000000' if v == 'schwarz' else '#ffffff'
        body = (f'<defs><mask id="m-{key}" maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">'
                f'{layers}</mask></defs><rect width="64" height="64" fill="{ink}" mask="url(#m-{key})"/>')
    svg = HEADER + f'<title>{html.escape(label)} · {v}</title>' + body + '</svg>'
    (root/'SVG'/tag).mkdir(parents=True, exist_ok=True)
    (root/'SVG'/tag/(key+'.svg')).write_text(svg)
    # Einmal supersamplen. Masken explizit als Luminanz rastern (CairoSVG maskiert über Alpha).
    src = HEADER + ('<rect width="64" height="64" fill="black"/>' if ism else '') + layers + '</svg>'
    img = Image.open(io.BytesIO(raster(src.encode(), 768, 768))).convert('RGBA')
    if ism:
        alpha = img.convert('L'); img = Image.new('RGBA', img.size, ink); img.putalpha(alpha)
    for size in GROESSEN:
        d = root/'PNG'/str(size)/tag; d.mkdir(parents=True, exist_ok=True)
        img.resize((size, size), Image.Resampling.LANCZOS).save(d/(key+'.png'))
    asset = root/AREAS[area]['cat']/(key+'.imageset'); asset.mkdir(parents=True, exist_ok=True)
    entries = []
    for n in (1, 2, 3):
        fname = f'{key}@{n}x.png'
        (asset/fname).write_bytes((root/'PNG'/str(32*n)/tag/(key+'.png')).read_bytes())
        entries.append(dict(idiom='universal', filename=fname, scale=f'{n}x'))
    info = dict(version=1, author='xcode')
    (asset/'Contents.json').write_text(json.dumps(dict(images=entries, info=info,
        properties={'template-rendering-intent': 'original'}), indent=2))
    (root/AREAS[area]['cat']/'Contents.json').write_text(json.dumps(dict(info=info)))
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()

def prune(area, keep):
    """Artefakte entfernen, deren Motiv nicht mehr in der Gruppentabelle steht."""
    root = ROOT/area
    for d in list((root/'SVG').glob('*')) + [p for s in GROESSEN for p in (root/'PNG'/str(s)).glob('*')]:
        if not d.is_dir(): continue
        for f in d.glob('*'):
            if f.is_file() and f.stem not in keep: f.unlink()
        if not any(d.iterdir()): d.rmdir()
    for cat in (root/'SVG', root/'PNG'):
        for s in list(cat.glob('*')):
            if s.is_dir() and not any(s.iterdir()): s.rmdir()
    for name in {AREAS[area]['cat'], 'Blattwerk.xcassets', 'Blattwerk-Beta.xcassets'}:
        cat = root/name
        if not cat.is_dir(): continue
        for imgset in cat.glob('*.imageset'):
            if imgset.name[:-len('.imageset')] not in keep: shutil.rmtree(imgset)
        if not any(p.name != 'Contents.json' for p in cat.iterdir()): shutil.rmtree(cat)

def vorschau(area, data, n_motive, n_exporte):
    tag = AREAS[area]['tag']
    beta = area == 'Beta'
    tpl = (ROOT/'vorschau.template').read_text()
    feld = {
     '/*TITEL*/': 'Blattwerk — Beta-Icons' if beta else 'Blattwerk — Icon-Atlas',
     '/*SERIE*/': 'Beta' if beta else 'Serie 01',
     '/*KURZ*/': 'Beta' if beta else '01',
     '/*UEBERSCHRIFT*/': 'Blattwerk&nbsp;Beta.' if beta else 'Blattwerk.',
     '/*UNTERTITEL*/': 'Neue Icons in Arbeit — noch nicht freigegeben' if beta else 'Icon-Atlas für die iPad-Notizleiste',
     '/*BANNER*/': ('<b>Beta</b> — diese Motive sind noch nicht freigegeben und dürfen nicht in '
                    '<code>Normal/</code> auftauchen. Übernahme nur auf ausdrückliche Anweisung '
                    '(siehe <code>AGENTS.md</code>).') if beta else '',
     '/*GRUPPE*/': tag,
     '/*FOOTER*/': f'{n_motive} Motive &nbsp; / &nbsp; {n_exporte} Varianten',
     '/*ICON_DATA*/': json.dumps(data, ensure_ascii=False),
    }
    for ph, wert in feld.items(): tpl = tpl.replace(ph, wert)
    (ROOT/area/'Vorschau.html').write_text(tpl)

def index(area, rows, n_motive, n_exporte):
    tag, cat = AREAS[area]['tag'], AREAS[area]['cat']
    if area == 'Beta':
        kopf = ('# Blattwerk · Beta — Index\n\n'
                '> **Beta — nicht freigegeben.** Jedes neu erzeugte Motiv landet hier.\n'
                '> Übernahme nach `Normal/` **nur auf ausdrückliche Anweisung** des Owners.\n'
                '> Regeln: [`AGENTS.md`](../AGENTS.md) · Stil: [`STILGUIDE.md`](../STILGUIDE.md)\n\n')
    else:
        kopf = ('# Blattwerk · Normal — Index\n\n'
                '> **Freigegeben.** Alle abgenommenen Motive. Neues kommt zuerst nach `Beta/`.\n'
                '> Regeln: [`AGENTS.md`](../AGENTS.md) · Stil: [`STILGUIDE.md`](../STILGUIDE.md)\n\n')
    kopf += '%d Motive · %d Exporte · Gruppen %s01–%s%02d\n' % (n_motive, n_exporte, tag, tag, len(rows))
    for t, g in rows:
        kopf += '\n## %s · %s\n\n| # | Slug | Anzeigename | Palette | Code | Exporte |\n|---|---|---|---|---|---|\n' % (t, g['name'])
        for n, it in enumerate(g['items'], 1):
            exp = ' '.join('`%s`' % v for v in it['variants'])
            kopf += '| %d | `%s` | %s | %s | `*%s` | %s |\n' % (n, it['id'], it['label'], it['palette'], it['code'], exp)
    kopf += ('\nDateien je Export: `SVG/%sXX/%sxx-slug-variante.svg`, '
             '`PNG/{32,64,96,256}/%sXX/….png` und ein Imageset in `%s/`.\n'
             % (tag, tag, tag, cat))
    (ROOT/area/'INDEX.md').write_text(kopf)

def main(which='beide'):
    tmpl_ok = (ROOT/'vorschau.template').exists()
    if not tmpl_ok: sys.exit('vorschau.template fehlt neben generate.py')
    for area, cfg in AREAS.items():
        tag, groups, glyph = cfg['tag'], cfg['groups'], cfg['glyph']
        if which not in ('beide', area.lower()): continue
        data, keys, n_exp = [], set(), 0
        rows = []
        for i, (name, items) in enumerate(groups, 1):
            t = f'{tag}{i:02}'
            out = []
            for k, label, palette, code in items:
                vs = varianten(code)
                if 'gruen' in vs and palette != 'fern':
                    print(f'  Hinweis: {k} soll *1 (grün) sein, Palette ist aber {palette!r}')
                if 'rot' in vs and palette != 'rot':
                    print(f'  Hinweis: {k} nutzt *S, Palette ist aber {palette!r}')
                icons = {}
                for v in vs:
                    icons[v] = build(area, t, glyph, k, label, palette, v)
                    keys.add(f'{t.lower()}-{k}-{v}'); n_exp += 1
                out.append(dict(label=label, id=k, palette=palette, code=code, variants=vs, icons=icons))
            data.append(dict(name=name, items=out)); rows.append((t, data[-1]))
        (ROOT/area).mkdir(parents=True, exist_ok=True)
        prune(area, keys)
        vorschau(area, data, sum(len(g['items']) for g in data), n_exp)
        index(area, rows, sum(len(g['items']) for g in data), n_exp)
        print(f'{area}: {sum(len(g["items"]) for g in data)} Motive, {n_exp} Exporte')

if __name__ == '__main__':
    main(sys.argv[1].lower() if len(sys.argv) > 1 else 'beide')
