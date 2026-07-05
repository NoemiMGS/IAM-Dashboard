"""
Modul 1: branchenweite Marktsignale (KEIN Kundenbezug).

Beobachtet generische Themen-/Ereigniskategorien über Google News RSS
(z.B. CISO-Wechsel allgemein, Sicherheitsvorfälle in der DACH-Region,
IAM/IGA-Ausschreibungen). Es wird an keiner Stelle nach einem konkreten
Unternehmensnamen gesucht, gefiltert oder dieser gespeichert.
"""
import sys
import os
import urllib.parse
import feedparser
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from common import load_existing, save_data, merge_and_trim  # noqa: E402

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "market_signals.yml")
OUTPUT_FILE = "market-signals.json"


def build_google_news_url(query):
    encoded = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=de&gl=DE&ceid=DE:de"


def collect():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    categories = config.get("signal_categories", [])
    new_items = []

    for cat in categories:
        name = cat["name"]
        query = cat["query"]
        is_critical = cat.get("critical", False)
        url = build_google_news_url(query)
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"Fehler beim Abruf für Kategorie '{name}': {e}")
            continue

        for entry in feed.entries[:8]:
            new_items.append({
                "category": name,
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "critical": is_critical,
                "module": "market_signals",
            })

    existing = load_existing(OUTPUT_FILE)
    merged = merge_and_trim(existing.get("items", []), new_items)
    save_data(OUTPUT_FILE, merged)

    critical_new = [i for i in new_items if i.get("critical")]
    print(f"Modul 1: {len(new_items)} neue Treffer, davon {len(critical_new)} kritisch.")
    return critical_new


if __name__ == "__main__":
    critical = collect()
    if critical:
        with open(os.path.join(os.path.dirname(__file__), "..", "data", ".critical_market_signals"), "w") as f:
            f.write(str(len(critical)))
