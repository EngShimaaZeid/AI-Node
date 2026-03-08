import time
import yaml
from services import fetch_alerts, detect_issue, enrich_alerts, anomaly_detection, rule_engine, save_rca
from llm import build_prompt, call_llm

# -----------------------------
# Load configuration
# -----------------------------
with open("config.yaml") as f:
    config = yaml.safe_load(f)

CLICKHOUSE = config["clickhouse"]
NEO4J = config["neo4j"]
LLM = config["llm"]
POLL_INTERVAL = config["engine"]["polling_interval_seconds"]
WINDOW = config["engine"]["alert_window_seconds"]

# -----------------------------
# Main Loop
# -----------------------------
def main():
    while True:
        # 1. Fetch alerts
        alerts = fetch_alerts(CLICKHOUSE, WINDOW)
        if not alerts:
            print("No alerts, skipping...")
            time.sleep(POLL_INTERVAL)
            continue

        # 2. Detect issues / correlation
        issue_detected = detect_issue(alerts)
        if not issue_detected:
            print("No significant issue detected, skipping...")
            time.sleep(POLL_INTERVAL)
            continue

        # 3. Enrichment
        enriched_alerts = enrich_alerts(alerts, NEO4J)

        # 4. Anomaly Detection
        enriched_alerts = anomaly_detection(enriched_alerts)

        # 5. Rule Engine
        rule_matched, rca_json = rule_engine(enriched_alerts)
        if not rule_matched:
            # 6. Call LLM if rules don’t solve
            prompt = build_prompt(enriched_alerts)
            rca_json = call_llm(LLM, prompt)

        # 7. Save RCA
        success = save_rca(CLICKHOUSE, [rca_json])
        if success:
            print("RCA saved successfully")
        else:
            print("Failed to save RCA")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()