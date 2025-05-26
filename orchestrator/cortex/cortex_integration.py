#!/usr/bin/env python3
"""
cortex_integration.py: Integration with Cortex for running analyzers and retrieving results.

Uses environment variables for configuration:
  CORTEX_URL         - Base URL of Cortex server (e.g., https://cortex.example.com)
  CORTEX_API_KEY     - API key for Cortex
  CORTEX_VERIFY_SSL  - 'True' or 'False' to verify SSL certificates

Provides CortexClient class with methods to:
  - list available analyzers
  - run an analyzer against an indicator
  - check job status and retrieve results

Example usage:
  client = CortexClient()
  analyzers = client.list_analyzers()
  job = client.run_analyzer('MISPGeneric', indicator={'value': '1.2.3.4', 'type': 'ip'})
  result = client.get_job_result(job['id'])
"""
import os
import logging
import requests
import time
from typing import Any, Dict, List, Optional

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

# Cortex configuration from environment
CORTEX_URL = os.getenv('CORTEX_URL')
CORTEX_API_KEY = os.getenv('CORTEX_API_KEY')
CORTEX_VERIFY = os.getenv('CORTEX_VERIFY_SSL', 'True').lower() in ('true', '1', 'yes')


class CortexClient:
    """Client for interacting with Atlas Cortex server."""

    def __init__(self):
        setup_logging()
        if not CORTEX_URL or not CORTEX_API_KEY:
            logging.error('CORTEX_URL and CORTEX_API_KEY must be set as environment variables')
            raise ValueError('Missing Cortex configuration')
        self.base_url = CORTEX_URL.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {CORTEX_API_KEY}',
            'Content-Type': 'application/json'
        }
        logging.info(f'Initialized Cortex client for {self.base_url}')

    def list_analyzers(self) -> List[Dict[str, Any]]:
        """Retrieve list of available analyzers from Cortex."""
        url = f'{self.base_url}/api/analyzer'
        resp = requests.get(url, headers=self.headers, verify=CORTEX_VERIFY)
        resp.raise_for_status()
        data = resp.json()
        return data.get('data', [])

    def run_analyzer(
        self,
        analyzer: str,
        indicator: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a specified analyzer against an indicator.

        :param analyzer: Name of the analyzer (e.g., 'MISPGeneric')
        :param indicator: Indicator payload, e.g., {'value': '1.2.3.4', 'type': 'ip'}
        :param params: Optional analyzer-specific parameters
        :return: Job object containing job 'id'
        """
        url = f'{self.base_url}/api/analyzer/{analyzer}/run'
        payload = {
            'dataType': indicator.get('type'),
            'data': indicator.get('value')
        }
        if params:
            payload['params'] = params
        logging.info(f'Running analyzer {analyzer} on {indicator}')
        resp = requests.post(url, json=payload, headers=self.headers, verify=CORTEX_VERIFY)
        resp.raise_for_status()
        return resp.json().get('data', {})

    def get_job_result(self, job_id: str, wait: bool = True, timeout: int = 300) -> Dict[str, Any]:
        """Retrieve results of a previously submitted job.

        :param job_id: Job identifier returned by run_analyzer
        :param wait: If True, poll until job is done or timeout
        :param timeout: Max seconds to wait
        :return: Result data
        """
        url = f'{self.base_url}/api/job/{job_id}'
        start = time.time()
        while True:
            resp = requests.get(url, headers=self.headers, verify=CORTEX_VERIFY)
            resp.raise_for_status()
            data = resp.json().get('data', {})
            status = data.get('status')
            if not wait or status in ('Done', 'Failed'):
                break
            if time.time() - start > timeout:
                logging.error(f'Timeout waiting for job {job_id}')
                break
            time.sleep(5)
        return data


if __name__ == '__main__':
    setup_logging()
    client = CortexClient()
    analyzers = client.list_analyzers()
    logging.info(f'Available analyzers: {[a.get("name") for a in analyzers]}')
    # Example: run and get result for an IP indicator
    job = client.run_analyzer('MISPGeneric', {'value': '1.2.3.4', 'type': 'ip'})
    result = client.get_job_result(job.get('id'))
    logging.info(f'Job result: {result}')
#!/usr/bin/env python3
# Cortex executor
