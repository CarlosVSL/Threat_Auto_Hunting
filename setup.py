#!/usr/bin/env python3
"""
setup.py: Inicializador interactivo para la plataforma de Threat Hunting.
  - Solicita todas las credenciales y parámetros de entorno.
  - Rellena orchestrator/playbooks/config.yml.
  - Genera .env con TODO lo necesario.
  - Arranca docker-compose.
"""

import os
import subprocess
import sys
import getpass

try:
    import yaml
except ImportError:
    print("ERROR: necesitas instalar PyYAML: pip install pyyaml")
    sys.exit(1)


def prompt(text, default=None, secret=False):
    if default:
        q = f"{text} [{default}]: "
    else:
        q = f"{text}: "
    if secret:
        val = getpass.getpass(q)
    else:
        val = input(q)
    return val.strip() or default


def main():
    print("=== Inicialización Threat Hunting Platform ===\n")

    # 1) Variables de entorno para .env
    misp_url        = prompt("MISP_URL",            "https://misp.example.com")
    misp_key        = prompt("MISP_KEY (secreto)",              secret=True)
    misp_lookback   = prompt("MISP_LOOKBACK_HOURS",  "24")
    es_host         = prompt("ELASTICSEARCH_HOST",  "http://localhost:9200")
    cortex_url      = prompt("CORTEX_URL",           "https://cortex.example.com")
    cortex_key      = prompt("CORTEX_API_KEY",                  secret=True)
    cortex_verify   = prompt("CORTEX_VERIFY_SSL (True/False)",  "True")

    # 2) Credenciales Orquestador (config.yml)
    aws_key         = prompt("AWS_ACCESS_KEY_ID")
    aws_secret      = prompt("AWS_SECRET_ACCESS_KEY",     secret=True)
    aws_region      = prompt("AWS_REGION",               "us-east-1")
    sg_id           = prompt("Restrictive Security Group ID")
    fw_api          = prompt("FIREWALL_API_URL",        "https://firewall-api.example.com")
    fw_key          = prompt("FIREWALL_API_KEY (secreto)",    secret=True)

    # 3) Actualizar orchestrator/playbooks/config.yml
    cfg_path = os.path.join("orchestrator", "playbooks", "config.yml")
    print(f"\n– Actualizando {cfg_path}")
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    cfg['aws']['access_key']  = aws_key
    cfg['aws']['secret_key']  = aws_secret
    cfg['aws']['region']      = aws_region
    cfg['restrictive_security_group_id'] = sg_id
    cfg['firewall']['api_url'] = fw_api
    cfg['firewall']['api_key'] = fw_key
    with open(cfg_path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)
    print("  ✔ config.yml actualizado")

    # 4) Generar .env completo
    print("– Generando .env")
    with open(".env", "w") as f:
        f.write(f"MISP_URL={misp_url}\n")
        f.write(f"MISP_KEY={misp_key}\n")
        f.write(f"MISP_LOOKBACK_HOURS={misp_lookback}\n")
        f.write(f"ELASTICSEARCH_HOST={es_host}\n")
        f.write(f"CORTEX_URL={cortex_url}\n")
        f.write(f"CORTEX_API_KEY={cortex_key}\n")
        f.write(f"CORTEX_VERIFY_SSL={cortex_verify}\n")
    print("  ✔ .env creado")

    # 5) Arrancar Docker Compose
    print("\n=== Levantando plataforma con Docker Compose ===")
    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("✔ Plataforma desplegada correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR al ejecutar docker-compose: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

