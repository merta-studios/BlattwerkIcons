# Brief: Redesign der Beta-Icons auf exakten Blattwerk-Stil

> Prompt an einen neuen Agenten. Arbeitsrepo: `merta-studios/BlattwerkIcons`
> (Branch laut Session-Notiz). Lies zusätzlich `AGENTS.md`, `STILGUIDE.md`,
> `Normal/AGENTS.md`, `Beta/AGENTS.md` — dieser Brief ersetzt nichts davon, er setzt es voraus.

## Ausgangslage

Das Repo führt zwei Bereiche: freigegebene Icons in `Normal/` (Gruppen G01–G07) und
unfreigegebene in `Beta/` (Gruppen B01–B04, Dateien `b0X-slug-variante.*`). Die 15 Beta-Motive
sind funktional korrekt und regelkonform erzeugt, aber dem Owner **nicht schön genug**: Sie lesen
aktuell wie abstrakte UI-Glyphen (flache Flächen, drahtige Balken), während die Normal-Icons
gezeichnete Werkzeuge und Objekte mit Material, Licht und Charakter sind.

## Deine Aufgabe

Zeichne **alle 15 Beta-Motive neu** (oder überarbeite sie so tief, dass es equivaliert), bis sie
im Side-by-side mit den Normal-Icons als dieselbe Serie durchgehen — bei 256 px **und** bei 32 pt.
„Derselbe Style exakt" heißt: gleiche Strichstärken, gleiche Farblogik, gleiche Materialität,
gleiche Detaildichte, gleiche optische Ruhe. Nicht: ähnliche Bedeutung.

## Pflicht-Vorarbeit, vor der ersten Geometrie-Zeile

1. **Normal-Icons richtig ansehen.** Öffne `Normal/Vorschau.html` und geh jedes Motiv durch.
   Öffne danach einzeln Dateien aus `Normal/PNG/256/` (und bei Unklarheit `Normal/SVG/`) und
   lies die zugehörige Geometrie in `generate.py` (`icon()`): `stift`, `radiergummi`, `notizzettel`,
   `bilder`, `fueller`, `pinsel`, `tape`, `suche`, `seite-hinzufuegen` sind die besten Lehrstücke.
2. Pro Lehrstück notieren: Wo sitzt die helle Papier-/Materialfläche (L)? Wo Körperfarbe (B),
   Schatten (M), Lichtstrich (H), der eine Akzent (A)? Wie sind Überlappungen getrennt?
   Welche Kontur ist 2,6, welche Innenkontur dünner, welche Gestenlinie stärker? Wo ist gerundet
   (2–5), wo bewusst scharf? Wie ist gekippt (+38° um (32,32)) bzw. warum steht etwas gerade?
3. Daraus eine eigene Prüfcheckliste ableiten und beim Zeichnen danebenlegen:
   Raster `viewBox 0 0 64 64`, optische Mitte (32,32), Motivumfang 42–50 Einheiten, Rand meist ≥ 5,
   Kontur 2,6 in passender dunkler Tinte, Innenkonturen 1,6–2,3, Gestenlinien bis 3,6,
   runde Kappen/Verbindungen, keine Verläufe/Schatten/Glow/3D, höchstens ein Akzent + ein
   kurzer Lichtstrich, echte Transparenz statt Hintergrundplatte.

## Die Original-Aufforderungen des Owners (wörtlich, verbindlich)

> Größe ändern Icon (vier abgerundete Vierecke, mit anderer Füllung, einer oben links, einer
> unten rechts, einer oben rechts, einer unten links, und alle sind von einem Viereck verbunden) \*1
> Ausschneiden (Schere) \*1
> Duplizieren \*1
> Löschen (Mülltonne) \*Special: rot
> Ebene nach vorne \*1
> Ebene nach hinten \*1
> Kopieren \*1
> Einfügen \*1
> Bildschirmfoto \*1
> Objekt erstellen (abgeleitet von Objekt/sticker Icon) \*1
> Umwandeln (z.b. Handschrift in Text, Text in Handschrift, Handschrift in Mathe, Text in Mathe,
> Mathe in Text, Mathe in Handschrift) \*1
> Umwandeln in Text \*1
> Umwandeln in Mathe \*1
> Farbe ändern \*1
> Bild zuschneiden \*1

