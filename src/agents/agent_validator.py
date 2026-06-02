"""
Agente 3 – Validator
Executa o Alloy Analyzer via JPype, coleta métricas de sintaxe,
consistência e validade, e decide se deve solicitar retry ao Agente 1.
"""
import jpype
import jpype.imports
from src.config import ALLOY_JAR_PATH

# Garante que a JVM inicie apenas uma vez durante as iterações em lote
if not jpype.isJVMStarted():
    jpype.startJVM(classpath=[ALLOY_JAR_PATH])

from edu.mit.csail.sdg.parser import CompUtil
from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod
from edu.mit.csail.sdg.alloy4 import A4Reporter

def run_alloy(alloy_code: str, tmp_file: str = "tmp_test.als") -> dict:
    syntax_ok = False
    consistent = False
    raw_output = ""
    
    # 1. Checagem de Sintaxe
    try:
        world = CompUtil.parseEverything_fromString(None, alloy_code)
        syntax_ok = True
    except Exception as e:
        raw_output = str(e)
        return {
            "syntax": False,
            "consistent": False,
            "valid": False,
            "raw_output": raw_output
        }
        
    # 2. Checagem de Consistência e Semântica (Oracle)
    try:
        commands = world.getAllCommands()
        options = A4Options()
        all_consistent = True
        
        for command in commands:
            solution = TranslateAlloyToKodkod.execute_command(A4Reporter(), world.getAllReachableSigs(), command, options)
            
            # Se a command espera SAT (1) mas é UNSAT
            if command.expects == 1 and not solution.satisfiable():
                all_consistent = False
                raw_output = f"O comando falhou: Esperava encontrar uma instância (expect 1), mas nenhuma foi encontrada."
                break
            # Se a command espera UNSAT (0) mas é SAT
            elif command.expects == 0 and solution.satisfiable():
                all_consistent = False
                raw_output = f"O comando falhou: Esperava NÃO encontrar instâncias (expect 0), mas um contraexemplo/instância foi encontrado."
                break
                
        consistent = all_consistent
        if consistent:
            raw_output = "Success"
            
    except Exception as e:
        raw_output = str(e)
        
    return {
        "syntax": syntax_ok,
        "consistent": consistent,
        "valid": syntax_ok and consistent,
        "raw_output": raw_output
    }
