#!/usr/bin/env python3
"""
misp_client.py: MISP API integration module using PyMISP.
Provides helper functions to fetch events, retrieve IOCs, and push indicators to a MISP instance.
"""
import os
import logging
from typing import List, Optional, Dict, Any

from pymisp import ExpandedPyMISP, MISPEvent, MISPAttribute

# Configuration from environment variables
MISP_URL = os.getenv('MISP_URL')  # e.g., https://misp.example.com
MISP_KEY = os.getenv('MISP_KEY')  # your API key
MISP_VERIFY = os.getenv('MISP_VERIFY', 'False').lower() in ('true', '1', 'yes')


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )


class MISPClient:
    """Client for interacting with MISP via REST API."""

    def __init__(self, url: str = MISP_URL, key: str = MISP_KEY, verify_ssl: bool = MISP_VERIFY):
        if not url or not key:
            raise ValueError("MISP_URL and MISP_KEY environment variables must be set")
        self.url = url.rstrip('/')
        self.key = key
        self.verify_ssl = verify_ssl
        self.client = ExpandedPyMISP(self.url, self.key, ssl=self.verify_ssl)
        setup_logging()
        logging.info(f"Initialized MISP client for {self.url}")

    def get_events(self, last: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch events from MISP. If 'last' (in seconds) is provided, returns events created/modified in that timeframe.
        """
        params: Dict[str, Any] = {"returnFormat": "json"}
        if last:
            params['last'] = last
            logging.info(f"Fetching events from last {last} seconds")
        else:
            logging.info("Fetching all events")
        result = self.client.search('events', **params)
        events = result.get('response', [])
        logging.info(f"Retrieved {len(events)} events from MISP")
        return events

    def get_iocs_from_event(self, event_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all attributes (IOCs) from a specific event by ID.
        """
        logging.info(f"Fetching attributes for event {event_id}")
        event = self.client.get_event(event_id)
        misp_event = MISPEvent(event)
        attributes = []
        for attr in misp_event.attributes:
            attributes.append({
                'type': attr.type,
                'value': attr.value,
                'uuid': attr.uuid,
                'comment': attr.comment
            })
        logging.info(f"Event {event_id} has {len(attributes)} attributes")
        return attributes

    def add_ioc(self, event_id: int, ioc_type: str, value: str, comment: Optional[str] = None) -> Dict[str, Any]:  
        """
        Add a new IOC (attribute) to an existing event.
        """
        logging.info(f"Adding IOC to event {event_id}: {ioc_type}={value}")
        attribute = self.client.add_named_attribute(
            event_id,
            ioc_type,
            value,
            comment=comment or ''
        )
        return attribute

    def create_event(self, info: str, distribution: int = 0, threat_level: int = 3, analysis: int = 0) -> Dict[str, Any]:
        """
        Create a new MISP event with basic metadata. Returns the created event.
        """
        logging.info(f"Creating new event: {info}")
        event = self.client.new_event(
            info,
            distribution=distribution,
            threat_level_id=threat_level,
            analysis=analysis
        )
        return event


if __name__ == '__main__':
    setup_logging()
    # Example usage
    client = MISPClient()
    events = client.get_events(last=86400)
    if events:
        first_event_id = events[0]['Event']['id']
        iocs = client.get_iocs_from_event(first_event_id)
        logging.info(f"First event {first_event_id} IOCs: {iocs}")
