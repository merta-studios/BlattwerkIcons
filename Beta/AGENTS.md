# Beta — Arbeitsbereich (nicht freigegeben)

Alles in diesem Ordner ist **Beta**: neue Motive, die noch keine Freigabe haben.

- Neue Motive kommen **immer** hierher (Gruppen `B01…`, Dateien `b0X-slug-variante.*`).
- **Niemals selbst** nach `../Normal/` verschieben, kopieren oder dort referenzieren — auch nicht
  teilweise und nicht „zum Aufräumen". Das geschieht ausschließlich auf **ausdrückliche
  Anweisung** des Owners; Ablauf siehe [`../AGENTS.md`](../AGENTS.md) §2.
- Nichts hier ist stabil: Slugs, Gruppen, Varianten und Dateien dürfen sich jederzeit ändern.
- `Blattwerk-Beta.xcassets` dient nur Vorschau/Test, nicht dem App-Target.
- Erzeugt wird alles über `python generate.py beta` im Wurzelordner des Repos.
