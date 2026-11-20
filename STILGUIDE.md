# Blattwerk · Stilhandbuch für weitere Icons

**Auftrag an den nächsten Agenten:** Erweitere diese iPad-Notizwerkzeuge durch geskriptete Vektorgeometrie, nicht durch generative Bilder, Emoji, Icon-Fonts oder nachgezeichnete Screenshots. Alle Icons sind freigestellte Piktogramme. Sie sind keine quadratischen App-Logos mit Hintergrundplatte. Die quadratische Fläche ist nur das Koordinatensystem.

## Visuelle Grammatik

- **Raster:** `viewBox="0 0 64 64"`. Optische Mitte bei (32,32), typischer Motivumfang 42–50 Einheiten, meist mindestens 5 Einheiten Rand. Sehr schmale Schreibgeräte dürfen länger sein. Die tatsächliche Fußfläche nicht zwanghaft auf dieselbe Breite skalieren.
- **Silhouette zuerst:** An einem prägnanten Merkmal muss man das Werkzeug schon bei 32 pt erkennen: Spalt und Luftloch beim Füller, Clip beim Kuli, weiche geschwungene Spitze beim Pinsel. Verwende nur Details, die eine Funktion, eine Materialkante oder eine Überlappung erklären.
- **Kontur:** 2,6 Einheiten in dunkler, zur Körperfarbe passender Tinte. Innenkonturen 1,6–2,3; wichtige Gestenlinien bis 3,6. Runde Kappen und Verbindungen. Normale Ecken mit 2–5 Einheiten Radius, scharf belassene Papierfalze, Federn und Bleistiftspitzen. Kein Außen-Schatten, Glow, Farbverlauf oder 3D-Rendering.
- **Lage:** Dokumente und Bedienelemente stehen gerade. Handgeräte meist aufrecht konstruieren und um **+38° um (32,32)** drehen: Spitze links unten, Schaft rechts oben. Flache Blockradierer ca. +42°. Gestapelte Blätter hinten maximal 9° drehen.
- **Farbflächen:** Eine helle Papier- oder Materialfläche, eine kräftige Körperfarbe und dunkle Kontur. Höchstens ein Akzent (z. B. goldene Manschette), ein kurzer Lichtstrich. Überlappende Flächen besitzen klare Kanten; Grün ist Leitfarbe, kein Zwang für jedes Material.
- **Monochrom:** Genau **eine** sichtbare RGB-Farbe: `#000000` oder `#FFFFFF`. Innenlichter, Fenster und Aussparungen sind transparent, nicht mit der Gegenfarbe gefüllt. Beide Varianten haben dieselbe Alphamaske. Auf beliebigen Hintergründen darf keine weiße bzw. schwarze Platte erscheinen.

## Verbindliche Palette · sRGB

| Palette | I · Kontur | B · Körper | L · hell | M · Schatten | H · Licht | A · Akzent | D · Detail |
|---|---|---|---|---|---|---|---|
| fern | #174C40 | #58BD8B | #D5F2CF | #328862 | #F5FFF0 | #DBEC79 | #255E49 |
| cobalt | #29476A | #609CDE | #D7EAFF | #477CB6 | #F4FAFF | #F6C770 | #345978 |
| iris | #493D70 | #AC92D8 | #E8DDF8 | #8269B5 | #FCF6FF | #FFD589 | #63508B |
| coral | #703E4A | #ED98A0 | #FFE0D4 | #CF7685 | #FFF5E9 | #FFC979 | #965660 |
| honey | #624D2D | #EAC365 | #FFF0BC | #CC9845 | #FFFAE3 | #F39C71 | #876936 |
| sea | #28555C | #63BCB6 | #D1EEEB | #418F94 | #F3FFFB | #F4C775 | #346D74 |
| ember | #743D34 | #EE876A | #FFDFB9 | #C46552 | #FFF5D8 | #FFCF62 | #94503E |

