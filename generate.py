#!/usr/bin/env python3
"""Blattwerk · reproduzierbarer SVG/PNG/Asset-Export für `Normal/` und `Beta/`.

Aufruf:  python generate.py             beide Bereiche neu erzeugen
         python generate.py normal      nur Normal/ (G01…G07)
         python generate.py beta        nur Beta/   (B01…B04)

Regeln:  AGENTS.md    → Stern-Codes (*1 *2 *3 *S), Beta-Policy, Freigabe
         STILGUIDE.md → Geometrie, Paletten, Abnahme

Alles wird aus diesem Skript erzeugt; `SVG/`, `PNG/`, `*.xcassets/` und
`Vorschau.html` sind Artefakte. Dateien zu Motiven, die nicht mehr in den
Gruppentabellen stehen, werden beim Lauf entfernt (prune).
"""
from pathlib import Path
import base64, html, io, json, shutil, sys

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

# ── Normal: freigegebene Motive (G01…G07) ───────────────────────────────────
def nibpen(): return tilt(r(26,5,12,31,4,'B')+r(26,10,12,5,1,'A','I',1.8)+line('M29 19v12','H')+p('M26 35h12l3 8-9 16-9-16Z','L')+line('M32 56V46')+c(32,44,2,'I','none'))
def standard(): return tilt(r(18,17,28,33,5,'B')+p('M18 34h28v11q0 5-5 5H23q-5 0-5-5Z','L')+line('M23 23h12','H',2.6)+line('M22 39h20','M'),42)
def shapes(): return r(8,12,27,29,5,'B')+p('m40 9 15 26H25Z','A')+c(38,43,13,'L')+line('M30 43q0-6 6-8','M')
def page(): return p('M17 8h22l10 10v34q0 4-4 4H17q-4 0-4-4V12q0-4 4-4Z','L')+p('M38 8v11h11Z','B','I',2)

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
    raise KeyError(k)

# ── Beta: neue Motive (B01…B04) ─────────────────────────────────────────────
# Aktionsicons (Bearbeiten, Ebenen, Umwandeln) stehen gerade — sie sind
# Bedienelemente, keine Handgeräte. Handgeräte würden +38° gekippt (STILGUIDE).
def bicon(k):
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
        return (group(r(19,9,34,37,4,'M'),'rotate(7 36 27)')
                +r(10,18,34,37,4,'L')+r(15,23,24,10,2,'B','I',1.8)
                +line('M16 41h20m-20 6h14','D',2.2)+line('M18 26h10','H',1.8))
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
    if k=='objekt-erstellen':  # Sticker aus G01, verkleinert, mit Plus-Badge
        return (group(icon('sticker'),'translate(4.8 4.64) scale(0.84)')
                +c(50,50,9,'B','I',2.4)+line('M45 50h10m-5-5v10','H',2.8))
    if k=='bildschirmfoto':  # Kamera
        return (r(25,10,14,10,2.5,'B','I',2.4)+r(8,18,48,34,6,'B')
                +c(32,35,11.5,'L','I',2.6)+c(32,35,5.4,'M','I',2)
                +p('M29.4 32.6q.5-2 2.6-2.4','none','H',2)+c(48.5,25,2.8,'A','I',1.7))
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
]
BETA_GROUPS = [
 ('Bearbeiten', [('groesse-aendern','Größe ändern','fern','1'),('ausschneiden','Ausschneiden','fern','1'),('duplizieren','Duplizieren','fern','1'),('loeschen','Löschen','rot','S'),('kopieren','Kopieren','fern','1'),('einfuegen','Einfügen','fern','1'),('farbe-aendern','Farbe ändern','fern','1'),('bild-zuschneiden','Bild zuschneiden','fern','1')]),
 ('Ebenen', [('ebene-nach-vorne','Ebene nach vorne','fern','1'),('ebene-nach-hinten','Ebene nach hinten','fern','1')]),
 ('Umwandeln', [('umwandeln','Umwandeln','fern','1'),('umwandeln-in-text','In Text umwandeln','fern','1'),('umwandeln-in-mathe','In Mathe umwandeln','fern','1')]),
 ('Objekte & Aufnahme', [('objekt-erstellen','Objekt erstellen','fern','1'),('bildschirmfoto','Bildschirmfoto','fern','1')]),
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
