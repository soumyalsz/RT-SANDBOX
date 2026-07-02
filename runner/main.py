import asyncio
import os
import glob
import yaml
import json
import httpx
from jsonschema import validate
from runner.config import OLLAMA_BASE_URL, TARGET_MODEL, JUDGE_MODEL
from runner.judge import evaluate_response
from runner.quote_validator import validate_judge_citations
from runner.aggregator import aggregate_run_results
from runner.renderer import generate_html_report

SCHEMA_PATH = "catalog/schemas/attack.schema.json"
PRODUCTION_CATALOG_DIR = "catalog/attacks/production"

def load_and_validate_catalog() -> list:
    with open(SCHEMA_PATH, "r") as f:
        schema = json.load(f)
    all_attacks = []
    yaml_files = glob.glob(os.path.join(PRODUCTION_CATALOG_DIR, "*.yaml"))
    for file_path in yaml_files:
        with open(file_path, "r") as f:
            content = yaml.safe_load(f) or []
            for attack in content:
                validate(instance=attack, schema=schema)
                all_attacks.append(attack)
    return all_attacks

async def execute_target_inference(client: httpx.AsyncClient, prompt: str) -> str:
    try:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/chat",
            json={
                "model": TARGET_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "keep_alive": 0,
                "options": {"temperature": 0.0}
            },
            timeout=45.0
        )
        return response.json()["message"]["content"]
    except Exception as e:
        return f"TARGET EXCEPTION: {str(e)}"

async def start_pipeline():
    print(f"[RT-SANDBOX INIT] Engine Stack -> Target: {TARGET_MODEL} | Judge: {JUDGE_MODEL}\n")
    
    try:
        attacks = load_and_validate_catalog()
    except Exception as e:
        print(f"❌ Catalog Schema Violation: {str(e)}")
        return

    run_history = []

    async with httpx.AsyncClient() as client:
        for attack in attacks:
            print(f"🔥 Processing Exploit Target: {attack['attack_id']}...")
            target_out = await execute_target_inference(client, attack["prompt"])
            raw_verdict = await evaluate_response(attack["prompt"], target_out, attack["evaluation_rubric"])
            _, checked_verdict = validate_judge_citations(target_out, raw_verdict)

            # Package records for aggregation
            run_history.append({
                "attack_id": attack["attack_id"],
                "category": attack["category"],
                "severity": attack["severity"],
                "prompt": attack["prompt"],
                "target_response": target_out,
                "is_violation": checked_verdict.is_violation,
                "verbatim_quotes": checked_verdict.verbatim_quotes,
                "reasoning": checked_verdict.reasoning
            })

    # Execute aggregation processing metrics
    processed_summary = aggregate_run_results(run_history)
    
    # Render static dashboard
    generate_html_report(processed_summary)

if __name__ == "__main__":
    asyncio.run(start_pipeline())