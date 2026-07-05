"""
Modul 2: Vendor-News & CVEs (One Identity, SailPoint, CyberArk, Entra ID)
sowie NIS2/DORA-relevante RSS-Quellen.

CVE-Daten kommen über die öffentliche NVD-API (kein Key für moderates
Abfragevolumen nötig, aber Rate-Limits beachten -> kleine Pause zwischen
Requests). RSS-Quellen kommen aus config/sources.yml.
"""
import os
import sys
import time
import requests
import feedparser
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from common import load_existing, save_data, merge_and_trim  # noqa: E402

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.yml")
OUTPUT_FILE = "vendor-news.json"
NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def fetch_cves(keyword, critical_threshold):
    params = {"keywordSearch": keyword, "resultsPerPage": 10}
    try:
        resp = requests.get(NVD_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Fehler bei CVE-Abfrage für '{keyword}': {e}")
        return []

    items = []
    for vuln in data.get("vulnerabilities", []):
        cve = vuln.get("cve", {})
        cve_id = cve.get("id", "unknown")
        descriptions = cve.get("descriptions", [])
        desc_text = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")

        metrics = cve.get("metrics", {})
        score = None
        for metric_key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            if metric_key in metrics and metrics[metric_key]:
                score = metrics[metric_key][0].get("cvssData", {}).get("baseScore")
                break

        items.append({
            "vendor_keyword": keyword,
            "title": f"{cve_id}: {desc_text[:180]}",
            "link": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
            "cvss_score": score,
            "critical": bool(score and score >= critical_threshold),
            "module": "vendor_news",
            "source": "NVD",
        })
    return items


def fetch_rss(feeds):
    items = []
    for feed_cfg in feeds:
        url = feed_cfg.get("url")
        if not url:
            continue
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"Fehler beim RSS-Abruf {feed_cfg.get('name')}: {e}")
            continue
        for entry in feed.entries[:5]:
            items.append({
                "vendor_keyword": feed_cfg.get("name"),
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "critical": False,
                "module": "vendor_news",
                "source": feed_cfg.get("name"),
            })
    return items


def collect():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    threshold = config.get("cve_critical_cvss_threshold", 7.0)
    new_items = []

    for keyword in config.get("cve_vendor_keywords", []):
        new_items.extend(fetch_cves(keyword, threshold))
        time.sleep(6)  # NVD Rate-Limit ohne API-Key: ~5 Requests / 30s

    new_items.extend(fetch_rss(config.get("vendor_rss_feeds", [])))

    existing = load_existing(OUTPUT_FILE)
    merged = merge_and_trim(existing.get("items", []), new_items)
    save_data(OUTPUT_FILE, merged)

    critical_new = [i for i in new_items if i.get("critical")]
    print(f"Modul 2: {len(new_items)} neue Treffer, davon {len(critical_new)} kritisch (CVSS >= {threshold}).")
    return critical_new


if __name__ == "__main__":
    critical = collect()
    if critical:
        with open(os.path.join(os.path.dirname(__file__), "..", "data", ".critical_vendor_news"), "w") as f:
            f.write(str(len(critical)))
