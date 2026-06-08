import argparse
import copy
import json
import os
import sys
import time

from src.agents.agent_generator import generate_test_cases
from src.agents.agent_postprocessor import postprocess
from src.agents.agent_validator import run_alloy
from src.config import MAX_RETRIES


def run_sample(limit=2, output_tag="sample_3try"):
    dataset_path = "prepare/results/dataset.json"
    if not os.path.exists(dataset_path):
        print(f"Erro: {dataset_path} nao encontrado.")
        sys.exit(1)

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    dataset_raw = copy.deepcopy(dataset)
    dataset_processed = copy.deepcopy(dataset)
    total_reqs = min(sum(len(ex["requirements"]) for ex in dataset), limit)
    count = 0

    print(f"Lendo dataset: {dataset_path}")
    print(f"Iniciando amostra de {total_reqs} requisitos com {MAX_RETRIES} tentativas...")

    for i, example in enumerate(dataset):
        model_code = example["model"]
        last_processed_j = -1

        for j, req in enumerate(example["requirements"]):
            if count >= limit:
                break

            print(f"[{count + 1}/{total_reqs}] Processando: {example['example']} -> {req['pred']}")
            previous_code = None
            previous_error = None
            previous_processed_code = None
            previous_full_alloy_code = None
            previous_validation = None
            final_result = {"instances": "", "input tokens": 0, "output tokens": 0}
            success_reflection = False

            for reflection in range(MAX_RETRIES):
                print(f"  [Reflexao {reflection + 1}/{MAX_RETRIES}] Iniciando geracao...")
                try:
                    current_result = generate_test_cases(
                        requirement=req["description"],
                        model_code=model_code,
                        oracle=req.get("oracle"),
                        previous_code=previous_code,
                        previous_error=previous_error,
                        previous_processed_code=previous_processed_code,
                        previous_full_alloy_code=previous_full_alloy_code,
                        previous_validation=previous_validation,
                    )
                except Exception as e:
                    print(f"    [API Erro] {e}")
                    if "429" in str(e) or "Quota exceeded" in str(e):
                        print("    Quota atingida. Encerrando amostra sem salvar resultados parciais contaminados.")
                        return False
                    time.sleep(5)
                    continue

                final_result["input tokens"] += current_result.get("input tokens", 0)
                final_result["output tokens"] += current_result.get("output tokens", 0)
                final_result["instances"] = current_result["instances"]

                raw_instances = current_result["instances"]
                processed_instances = postprocess(raw_instances)
                full_alloy_code = model_code + "\n" + processed_instances
                val_result = run_alloy(full_alloy_code)

                if val_result["valid"]:
                    print(f"  [Sucesso] Valido na reflexao {reflection + 1}.")
                    success_reflection = True
                    break

                print("  [Erro JVM] Realimentando LLM com contexto da falha...")
                print(f"    [Motivo] {val_result['raw_output']}")
                previous_code = raw_instances
                previous_error = val_result["raw_output"]
                previous_processed_code = processed_instances
                previous_full_alloy_code = full_alloy_code
                previous_validation = {
                    "syntax": val_result["syntax"],
                    "consistent": val_result["consistent"],
                    "valid": val_result["valid"],
                }
                time.sleep(5)

            if not success_reflection:
                print("  [Aviso] Falha apos todas as reflexoes. Salvando ultima tentativa.")

            dataset_raw[i]["requirements"][j]["instances"] = final_result["instances"]
            dataset_raw[i]["requirements"][j]["input tokens"] = final_result["input tokens"]
            dataset_raw[i]["requirements"][j]["output tokens"] = final_result["output tokens"]

            dataset_processed[i]["requirements"][j]["instances"] = postprocess(final_result["instances"])
            dataset_processed[i]["requirements"][j]["input tokens"] = final_result["input tokens"]
            dataset_processed[i]["requirements"][j]["output tokens"] = final_result["output tokens"]

            count += 1
            last_processed_j = j
            time.sleep(5)

        if count >= limit:
            dataset_raw = dataset_raw[: i + 1]
            dataset_processed = dataset_processed[: i + 1]
            dataset_raw[-1]["requirements"] = dataset_raw[-1]["requirements"][: last_processed_j + 1]
            dataset_processed[-1]["requirements"] = dataset_processed[-1]["requirements"][: last_processed_j + 1]
            break

    raw_path = f"data/raw/{output_tag}_raw.json"
    processed_path = f"data/processed/{output_tag}_processed.json"
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(dataset_raw, f, indent=4)
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(dataset_processed, f, indent=4)

    print(f"Salvo: {raw_path}")
    print(f"Salvo: {processed_path}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--output-tag", default="sample_3try")
    args = parser.parse_args()
    ok = run_sample(args.limit, args.output_tag)
    sys.exit(0 if ok else 2)
