"""Direct prompting vs Chain-of-Thought on three reasoning-only questions.
No tools involved here - every number needed is inside the question."""

from config import client, MODEL, banner

QUESTIONS = [
    # 1. Multi-step arithmetic (uses the three actual service costs)
    "Your vehicle's three past services cost Rs. 4,500, Rs. 2,800, and "
    "Rs. 1,200. Your service center offers a 12% loyalty discount on the "
    "combined total of these three services. How much would the "
    "discounted total be?",
    # 2. Multi-step comparison (uses the actual schedule intervals/last-done km)
    "Your car is currently at 38,450 km. Brake Inspection is done every "
    "10,000 km and was last done at 30,000 km. Coolant Replacement is "
    "done every 40,000 km and was last done at 5,000 km. How many km "
    "away is each task from being due, and which one is due sooner?",
    # 3. Ordering / logic (uses the actual service records)
    "Your three past services were: Rs. 4,500 for a General Service "
    "that found 1 issue, Rs. 2,800 for an Oil Change that found 0 "
    "issues, and Rs. 1,200 for a Tyre Rotation that found 1 issue. "
    "Rank the three services from most expensive to least expensive, "
    "and name which one found no issues.",
]

DIRECT_PROMPT = "You are a helpful assistant. Give only the final answer. Do not explain."
COT_PROMPT = (
    "You are a helpful assistant. Solve the problem step by step. "
    "Number each step and show the calculation in that step. "
    "After the steps, write the last line exactly as: Final Answer: <answer>"
)


def ask(system_prompt, question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    banner("CHAIN-OF-THOUGHT COMPARISON")
    for number, question in enumerate(QUESTIONS, start=1):
        print("=" * 72)
        print(f"QUESTION {number}: {question}\n")
        print("--- WITHOUT CoT ---")
        print(ask(DIRECT_PROMPT, question), "\n")
        print("--- WITH CoT ---")
        print(ask(COT_PROMPT, question), "\n")
