"""
Modul 3: Compliance-Updates (BSI, DSGVO-Rechtsprechung, ISO-Änderungen).
Läuft wöchentlich. Reine RSS-Aggregation, kein Scraping.
"""
import os
import sys
import feedparser
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from common import load_existing, save_data, merge_and_trim  # noqa: E402

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.yml")
OUTPUT_FILE = "compliance-updates.json"


def collect():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    new_items = []
    for feed_cfg in config.get("compliance_rss_feeds", []):
        url = feed_cfg.get("url")
        if not url:
            continue
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"Fehler beim RSS-Abruf {feed_cfg.get('name')}: {e}")
            continue
        for entry in feed.entries[:10]:
            new_items.append({
                "source": feed_cfg.get("name"),
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "critical": False,
                "module": "compliance_updates",
            })

    existing = load_existing(OUTPUT_FILE)
    merged = merge_and_trim(existing.get("items", []), new_items)
    save_data(OUTPUT_FILE, merged)
    print(f"Modul 3: {len(new_items)} neue Treffer.")


if __name__ == "__main__":
    collect()
