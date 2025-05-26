# Threat Hunting Platform

**Plataforma de Threat Hunting y Respuesta Automatizada**  
Integra Elastic Stack, Machine Learning y SOAR en un único flujo.

---

## Descripción

Recoge datos de endpoints, red, honeypots y OSINT, los envía a Elasticsearch, aplica ML para detección proactiva y orquesta respuestas automáticas.

---

## Características

- **Ingestión**: Filebeat, Packetbeat, Winlogbeat, NetFlow y Cowrie  
- **Procesamiento**: Logstash (Grok, GeoIP, JSON)  
- **Detección**: Elastic ML jobs & modelos Python custom  
- **Enriquecimiento**: IOCs desde MISP/OSINT  
- **Visualización**: Dashboards MITRE ATT&CK, Timeline, Graph  
- **Respuesta**: Playbooks Python, TheHive/Cortex integration  
- **Métricas**: MTTD/MTTR scripts y plantilla de informe  
- **Despliegue**: Docker Compose & Kubernetes manifests  
- **Setup interactivo**: `setup.py` para generación de `.env`, configuración y arranque automático  

---

## Estructura del Proyecto

```text
threat-hunting-platform/
├── beats/         # Config Beats (filebeat, packetbeat, winlogbeat)
├── logstash/      # Pipelines y configuración de Logstash
├── honeypots/     # Cowrie SSH honeypot
├── osint/         # Scrapers y scripts de enriquecimiento IOC
├── misp/          # Cliente Python para MISP
├── ml/            # Jobs Elastic ML y modelos custom
├── kibana/        # Dashboards y patrones de índice
├── orchestrator/  # Playbooks, runner y utils
├── metrics/       # Cálculo MTTD/MTTR y plantilla de informe
├── deployment/    # Docker Compose & Kubernetes manifests
├── docs/          # Documentación (arquitectura, runbooks, onboarding)
└── setup.py       # Script interactivo de configuración y arranque
```

---

## Requisitos Previos

- Docker ≥ 19.03 & Docker Compose ≥ 1.25  
- Python ≥ 3.8 (se recomienda en virtualenv)  
- (Opcional) Kubernetes ≥ 1.18 para despliegue en prod  
- AWS CLI si usas playbook de aislamiento en AWS  

---

## Setup Interactivo y Quickstart (Local)

1. **Clona el repositorio**  
```bash
git clone https://github.com/tu-org/threat-hunting-platform.git
cd threat-hunting-platform
```

2. **Crea y activa un entorno virtual** (recomendado)  
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyyaml
```

3. **Ejecuta el script de setup**  
```bash
chmod +x setup.py
./setup.py
``` 
- Te pedirá valores para MISP, Elasticsearch, Cortex, AWS y firewall.  
- Generará un archivo `.env` en la raíz.  
- Actualizará el `config.yml` de tu Orquestador.  
- Levantará todos los servicios con Docker Compose.

4. **Comprueba los servicios**  
```bash
docker-compose -f deployment/docker-compose.yml logs -f
``` 
- Elasticsearch: http://localhost:9200  
- Kibana:       http://localhost:5601  
- SSH honeypot: `ssh -p 2222 honeypot@localhost`  

---

## Despliegue en Producción (Kubernetes)

1. Crea el namespace  
```bash
kubectl create namespace threat-hunting
```

2. Aplica manifiestos  
```bash
kubectl apply -f deployment/k8s/elastic-stack.yaml
kubectl apply -f deployment/k8s/beats-daemonset.yaml
kubectl apply -f deployment/k8s/misp-deployment.yaml
kubectl apply -f deployment/k8s/orchestrator-deployment.yaml
```

3. Configura Ingress/LoadBalancer para exponer Kibana y MISP.

---

## Licencia

MIT © CarlosVSL  

