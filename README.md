# Threat Hunting Platform

**Plataforma de Threat Hunting y Respuesta Automatizada**  
Integra Elastic Stack, Machine Learning y SOAR.

---

## Descripción

Recolecta datos de endpoints, red, honeypots y OSINT, los ingiere en Elasticsearch, aplica ML para detección proactiva y orquesta respuestas automáticas.

---

## Características

- **Ingestión**: Filebeat, Packetbeat, Winlogbeat, NetFlow, Cowrie  
- **Procesamiento**: Logstash (Grok, GeoIP, JSON)  
- **Detección**: Elastic ML & modelos Python custom  
- **Enriquecimiento**: IOC tags desde MISP/OSINT  
- **Visualización**: Dashboards MITRE ATT&CK, Timeline, Graph  
- **Respuesta**: Playbooks Python, TheHive/Cortex  
- **Métricas**: MTTD/MTTR scripts y plantillas  
- **Despliegue**: Docker Compose & Kubernetes

---

## Estructura del Proyecto

```text
threat-hunting-platform/
├── beats/         # Configuración Filebeat, Packetbeat, Winlogbeat
├── logstash/      # Pipelines y configuración de Logstash
├── honeypots/     # Cowrie honeypot
├── osint/         # Scrapers y enriquecimiento IOC
├── misp/          # Cliente MISP
├── ml/            # Jobs Elastic ML y modelos custom
├── kibana/        # Dashboards y patterns de Kibana
├── orchestrator/  # Playbooks y Cortex integration
├── metrics/       # Cálculo MTTD/MTTR y reportes
├── deployment/    # Docker Compose y Kubernetes manifiestos
└── docs/          # Documentación (arquitectura, runbooks, onboarding)
```

## Quickstart (Local)

### Clona el repositorio

```bash
git clone https://github.com/tu-org/threat-hunting-platform.git
cd threat-hunting-platform
```

### Configura variables

- Ajusta `orchestrator/playbooks/config.yml`.  
- Define en tu entorno:

```bash
export MISP_URL=https://misp.example.com
export MISP_KEY=<tu_api_key>
export ELASTICSEARCH_HOST=http://localhost:9200
```

### Levanta con Docker Compose

```bash
docker-compose up -d
```

### Accede

- **Elasticsearch**: `http://localhost:9200`  
- **Kibana**:       `http://localhost:5601`  
- **Cowrie SSH Honeypot**:

```bash
  ssh -p 2222 honeypot@localhost
```

---

## Despliegue en Producción (Kubernetes)

### Crea el namespace

```bash
kubectl create namespace threat-hunting
```

### Aplica manifiestos

```bash
kubectl apply -f deployment/k8s/elastic-stack.yaml
kubectl apply -f deployment/k8s/beats-daemonset.yaml
kubectl apply -f deployment/k8s/misp-deployment.yaml
kubectl apply -f deployment/k8s/orchestrator-deployment.yaml
```

Configura tu **Ingress** o **LoadBalancer** para exponer Kibana y MISP.

---

## Licencia

MIT © CarlosVSL

