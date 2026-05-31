"""
Agente 2 – Post-Processor
Aplica regras de correção sintática nas saídas brutas do Gemini
para aumentar a taxa de validade sintática antes da validação.
"""
import re

def fix_run_command(code: str) -> str:
    """Garante que o bloco run tenha escopo definido."""
    if re.search(r'run\s+\w+\s*$', code, re.MULTILINE):
        code = re.sub(r'(run\s+\w+)\s*$', r'\1 for 4', code, flags=re.MULTILINE)
    return code

def fix_none_typing(code: str) -> str:
    """Substitui 'none' solto por 'none -> none' em relações binárias."""
    code = re.sub(r'(?<!\w)none(?!\s*->)', 'none -> none', code)
    return code

def remove_duplicate_preds(code: str) -> str:
    """Remove predicados duplicados."""
    seen = set()
    result = []
    for line in code.splitlines():
        if line.strip() not in seen:
            seen.add(line.strip())
            result.append(line)
    return "\n".join(result)

def ensure_single_run(code: str) -> str:
    """Garante que existe exatamente um comando run."""
    runs = re.findall(r'^run\s+.*$', code, re.MULTILINE)
    if len(runs) > 1:
        for r in runs[:-1]:
            code = code.replace(r, "", 1)
    return code

def postprocess(raw_code: str) -> str:
    code = fix_run_command(raw_code)
    code = fix_none_typing(code)
    code = remove_duplicate_preds(code)
    code = ensure_single_run(code)
    return code.strip()
