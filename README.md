# DocLens

Ein schlanker PDF-Reader mit integrierter KI-Sidebar. Verbindet sich mit jedem OpenAI-kompatiblen LLM-Endpoint (vLLM, Ollama, OpenAI, LM Studio) und ermoeglicht interaktive PDF-Analyse direkt im Reader.

## Features

- **PDF-Viewer**: Oeffnen, blaettern, zoomen, Text markieren
- **KI-Chat-Sidebar**: Fragen zum Dokument stellen, Streaming-Antworten
- **Text markieren + Rechtsklick**: "Erklaere das", "Zusammenfassen", "Uebersetzen"
- **Prompt-Templates**: Ein-Klick-Aktionen (Zusammenfassen, Uebersetzen, Vereinfachen, Fachbegriffe)
- **Mehrere PDFs in Tabs**: Jeder Tab hat eigenen Chat-Verlauf
- **Kontext-Steuerung**: Aktuelle Seite, ganzes PDF, oder markierter Text als Kontext
- **Dark/Light Mode**: Umschaltbar
- **Chat-Export**: Verlauf als Markdown speichern
- **Drag & Drop**: PDFs per Drag & Drop oeffnen

## Installation

### Voraussetzungen

- Python 3.10 oder neuer
- Ein OpenAI-kompatibler LLM-Endpoint (z.B. vLLM, Ollama, OpenAI API)

### Schritte

```bash
# Repository klonen
git clone https://github.com/clschwarz/pdf-llm-reader.git
cd pdf-llm-reader

# Abhaengigkeiten installieren
pip install -r requirements.txt

# Starten
python main.py
```

### Auf Windows

1. Python installieren: https://www.python.org/downloads/ (bei der Installation "Add to PATH" ankreuzen)
2. Eingabeaufforderung (cmd) oeffnen
3. Befehle oben ausfuehren

## Einrichtung

Beim ersten Start: **Einstellungen** oeffnen und LLM-Verbindung konfigurieren:

| Feld | Beispiel | Beschreibung |
|------|----------|--------------|
| API-URL | `http://192.168.50.10:8000/v1` | OpenAI-kompatibler Endpoint |
| API-Key | `sk-...` | Optional, je nach Server |
| Modell | `gx10-llm` | Modellname am Server |
| Temperature | `0.7` | Kreativitaet (0.0 = exakt, 1.0 = kreativ) |
| Max Tokens | `4096` | Maximale Antwortlaenge |

### Kompatible Backends

| Backend | API-URL Beispiel |
|---------|-----------------|
| vLLM | `http://host:8000/v1` |
| Ollama | `http://host:11434/v1` |
| OpenAI | `https://api.openai.com/v1` |
| LM Studio | `http://localhost:1234/v1` |

## Benutzung

1. **PDF oeffnen**: Datei > PDF oeffnen, oder PDF per Drag & Drop ins Fenster ziehen
2. **Fragen stellen**: Frage ins Chat-Feld eingeben, Enter druecken
3. **Text analysieren**: Text im PDF markieren, Rechtsklick > Aktion waehlen
4. **Kontext waehlen**: "Seite" (nur aktuelle Seite), "Ganzes PDF", oder "Markierung"
5. **Prompt-Templates**: Buttons oben in der Sidebar fuer haeufige Aktionen

## Tastenkuerzel

| Kuerzel | Aktion |
|---------|--------|
| Ctrl+O | PDF oeffnen |
| Ctrl+T | Neuer Tab |
| Ctrl+W | Tab schliessen |
| Ctrl+, | Einstellungen |
| Ctrl+Q | Beenden |
| Ctrl++ | Vergroessern |
| Ctrl+- | Verkleinern |
| Ctrl+Mausrad | Zoom |

## Lizenz

MIT License
