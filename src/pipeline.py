"""
Orquestra os 3 agentes.
"""

from agents.agent_generator import generate_test_cases
from agents.agent_postprocessor import postprocess
from agents.agent_validator import validate

def run_pipeline(prompt: str):
    print("1. Gerando casos de teste...")
    raw_output = generate_test_cases(prompt)
    
    print("2. Pós-processando o modelo...")
    processed_output = postprocess(raw_output)
    
    print("3. Validando com Alloy Analyzer...")
    metrics = validate(processed_output)
    
    return metrics

if __name__ == "__main__":
    # Exemplo de execução
    run_pipeline("Exemplo de prompt")
