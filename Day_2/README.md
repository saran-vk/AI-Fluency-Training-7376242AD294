# Vehicle Maintenance Assistant — Direct vs CoT vs ReAct

Day 2 Task: comparing direct prompting,
Chain-of-Thought prompting, and a ReAct agent on a scenario of my own
— a vehicle maintenance assistant built on real vehicle, service
history, and maintenance schedule data.

## Scenario

**Vehicle:** Honda City (2022), current odometer 38,450 km.

- `data/vehicle.json` — current vehicle state (odometer, fuel type)
- `data/service_history.json` — 3 past services with cost and issues found
- `data/maintenance_schedule.json` — 5 recurring tasks, each with an
  interval_km and the odometer reading it was last done at

**Tool-needing question** (needs live data, can't be answered from
parametric knowledge alone):
> "Which maintenance task is due soonest, how many km away is it, and
> what is the total amount spent on servicing so far?"

**Reasoning-only questions** (all data is inside the question itself —
no tool required, but every number comes from the actual JSON files):
1. Arithmetic: 12% loyalty discount on the total of the three real service costs
2. Multi-step comparison: km remaining until Brake Inspection vs. Coolant Replacement are due
3. Ordering/logic: rank the three real service records by cost and identify which found no issues

## Files

| File | Role |
|---|---|
| `config.py` | Picks the LLM provider (Ollama/Groq/Hugging Face via `.env`), loads the three JSON files from `data/`, defines `client`, `MODEL`, `banner` |
| `tools.py` | `get_vehicle_info`, `list_maintenance_tasks`, `get_maintenance_status(task)`, `get_total_service_cost`, `calculator` (safe AST-based, no `eval`) |
| `agent.py` | ReAct loop: reasons, calls tools, feeds results back, repeats until a final answer or `max_steps` |
| `data/` | `vehicle.json`, `service_history.json`, `maintenance_schedule.json` |
| `react_trace.py` | **Approach 3 (ReAct):** runs the tool-needing question through `agent()`, printing every step |
| `cot_compare.py` | **Approaches 1 & 2 (Direct vs CoT):** asks all three reasoning-only questions both ways, `temperature=0` |
| `self_consistency.py` | Runs the first CoT question 5× at `temperature=0.8` and takes the majority answer |
| `analysis.md` | Full written analysis: explanation of each approach, comparison table, self-consistency observation, suitability analysis, conclusion |
| `screenshots/` | Terminal output of all three scripts running |

## Setup

```bash
pip install openai python-dotenv
```

## How to run

```bash
python react_trace.py        # Approach 3: ReAct on the tool-needing question
python cot_compare.py        # Approaches 1 & 2: direct vs CoT on 3 reasoning questions
python self_consistency.py   # Self-consistency: 5 CoT runs + majority vote
```

## Results

- **`react_trace.py`** — the agent called `list_maintenance_tasks`,
  then `get_maintenance_status` for each of the 5 tasks, then
  `get_total_service_cost` (7 tool calls total). Correctly found
  **Engine Oil Change and Brake Inspection tied, both due at 40,000 km
  → 1,550 km away**, and correctly totalled **8,500** spent on
  servicing so far.
- **`cot_compare.py`** — on `gpt-oss-120b`, direct prompting and CoT
  both answered all 3 reasoning questions correctly: Q1 = **7,480**,
  Q2 = **Brake Inspection due sooner (1,550 km) vs. Coolant Replacement
  (6,550 km)**, Q3 = **General Service > Oil Change > Tyre Rotation by
  cost; Oil Change found no issues**. CoT showed its full step-by-step
  working in every case; direct prompting gave no visible reasoning.
- **`self_consistency.py`** — all 5 runs at `temperature=0.8` on Q1
  converged to the same number, **7,480**; the majority-vote count
  showed only "1 of 5" due to formatting differences in the raw
  strings (see `analysis.md` for the full breakdown), not an actual
  disagreement in the model's reasoning.

Full discussion in [`analysis.md`](./analysis.md).
