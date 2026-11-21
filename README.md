# BlattwerkIcons

Icon-Atlas für die iPad-Notizapp **Blattwerk**: freigestellte Vektor-Piktogramme,
skriptbasiert erzeugt (kein generatives Bildmaterial), in zwei Bereichen organisiert.

| Ordner | Inhalt |
|---|---|
| [`Normal/`](Normal/) | freigegebene Motive, Gruppen G01–G07 — der Stand für die App |
| [`Beta/`](Beta/) | neue Motive in Arbeit, Gruppen B01–… — **nicht freigegeben** |
| [`STILGUIDE.md`](STILGUIDE.md) | visuelle Grammatik: Raster, Konturen, Paletten, Abnahme |
| [`AGENTS.md`](AGENTS.md) | Arbeitsregeln: Stern-Codes (`*1 *2 *3 *S`), Beta-Policy, Freigabe-Ablauf |

## Kurzüberblick

- **Stern-Codes** steuern die Varianten eines Motivs: `*1` grün (mehrere Grüntöne),
  `*2` schwarz + weiß, `*3` farbenfroh, `*S` Sonderfarbe (rot). Kombinationen wie `*12`.
- **Beta bleibt Beta:** Neues landet in `Beta/`; Übernahme nach `Normal/` nur auf
  ausdrückliche Anweisung (siehe `AGENTS.md`).
- Alles wird aus [`generate.py`](generate.py) erzeugt:

  ```bash
  python -m pip install pillow cairosvg   # oder: pillow resvg-py
  python generate.py                      # beide Bereiche
  python generate.py beta                 # nur Beta/
  ```

  Ergebnis je Bereich: `SVG/`, `PNG/{32,64,96,256}/`, Xcode-Katalog, `Vorschau.html`, `INDEX.md`.

## Vorschau

`Normal/Vorschau.html` und `Beta/Vorschau.html` sind offline-fähige Atlanten
(Icon-Daten als Daten-URIs eingebettet) mit Filter nach Variante.
