# ERP Gastro Software – Claude Code Guidelines

**Projekt:** Gastro ERP (Warenkreislauf-Management)
**Repository:** https://github.com/RVH3000/gastro-erp
**Letzte Aktualisierung:** 2026-02-27

---

## 🌿 Branch-Strategie für Claude Code Änderungen

### Aktiver Claude-Branch
```
claude/erp-changes
```

**Alle Claude Code Änderungen gehören auf diesen Branch — NIEMALS direkt auf `main`!**

### Workflow
```bash
# 1. Sicherstellen, dass man auf dem richtigen Branch ist
git checkout claude/erp-changes

# 2. Vor jeder Arbeit: aktuellen Stand holen
git pull origin claude/erp-changes

# 3. Änderungen committen
git add <dateien>
git commit -m "feat/fix/chore: kurze Beschreibung"

# 4. Pushen
git push origin claude/erp-changes

# 5. Pull Request auf GitHub öffnen:
#    https://github.com/RVH3000/gastro-erp/pull/new/claude/erp-changes
```

### Branch-Übersicht
| Branch | Zweck |
|--------|-------|
| `main` | Produktions-Code — nur via PR |
| `claude/erp-changes` | **Claude Code Änderungen** (dieser Branch) |
| `feature/gastro-erp-init` | Initiale Feature-Entwicklung |
| `clean-main` | Backup/Referenz |

---

## 📋 Commit-Konventionen

```
feat:     Neue Funktion
fix:      Bugfix
chore:    Wartung, Konfiguration, Tooling
docs:     Dokumentation
refactor: Code-Umstrukturierung ohne Funktionsänderung
test:     Tests hinzufügen oder korrigieren
```

**Beispiele:**
```bash
git commit -m "feat: Wareneingang-Modul mit Lieferanten-Validierung"
git commit -m "fix: Kassenbericht Datumsfilter korrigiert"
git commit -m "chore: Docker-Compose für lokale Entwicklung aktualisiert"
```

---

## 🏗️ Projekt-Struktur

```
ERP Gastro Sotware/
├── backend/        # Python Backend (FastAPI / Django)
├── deploy/         # Deployment-Konfigurationen
├── docs/           # Dokumentation
├── ops/            # DevOps / Infrastruktur
├── e2e/            # End-to-End Tests (Playwright)
├── monitoring/     # Monitoring-Stack
├── .github/        # GitHub Actions, PR-Templates
└── CLAUDE.md       # Diese Datei
```

---

## ⚠️ Wichtige Regeln

1. **Niemals direkt auf `main` committen** — immer über `claude/erp-changes`
2. **Keine Secrets in Git** — API-Keys, Passwörter nur in `.env` (ist in `.gitignore`)
3. **Vor großen Änderungen:** `git pull` ausführen um Konflikte zu vermeiden
4. **Pull Request öffnen** wenn Änderungen für `main` bereit sind

---

## 🚀 Lokale Entwicklung

```bash
# Branch wechseln
git checkout claude/erp-changes

# Status prüfen
git status
git log --oneline -10

# Branches anzeigen
git branch -a
```

---

## 🔗 Nützliche Links

- **Repository:** https://github.com/RVH3000/gastro-erp
- **Branch direkt:** https://github.com/RVH3000/gastro-erp/tree/claude/erp-changes
- **Neuen PR erstellen:** https://github.com/RVH3000/gastro-erp/pull/new/claude/erp-changes
