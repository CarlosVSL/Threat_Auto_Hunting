#!/usr/bin/env python3
"""
runner.py: Orquestador principal que supervisa anomalías de Elastic ML y ejecuta playbooks.
 - anomaly_login -> bloquea IP con block_ip.py
 - anomaly_traffic -> aísla instancias EC2 con isolate_endpoint.py

Configuración en orchestrator/playbooks/config.yml:
  aws: {access_key, secret_key, region}
  firewall: {api_url, api_key}
  (Opcional) elasticsearch_host, score_threshold, poll_interval
"""
import os
import time
import logging
import subprocess

import boto3
from elasticsearch import Elasticsearch
from orchestrator.utils import setup_logging, load_yaml_config

# Cargar configuración del playbook
default_config_path = os.path.join(os.path.dirname(__file__), 'playbooks', 'config.yml')
config = load_yaml_config(default_config_path)

# Parámetros de Elasticsearch
ES_HOST = os.getenv('ELASTICSEARCH_HOST', config.get('elasticsearch_host', 'http://elasticsearch:9200'))
SCORE_THRESHOLD = config.get('score_threshold', 75.0)
POLL_INTERVAL = config.get('poll_interval', 60)

# AWS y Firewall (block_ip e isolate_endpoint usan estas credenciales internamente)
AWS_CFG = config.get('aws', {})

# Paths de scripts
BASE_DIR = os.getcwd()
BLOCK_IP_SCRIPT = os.path.join(BASE_DIR, 'orchestrator', 'playbooks', 'block_ip.py')
ISOLATE_SCRIPT = os.path.join(BASE_DIR, 'orchestrator', 'playbooks', 'isolate_endpoint.py')


def get_es_client():
    return Elasticsearch([ES_HOST])


def get_aws_client():
    return boto3.Session(
        aws_access_key_id=AWS_CFG.get('access_key'),
        aws_secret_access_key=AWS_CFG.get('secret_key'),
        region_name=AWS_CFG.get('region')
    ).client('ec2')


def process_login_anomalies(es, processed):
    try:
        resp = es.ml.get_records(job_id='anomaly_login', record_score=SCORE_THRESHOLD, size=100)
        for rec in resp.get('records', []):
            rid = rec['record_id']
            if rid in processed:
                continue
            processed.add(rid)
            ip = rec.get('partition_field_value')
            if not ip:
                continue
            logging.info(f"[LoginAnomaly] ID={rid}, IP={ip}")
            subprocess.run(['python3', BLOCK_IP_SCRIPT, ip], check=False)
    except Exception as e:
        logging.error(f"Error procesando anomaly_login: {e}")


def process_traffic_anomalies(es, aws, processed):
    try:
        resp = es.ml.get_records(job_id='anomaly_traffic', record_score=SCORE_THRESHOLD, size=100)
        for rec in resp.get('records', []):
            rid = rec['record_id']
            if rid in processed:
                continue
            processed.add(rid)
            ip = rec.get('partition_field_value')
            if not ip:
                continue
            logging.info(f"[TrafficAnomaly] ID={rid}, IP={ip}")
            # Resolver IP a InstanceId
            try:
                ec2 = aws
                out = ec2.describe_instances(Filters=[{'Name': 'private-ip-address', 'Values': [ip]}])
                instances = [i['InstanceId'] for r in out['Reservations'] for i in r['Instances']]
                for iid in instances:
                    logging.info(f"Aislando instancia {iid} para IP {ip}")
                    subprocess.run(['python3', ISOLATE_SCRIPT, iid], check=False)
            except Exception as ae:
                logging.error(f"Error aislando instancia para IP {ip}: {ae}")
    except Exception as e:
        logging.error(f"Error procesando anomaly_traffic: {e}")


def main():
    setup_logging()
    es = get_es_client()
    aws = get_aws_client()
    processed = set()
    logging.info("Orquestador iniciado. Monitoreando anomalías...")
    while True:
        process_login_anomalies(es, processed)
        process_traffic_anomalies(es, aws, processed)
        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()

