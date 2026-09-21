# Vehicle Maintenance Tracker — Chatbot vs Workflow vs Agent

> Fill this in after you've actually run chatbot.py, workflow.py, agent.py, and
> challenge.py, and looked at the real output on your machine. Write in full
> paragraphs, not bullet fragments — this file is graded on its own, without
> your code.

## 1. Scenario

Briefly describe the scenario in your own words: a Honda City's private
maintenance data (odometer, service history, upcoming maintenance schedule)
that no public LLM has ever seen.

## 2. Explanation of each approach

### 2.1 Plain chatbot
- What data can it access? (Hint: none — it only has what's in its training data.)
- What happened when you ran chatbot.py on the fee/km questions? Did it
  guess numbers? Did it admit it didn't know?
- Where exactly did it go wrong on your questions 1–3, and why did it get
  question 4 right?

### 2.2 Rule-based workflow
- What rules did workflow.py actually contain? (Two hard-coded ones:
  Engine Oil Change and Brake Inspection, plus a total-cost rule.)
- Why did it succeed instantly and consistently on the questions it was
  built for?
- Why did it fail on the reminder-message question, and on the challenge
  question?

### 2.3 AI agent
- Walk through what agent.py printed for one question — which tools did
  it call, in what order?
- How did the agent handle the challenge question that workflow.py could
  not answer at all?
- Did the agent ever call the wrong tool or hallucinate a number instead
  of calling a tool? Note it if so — that's a real observation, not a
  failure to hide.

## 3. Comparison table

| Basis for comparison   | Plain chatbot | Rule-based workflow | AI agent |
|-------------------------|---------------|----------------------|----------|
| Flexibility              |               |                      |          |
| Decision-making          |               |                      |          |
| Tool usage                |               |                      |          |
| Private-data access      |               |                      |          |
| Multi-step task handling |               |                      |          |
| Automation                |               |                      |          |
| Reliability               |               |                      |          |

## 4. Suitability analysis

Which of the three would you actually deploy for a real vehicle-service
reminder app used by hundreds of car owners? Justify using rows from your
table above — e.g. is reliability more important than flexibility for a
maintenance reminder, or the reverse?

## 5. Conclusion

In general (not just for this scenario) — when is a plain chatbot enough?
When does a rule-based workflow beat an agent? When is an agent worth its
unpredictability? Write 2–3 sentences per case.
