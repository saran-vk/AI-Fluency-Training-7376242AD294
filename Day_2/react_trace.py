"""ReAct: run the tool-needing scenario question through the agent and
print its Thought/Action/Observation-style trace."""

from agent import agent

QUESTION = (
    "Which maintenance task is due soonest, how many km away is it, "
    "and what is the total amount spent on servicing so far?"
)

print("QUESTION:", QUESTION, "\n")
print("--- agent's actions and observations ---")
answer = agent(QUESTION, max_steps=8)
print("\nFINAL ANSWER:", answer)
