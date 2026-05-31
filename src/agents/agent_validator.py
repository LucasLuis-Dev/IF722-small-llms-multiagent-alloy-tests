"""
Agente 3 – Validator
Executa o Alloy Analyzer via JPype, coleta métricas de sintaxe,
consistência e validade, e decide se deve solicitar retry ao Agente 1.
"""
import subprocess
from src.config import ALLOY_JAR_PATH, MAX_RETRIES

def run_alloy(alloy_code: str, tmp_file: str = "tmp_test.als") -> dict:
    with open(tmp_file, "w") as f:
        f.write(alloy_code)
    try:
        result = subprocess.run(
            ["java", "-jar", ALLOY_JAR_PATH, tmp_file],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        syntax_ok = "Syntax error" not in output
        consistent = "No counterexample found" in output or "Instance found" in output
        return {
            "syntax": syntax_ok,
            "consistent": consistent,
            "valid": syntax_ok and consistent,
            "raw_output": output
        }
    except subprocess.TimeoutExpired:
        return {"syntax": False, "consistent": False, "valid": False, "raw_output": "timeout"}
