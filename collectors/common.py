"""Gemeinsame Hilfsfunktionen für alle Collector-Skripte."""
import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_existing(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"items": [], "last_updated": None}
    return {"items": [], "last_updated": None}


def save_data(filename, items):
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(DATA_DIR, exist_ok=True)
    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "items": items,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


def dedupe_by_link(items):
    seen = set()
    result = []
    for item in items:
        link = item.get("link")
        if link and link in seen:
            continue
        if link:
            seen.add(link)
        result.append(item)
    return result


def merge_and_trim(existing_items, new_items, max_items=200):
    """Neue Items vorne anfügen, nach Link deduplizieren, auf max_items begrenzen."""
    merged = dedupe_by_link(new_items + existing_items)
    return merged[:max_items]
