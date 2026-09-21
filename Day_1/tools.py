"""Tools the agent is allowed to use, plus their JSON Schema descriptions."""
import ast
import operator

from config import MAINTENANCE_BY_TASK, MAINTENANCE_SCHEDULE, SERVICE_HISTORY, VEHICLE


def get_vehicle_info() -> str:
    """Return the vehicle's basic details and current odometer reading."""
    return (
        f"{VEHICLE['vehicle']} ({VEHICLE['year']}, {VEHICLE['fuel_type']}), "
        f"ID {VEHICLE['vehicle_id']}, odometer {VEHICLE['odometer_km']} km"
    )


def list_maintenance_tasks() -> str:
    """List every maintenance task tracked for this vehicle."""
    return ", ".join(MAINTENANCE_BY_TASK.keys())


def get_maintenance_status(task: str) -> str:
    """Get how many km remain (or how overdue) a maintenance task is, by task name."""
    item = MAINTENANCE_BY_TASK.get(task)
    if item is None:
        return f"Unknown maintenance task: {task}"
    due_at_km = item["last_done_km"] + item["interval_km"]
    remaining = due_at_km - VEHICLE["odometer_km"]
    if remaining >= 0:
        return f"{task}: due at {due_at_km} km, {remaining} km remaining"
    return f"{task}: OVERDUE by {abs(remaining)} km (was due at {due_at_km} km)"


def get_total_service_cost() -> str:
    """Sum the cost of every past service in the vehicle's history."""
    return str(sum(record["cost"] for record in SERVICE_HISTORY))


# A safe calculator: only numbers and + - * / ( ) are allowed. Never use eval().
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression such as (38450 - 35000)."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}"


TOOL_FUNCTIONS = {
    "get_vehicle_info": get_vehicle_info,
    "list_maintenance_tasks": list_maintenance_tasks,
    "get_maintenance_status": get_maintenance_status,
    "get_total_service_cost": get_total_service_cost,
    "calculator": calculator,
}

# These descriptions are what the LLM reads when deciding which tool to call
TOOLS = [
    {"type": "function", "function": {
        "name": "get_vehicle_info",
        "description": "Get the vehicle's basic details and current odometer reading.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "list_maintenance_tasks",
        "description": "List every maintenance task tracked for this vehicle.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "get_maintenance_status",
        "description": "Get km remaining (or how overdue) a maintenance task is, by exact task name.",
        "parameters": {"type": "object",
                        "properties": {"task": {"type": "string"}},
                        "required": ["task"]}}},
    {"type": "function", "function": {
        "name": "get_total_service_cost",
        "description": "Get the total amount spent across all past services.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression using + - * / and brackets.",
        "parameters": {"type": "object",
                        "properties": {"expression": {"type": "string"}},
                        "required": ["expression"]}}},
]

if __name__ == "__main__":
    print("get_vehicle_info() ->", get_vehicle_info())
    print("list_maintenance_tasks() ->", list_maintenance_tasks())
    print("get_maintenance_status('Engine Oil Change') ->", get_maintenance_status("Engine Oil Change"))
    print("get_maintenance_status('Brake Inspection') ->", get_maintenance_status("Brake Inspection"))
    print("get_total_service_cost() ->", get_total_service_cost())
    print("calculator('(38450 - 35000)') ->", calculator("(38450 - 35000)"))
