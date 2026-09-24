"""Shared configuration: chooses the LLM provider (same switch as Day 2) and holds the questions."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads the .env file in this folder

PROVIDER = os.getenv("PROVIDER", "ollama").strip().lower()

if PROVIDER == "ollama":  # Option A: local model, no key
    BASE_URL = "http://localhost:11434/v1"
    API_KEY = "ollama"  # any text works for Ollama
    MODEL = os.getenv("MODEL", "qwen3:4b")
elif PROVIDER == "groq":  # Option B: free cloud key
    BASE_URL = "https://api.groq.com/openai/v1"
    API_KEY = os.getenv("GROQ_API_KEY")
    MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")
elif PROVIDER == "huggingface":  # Option C: free cloud key
    BASE_URL = "https://router.huggingface.co/v1"
    API_KEY = os.getenv("HF_TOKEN")
    MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")
else:
    raise SystemExit(f"Unknown PROVIDER '{PROVIDER}'. Use ollama, groq or huggingface.")

if not API_KEY:
    raise SystemExit(f"No API key found for PROVIDER={PROVIDER}. Check your .env file.")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# Same base prompt for both runs, so the ONLY difference is tool access.
SYSTEM_PROMPT = "You are a vehicle maintenance assistant for the owner's Honda City."

# Q1-Q3 need the private records + arithmetic. Q4-Q5 are general knowledge.
QUESTIONS = [
    "How many more kilometers until the next Engine Oil Change is due?",
    "Is the Brake Inspection overdue, and by how many km?",
    "How many km are left before the Air Filter Replacement is due?",
    "Why does engine oil need to be changed regularly?",
    "What does a tyre rotation do, and why is it done?",
]


def banner(title):
    print(f"\n=== {title} | provider: {PROVIDER} | model: {MODEL} ===\n")
