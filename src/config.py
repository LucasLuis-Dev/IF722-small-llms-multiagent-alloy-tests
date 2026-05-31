"""
Configs: modelo, API key, paths
"""

import os

# Configurações do LLM
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
API_KEY = os.getenv("API_KEY", "")

# Caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOY_JAR_PATH = os.path.join(BASE_DIR, "alloytools.jar")
