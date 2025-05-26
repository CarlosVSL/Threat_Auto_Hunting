#!/usr/bin/env python3
"""
cve_feed.py: RSS scraper for recent CVEs from the NVD (National Vulnerability Database).
Fetches the NVD RSS feed and writes parsed entries to a timestamped JSON file.
"""
import os
import json
import logging
from datetime import datetime

import feedparser

# URL of the NVD CVE RSS feed
FEED_URL = 'https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml'
# Directory to store output JSON files
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')


def setup_logging():
    """Configure root logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )


def fetch_feed(url):
    """Fetch and parse RSS feed entries."""
    logging.info(f'Fetching CVE feed from {url}')
    feed = feedparser.parse(url)
    if feed.bozo:
        logging.error(f'Error parsing feed: {feed.bozo_exception}')
        raise feed.bozo_exception
    return feed.entries


def parse_entries(entries):
    """Extract relevant fields from feed entries."""
    parsed = []
    for entry in entries:
        cve_id = entry.get('title', '').split()[0]
        parsed.append({
            'id': entry.get('id', entry.get('link')),
            'cve': cve_id,
            'title': entry.get('title'),
            'link': entry.get('link'),
            'published': entry.get('published'),
            'summary': entry.get('summary')
        })
    return parsed


def save_to_file(data, output_dir):
    """Save parsed data to a timestamped JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    filename = f'cve_feed_{timestamp}.json'
    path = os.path.join(output_dir, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    logging.info(f'Saved {len(data)} CVE entries to {path}')
    return path


def main():
    setup_logging()
    try:
        entries = fetch_feed(FEED_URL)
        parsed = parse_entries(entries)
        save_to_file(parsed, OUTPUT_DIR)
    except Exception as e:
        logging.exception('Failed to fetch or save CVE feed')
        exit(1)


if __name__ == '__main__':
    main()
