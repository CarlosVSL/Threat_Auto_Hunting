#!/usr/bin/env python3
"""
mib_crawl.py: Custom OSINT & MISP crawler.
- Fetches recent events from a MISP instance via REST API.
- Optionally, crawls additional OSINT RSS/JSON feeds for IOCs.
- Writes combined IOC list to a timestamped JSON file.
"""
import os
import json
import logging
from datetime import datetime, timedelta

import requests
from feedparser import parse as parse_feed

# Output directory for JSON files\ OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
# Environment variables to configure MISP connection
MISP_URL = os.getenv('MISP_URL')  # e.g. https://misp.example.com
MISP_KEY = os.getenv('MISP_KEY')  # your API key
# OSINT feeds (add RSS/JSON URLs here)
OSINT_FEEDS = [
    # 'https://example.com/iocs-feed.json',
    # 'https://some-rss-feed.com/osint.xml',
]
# Time window for MISP events (in hours)
MISP_LOOKBACK_HOURS = int(os.getenv('MISP_LOOKBACK_HOURS', '24'))


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )

def fetch_misp_events():
    """Fetch events from MISP in the last N hours."""
    if not MISP_URL or not MISP_KEY:
        raise ValueError('MISP_URL and MISP_KEY environment variables must be set')
    since = (datetime.utcnow() - timedelta(hours=MISP_LOOKBACK_HOURS)).isoformat()
    logging.info(f'Fetching MISP events since {since} UTC')
    url = f"{MISP_URL.rstrip('/')}/events/restSearch"
    headers = {
        'Authorization': MISP_KEY,
        'Accept': 'application/json'
    }
    params = {
        'returnFormat': 'json',
        'last': MISP_LOOKBACK_HOURS * 3600
    }
    resp = requests.get(url, headers=headers, params=params, verify=False)
    resp.raise_for_status()
    data = resp.json()
    events = data.get('response', [])
    logging.info(f'Retrieved {len(events)} events from MISP')
    return events


def fetch_osint_feeds():
    """Fetch IOCs from configured OSINT feeds."""
    iocs = []
    for feed_url in OSINT_FEEDS:
        logging.info(f'Fetching OSINT feed {feed_url}')
        feed = parse_feed(feed_url)
        for entry in feed.entries:
            iocs.append({
                'title': entry.get('title'),
                'link': entry.get('link'),
                'published': entry.get('published'),
                'summary': entry.get('summary')
            })
    logging.info(f'Collected {len(iocs)} items from OSINT feeds')
    return iocs


def save_to_file(data, prefix):
    """Save data to a timestamped JSON file in OUTPUT_DIR."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    filename = f'{prefix}_{timestamp}.json'
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    logging.info(f'Saved {len(data)} items to {path}')
    return path


def main():
    setup_logging()
    all_iocs = []
    try:
        misp_events = fetch_misp_events()
        all_iocs.extend(misp_events)
    except Exception as e:
        logging.exception('Error fetching MISP events')
    try:
        osint_items = fetch_osint_feeds()
        all_iocs.extend(osint_items)
    except Exception as e:
        logging.exception('Error fetching OSINT feeds')
    if all_iocs:
        save_to_file(all_iocs, 'mib_crawl')
    else:
        logging.warning('No items collected; nothing to save.')


if __name__ == '__main__':
    main()
