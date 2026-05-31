"""
Pipeline principal – orquestra os 3 agentes para cada requisito.
"""
from src.agents.agent_generator import generate_test_cases
from src.agents.agent_postprocessor import postprocess
from src.agents.agent_validator import run_alloy
from src.config import MAX_RETRIES
import json, os

def run_pipeline(requirement: str) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[Agente 1] Gerando test cases (tentativa {attempt})...")
        raw = generate_test_cases(requirement)
        
        print("[Agente 2] Aplicando pós-processamento sintático...")
        processed = postprocess(raw)
        
        print("[Agente 3] Validando com Alloy Analyzer...")
        result = run_alloy(processed)
        result["attempt"] = attempt
        result["raw"] = raw
        result["processed"] = processed
        
        if result["valid"]:
            print(f"[Pipeline] Válido na tentativa {attempt}.")
            return result
    
    print("[Pipeline] Máximo de tentativas atingido.")
    return result

if __name__ == "__main__":
    req = input("Digite o requisito: ")
    result = run_pipeline(req)
    print(json.dumps(result, indent=2))
