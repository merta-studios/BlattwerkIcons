# Beta-Redesign · Prüfbericht

Die Motive bleiben Beta. Das Kontaktblatt `Beta-Normal-Kontaktblatt.png` zeigt je Motiv links ein thematisch verwandtes freigegebenes Icon und rechts das Beta-Icon, jeweils als 256-px-Export und daneben in 32 px. Die Normal-Serie hat keine entsprechenden Beta-Gruppen; die Vergleichsmotive wurden daher nach Inhalt gewählt.

## Änderungen

- **Größe ändern:** Vorher wirkten die Eckgriffe wie ein leeres Drahtgitter. Jetzt tragen eine helle Fläche, differenzierte Griffe und feine Innenlinien das Motiv.
- **Ausschneiden:** Vorher waren Klingen und Griffe gleichförmige Balken. Jetzt bilden zugespitzte Klingen, Schneiden, Ösen und Niet eine Schere.
- **Duplizieren:** Vorher waren es zwei flache Rechtecke. Jetzt zeigen versetzte Karten mit Etikett und Zeilen den doppelten Gegenstand.
- **Löschen:** Vorher war die Tonne eine einfache helle Fläche mit Strichen. Jetzt tragen Deckelwulst, Griff und eingefasste Sicken die rote Tonne.
- **Kopieren:** Vorher fehlte den Blättern Materialcharakter. Jetzt geben Falze, Papierfläche und Textzeilen dem Blattstapel Kontur.
- **Einfügen:** Vorher war das Klemmbrett sehr flach. Jetzt trennen eine umlaufende Materialkante, Papier und eine geformte Klammer die Bestandteile.
- **Farbe ändern:** Vorher fehlte dem Farbfächer ein Lichtdetail. Jetzt geben gerundete Blätter, Niet und Lichtstrich dem Fächer mehr Materialität.
- **Bild zuschneiden:** Vorher dominierten abstrakte Winkel ein sehr kleines Bild. Jetzt liegt eine Landschaft mit Sonne in einem greifbaren Zuschnittrahmen.
- **Ebene nach vorne:** Vorher waren die Ebenen flache Blöcke mit schwer lesbarem Pfeil. Jetzt zeigen Blattkanten und ein Aufwärts-Badge die Aktion.
- **Ebene nach hinten:** Vorher war die Richtung im überlappenden Block schwer zu erkennen. Jetzt zeigen umgekehrte Blattfolge und Abwärts-Badge die Aktion.
- **Umwandeln:** Vorher standen zwei flache Felder über einem schmalen Pfeil. Jetzt verbinden Papier, gemeinsame Handschrift und ein Doppelpfeil Quelle und Ziel.
- **In Text umwandeln:** Vorher blieb die Herkunft wenig greifbar. Jetzt verbindet das gemeinsame Handschriftblatt ein gerichteter Pfeil mit dem Textziel.
- **In Mathe umwandeln:** Vorher blieb die Herkunft wenig greifbar. Jetzt verbindet das gemeinsame Handschriftblatt ein gerichteter Pfeil mit dem Matheziel.
- **Objekt erstellen:** Vorher wurde das vorhandene Sticker-Motiv lediglich verkleinert. Jetzt ist ein eigener gefalzter Sticker mit Gesicht und Plus-Badge gezeichnet.
- **Bildschirmfoto:** Vorher war die Kamera ein flaches Rechteck mit Kreisen. Jetzt tragen Gehäusekante, Sucheraufbau und gefasste Linse die Kamera.

## Prüfstand und offene Punkte

Der Beta-Generator wurde mit Pillow und resvg-py ausgeführt. Alle 60 PNG-Exporte haben die erwarteten quadratischen Maße und freie Außenkanten bei einer Alphaprägung über 8/255; die Ecken sind transparent. Das Kontaktblatt wurde nach der Überarbeitung insgesamt visuell angesehen. Eine separate, dokumentierte Abnahme nach *jedem einzelnen* Motiv sowie eine vollständige Prüfung der Vorschau bei 24 pt wurden nicht durchgeführt. Die Monomaske wurde als Schwarz-auf-Hell-Kontaktübersicht geprüft, aber Weiß-auf-Dunkel nicht separat abgenommen; insbesondere verschmelzen beim Farbfächer dunkle benachbarte Flächen. Daher ist die geforderte vollständige Mono-Festigkeit und die exakte Stilgleichheit noch nicht als abgenommen zu betrachten.
