"""
Script para rodar o experimento no dataset Alloy4Fun.
Lê models_20250916.json.gz, chama os agentes e exporta os JSONs de raw e processed.
"""
import gzip
import json
import os
import copy
import time
import sys

from src.agents.agent_generator import generate_test_cases
from src.agents.agent_postprocessor import postprocess
from src.agents.agent_validator import run_alloy

def run_experiment(limit=None):
    dataset_path = "prepare/results/dataset.json"
    
    if not os.path.exists(dataset_path):
        print(f"Erro: {dataset_path} não encontrado.")
        sys.exit(1)
        
    print(f"Lendo dataset: {dataset_path}")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
    dataset_raw = copy.deepcopy(dataset)
    dataset_processed = copy.deepcopy(dataset)
    
    count = 0
    total_reqs = sum(len(ex['requirements']) for ex in dataset)
    if limit:
        total_reqs = min(total_reqs, limit)
    
    print(f"Iniciando processamento de {total_reqs} requisitos...")
    
    for i, example in enumerate(dataset):
        model_code = example['model']
        
        for j, req in enumerate(example['requirements']):
            if limit and count >= limit:
                break
                
            req_desc = req['description']
            print(f"[{count+1}/{total_reqs}] Processando: {example['example']} -> {req['pred']}")
            
            # Multi-Agent Self-Reflection Loop
            max_reflections = 3
            previous_code = None
            previous_error = None
            final_result = {"instances": "", "input tokens": 0, "output tokens": 0}
            success_reflection = False
            
            for reflection in range(max_reflections):
                print(f"  [Reflexão {reflection+1}/{max_reflections}] Iniciando geração...")
                success_api = False
                
                # Retry loop apenas para erros de HTTP/API (Timeouts, Rate Limits)
                for api_attempt in range(3):
                    try:
                        current_result = generate_test_cases(req_desc, model_code, previous_code, previous_error)
                        success_api = True
                        break
                    except Exception as e:
                        print(f"    [API Erro] Tentativa {api_attempt+1} falhou: {e}")
                        time.sleep(5)
                
                if not success_api:
                    print("    Falha de API persistente. Abortando reflexões deste requisito.")
                    break
                
                # Acumula os tokens usados nas várias chamadas de reflexão
                final_result["input tokens"] += current_result.get("input tokens", 0)
                final_result["output tokens"] += current_result.get("output tokens", 0)
                final_result["instances"] = current_result["instances"] # Mantém a última gerada
                
                # Agente 2: Limpa código
                raw_instances = current_result['instances']
                processed_instances = postprocess(raw_instances)
                
                # Agente 3: Validação da JVM
                full_alloy_code = model_code + "\n" + processed_instances
                val_result = run_alloy(full_alloy_code)
                
                if val_result["valid"]:
                    print(f"  [Sucesso] Teste perfeitamente válido gerado na reflexão {reflection+1}!")
                    success_reflection = True
                    break
                else:
                    print(f"  [Erro JVM] Falha de sintaxe ou consistência. Realimentando LLM...")
                    print(f"    [Motivo] {val_result['raw_output']}")
                    previous_code = raw_instances
                    previous_error = val_result["raw_output"]
                    time.sleep(5) # Delay do Rate Limit da API
            
            if not success_reflection:
                print("  [Aviso] Falha após todas as reflexões. Salvando a última tentativa (com erro).")
            
            # Popula RAW com a última tentativa (melhor esforço)
            dataset_raw[i]['requirements'][j]['instances'] = final_result['instances']
            dataset_raw[i]['requirements'][j]['input tokens'] = final_result['input tokens']
            dataset_raw[i]['requirements'][j]['output tokens'] = final_result['output tokens']
            
            # Popula PROCESSED com o pós-processamento da última tentativa
            dataset_processed[i]['requirements'][j]['instances'] = postprocess(final_result['instances'])
            dataset_processed[i]['requirements'][j]['input tokens'] = final_result['input tokens']
            dataset_processed[i]['requirements'][j]['output tokens'] = final_result['output tokens']
            
            count += 1
            
            # Delay final antes do próximo requisito
            time.sleep(5)
            
        if limit and count >= limit:
            break
            
    # Salvar apenas os processados/raw se tiver limite (cortar os nao processados)
    if limit:
        # Poda o dataset
        dataset_raw = dataset_raw[:i+1]
        dataset_processed = dataset_processed[:i+1]
        dataset_raw[-1]['requirements'] = dataset_raw[-1]['requirements'][:j] # O atual não foi processado se quebrou no limit antes do loop
        dataset_processed[-1]['requirements'] = dataset_processed[-1]['requirements'][:j]
    
    raw_path = "data/raw/experiment_raw.json"
    processed_path = "data/processed/experiment_processed.json"
    
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    
    with open(raw_path, "w", encoding='utf-8') as f:
        json.dump(dataset_raw, f, indent=4)
    print(f"Salvo: {raw_path}")
    
    with open(processed_path, "w", encoding='utf-8') as f:
        json.dump(dataset_processed, f, indent=4)
    print(f"Salvo: {processed_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Limit number of requirements to process", default=None)
    args = parser.parse_args()
    
    run_experiment(args.limit)
