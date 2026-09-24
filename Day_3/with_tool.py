"""Day 3, run B: the same LLM with ONE tool. A single tool call, no loop."""
import json

from config import MODEL, QUESTIONS, SYSTEM_PROMPT, banner, client
from tool import TOOL_FUNCTIONS, TOOLS

TOOL_PROMPT = SYSTEM_PROMPT + (
    " Never guess a figure about this vehicle: use the tool to look it up. "
    "If no tool is needed, answer directly."
)


def ask_with_tool(question):
    """Returns (list of tool calls made, final answer)."""
    messages = [{"role": "system", "content": TOOL_PROMPT},
                {"role": "user", "content": question}]

    # 1. The model reads the question + the tool schema and decides
    first = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOLS, temperature=0).choices[0].message
    if not first.tool_calls:  # no tool needed: it answers directly
        return [], (first.content or "").strip()

    messages.append({
        "role": "assistant", "content": first.content or "",
        "tool_calls": [{"id": c.id, "type": "function",
                         "function": {"name": c.function.name,
                                      "arguments": c.function.arguments}}
                        for c in first.tool_calls]})

    # 2. Our code runs the requested function(s) and hands back the plain-text result
    calls = []
    for call in first.tool_calls:
        arguments = json.loads(call.function.arguments or "{}")
        function = TOOL_FUNCTIONS.get(call.function.name)
        result = function(**arguments) if function else f"Unknown tool: {call.function.name}"
        calls.append(f"{call.function.name}({arguments}) -> {result}")
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    # 3. The model turns the tool result into the final answer
    final = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOLS, temperature=0).choices[0].message
    return calls, (final.content or "").strip()


if __name__ == "__main__":
    banner("RUN B: LLM WITH ONE TOOL")
    for number, question in enumerate(QUESTIONS, 1):
        calls, answer = ask_with_tool(question)
        shown = "\n".join(f"  TOOL CALL: {c}" for c in calls) or "  TOOL CALL: (none)"
        print(f"Q{number}: {question}\n{shown}\nA{number}: {answer}\n" + "-" * 70)
