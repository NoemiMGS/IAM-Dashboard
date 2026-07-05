# IAM Intelligence Dashboard

Eigenständiges Repository (unabhängig vom Musiker-Dashboard) zur automatisierten
Beobachtung von Trigger-Events bei Zielkunden, Vendor-News/CVEs, Compliance-Updates
und einer Content-Draft-Pipeline für Marketing.

- **Täglich, 07:00 Uhr (Europe/Berlin):** Modul 1 (Markt-Signale, branchenweit) + Modul 2 (Vendor-News/CVE)
- **Wöchentlich, montags 07:00 Uhr (Europe/Berlin):** Modul 3 (Compliance) + Modul 4 (Content-Drafts)
- **Kritische Treffer** werden zusätzlich per E-Mail an `noemi.schwarztrauber@outlook.com` gesendet.
- **Kein Kundenbezug:** Modul 1 beobachtet ausschließlich branchenweite, generische Themenkategorien (z.B. CISO-Wechsel allgemein, Sicherheitsvorfälle in der DACH-Region). Es wird nirgends nach einem konkreten Unternehmensnamen gesucht, gefiltert oder gespeichert.

## 1. Repo einrichten

```bash
# Im entpackten Ordner:
git init
git add .
git commit -m "Initial commit: IAM Intelligence Dashboard"
gh repo create iam-intelligence-dashboard --private --source=. --push
# oder ohne gh-CLI: Repo auf github.com neu anlegen und dann
git remote add origin https://github.com/<dein-user>/iam-intelligence-dashboard.git
git branch -M main
git push -u origin main
```

## 2. GitHub Pages aktivieren

Repo-Settings → Pages → Source: `main` Branch, Ordner `/docs`. Danach ist das
Dashboard unter `https://<dein-user>.github.io/iam-intelligence-dashboard/` erreichbar.

## 3. Secrets hinterlegen (Repo-Settings → Secrets and variables → Actions)

| Secret | Zweck | Beispielwert |
|---|---|---|
| `MAIL_SERVER` | SMTP-Server für Alert-Mails | `smtp.office365.com` |
| `MAIL_PORT` | SMTP-Port | `587` |
| `MAIL_USERNAME` | SMTP-Login | dein Absender-Postfach |
| `MAIL_PASSWORD` | SMTP-Passwort / App-Passwort | — |
| `ANTHROPIC_API_KEY` | Nur für Modul 4 (Content-Drafts), optional | — |

**Hinweis zu Outlook/Microsoft 365 als Absender:** Microsoft hat Basic-Auth für
SMTP bei vielen Tenants deaktiviert. Falls `smtp.office365.com` mit Benutzername/
Passwort nicht funktioniert, brauchst du entweder ein App-Passwort (bei aktivierter
MFA) oder einen alternativen Versand-Dienst (z. B. Gmail mit App-Passwort, oder ein
Transaktions-Mail-Dienst wie Resend/SendGrid mit kostenlosem Kontingent). Der
Workflow selbst (`.github/workflows/daily.yml`) muss dann nur die Secrets anpassen,
nicht den Code.

## 4. Signal-Kategorien & Quellen pflegen

`config/market_signals.yml` — hier stehen die branchenweiten Themenkategorien
für Modul 1 (z.B. CISO-Wechsel, Sicherheitsvorfälle, IAM-Ausschreibungen).
Es gibt bewusst keine Kundenliste und keine Möglichkeit, nach einem konkreten
Unternehmensnamen zu filtern — neue Kategorien einfach als weiteren Eintrag
unter `signal_categories` ergänzen. `config/sources.yml` enthält die RSS-Quellen
für Modul 2/3; Einträge mit `status: "PRÜFEN"` bitte einmal im Browser
verifizieren, bevor der erste produktive Lauf stattfindet (Hersteller-Portale
ändern Feed-URLs gelegentlich oder bieten teils kein öffentliches RSS an).

## 5. Zeitlogik (07:00 Uhr, DST-sicher)

GitHub Actions cron läuft immer in UTC. Da Regensburg zwischen UTC+1 (Winter)
und UTC+2 (Sommer) wechselt, sind in den Workflows zwei Cron-Trigger hinterlegt
(05:00 und 06:00 UTC). Ein Zeit-Check-Schritt prüft die tatsächliche lokale
Stunde in `Europe/Berlin` und lässt nur den passenden Lauf wirklich etwas tun —
der andere bricht sofort ohne Nebenwirkungen ab. Damit läuft es unabhängig von
der Jahreszeit korrekt um 07:00 Uhr.

## 6. Manuell testen

Jeder Workflow hat `workflow_dispatch` aktiviert — in GitHub unter "Actions" den
gewünschten Workflow auswählen und "Run workflow" klicken, um sofort zu testen,
ohne auf den Cron zu warten.

## 7. Struktur

```
collectors/           Python-Skripte pro Modul (RSS/API, kein Scraping)
config/                Zielkunden, Keywords, Quellen-URLs
data/                  JSON-Ergebnisse je Modul (wird von Actions committed)
docs/                  GitHub Pages Dashboard (index.html/app.js/style.css)
scripts/               E-Mail-Alert-Aufbereitung
.github/workflows/     daily.yml (Modul 1+2), weekly.yml (Modul 3+4)
```

## 8. Autonomielevel (Bezug zum Identity-First-Practice-Framework)

| Modul | Level | Freigabe |
|---|---|---|
| Modul 1 (Markt-Signale, branchenweit) | L4 | Reine Aggregation, kein Kundenbezug, autonom |
| Modul 2 (Vendor-News/CVE) | L4 | Reine Aggregation, autonom |
| Modul 3 (Compliance) | L4 | Reine Aggregation, autonom |
| Modul 4 (Content-Drafts) | L1–L2 | Nie automatisch veröffentlicht |
