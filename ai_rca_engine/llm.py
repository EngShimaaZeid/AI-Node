import requests
import json

def build_prompt(enriched_alerts):
    prompt = "Analyze the following alerts and generate RCA in JSON:\n"
    for alert in enriched_alerts:
        prompt += json.dumps(alert) + "\n"
    return prompt


def call_llm(llm_config, prompt):
    headers = {"Authorization": f"Bearer {llm_config['api_key']}"}
    payload = {"prompt": prompt}

    response = requests.post(
        llm_config['endpoint'],
        json=payload,
        headers=headers
    )

    if response.status_code == 200:
        try:
            return response.json()
        except Exception:
            return {"error": "Invalid LLM output"}

    return {"error": "LLM call failed"}