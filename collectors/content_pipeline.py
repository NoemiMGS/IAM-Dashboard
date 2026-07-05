"""
Modul 4: Content-Pipeline (Fachartikel-/LinkedIn-Post-Entwürfe).

Nimmt die Top-Themen aus Modul 2 & 3 der letzten Woche und lässt über die
Anthropic API 2-3 Entwurfsvarianten generieren. Es wird NICHTS automatisch
veröffentlicht - alles landet nur als Draft in data/content-drafts.json und
wird im Dashboard mit Status "Zur Freigabe" angezeigt (Autonomielevel L1-L2).

Benötigt Secret ANTHROPIC_API_KEY. Ist das Secret nicht gesetzt, wird der
Schritt übersprungen (kein Fehler, damit der restliche Workflow durchläuft).
"""
import os
import sys
import json
import requests

sys.path.insert(0, os.path.dirname(__file__))
from common import load_existing, save_data  # noqa: E402

OUTPUT_FILE = "content-drafts.json"
API_URL = "https://api.anthropic.com/v1/messages"


def top_topics(max_topics=5):
    topics = []
    for filename in ("vendor-news.json", "compliance-updates.json"):
        data = load_existing(filename)
        for item in data.get("items", [])[:10]:
            topics.append(item.get("title", ""))
    return [t for t in topics if t][:max_topics]


def generate_draft(api_key, topic):
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    prompt = (
        "Du hilfst einer IAM-Beratung (Identity & Access Management, Fokus "
        "Zero Trust, PAM, NIS2) mit Content-Entwürfen.\n\n"
        f"Thema: {topic}\n\n"
        "Erstelle:\n"
        "1) Einen kurzen LinkedIn-Post-Entwurf (max. 150 Wörter, Deutsch)\n"
        "2) Drei Stichpunkte für einen möglichen Fachartikel zu diesem Thema\n\n"
        "Antworte NUR mit einem JSON-Objekt: "
        '{"linkedin_post": "...", "article_bullets": ["...", "...", "..."]}'
    )
    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 600,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
    cleaned = text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


def collect():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Modul 4: ANTHROPIC_API_KEY nicht gesetzt - Content-Pipeline wird übersprungen.")
        return

    topics = top_topics()
    if not topics:
        print("Modul 4: keine Themen aus Modul 2/3 gefunden - nichts zu generieren.")
        return

    drafts = []
    for topic in topics:
        try:
            draft = generate_draft(api_key, topic)
            drafts.append({
                "topic": topic,
                "linkedin_post": draft.get("linkedin_post", ""),
                "article_bullets": draft.get("article_bullets", []),
                "status": "Zur Freigabe",
                "module": "content_pipeline",
            })
        except Exception as e:
            print(f"Fehler bei Draft-Generierung für '{topic}': {e}")

    existing = load_existing(OUTPUT_FILE)
    merged = (drafts + existing.get("items", []))[:50]
    save_data(OUTPUT_FILE, merged)
    print(f"Modul 4: {len(drafts)} neue Entwürfe erstellt (Status: Zur Freigabe).")


if __name__ == "__main__":
    collect()