`F` bezeichnet ein Detail **auf gefülltem Körper**: im Farbsatz Konturtinte, in Mono ausgespart (z. B. Stickeraugen). In der Luminanzmaske sind I/B/M/D deckend, L/H/A/F ausgespart. Neue Motive immer in Mono prüfen: Benachbarte Flächen dürfen nicht zu einem unlesbaren Block verschmelzen.

## Welche Varianten gehören wohin?

| Gruppe | Familie | Exporte pro Motiv |
|---|---|---|
| G01 | Werkzeugleiste | farbe, schwarz, weiss |
| G02 | Navigation & Seiten | gruen (Palette fern; auch große Flächen füllen) |
| G03 | Schreibspitzen | farbe, schwarz, weiss |
| G04 | Zeichenwerkzeuge | farbe, schwarz, weiss |
| G05 | Radierer | farbe |
| G06 | Verlauf | schwarz, weiss |
| G07 | App-Navigation | schwarz, weiss |

**Verwandt, nicht identisch:** „Formen“ in G01 ist das Menü für mehrere geometrische Objekte; „Formen“ in G04 ist ein Zeichenwerkzeug (Dreiecklineal mit Kreis). Ebenso sind Werkzeugwahl „Radiergummi“ und die drei Radierertypen getrennte Motive.

## Umsetzung & Übergabe

1. Wenn das Pack vorliegt, verwende `generate.py` als geometrische Referenz. Zeichne ein neues Motiv in `icon(k)` aus `p` (Pfad), `r` (Rechteck), `c` (Kreis), `line`, `tilt` oder `group`. Nur die obigen Farbrollen einsetzen. Beispiel für das Prinzip: `r(14,12,36,40,4,'L') + line('M21 24h22m-22 7h14','D',2)` ergibt ein Blatt mit zwei Textzeilen.
2. Füge in `groups` **einen** Eintrag `(slug, deutscher Anzeigename, Palette)` hinzu. Die Variantentabelle steuert die Exporte. Slugs: Kleinbuchstaben, Bindestriche, `ae/oe/ue/ss`. Schlüssel z. B. `g03-fueller-farbe`. Bestehende Slugs nicht umbenennen.
3. Python 3, Pillow und CairoSVG installieren (`python -m pip install pillow cairosvg`; Cairo muss systemweit verfügbar sein). Im Pack `python generate.py` ausführen. SVG, PNG, Xcode-Katalog und Offline-Vorschau werden relativ zur Skriptdatei erzeugt. `vorschau.template` neben dem Skript lassen. Bei einer Erweiterung die Zähler im Vorschau-Footer aktualisieren.
4. **Ohne Quelldateien:** Dieselben Geometrie-, Farb- und Namensregeln in einem neuen Skript verwenden. Füllungen und Aussparungen mit einer SVG-Luminanzmaske oder zusammengesetzten Pfaden trennen, keine Hintergrundfarbe setzen. PNGs mit Alphakanal ausgeben. Nicht jeden Pfad einfach global umfärben: Dadurch verschwinden Innendetails.
5. **Abnahme:** Alle Varianten bei 24 und 32 pt visuell prüfen. Ist die Silhouette lesbar? Unterscheiden sich verwandte Werkzeuge? Prüfe quadratische Maße, freie Außenkanten, gleiche Ausrichtung, keine angeschnittenen Konturen, echte Transparenz sowie Weiß auf Dunkel und Schwarz auf Hell. Bei einem neuen Icon die Variantenzahl ausschließlich nach seiner Gruppe wählen.

## In der App

`Blattwerk.xcassets` in das Xcode-Projekt aufnehmen und dem App-Target zuordnen. Beispiel: `Image("g03-fueller-farbe").renderingMode(.original)` in SwiftUI. Das Set nutzt 32 pt als Nenngröße mit 32/64/96 px bei 1×/2×/3×. Für farbige Icons Originalfarben beibehalten. Weiß auf dunklen, Schwarz auf hellen Flächen einsetzen. Der 256-px-Export ist für größere Darstellungen vorgesehen; für weitere Größen vom SVG ausgehen. Eine Toolbar-Schaltfläche kann eine größere Trefferfläche als ihr sichtbares Icon haben (z. B. 44 × 44 pt).
