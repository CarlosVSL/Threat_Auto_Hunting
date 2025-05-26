#!/usr/bin/env python3
"""
isolate_endpoint.py: Isolate an AWS EC2 instance by modifying its security groups to a restrictive group.
Uses AWS credentials and target security group ID from playbooks/config.yml.
"""
import os
import sys
import yaml
import logging
import argparse

import boto3
from botocore.exceptions import ClientError

# Load shared utilities (e.g., for common logging setup)
try:
    from orchestrator.utils import setup_logging
except ImportError:
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%SZ'
        )

# Path to playbook configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yml')


def load_config(path: str) -> dict:
    """Load YAML configuration for AWS and playbook settings."""
    with open(path) as f:
        cfg = yaml.safe_load(f)
    return cfg


def isolate_instance(instance_id: str, restrictive_sg: str, ec2_client) -> None:
    """Modify the security groups of the instance to the restrictive security group."""
    try:
        # Retrieve current network interfaces
        resp = ec2_client.describe_instances(InstanceIds=[instance_id])
        reservations = resp.get('Reservations', [])
        if not reservations:
            logging.error(f"Instance {instance_id} not found")
            sys.exit(1)
        instance = reservations[0]['Instances'][0]
        interfaces = instance.get('NetworkInterfaces', [])
        if not interfaces:
            logging.error(f"No network interfaces found on {instance_id}")
            sys.exit(1)

        for iface in interfaces:
            eni_id = iface['NetworkInterfaceId']
            logging.info(f"Updating ENI {eni_id} security groups to [{restrictive_sg}]")
            ec2_client.modify_network_interface_attribute(
                NetworkInterfaceId=eni_id,
                Groups=[restrictive_sg]
            )
        logging.info(f"Instance {instance_id} isolated successfully.")
    except ClientError as e:
        logging.error(f"Error isolating instance {instance_id}: {e}")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Isolate an EC2 instance by assigning a restrictive security group.")
    parser.add_argument('instance_id', help='EC2 Instance ID to isolate')
    return parser.parse_args()


def main():
    setup_logging()
    args = parse_args()

    # Load playbook config
    cfg = load_config(CONFIG_PATH)
    aws_cfg = cfg.get('aws', {})
    restrictive_sg = cfg.get('restrictive_security_group_id')
    if not restrictive_sg:
        logging.error('restrictive_security_group_id not set in config.yml')
        sys.exit(1)

    # Initialize EC2 client
    session = boto3.Session(
        aws_access_key_id=aws_cfg.get('access_key'),
        aws_secret_access_key=aws_cfg.get('secret_key'),
        region_name=aws_cfg.get('region')
    )
    ec2_client = session.client('ec2')

    # Perform isolation
    isolate_instance(args.instance_id, restrictive_sg, ec2_client)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# Isolate endpoint playbook
