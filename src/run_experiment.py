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
            
            # Agente 1
            max_retries = 3
            success = False
            for attempt in range(max_retries):
                try:
                    result = generate_test_cases(req_desc, model_code)
                    success = True
                    break
                except Exception as e:
                    print(f"  Tentativa {attempt+1} falhou: {e}")
                    time.sleep(5)
            
            if not success:
                print("  Falha após todas as tentativas. Salvando vazio.")
                result = {"instances": "", "input tokens": 0, "output tokens": 0}
            
            # Popula RAW
            raw_instances = result['instances']
            dataset_raw[i]['requirements'][j]['instances'] = raw_instances
            dataset_raw[i]['requirements'][j]['input tokens'] = result['input tokens']
            dataset_raw[i]['requirements'][j]['output tokens'] = result['output tokens']
            
            # Agente 2
            processed_instances = postprocess(raw_instances)
            dataset_processed[i]['requirements'][j]['instances'] = processed_instances
            dataset_processed[i]['requirements'][j]['input tokens'] = result['input tokens']
            dataset_processed[i]['requirements'][j]['output tokens'] = result['output tokens']
            
            count += 1
            
            # Free tier do Gemini permite 15 requisições por minuto (1 a cada 4 segundos)
            # Como geramos 1 por vez, 5 segundos é uma margem segura
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
