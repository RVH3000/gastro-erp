# 🍽️ Gastro ERP – Warenkreislauf Management

Vollständiges Warenwirtschaftssystem für die professionelle Gastronomie.
Fokus: Steiermark / Österreich (RKSV-konform, 10% USt, de-AT Formatierung).

## Module

| # | Modul | Funktion |
|---|-------|----------|
| 1 | Wareneingang | Wareneingänge mit Charge, MHD und Lieferant erfassen |
| 2 | MHD-Tracking | FEFO-sortiertes Frühwarnsystem (dynamisch, ab heute berechnet) |
| 3 | Warenstand | Echtzeit-Bestände aggregiert aus Chargen |
| 4 | Menüentwicklung | KI-Vorschläge basierend auf Warenstand + kritischen MHD-Artikeln |
| 5 | Rezeptur | Kalkulation mit aktuellen EK-Preisen aus Store |
| 6 | Kalkulation | Planungs- (33%-Ziel) + Kassenkalkulation (Ist-Analyse) |
| 7 | Inventur | Soll-Ist-Abgleich, Schwundanalyse, automatische Bestandskorrektur |

## Architektur

```
src/
├── data/
│   └── store.js          # Single Source of Truth – alle Module lesen hier
├── js/
│   ├── app.js            # Einstiegspunkt – initialisiert alle Module
│   ├── modules/
│   │   ├── tabs.js       # Tab-Navigation (ARIA, Keyboard-Navigation)
│   │   ├── wareneingang.js
│   │   ├── mhd.js
│   │   ├── warenstand.js
│   │   ├── menu.js
│   │   ├── kalkulation.js
│   │   └── inventur.js
│   └── utils/
│       ├── format.js     # de-AT Formatierung (€, Datum)
│       ├── validate.js   # Formular-Validierung
│       └── toast.js      # Non-blocking Benachrichtigungen
└── css/
    ├── variables.css     # CSS Custom Properties (Dark-Mode-fähig)
    ├── base.css          # Basis-Styles, Komponenten
    └── layout.css        # Header, Tabs, Cards, Toast
```

## Optimierungen gegenüber Original

### Architektur
- **Monolith aufgetrennt**: 1 HTML-Datei → modulare ES-Module-Struktur
- **Single Source of Truth**: Zentraler Store statt statischer Mock-Daten in jedem Tab
- **Event-driven**: `CustomEvent`-basierte Kommunikation zwischen Modulen (keine direkte Kopplung)
- **localStorage-Persistenz**: Daten bleiben über Session-Reload erhalten

### Funktionalität
- **Echter FEFO-Algorithmus**: Chargen werden nach MHD sortiert – älteste zuerst
- **Dynamische MHD-Berechnung**: Status wird ab `new Date()` berechnet, nicht hardcodiert
- **Reale Datenverknüpfung**: Wareneingang → Warenstand → Menüvorschlag → Kalkulation (echte Pipeline)
- **Chargenmanagement**: Jede Lieferung als eigene Charge mit ID; mehrere Chargen pro Artikel möglich
- **Validierung**: Formular-Validierung mit Inline-Fehlermeldungen statt `alert()`

### UX / Accessibility
- **ARIA-Attribute**: `role="tab"`, `aria-selected`, `role="tabpanel"`, `hidden`
- **Keyboard-Navigation**: Pfeiltasten in Tab-Nav
- **Toast-Notifications**: Non-blocking, screen-reader-kompatibel
- **Skeleton-Loading**: Platzhalter-Animationen beim initialen Laden
- **Event-Delegation**: Kein Memory-Leak durch zu viele Event-Listener

### Code-Qualität
- **Kein globales `event`**: `switchTab(tabName)` nutzte `event.target` – jetzt sauber gebunden
- **Keine `alert()`/`confirm()`**: Ersetzt durch Toast-System
- **Konsistentes Sub-Tab-System**: Kalkulations-Sub-Tabs nutzen dasselbe Pattern wie Haupt-Tabs
- **Formatierung lokalisiert**: `Intl.NumberFormat('de-AT')` für €, Datum, Zahlen

## Starten

Kein Build-Schritt nötig – einfach `index.html` in einem Browser öffnen (ES Modules benötigen einen HTTP-Server):

```bash
npx serve .
# oder
python3 -m http.server 8080
```

## Bekannte Risiken (Fallstricke-Tab)

Siehe [Tab ⚠️ Fallstricke](index.html) für die vollständige Risiko-Matrix mit 12 identifizierten Problemfeldern und Lösungsansätzen.
