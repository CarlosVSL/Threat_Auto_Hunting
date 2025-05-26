# Arquitectura de la Plataforma de Threat Hunting y Respuesta Automatizada

Esta arquitectura integra ingestión de datos, procesamiento, detección de anomalías, visualización y respuesta automática en un flujo unificado.

---

## 1. Fuentes de Datos (Ingestión)

1. **Endpoints**  
   - **Filebeat**: agentes ligeros recolectan logs de aplicaciones y sistema (`/var/log`).  
   - **Winlogbeat**: recoge eventos de Windows (Security, Application, System).

2. **Red**  
   - **Packetbeat**: captura paquetes en tiempo real sobre puertos HTTP, DNS, MySQL, TLS, gRPC, Kafka.  
   - **NetFlow**: Logstash UDP en puerto 2055 consume flujos NetFlow v5/9/10.

3. **Honeypots**  
   - **Cowrie**: emulación SSH en puerto 2222, genera logs JSON.

4. **Inteligencia de Amenazas (OSINT & MISP)**  
   - **cve_feed.py**: scraper RSS de NVD para CVEs.  
   - **mib_crawl.py**: crawler de MISP y otros feeds, produce JSON con IOCs.  
   - **misp_client.py**: módulo Python para interactuar con MISP (push/pull).

---

## 2. Procesamiento y Enriquecimiento (Logstash & Ingest Pipelines)

1. **Logstash** (puertos 5044, 5045 TCP y 2055 UDP)  
   - `01-syslog.conf`: grok de syslog, fecha, GeoIP.  
   - `02-netflow.conf`: codec NetFlow, GeoIP, conversión de bytes/paquetes.  
   - `03-endpoint.conf`: parseo JSON, fecha ISO8601, GeoIP.

2. **Ingest Pipelines de Elasticsearch**  
   - **Filebeat** (`filebeat-pipeline`): grok genérico, fecha, GeoIP, User-Agent.  
   - **Packetbeat** (`packetbeat-pipeline`): GeoIP, renombrado de transport.  
   - **ioc_enrichment**: script Painless para etiquetar IOCs (IPs, dominios, hashes).

---

## 3. Almacenamiento y Búsqueda (Elasticsearch)

- Índices:  
  - `syslog-*`, `netflow-*`, `endpoint-*`, `filebeat-*`, `packetbeat-*`, `winlogbeat-*`.  
- Plantilla de índices con compresión y número de shards ajustable.

---

## 4. Detección y Machine Learning

1. **Jobs nativos de Elastic ML**  
   - `anomaly_traffic`: suma de bytes por IP origen.  
   - `anomaly_login`: conteo de intentos SSH fallidos por host.

2. **Modelos personalizados**  
   - Clasificador de movimiento lateral entrenado en Python (RandomForest).

---

## 5. Visualización (Kibana)

- **Dashboards** basados en MITRE ATT&CK:  
  - `mitre_attack_dashboard`  
  - `timeline_view`  
  - `network_graph` (Graph workspace)

- **Index Patterns**: `logs-*` con campo `@timestamp`.

---

## 6. Orquestación y Respuesta Automática

- **Playbooks Python**:  
  - `isolate_endpoint.py`: modifica security groups de EC2.  
  - `block_ip.py`: llama API de firewall/EDR.

- **Integración SOAR**:  
  - **TheHive/Cortex** (`cortex_integration.py`): lanza analizadores y recoge resultados.

- **utils.py**: configuración común de logging y carga de YAML.

---

## 7. Métricas y Reportes

- **calculate_mttd.py**: MTTD a partir de CSV de incidentes.  
- **calculate_mttr.py**: MTTR a partir de CSV.  
- **report_template.md**: plantilla Markdown para informes ejecutivos.

---

## 8. Despliegue

1. **Docker Compose** (`deployment/docker-compose.yml`)  
   - Levanta Elasticsearch, Kibana, Logstash, Beats y Cowrie.

2. **Kubernetes** (`deployment/k8s/`)  
   - Manifiestos para Elasticsearch, Kibana, Logstash, Beats (DaemonSets), MISP y Orquestador.

---

### Flujos de Datos (Resumen)

```text
[Fuentes] --> [Beats / UDP inputs] --> [Logstash pipelines] --> [Ingest Pipelines] --> [Elasticsearch]
                                                       |--> [IOC Enrichment]
                                                       |--> [ML Jobs]
                                                       |--> [Cortex SOAR]
                                                       |--> [Dashboards Kibana]
                                                       |--> [Playbooks / API Calls]
                                                       |--> [Métricas & Reportes]

