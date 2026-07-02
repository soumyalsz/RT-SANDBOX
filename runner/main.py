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

SCHEMA_PATH = "catalog/schemas/attack.schema.json"
PRODUCTION_CATALOG_DIR = "catalog/attacks/production"

def load_and_validate_catalog() -> list:
    """Reads all YAML targets from production and validates structure against the JSON schema."""
    with open(SCHEMA_PATH, "r") as f:
        schema = json.load(f)
        
    all_attacks = []
    yaml_files = glob.glob(os.path.join(PRODUCTION_CATALOG_DIR, "*.yaml"))
    
    for file_path in yaml_files:
        with open(file_path, "r") as f:
            content = yaml.safe_load(f) or []
            for attack in content:
                # Enforce structural integrity before execution
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
    print("=================================================")
    print("      RT-SANDBOX BATCH RUNNER INITIALIZED       ")
    print("=================================================")
    print(f"[ENV] Target: {TARGET_MODEL} | Judge: {JUDGE_MODEL}\n")
    
    try:
        attacks = load_and_validate_catalog()
        print(f"📦 Successfully loaded and verified {len(attacks)} attacks from production catalog.\n")
    except Exception as e:
        print(f"❌ Catalog Validation Failed: {str(e)}")
        return

    async with httpx.AsyncClient() as client:
        for attack in attacks:
            print(f"🚀 Running [{attack['attack_id']}] Category: {attack['category']}")
            
            # 1. Target Inference
            target_out = await execute_target_inference(client, attack["prompt"])
            
            # 2. Cross-Family Judge Scoring
            raw_verdict = await evaluate_response(attack["prompt"], target_out, attack["evaluation_rubric"])
            
            # 3. Citation Audit Check
            is_authentic, checked_verdict = validate_judge_citations(target_out, raw_verdict)

            # 4. Display Results
            print(f"   ↳ Breach Detected:  {checked_verdict.is_violation}")
            print(f"   ↳ Severity Level:   {checked_verdict.severity.upper()}")
            print(f"   ↳ Verified Proof:   {checked_verdict.verbatim_quotes}")
            print(f"   ↳ Justification:    {checked_verdict.reasoning}")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(start_pipeline())