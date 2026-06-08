"""
Pipeline principal – orquestra os 3 agentes para cada requisito.
"""
from src.agents.agent_generator import generate_test_cases
from src.agents.agent_postprocessor import postprocess
from src.agents.agent_validator import run_alloy
from src.config import MAX_RETRIES
import json, os

def run_pipeline(requirement: str, model_code: str = "", oracle: str = None) -> dict:
    previous_code = None
    previous_error = None
    previous_processed_code = None
    previous_full_alloy_code = None
    previous_validation = None
    
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[Agente 1] Gerando test cases (tentativa {attempt})...")
        raw = generate_test_cases(
            requirement,
            model_code,
            oracle,
            previous_code,
            previous_error,
            previous_processed_code=previous_processed_code,
            previous_full_alloy_code=previous_full_alloy_code,
            previous_validation=previous_validation,
        )
        
        print("[Agente 2] Aplicando pós-processamento sintático...")
        processed_instances = postprocess(raw['instances'])
        
        # Agente 3 precisa do modelo completo para avaliar as assinaturas base
        full_alloy_code = model_code + "\n" + processed_instances
        
        print("[Agente 3] Validando com Alloy Analyzer...")
        result = run_alloy(full_alloy_code)
        result["attempt"] = attempt
        result["raw"] = raw['instances']
        result["processed"] = processed_instances
        
        if result["valid"]:
            print(f"[Pipeline] Válido na tentativa {attempt}.")
            return result
        else:
            print(f"[Pipeline] Erro detectado na tentativa {attempt}. Iniciando self-reflection para a próxima...")
            previous_code = raw['instances']
            previous_error = result["raw_output"]
            previous_processed_code = processed_instances
            previous_full_alloy_code = full_alloy_code
            previous_validation = {
                "syntax": result["syntax"],
                "consistent": result["consistent"],
                "valid": result["valid"],
            }
            
    print("[Pipeline] Máximo de tentativas atingido. O código final ainda possui erros.")
    return result

if __name__ == "__main__":
    req = input("Digite o requisito (NL): ")
    # Simulação para pipeline interativo onde o usuário pode testar com modelo vazio
    print("Aviso: O modelo base local (sig) está vazio neste teste interativo.")
    result = run_pipeline(req, model_code="")
    print(json.dumps(result, indent=2))
