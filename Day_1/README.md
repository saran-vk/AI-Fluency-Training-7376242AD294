# Day 1 — Vehicle Maintenance Tracker (Chatbot vs Workflow vs Agent)

## Setup

1. Open this `day1_lab` folder in VS Code (File > Open Folder).
2. Create and select a virtual environment:
   - Press `Ctrl+Shift+P` → `Python: Create Environment` → `Venv` → pick your Python 3.11+.
3. Open a terminal (`` Ctrl+` ``) and install packages:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env`:
   ```
   copy .env.example .env
   ```
5. Run ollama models or use API keys through th .env file

## Run, in this order

```
python check_setup.py
python chatbot.py
python workflow.py
python tools.py
python agent.py
python challenge.py
```


