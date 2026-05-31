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

def generate_test_cases(requirement: str) -> str:
    template = load_prompt_template()
    prompt = template.replace("{{REQUIREMENT}}", requirement)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text
