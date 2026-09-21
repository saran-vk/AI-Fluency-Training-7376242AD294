"""System 2: a rule-based workflow. Fixed if/else rules, no LLM at all."""
from config import MAINTENANCE_BY_TASK, QUESTIONS, SERVICE_HISTORY, VEHICLE


def _maintenance_status(task_name):
    item = MAINTENANCE_BY_TASK[task_name]
    due_at_km = item["last_done_km"] + item["interval_km"]
    remaining = due_at_km - VEHICLE["odometer_km"]
    return due_at_km, remaining


def workflow(question):
    text = question.lower()

    # Rule 1: total money spent on servicing
    if "total" in text and ("cost" in text or "spent" in text):
        total = sum(record["cost"] for record in SERVICE_HISTORY)
        return f"Total spent on servicing so far: Rs. {total:,}"

    # Rule 2: hard-coded rule, only knows about Engine Oil Change
    if "oil change" in text:
        due_at_km, remaining = _maintenance_status("Engine Oil Change")
        if remaining >= 0:
            return f"Engine Oil Change is due at {due_at_km:,} km ({remaining:,} km remaining)."
        return f"Engine Oil Change is overdue by {abs(remaining):,} km."

    # Rule 3: hard-coded rule, only knows about Brake Inspection
    if "brake inspection" in text:
        due_at_km, remaining = _maintenance_status("Brake Inspection")
        if remaining < 0:
            return f"Yes, Brake Inspection is overdue by {abs(remaining):,} km."
        return f"No, Brake Inspection is not overdue. {remaining:,} km remaining."

    return "Sorry, I do not have a rule for this type of question."


if __name__ == "__main__":
    print("\n=== SYSTEM 2: RULE-BASED WORKFLOW (no LLM) ===\n")
    for question in QUESTIONS:
        print("Q:", question)
        print("A:", workflow(question))
        print("-" * 70)
