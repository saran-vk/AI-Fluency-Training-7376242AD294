# Day 3: From Prompt to Action (LLM vs LLM + one tool)

Scenario: a vehicle-maintenance assistant for a 2022 Honda City (odometer 38,450 km).
The maintenance records are private data that no public LLM has seen.

## Files
| File | Purpose |
|---|---|
| `tool.py` | The one tool, `get_maintenance_status(task)`, and its JSON schema |
| `no_tool.py` | Run A: the question goes straight to the LLM |
| `with_tool.py` | Run B: same LLM, same questions, with the tool available (one tool call, no loop) |
| `config.py` | Provider switch (ollama / groq / huggingface) and the shared questions |
| `data/` | `vehicle.json`, `maintenance_schedule.json` |
| `screenshots/` | Output screenshots of both runs |
| `analysis.md` | Written analysis |

## Run
```bash
pip install -r requirements.txt
cp .env.example .env        # pick a provider
python tool.py              # tests the tool alone, no LLM needed
python no_tool.py           # Run A  -> results_no_tool.txt
python with_tool.py         # Run B  -> results_with_tool.txt
```
