"""System 3: an AI agent. LLM + tools + loop."""
import json

from config import MODEL, QUESTIONS, banner, client
from tools import TOOL_FUNCTIONS, TOOLS

SYSTEM_PROMPT = (
    "You are a vehicle maintenance assistant. Never guess a figure: always use the "
    "tools to look up vehicle info, maintenance status, or service cost. Use the "
    "calculator for any arithmetic. If no tool is needed, answer directly."
)


def agent(question, max_steps=6, verbose=True):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for step in range(1, max_steps + 1):
        # 1. REASON: ask the LLM what to do next
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0)
        message = response.choices[0].message

        # 2. If no tool is requested, the LLM has finished
        if not message.tool_calls:
            return message.content.strip()

        messages.append({
            "role": "assistant", "content": message.content or "",
            "tool_calls": [{"id": call.id, "type": "function",
                             "function": {"name": call.function.name,
                                          "arguments": call.function.arguments}}
                            for call in message.tool_calls]})

        # 3. ACT and OBSERVE: run each tool, send the result back
        for call in message.tool_calls:
            name = call.function.name
            arguments = json.loads(call.function.arguments or "{}")
            function = TOOL_FUNCTIONS.get(name)
            result = function(**arguments) if function else f"Unknown tool: {name}"
            if verbose:
                print(f"  step {step}: {name}({arguments}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    return "Stopped: maximum steps reached without a final answer."


if __name__ == "__main__":
    banner("SYSTEM 3: AI AGENT")
    for question in QUESTIONS:
        print("Q:", question)
        print("A:", agent(question))
        print("-" * 70)
