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

def generate_test_cases(requirement: str, model_code: str, previous_code: str = None, previous_error: str = None) -> dict:
    template = load_prompt_template()
    prompt = template.replace("{{REQUIREMENT}}", requirement).replace("{{MODEL}}", model_code)
    
    if previous_code and previous_error:
        prompt += f"\n\n--- SELF-REFLECTION ---\nIn your previous attempt, you generated this code:\n```alloy\n{previous_code}\n```\nBut the Alloy Analyzer returned the following error:\n{previous_error}\nPlease fix the syntax or structural errors and generate the updated code. Ensure you strictly follow all original rules."

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