Bedeutung der Stern-Codes (steht auch in `AGENTS.md` §3): `*1` = nur grüner Stil mit mehreren
Grüntönen (Palette `fern`); `*2` = schwarzer und weißer Stil, beide je einmal, nur schwarz und
weiß, keine Farbunterschiede pro Icon; `*3` = farbenfroh, mehrere zum Icon passende Farben;
mehrere Ziffern kombinieren, z. B. `*12` = grün, weiß und schwarz. `*Special: rot` = Sonderpalette
`rot` für destruktive Aktionen. **Codes, Slugs und Gruppenzuordnung (`BETA_GROUPS` in
`generate.py`) bleiben unverändert** — geändert wird nur die Geometrie in `bicon(k)`.

## Konkret heißt „schöner" hier

- **Material statt Drahtgitter:** Flächen bekommen Papier-/Materialcharakter wie bei
  `notizzettel` (helles Blatt, dunkle Textzeilen, Falz, Klebestreifen) oder `bilder`
  (gestapelte Rahmen, Bergsilhouette, Sonnenakzent) — nicht zwei flache Rechtecke.
- **Prägnante Silhouette:** Jedes Motiv bei 32 pt an einem Merkmal erkennbar, wie der Füller an
  Spalt und Luftloch, der Kuli am Clip. Bei der Schere z. B. echte Klingenform mit Schneide und
  Niet statt uniformer Doppelstriche; bei der Mülltonne Deckelwulst, Griffmulde, Sicken.
- **Tiefe in den Grüntönen (`*1`):** alle `fern`-Rollen ausspielen (I/B/L/M/H, A sparsam),
  Lichtstrich und Schattenkante setzen, wo Flächen sich überlappen.
- **Familien bilden, Verwandte trennen:** `kopieren` / `duplizieren` / `einfuegen` deutlich
  verschieden; `groesse-aendern` / `bild-zuschneiden` deutlich verschieden; die drei
  `umwandeln*`-Motive als erkennbare Familie mit derselben Quelldarstellung (Handschrift-Kritzel).
- **Mono-fest konstruieren:** Auch wenn aktuell nur `gruen` bzw. `rot` exportiert wird, muss die
   Geometrie in Schwarz/Weiß funktionieren (keine benachbarten Flächen, die verschmelzen).

## Prozessregeln

- **Beta bleibt Beta.** Nichts nach `Normal/` verschieben, kopieren oder dort referenzieren;
  `Normal/` gar nicht anfassen. Übernahme nur, wenn der Owner es ausdrücklich anordnet
  (`AGENTS.md` §2).
- Geometrie ausschließlich in `generate.py` / `bicon(k)` mit den Helfern `p/r/c/line/group/tilt`
  und den Farbrollen `I B L M H A D F`. Keine generativen Bilder, keine Emoji, keine Icon-Fonts,
  keine Screenshots als Vorlage.
- Umgebung: Python 3 + Pillow; Renderer CairoSVG, Fallback `resvg-py` (steht so im Skript).
  `python -m pip install pillow cairosvg` bzw. `pillow resvg-py`, dann `python generate.py beta`.
- Nach **jedem** Motiv: generieren, dann visuell abnehmen — `Beta/Vorschau.html` plus selbst
  gebautes Kontaktblatt (Pillow) mit dem neuen Motiv **neben** einem Normal-Motiv derselben
  Gruppe, bei 256 px und 32 px. Solange iterieren, bis der Stilunterschied verschwindet.
- Abnahme additionally nach `STILGUIDE.md` §Abnahme: quadratische Maße, freie Außenkanten,
  gleiche Ausrichtung, keine angeschnittenen Konturen, echte Transparenz, Weiß-auf-Dunkel-/
  Schwarz-auf-Hell-Tauglichkeit der Maske.
- Commits je Gruppe (B01, B02, B03, B04) mit kurzer Begründung, was vorher schwach war.

## Definition of Done

- Alle 15 Motive neu gezeichnet; `python generate.py beta` läuft fehlerfrei; `Beta/INDEX.md`,
  `Beta/Vorschau.html` und `Blattwerk-Beta.xcassets` sind aktuell (erzeugt das Skript selbst).
- Side-by-side-Kontaktblatt (256 px und 32 px, Beta neben Normal) liegt als Prüfdatei bei oder
  ist im PR beschrieben; die Beta-Motive gehen darin als Teil der Serie durch.
- Kurzbericht pro Motiv: 1 Satz „vorher schwach weil …", 1 Satz „trägt jetzt durch …".
