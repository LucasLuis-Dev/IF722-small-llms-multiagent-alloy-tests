import json
import time
from src.pipeline import run_pipeline

def run_demo():
    print("="*60)
    print("🎓 DEMONSTRAÇÃO DO PIPELINE MULTI-AGENTE (ALLOY4FUN)")
    print("="*60)
    
    try:
        with open("prepare/results/dataset.json", "r", encoding="utf-8") as f:
            dataset = json.load(f)
    except Exception as e:
        print(f"Erro ao ler o dataset: {e}")
        return
        
    # Escolhendo o cenário "Photo sharing social network" (Primeiro do dataset)
    example = dataset[0]
    model_code = example["model"]
    # Vamos pegar o requisito 1 (this/inv1)
    req = example["requirements"][0]
    
    print(f"\n[Cenário Escolhido]: {example['example']}")
    print(f"[Requisito NL]: {req['description']}")
    print(f"[Predicado Alvo]: {req['pred']}")
    print("\n[Código Base (Signatures)]:")
    print("-" * 40)
    print(model_code.strip())
    print("-" * 40)
    
    input("\nPressione [ENTER] para iniciar a geração com Self-Reflection (Gemini Flash) + JPype...")
    
    print("\nIniciando orquestração dos agentes...\n")
    start_time = time.time()
    
    # Executa a pipeline
    result = run_pipeline(req['description'], model_code=model_code)
    
    end_time = time.time()
    
    print("="*60)
    print(f"✅ Execução Concluída em {end_time - start_time:.2f} segundos!")
    print("="*60)
    print("\n[Código Final Pós-Processado]:")
    print("-" * 40)
    print(result.get("processed", "Nenhum código gerado."))
    print("-" * 40)
    
    status = "✅ Válido (Passou na JVM)" if result.get("valid") else "❌ Inválido (Erros persistem)"
    print(f"\n[Status de Validação JVM]: {status}")
    
if __name__ == "__main__":
    run_demo()
