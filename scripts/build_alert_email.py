"""
Sammelt alle kritischen Treffer des heutigen Laufs (Flag-Dateien aus
collectors/*.py) und baut daraus einen HTML-Mail-Body. Schreibt den Body
nach data/alert_email_body.html und setzt in GITHUB_OUTPUT ein Flag
'has_critical', damit der Workflow den Mail-Versand-Schritt bedingt
ausführen kann.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FLAG_FILES = {
    "market-signals.json": ".critical_market_signals",
    "vendor-news.json": ".critical_vendor_news",
}


def load_items(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("items", [])


def main():
    has_critical = False
    sections = []

    for data_file, flag_file in FLAG_FILES.items():
        flag_path = os.path.join(DATA_DIR, flag_file)
        if not os.path.exists(flag_path):
            continue
        has_critical = True
        items = [i for i in load_items(data_file) if i.get("critical")]
        rows = "".join(
            f"<li><a href='{i.get('link', '#')}'>{i.get('title', 'Ohne Titel')}</a>"
            f"{' — ' + i['category'] if i.get('category') else ''}</li>"
            for i in items[:10]
        )
        sections.append(f"<h3>{data_file.replace('.json', '')}</h3><ul>{rows}</ul>")
        os.remove(flag_path)  # Flag verbrauchen, damit nächster Lauf wieder frisch prüft

    body = (
        "<h2>IAM Intelligence Dashboard - kritische Treffer</h2>"
        + "".join(sections)
        + "<p>Vollständiges Dashboard: siehe GitHub Pages Link im Repo.</p>"
    )

    with open(os.path.join(DATA_DIR, "alert_email_body.html"), "w", encoding="utf-8") as f:
        f.write(body)

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"has_critical={'true' if has_critical else 'false'}\n")

    print(f"has_critical={has_critical}")


if __name__ == "__main__":
    main()
