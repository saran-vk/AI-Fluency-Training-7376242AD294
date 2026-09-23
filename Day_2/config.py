"""Shared configuration: chooses the LLM provider and loads the private vehicle data."""
import json
import os
from pathlib import Path

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

# ---------------------------------------------------------------------------
# Private vehicle-maintenance data that no public LLM has ever seen.
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "vehicle.json") as f:
    VEHICLE = json.load(f)

with open(DATA_DIR / "service_history.json") as f:
    SERVICE_HISTORY = json.load(f)

with open(DATA_DIR / "maintenance_schedule.json") as f:
    MAINTENANCE_SCHEDULE = json.load(f)

# Quick lookup: task name -> its schedule entry
MAINTENANCE_BY_TASK = {item["task"]: item for item in MAINTENANCE_SCHEDULE}

QUESTIONS = [
    "How many more kilometers until the next Engine Oil Change is due?",
    "What is the total amount spent on servicing this vehicle so far?",
    "Is the Brake Inspection overdue, and by how many km?",
    "Write a two-line reminder message for the vehicle owner about upcoming maintenance.",
]


def banner(system_name):
    print(f"\n=== {system_name} | provider: {PROVIDER} | model: {MODEL} ===\n")
