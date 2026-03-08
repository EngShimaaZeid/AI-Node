import requests
from sklearn.ensemble import IsolationForest
from neo4j import GraphDatabase

# -----------------------------
# ClickHouse Fetching
# -----------------------------
def fetch_alerts(clickhouse_config, window_seconds):
    query = f'''
    SELECT * FROM alerts
    WHERE timestamp >= now() - INTERVAL {window_seconds} SECOND
    '''
    response = requests.post(
        f"{clickhouse_config['host']}/?database={clickhouse_config['database']}",
        data=query
    )
    if response.status_code == 200:
        return response.json()
    return []


# -----------------------------
# Clustering / Correlation
# -----------------------------
def detect_issue(alerts):
    if not alerts:
        return False

    device_count = {}
    for alert in alerts:
        device = alert['device_id']
        device_count[device] = device_count.get(device, 0) + 1

    for count in device_count.values():
        if count >= 3:
            return True

    return False


# -----------------------------
# Enrichment Layer
# -----------------------------
def enrich_alerts(alerts, neo4j_config):
    driver = GraphDatabase.driver(
        neo4j_config['uri'],
        auth=(neo4j_config['user'], neo4j_config['password'])
    )

    enriched = []
    with driver.session() as session:
        for alert in alerts:
            query = f"MATCH (d:Device {{id:'{alert['device_id']}'}}) RETURN d.topology AS topology"
            result = session.run(query)
            topo = result.single()

            alert['topology'] = topo['topology'] if topo else None
            enriched.append(alert)

    return enriched


# -----------------------------
# Anomaly Detection
# -----------------------------
def anomaly_detection(alerts, model=None):
    if not model:
        model = IsolationForest(contamination=0.1)

    features = [[a['severity']] for a in alerts]
    model.fit(features)

    scores = model.decision_function(features)

    for alert, score in zip(alerts, scores):
        alert['anomaly_score'] = float(score)

    return alerts


# -----------------------------
# Rule Engine
# -----------------------------
def rule_engine(alerts):
    for alert in alerts:
        if alert.get('severity') == 'critical':
            return True, {
                "root_cause": "Critical device failure",
                "confidence_score": 0.95,
                "recommended_action": "Dispatch immediately"
            }

    return False, {}


# -----------------------------
# Output Writer
# -----------------------------
def save_rca(clickhouse_config, rca_json):
    query = f"INSERT INTO rca_results FORMAT JSONEachRow {rca_json}"
    response = requests.post(
        f"{clickhouse_config['host']}/?database={clickhouse_config['database']}",
        data=query
    )
    return response.status_code == 200