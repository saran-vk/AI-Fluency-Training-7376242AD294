"""Day 3: the ONE tool, plus the JSON schema the LLM reads to decide whether to call it."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "vehicle.json") as f:
    VEHICLE = json.load(f)

with open(DATA_DIR / "maintenance_schedule.json") as f:
    MAINTENANCE_BY_TASK = {item["task"]: item for item in json.load(f)}


def get_maintenance_status(task: str) -> str:
    """Return how many km remain (or how overdue) a maintenance task is.

    Always returns plain text, even on failure, so the model can read the message
    and recover instead of the program crashing.
    """
    item = MAINTENANCE_BY_TASK.get(task)
    if item is None:
        valid = ", ".join(MAINTENANCE_BY_TASK)
        return f"Unknown maintenance task: '{task}'. Valid tasks are: {valid}"
    due_at_km = item["last_done_km"] + item["interval_km"]
    remaining = due_at_km - VEHICLE["odometer_km"]
    if remaining >= 0:
        return f"{task}: due at {due_at_km} km, {remaining} km remaining"
    return f"{task}: OVERDUE by {abs(remaining)} km (was due at {due_at_km} km)"


# What the model actually sees: name + description + parameters
TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_maintenance_status",
        "description": (
            "Look up the owner's private vehicle records and return how many km remain "
            "until a maintenance task is due, or how many km it is overdue. "
            "Use this for any question about when a specific task is due or overdue."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "enum": list(MAINTENANCE_BY_TASK),
                    "description": "Exact name of the maintenance task",
                }
            },
            "required": ["task"],
        },
    },
}]

TOOL_FUNCTIONS = {"get_maintenance_status": get_maintenance_status}

if __name__ == "__main__":
    for name in [*MAINTENANCE_BY_TASK, "Wheel Alignment"]:
        print(f"get_maintenance_status({name!r}) ->", get_maintenance_status(name))
