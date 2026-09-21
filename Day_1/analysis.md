# Vehicle Maintenance Tracker — Chatbot vs Workflow vs Agent

## 1. Scenario

This project uses a small set of private vehicle-maintenance data for a
Honda City (vehicle ID VH1024, 2022 model, petrol, current odometer 38,450
km) that no public LLM has ever seen: a service history of three past
visits with their costs and issues found, and a maintenance schedule of
five recurring tasks (Engine Oil Change, Brake Inspection, Air Filter
Replacement, Tyre Rotation, Coolant Replacement), each with an interval in
kilometers and the odometer reading it was last done at. The goal is to
answer questions like "how many km until the next oil change" or "what's
the total spent on servicing" using three different approaches — a plain
chatbot, a rule-based workflow, and an AI agent — and compare how each one
handles this private data.

## 2. Explanation of each approach

### 2.1 Plain chatbot

The chatbot sends the question directly to the LLM with no data and no
tools — it can only answer from whatever general knowledge it was trained
on. It has no way to access this vehicle's actual records.

Running `chatbot.py` confirmed this clearly. For Q1 ("How many more
kilometers until the next Engine Oil Change is due?"), the model didn't
know the vehicle's actual numbers, so instead of guessing a fee like the
lab manual's example, it asked the user to supply the mileage and interval
itself, then worked out a made-up example (15,000 km − 10,000 km = 5,000
km) that has nothing to do with the real vehicle. For Q2 (total spent) it
was honest that it has no access to the maintenance records and suggested
the user check them manually. For Q3 (Brake Inspection overdue) it gave a
generic multi-step explanation of *how* one would check, using industry-
average intervals (12,000–15,000 km) instead of this vehicle's actual
10,000 km interval — again, plausible-sounding but not grounded in the
real data. Only Q4 (write a two-line reminder message) was handled
reasonably, because it needs no private data at all — though the model
oddly inserted a Chinese character into the English sentence, which is
its own small reliability quirk worth noting.

The key observation: the chatbot did not confidently fabricate a wrong
number the way the lab manual's fee-example chatbot did. Instead it
mostly recognized it lacked the data and asked for it or explained a
generic method. This is arguably safer than confident hallucination, but
it is still useless for actually answering the question — it just shifts
the burden of doing the assistant's job back onto the user.

### 2.2 Rule-based workflow

The workflow (`workflow.py`) contains no LLM at all — just fixed Python
if/else logic. It has three hard-coded rules: one that matches "total" +
"cost"/"spent" and sums the service history costs, one that matches "oil
change" and computes the Engine Oil Change status, and one that matches
"brake inspection" and computes that task's status. Anything else falls
through to a fixed refusal message.

Running it gave exact, instant, correct answers for all three data
questions:
- Q1: "Engine Oil Change is due at 40,000 km (1,550 km remaining)."
- Q2: "Total spent on servicing so far: Rs. 8,500"
- Q3: "No, Brake Inspection is not overdue. 1,550 km remaining."

These are trivially verifiable: Engine Oil Change was last done at 35,000
km with a 5,000 km interval → due at 40,000 km; current odometer 38,450 km
→ 1,550 km remaining. Brake Inspection was last done at 30,000 km with a
10,000 km interval → also due at 40,000 km → also 1,550 km remaining (the
two tasks happen to be tied). Total cost 4,500 + 2,800 + 1,200 = 8,500.
All correct.

Q4 (the reminder message) hit the fallback: "Sorry, I do not have a rule
for this type of question" — exactly as expected, since no rule was ever
written for open-ended text generation. The workflow's reliability comes
directly from its rigidity: it is only ever as capable as the specific
rules a programmer wrote in advance.

### 2.3 AI agent

The agent (`agent.py`) combines the LLM with the five tools in `tools.py`
(`get_vehicle_info`, `list_maintenance_tasks`, `get_maintenance_status`,
`get_total_service_cost`, `calculator`) inside a reason → act → observe
loop. For each question it decides which tool(s) to call, reads the
result, and either calls another tool or gives a final answer.

Tracing the printed steps:
- **Q1**: called `get_maintenance_status('Engine Oil Change')`, got "due at
  40000 km, 1550 km remaining", and correctly reported "due in 1550
  kilometers." Correct.
- **Q2**: called `get_total_service_cost()`, got `8500`, and answered
  "$8500" (using a dollar sign instead of Rs., a minor localization slip,
  but the number itself is correct).
- **Q3**: called `get_maintenance_status('Brake Inspection')`, which
  returned "Brake Inspection: due at 40000 km, 1550 km remaining" — i.e.
  the tool itself said it is not overdue. But the agent's final answer was
  "The Brake Inspection is 1550 km overdue," which directly contradicts
  the data it just retrieved. This is the single most important
  observation in this whole exercise: the agent called the correct tool
  and received the correct data, but still produced a wrong final answer
  by misreading "remaining" as "overdue" during its own reasoning step.
  The workflow, using the exact same underlying numbers, got this one
  right — showing that having the right data is not the same as reasoning
  correctly about it.
- **Q4**: called `list_maintenance_tasks()` and then improvised a reminder
  naming the Engine Oil Change as the most urgent task — a reasonable
  answer that a rule-based system could never produce, since it requires
  generating fluent, context-aware text.

For the challenge question ("Which maintenance task is closest to being
due, and how many km away is it?") the workflow immediately failed with
its fixed refusal message, since no rule was written for cross-task
comparison. The agent's trace showed it first guessed a task name that
does not exist ("next_maintenance"), self-corrected by calling
`list_maintenance_tasks`, then checked only one of the five tasks (Engine
Oil Change) before answering "Engine Oil Change, 1,550 km away." This
happens to be correct — but only because Engine Oil Change and Brake
Inspection are tied at exactly 1,550 km remaining, and the agent never
checked Air Filter Replacement, Tyre Rotation, or Coolant Replacement at
all. A properly thorough agent should have called `get_maintenance_status`
on every task returned by `list_maintenance_tasks` before comparing. This
is a second real reliability gap: the agent reached the right answer
through incomplete reasoning, which is a dangerous pattern in an
unsupervised real product, since it will not always get lucky.


## 3. Comparison table

| Basis for comparison     | Plain chatbot                                                        | Rule-based workflow                                              | AI agent                                                                 |
|---------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Flexibility               | High — answers any phrasing, but only from general knowledge          | None — only the exact phrasings its rules were written for match  | High — can combine tools in new ways for questions it wasn't explicitly coded for |
| Decision-making           | None real — just generates plausible text                             | None — fixed if/else, no judgment involved                        | Some — chooses which tool(s) to call and in what order, but can misjudge results |
| Tool usage                | None                                                                   | None (uses plain Python logic instead of callable tools)          | Full — calls `get_maintenance_status`, `get_total_service_cost`, `list_maintenance_tasks`, `calculator` as needed |
| Private-data access       | None — has no way to see the vehicle's records at all                 | Full — reads the JSON data directly through Python                | Full — reads the same data, but only through the tools it chooses to call    |
| Multi-step task handling  | None — one-shot text generation                                       | None — one rule fires per question, no chaining                   | Yes — the challenge question needed multiple sequential tool calls           |
| Automation                | Fully automated, but not useful without the real data                 | Fully automated for the exact questions it was built for          | Fully automated and adapts to new question types, at the cost of predictability |
| Reliability               | Low on data questions (asks user for info or gives generic advice); safe on non-data questions | Very high — always exact and repeatable for its coded rules; hard failure otherwise | Mixed — correct on 3 of 4 main questions, but produced a data-contradicting answer on Q3 and an incomplete-but-lucky answer on the challenge question |

## 4. Suitability analysis

For this specific scenario — a personal vehicle maintenance tracker — the
rule-based workflow is the most suitable approach for the core, expected
questions (oil change status, brake inspection status, total cost),
because these are a small, fixed, well-known set of calculations where
getting the number wrong has real consequences. Missing a brake inspection
because the assistant said "not overdue" when it actually was — as
happened here with the agent — is a safety-relevant mistake, not just an
inconvenience. The workflow's rigidity is a feature here, not a
limitation, because the set of questions a car owner realistically asks
about scheduled maintenance is small and predictable.

However, the workflow's inability to handle anything outside its coded
rules — the reminder message, or comparing across all five tasks to find
the one closest to due — is a real gap that only the agent can fill. The
ideal real-world design would route the fixed, safety-relevant questions
(oil change status, brake inspection status, cost totals) to the
rule-based workflow for guaranteed correctness, and route open-ended or
exploratory questions (reminders, summaries, "what should I prioritize")
to the agent, while adding a verification step so the agent's final answer
is checked against the raw tool output before being shown to the user —
which would have caught the Q3 contradiction in this exact run.

## 5. Conclusion

A plain chatbot is the right choice when the task needs no private or
current data at all — general explanations, tone, phrasing help, or
one-off creative text like a reminder message. It should never be trusted
with structured private data, because even when it doesn't confidently
hallucinate a number, it also can't produce a correct one.

A rule-based workflow is the right choice when the set of possible
questions is small, well-understood in advance, and the cost of an
incorrect answer is high — safety, billing, or scheduling calculations
where "always exactly right or a clear refusal" matters more than handling
every possible phrasing.

An AI agent is worth its unpredictability when the task requires combining
multiple pieces of data or multiple steps that cannot all be anticipated
in advance — like comparing five different maintenance tasks to find the
most urgent one, or generating a naturally worded summary from raw data.
But as this run showed, an agent can retrieve the exactly correct data and
still misstate it in its final answer, or reach a correct conclusion
through incomplete reasoning that happened to get lucky. Any real
deployment of an agent on data as consequential as vehicle safety
maintenance should include a way to double-check the agent's stated
conclusion against the raw tool output it was given, rather than trusting
the LLM's final sentence at face value.
