# Runbooks de Investigación y Respuesta

## Propósito
Proporcionar pasos detallados para que un analista identifique, investigue y responda a incidentes comunes, con mapeo a MITRE ATT&CK.

---

## 1. Preparación del Entorno

1. Accede a **Kibana** (`http://<host>:5601`).  
2. Selecciona el dashboard **MITRE ATT&CK Dashboard**.  
3. Asegúrate de tener permisos para ejecutar playbooks (API keys configuradas en Orquestador).  
4. Abre la **línea de tiempo** (`Timeline View`).

---

## 2. Escenario: Intentos de Brute Force SSH (T1110)

1. **Detección**  
   - En el dashboard de **login failures**, busca picos inusuales en el conteo por host.  
   - Aplica filtro:
     program:sshd AND message:"Failed password"

2. **Investigación**  
   - Identifica las IPs origen con más fallos.  
   - Revisa geolocalización (`source.geo.country_name`).

3. **Respuesta Manual**  
   python orchestrator/playbooks/block_ip.py <IP>

4. **Respuesta Automática**  
   - Configura en el Orquestador una regla que dispare `block_ip.py` cuando el ML detecte anomalías en login.

5. **Seguimiento**  
   - Verifica que la IP no genere más eventos.  
   - Documenta en tu sistema de tickets (Jira, ServiceNow…).

---

## 3. Escenario: Tráfico Anómalo por IP (T1040)

1. **Detección**  
   - Consulta el job ML `anomaly_traffic` en Elasticsearch.  
   - Visualiza anomalías en el dashboard **Network Graph**.

2. **Investigación**  
   - Filtra eventos:
     netflow.ipv4_src_addr:<IP_sospechosa>  
   - Correlaciona con logs de endpoint (`endpoint-*`).

3. **Respuesta**  
   python orchestrator/playbooks/isolate_endpoint.py <InstanceID>

4. **Verificación**  
   - Asegúrate de que no haya tráfico posterior desde esa instancia.

---

## 4. Escenario: Enriquecimiento de IOCs (T1587)

1. **Detección**  
   - Filtra en el dashboard MITRE ATT&CK:
     tags:ioc.*

2. **Investigación**  
   from misp.misp_client import MISPClient  
   client = MISPClient()  
   client.get_iocs_from_event(<event_id>)

3. **Respuesta**  
   python osint/ioc_enrichment/enrich_iocs.py

---

## 5. Mapeo MITRE ATT&CK

| Táctica               | Técnica                   | ID     | Playbook                   | Dashboard               |
|-----------------------|---------------------------|--------|----------------------------|-------------------------|
| Initial Access        | Valid Accounts            | T1078  | block_ip.py                | MITRE ATT&CK Dashboard  |
| Credential Access     | Brute Force               | T1110  | block_ip.py                | Timeline View           |
| Discovery             | Network Service Scanning  | T1046  | isolate_endpoint.py        | Network Graph           |
| Lateral Movement      | Remote Services           | T1021  | isolate_endpoint.py        | MITRE ATT&CK Dashboard  |
| Exfiltration          | Data Transfer Size Limits | T1030  | (Alerta manual)            | Timeline View           |

---

## 6. Cierre del Incidente

1. Confirmar resolución: logs limpios, sin detección.  
2. Actualizar ticket con MTTD y MTTR.  
3. Generar informe usando `metrics/report_template.md`.  
4. Cerrar el incidente.  

