import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
ALLOY_JAR_PATH = "alloytools.jar"
PROMPT_PATH = "prompts/prompt_few_gemini.txt"
DATA_RAW_PATH = "data/raw/"
DATA_PROCESSED_PATH = "data/processed/"
MAX_RETRIES = 3
