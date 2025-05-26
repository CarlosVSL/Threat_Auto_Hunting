#!/usr/bin/env python3
"""
utils.py: Shared utility functions for the orchestrator module.
Provides logging setup and common helpers.
"""
import logging

def setup_logging(level: str = "INFO"):
    """
    Configure root logger with timestamped messages.

    :param level: Logging level as string (e.g., 'DEBUG', 'INFO').
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )


def load_yaml_config(path: str) -> dict:
    """
    Load a YAML configuration file and return its contents as a dict.

    :param path: Path to the YAML file.
    """
    try:
        import yaml
    except ImportError:
        logging.error('PyYAML is required to load YAML configs')
        raise
    with open(path, 'r') as f:
        return yaml.safe_load(f)
# Shared helper functions
