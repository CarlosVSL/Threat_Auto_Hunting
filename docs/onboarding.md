# Guía de despliegue y contribución

```markdown
# Guía de Onboarding

Esta guía explica cómo desplegar, configurar y contribuir a la Plataforma de Threat Hunting y Respuesta Automática.

---

## 1. Requisitos Previos

- **Hardware/VM**: 4 CPU, 8 GB RAM, 50 GB disco.  
- **Software**:  
  - Docker ≥ 19.03 & Docker Compose ≥ 1.25 (local).  
  - Kubernetes ≥ 1.18 (prod).  
  - Python ≥ 3.8 & pip.  
  - AWS CLI (si usas AWS).

---

## 2. Clonar el Repositorio

```bash
git clone https://github.com/CarlosVSL/threat-hunting-platform.git
cd threat-hunting-platform

```

## 3. Configuracion

Copia y adapta los ejemplos:

```bash
cp orchestrator/playbooks/config.yml.example orchestrator/playbooks/config.yml
cp misp/requirements.txt.example misp/requirements.txt

```
- Rellena access_key, secret_key, region, restrictive_security_group_id, firewall.api_url y api_key.

- Define en tu entorno (o .env):

```arduino
export MISP_URL=https://misp.example.com
export MISP_KEY=<tu_api_key>
export ELASTICSEARCH_HOST=http://localhost:9200

```

## 4. Despliegue Local con Docker Compose

```bash
docker-compose up -d

```

- Elasticsearch: http://localhost:9200

- Kibana: http://localhost:5601

- Cowrie (SSH):

```bash
ssh -p 2222 honeypot@localhost

```
Logs en tiempo real:

```bash
docker-compose logs -f elasticsearch kibana logstash filebeat packetbeat cowrie

```
## 5. Despliegue en Kubernetes

```bash
kubectl create ns threat-hunting
kubectl apply -f deployment/k8s/elastic-stack.yaml
kubectl apply -f deployment/k8s/beats-daemonset.yaml
kubectl apply -f deployment/k8s/misp-deployment.yaml
kubectl apply -f deployment/k8s/orchestrator-deployment.yaml

```
## 6. Test y Validaciones

```bash
docker-compose run --rm filebeat test config
docker-compose run --rm packetbeat test config
pytest tests/

```
