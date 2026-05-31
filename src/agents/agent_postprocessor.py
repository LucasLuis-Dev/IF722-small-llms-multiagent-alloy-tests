"""
Agente 2 – Post-Processor
Aplica regras de correção sintática nas saídas brutas do Gemini
para aumentar a taxa de validade sintática antes da validação.
"""
import re

def fix_run_command(code: str) -> str:
    """Garante que os blocos run tenham escopo definido."""
    # Se terminar em 'run { ... } expect 1' sem for
    # Adicionar for 4 antes do expect se estiver faltando
    # (Simplificado: só tenta garantir sintaxe básica)
    return code

def fix_none_typing(code: str) -> str:
    """Substitui 'none' solto por 'none -> none' em relações binárias."""
    # Como não sabemos a aridade real aqui, substituímos heuristincamente
    # apenas quando = none
    # Isso pode causar erros se for none unitário, mas é a regra 3.
    # Vou deixar o replace apenas onde for = none solto
    # code = re.sub(r'(?<!\w)none(?!\s*->)', 'none -> none', code)
    # Na verdade, a aridade correta é inferida pelo AlloyAnalyzer
    return code

def strip_base_model_signatures(code: str) -> str:
    """Remove repetições de declarações sig, open ou abstract sig."""
    # LLMs gostam de cuspir o modelo base de novo.
    lines = code.splitlines()
    new_lines = []
    in_sig = False
    for line in lines:
        if re.match(r'^(abstract\s+)?sig\s+', line.strip()) or line.strip().startswith('open util/'):
            in_sig = True
            if '{' in line and '}' in line:
                in_sig = False
            continue
        if in_sig:
            if '}' in line:
                in_sig = False
            continue
        new_lines.append(line)
    return "\n".join(new_lines)

def postprocess(raw_code: str) -> str:
    code = strip_base_model_signatures(raw_code)
    # Comentando as regras antigas que quebram blocos múltiplos:
    # code = fix_run_command(code)
    # code = fix_none_typing(code)
    # code = remove_duplicate_preds(code)
    # code = ensure_single_run(code)
    return code.strip()
