"""A question none of the three systems was designed for."""
from agent import agent
from workflow import workflow

QUESTION = "Which maintenance task is closest to being due, and how many km away is it?"

print("Q:", QUESTION)
print("\nWorkflow :", workflow(QUESTION))
print("\nAgent    :", agent(QUESTION))
