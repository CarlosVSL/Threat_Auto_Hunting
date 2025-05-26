#!/usr/bin/env python3
"""
block_ip.py: Block a malicious IP by calling the configured firewall/EDR API.
Uses API endpoint and key from playbooks/config.yml to submit a block request.
"""
import os
import sys
import yaml
import logging
import argparse

import requests

# Attempt to load shared logging setup
try:
    from orchestrator.utils import setup_logging
except ImportError:
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%SZ'
        )

# Path to playbook configuration\CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yml')


def load_config(path: str) -> dict:
    """Load YAML configuration for firewall settings."""
    try:
        with open(path) as f:
            cfg = yaml.safe_load(f)
        return cfg
    except Exception as e:
        logging.error(f"Failed to load config file {path}: {e}")
        sys.exit(1)


def block_ip(ip: str, api_url: str, api_key: str) -> None:
    """Call the firewall API to block the given IP."""
    url = api_url.rstrip('/') + '/block'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    payload = {'ip': ip}

    logging.info(f"Sending block request for IP {ip} to {url}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info(f"IP {ip} blocked successfully. API response: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error blocking IP {ip}: {e}")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Block an IP address via firewall API.")
    parser.add_argument('ip', help='IP address to block')
    return parser.parse_args()


def main():
    setup_logging()
    args = parse_args()

    cfg = load_config(CONFIG_PATH)
    fw_cfg = cfg.get('firewall', {})
    api_url = fw_cfg.get('api_url')
    api_key = fw_cfg.get('api_key')
    if not api_url or not api_key:
        logging.error('firewall.api_url or firewall.api_key not set in config.yml')
        sys.exit(1)

    block_ip(args.ip, api_url, api_key)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# Block IP playbook
