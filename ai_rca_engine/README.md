# AI RCA Engine

An automated AI-based Root Cause Analysis (RCA) engine for alert processing.

## Architecture

Workflow:

Scheduler → Fetch Alerts → Detect Issue → Enrichment → Anomaly Detection → Rule Engine → LLM → Save RCA

## Project Structure

ai_rca_engine/

- main.py (engine orchestrator)
- services.py (business logic)
- llm.py (LLM interaction layer)
- config.yaml (configuration)
- requirements.txt (dependencies)

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Configuration

Edit **config.yaml** to configure:

- ClickHouse connection
- Neo4j graph database
- LLM endpoint
- polling interval