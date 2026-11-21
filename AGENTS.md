# AGENTS.md — Arbeitsregeln für BlattwerkIcons

Dieses Repository verwaltet die Icon-Serien der iPad-App **Blattwerk**.
Geometrie, Paletten und Abnahme stehen in [`STILGUIDE.md`](STILGUIDE.md) — hier stehen die
**Arbeits-, Ordner- und Freigaberegeln**. Bei Widerspruch gilt diese Datei für den Ablauf,
der Stilguide für das Aussehen.

---

## 1. Zwei Bereiche: `Normal/` und `Beta/`

| Ordner | Inhalt | Status |
|---|---|---|
| `Normal/` | freigegebene Motive, Gruppen **G01–G11** (`g0X-slug-variante.*`) | abgenommen; die App nutzt `Normal/Blattwerk.xcassets` |
| `Beta/`   | neue Motive, Gruppen **B01–…** (`b0X-slug-variante.*`) | in Arbeit, **nicht freigegeben** |

In jedem Bereich liegen, vom Skript erzeugt: `SVG/<Gruppe>/`, `PNG/{32,64,96,256}/<Gruppe>/`,
der Xcode-Katalog (`Normal/Blattwerk.xcassets` bzw. `Beta/Blattwerk-Beta.xcassets`),
`Vorschau.html` und `INDEX.md`.

**Grundregel:** Alles, was ab jetzt neu erzeugt oder angefragt wird, ist **Beta** und landet in
`Beta/`. `Normal/` enthält ausschließlich bestehende, freigegebene Motive.

## 2. Beta → Normal: **nur auf ausdrückliche Anweisung**

- Ein Beta-Motiv wird **niemals von sich aus** nach `Normal/` verschoben, kopiert, umbenannt oder
  dort referenziert — auch nicht, wenn es fertig aussieht, auch nicht „der Ordnung halber",
  auch nicht zusammen mit anderen Änderungen.
- Einzige Ausnahme: Der Owner fordert die Übernahme **ausdrücklich** an
  (z. B. „Schieb *Ausschneiden* nach Normal"). Fehlt diese Anweisung, bleibt das Motiv in `Beta/`.
- Ablauf einer angeforderten Übernahme:
  1. In `generate.py` den Eintrag `(slug, Anzeigename, Palette, Code)` aus `BETA_GROUPS` in die
     passende Gruppe von `GROUPS` verschieben (passt keine, neue Gruppe anlegen, Nummerierung
     fortlaufend; bestehende Slugs nicht ändern).
  2. `python generate.py` ausführen. Das Skript schreibt die `g0X-…`-Dateien nach `Normal/` und
     **entfernt die alten `b0X-…`-Dateien aus `Beta/` automatisch** (prune).
  3. `INDEX.md` und die Vorschau-Fußzeilen beider Bereiche werden automatisch neu geschrieben.
  4. Die Übernahme im Commit-Text benennen.
- Umgekehrt ebenso tabu: Motive aus `Normal/` nach `Beta/` verschieben, löschen oder umbenennen.

## 3. Stern-Codes — welche Varianten gewünscht sind

Jedes Motiv trägt in `generate.py` einen Code. Mehrere Ziffern = mehrere Wünsche, z. B. `*12`.

| Code | Bedeutung | Exporte |
|---|---|---|
| `*1` | **nur grüner Stil mit mehreren Grüntönen** (Palette `fern`) | `gruen` |
| `*2` | **schwarzer und weißer Stil**, beide je einmal; nur Schwarz und Weiß, **keine Farbunterschiede pro Icon** | `schwarz`, `weiss` |
| `*3` | **farbenfroh**, mehrere zum Motiv passende Farben (nicht zwingend grün) | `farbe` |
| `*S` | **Special**: Sonderfarbe außerhalb der Serie, aktuell `rot` (destruktive Aktionen wie Löschen) | `rot` |

Kombinationen — die Exportreihenfolge ist fest (`farbe, gruen, rot, schwarz, weiss`):

- `*12` = grün + schwarz + weiss
- `*23` = farbe + schwarz + weiss (Standard der Werkzeugleiste G01/G03/G04)
- `*13` = grün + farbe
- `*123` = farbe + grün + schwarz + weiss
- `*S2` = rot + schwarz + weiss (falls für ein destruktives Icon Monovarianten gewünscht werden)

Regeln dazu:

- `*1` erzwingt die Palette `fern`. Eine andere Palette bei `*1` ist falsch (das Skript warnt).
- `*2`-Exporte sind echte Monochrome: genau **eine** sichtbare Farbe (`#000000` bzw. `#FFFFFF`),
  Aussparungen transparent, beide Varianten mit derselben Alphamaske.
- `*3` wählt eine Palette aus der verbindlichen Tabelle passend zum Motiv (STILGUIDE).
- Wünsche des Owners immer als Stern-Code in `generate.py`, Index und Commit notieren,
  damit Varianten reproduzierbar bleiben.

## 4. Ein neues Motiv anlegen (immer Beta)

1. Geometrie in `generate.py` als Zweig von `bicon(k)` schreiben — nur `p/r/c/line/group/tilt`
   und die Farbrollen `I B L M H A D F` verwenden (STILGUIDE „Visuelle Grammatik").
   Aktionsicons (Bearbeiten/Ebenen/Umwandeln) stehen **gerade**; Handgeräte werden +38° gekippt.
2. Eintrag in `BETA_GROUPS`: `(slug, deutscher Anzeigename, palette, stern_code)`.
   Slug: Kleinbuchstaben, Bindestriche, `ae/oe/ue/ss`.
3. `python generate.py beta` ausführen (ohne Argument: beide Bereiche).
4. Abnahme in `Beta/Vorschau.html` bei 24 und 32 pt prüfen (STILGUIDE „Abnahme").
5. **Nicht** nach `Normal/` kopieren — siehe §2.

## 5. Umgebung und Werkzeuge

- Python 3 + Pillow. Renderer: bevorzugt **CairoSVG** (braucht System-Cairo), automatischer
  Fallback **resvg-py** (reine Wheels, geometrisch identisch).
  `python -m pip install pillow cairosvg` oder `python -m pip install pillow resvg-py`.
- `python generate.py [normal|beta]` erzeugt SVG, PNG (32/64/96/256), Xcode-Katalog,
  `Vorschau.html`, `INDEX.md` und räumt verwaiste Dateien auf.
- `vorschau.template` liegt neben dem Skript und wird für beide Bereiche befüllt.
- `SVG/`, `PNG/`, `*.xcassets/`, `Vorschau.html`, `INDEX.md` sind **Artefakte**: nie von Hand
  editieren, immer über das Skript neu erzeugen.

## 6. No-Gos

- Keine generativen Bilder, Emoji, Icon-Fonts oder nachgezeichnete Screenshots.
- Keine Hintergrundplatten, Verläufe, Schatten, Glow oder 3D.
- Keine weißen bzw. schwarzen Platten in Monovarianten; Aussparungen sind transparent.
- Beta-Katalog (`Blattwerk-Beta.xcassets`) nicht in App-Targets mischen — die App nutzt
  ausschließlich `Normal/Blattwerk.xcassets`.
