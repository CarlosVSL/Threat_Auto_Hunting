#!/usr/bin/env python3
"""
enrich_iocs.py: Enrich logs in Elasticsearch with IOC data by installing an ingest pipeline.
Reads IOC JSON files produced by osint/feeds and creates or updates an Elasticsearch ingest pipeline
that tags events matching known malicious IPs, domains, or file hashes.
"""
import os
import glob
import json
import logging

from elasticsearch import Elasticsearch, exceptions as es_exceptions

# Configuration
ES_HOST = os.getenv('ELASTICSEARCH_HOST', 'http://elasticsearch:9200')
ES_PIPELINE_ID = 'ioc_enrichment'
# Directory where osint feed JSON files are stored
IOC_FEED_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'feeds', 'output')
)
IOC_FILE_PATTERN = '*.json'


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )


def load_iocs():
    """Load IOC values from all JSON feed files."""
    ips = set()
    domains = set()
    hashes = set()

    feed_path = os.path.join(IOC_FEED_DIR, IOC_FILE_PATTERN)
    for feed_file in glob.glob(feed_path):
        logging.info(f'Loading IOCs from {feed_file}')
        try:
            data = json.load(open(feed_file))
        except Exception as e:
            logging.warning(f'Could not load {feed_file}: {e}')
            continue
        for item in data:
            # IP IOC
            if 'ip' in item:
                ips.add(item['ip'])
            # Domain IOC
            if 'domain' in item:
                domains.add(item['domain'])
            # File hash IOC (md5, sha1, sha256)
            for key in ('md5', 'sha1', 'sha256', 'hash'):
                if key in item:
                    hashes.add(item[key])

    logging.info(f'Total IOCs loaded: {len(ips)} IPs, {len(domains)} domains, {len(hashes)} hashes')
    return list(ips), list(domains), list(hashes)


def build_pipeline(ips, domains, hashes):
    """Construct the ingest pipeline definition for IOC enrichment."""
    processors = []

    # Script processor to tag matching IPs
    ip_script = {
        'script': {
            'lang': 'painless',
            'source': (
                "if (ctx.source != null && params.ips.contains(ctx.source.ip)) {"
                "ctx.tags = ctx.tags == null ? [] : ctx.tags;"
                "ctx.tags.add('ioc.ip');"
                "ctx.ioc = ctx.ioc == null ? [:] : ctx.ioc;"
                "ctx.ioc.ip = ctx.source.ip;"
                "}"),
            'params': {'ips': ips}
        }
    }
    processors.append(ip_script)

    # Script processor to tag matching destination IPs
    dest_ip_script = {
        'script': {
            'lang': 'painless',
            'source': (
                "if (ctx.destination != null && params.ips.contains(ctx.destination.ip)) {"
                "ctx.tags = ctx.tags == null ? [] : ctx.tags;"
                "ctx.tags.add('ioc.dest_ip');"
                "ctx.ioc = ctx.ioc == null ? [:] : ctx.ioc;"
                "ctx.ioc.dest_ip = ctx.destination.ip;"
                "}"),
            'params': {'ips': ips}
        }
    }
    processors.append(dest_ip_script)

    # Script processor to tag matching domains (if HTTP request exists)
    if domains:
        domain_script = {
            'script': {
                'lang': 'painless',
                'source': (
                    "if (ctx.http != null && ctx.http.request != null && params.domains.contains(ctx.http.request.domain)) {"
                    "ctx.tags = ctx.tags == null ? [] : ctx.tags;"
                    "ctx.tags.add('ioc.domain');"
                    "ctx.ioc = ctx.ioc == null ? [:] : ctx.ioc;"
                    "ctx.ioc.domain = ctx.http.request.domain;"
                    "}"),
                'params': {'domains': domains}
            }
        }
        processors.append(domain_script)

    # Script processor to tag matching file hashes
    if hashes:
        hash_script = {
            'script': {
                'lang': 'painless',
                'source': (
                    "for (h in params.hashes) {"
                    " if (ctx.file != null && ctx.file.hash != null && ctx.file.hash == h) {"
                    " ctx.tags = ctx.tags == null ? [] : ctx.tags;"
                    " ctx.tags.add('ioc.hash');"
                    " ctx.ioc = ctx.ioc == null ? [:] : ctx.ioc;"
                    " ctx.ioc.hash = h;"
                    " }"
                    "}"),
                'params': {'hashes': hashes}
            }
        }
        processors.append(hash_script)

    pipeline = {
        'description': 'IOC enrichment pipeline',
        'processors': processors,
        'on_failure': [
            {'set': {'field': 'error.pipeline', 'value': '{{ _ingest.on_failure_message }}'}}
        ]
    }
    return pipeline


def install_pipeline(es, pipeline_body):
    """Create or update the ingest pipeline in Elasticsearch."""
    try:
        es.ingest.put_pipeline(id=ES_PIPELINE_ID, body=pipeline_body)
        logging.info(f'Ingest pipeline "{ES_PIPELINE_ID}" installed successfully')
    except es_exceptions.ElasticsearchException as e:
        logging.error(f'Failed to install ingest pipeline: {e}')
        raise


def main():
    setup_logging()

    # Load IOCs
    ips, domains, hashes = load_iocs()
    if not any([ips, domains, hashes]):
        logging.warning('No IOCs found; skipping pipeline installation.')
        return

    # Build pipeline definition
    pipeline = build_pipeline(ips, domains, hashes)

    # Connect to Elasticsearch and install pipeline
    es = Elasticsearch([ES_HOST])
    install_pipeline(es, pipeline)


if __name__ == '__main__':
    main()
