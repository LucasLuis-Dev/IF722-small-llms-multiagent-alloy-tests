"""
Agente 1 – Generator
Responsável por chamar o Gemini 2.0 Flash e gerar o rascunho
dos test cases Alloy a partir do requisito em linguagem natural.
"""
import google.generativeai as genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL, PROMPT_PATH

genai.configure(api_key=GEMINI_API_KEY)

def load_prompt_template() -> str:
    with open(PROMPT_PATH, "r") as f:
        return f.read()

def generate_test_cases(requirement: str, model_code: str) -> dict:
    template = load_prompt_template()
    prompt = template.replace("{{REQUIREMENT}}", requirement).replace("{{MODEL}}", model_code)
    
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    
    # Tentativa de extrair apenas blocos de código se houver, caso contrário pegar o texto todo
    import re
    code_blocks = re.findall(r'```alloy(.*?)```', response.text, re.DOTALL)
    if code_blocks:
        result_text = '\n'.join(code_blocks)
    else:
        result_text = response.text
        
    return {
        "instances": result_text,
        "input tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') and response.usage_metadata else 0,
        "output tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') and response.usage_metadata else 0
    }
