"""
Agente 1 – Generator
Responsável por chamar o Gemini 2.0 Flash e gerar o rascunho
dos test cases Alloy a partir do requisito em linguagem natural.
"""
import google.generativeai as genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL, PROMPT_PATH, USE_ORACLE_IN_REFLECTION

genai.configure(api_key=GEMINI_API_KEY)

def load_prompt_template() -> str:
    with open(PROMPT_PATH, "r") as f:
        return f.read()

def _extract_model_vocabulary(model_code: str) -> str:
    import re

    sigs = re.findall(r"\b(?:abstract\s+)?(?:one\s+)?sig\s+(\w+)(?:\s+extends\s+\w+|\s+in\s+\w+)?\s*(?:\{([^}]*)\})?", model_code)
    if not sigs:
        return "No signatures or fields could be extracted automatically; rely on the base model exactly as provided."

    lines = []
    for sig_name, body in sigs:
        fields = []
        if body:
            for field_name, field_type in re.findall(r"(\w+)\s*:\s*([^,\n}]+)", body):
                fields.append(f"{field_name}: {field_type.strip()}")
        if fields:
            lines.append(f"- {sig_name}: fields {', '.join(fields)}")
        else:
            lines.append(f"- {sig_name}: no declared fields")
    return "\n".join(lines)


def _build_semantic_guidance(requirement: str, model_code: str, oracle: str = None) -> str:
    sections = [
        "\n\n--- SEMANTIC GUIDANCE ---",
        "Do not only repair syntax. Preserve the formal meaning of the natural-language requirement.",
        f"\n[Natural-language requirement]\n{requirement}",
        "\n[Available model vocabulary]\n"
        f"{_extract_model_vocabulary(model_code)}",
    ]

    if USE_ORACLE_IN_REFLECTION and oracle:
        sections.append(
            "\n[Reference oracle predicate body]\n"
            "Use this only to understand the intended semantics. Do not repeat it as a fact or base-model signature.\n"
            f"```alloy\n{oracle}\n```"
        )

    sections.append(
        "\n[Relational reasoning checklist]\n"
        "- Use only signatures, fields, and aliases that exist in the base model.\n"
        "- Do not invent helper predicates such as Requirement, ValidRequirement, Positive1, NoSelfFollow, or similar names unless they are declared in the generated output before use.\n"
        "- Respect relation direction. For a field like User.posts: set Photo, use u.posts for photos posted by a user and posts.p for users that post photo p.\n"
        "- Match quantifiers and cardinality to the requirement: one means exactly one, lone means at most one, some means at least one, no means none.\n"
        "- For negative tests with expect 0, encode a real violation of the requirement, not another valid instance.\n"
        "- Keep generated commands self-contained and compatible with the base model."
    )
    return "\n".join(sections)

def _build_reflection_context(
    requirement: str,
    model_code: str,
    oracle: str = None,
    previous_code: str = None,
    previous_error: str = None,
    previous_processed_code: str = None,
    previous_full_alloy_code: str = None,
    previous_validation: dict = None,
) -> str:
    sections = [
        "\n\n--- SELF-REFLECTION CONTEXT ---",
        "The previous attempt failed validation. Use all context below to generate a corrected full set of Alloy test commands.",
    ]
    sections.append(_build_semantic_guidance(requirement, model_code, oracle))

    if previous_code:
        sections.append(
            "\n[Previous raw LLM output]\n"
            f"```alloy\n{previous_code}\n```"
        )

    if previous_processed_code:
        sections.append(
            "\n[Previous output after post-processing]\n"
            f"```alloy\n{previous_processed_code}\n```"
        )

    if previous_full_alloy_code:
        sections.append(
            "\n[Complete Alloy code submitted to the Analyzer]\n"
            f"```alloy\n{previous_full_alloy_code}\n```"
        )

    if previous_validation:
        sections.append(
            "\n[Validation result]\n"
            f"syntax: {previous_validation.get('syntax')}\n"
            f"consistent: {previous_validation.get('consistent')}\n"
            f"valid: {previous_validation.get('valid')}"
        )

    if previous_error:
        sections.append(f"\n[Alloy Analyzer error/output]\n{previous_error}")

    sections.append(
        "\nFix the syntax, consistency, or structural problems while preserving the original requirement, model, and output rules. "
        "Generate only the corrected Alloy test commands, without repeating the base model signatures."
    )
    return "\n".join(sections)


def generate_test_cases(
    requirement: str,
    model_code: str,
    oracle: str = None,
    previous_code: str = None,
    previous_error: str = None,
    previous_processed_code: str = None,
    previous_full_alloy_code: str = None,
    previous_validation: dict = None,
) -> dict:
    template = load_prompt_template()
    prompt = template.replace("{{REQUIREMENT}}", requirement).replace("{{MODEL}}", model_code)
    
    if previous_code and previous_error:
        prompt += _build_reflection_context(
            requirement=requirement,
            model_code=model_code,
            oracle=oracle,
            previous_code=previous_code,
            previous_error=previous_error,
            previous_processed_code=previous_processed_code,
            previous_full_alloy_code=previous_full_alloy_code,
            previous_validation=previous_validation,
        )

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
