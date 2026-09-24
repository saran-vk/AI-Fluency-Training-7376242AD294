# Day 3 Analysis: From Prompt to Action

**Scenario.** I built a small vehicle-maintenance assistant for a 2022 Honda City whose odometer currently reads 38,450 km. The car's service records live in two private JSON files: `vehicle.json` (current odometer) and `maintenance_schedule.json` (each task, its interval in km, and the odometer reading at which it was last done). No public language model has ever seen these files. Some questions about the car can only be answered from them, for example "How many km until my next oil change?", and others are ordinary car knowledge, for example "Why does engine oil need changing?". That mix lets me compare a plain LLM prompt with the same LLM given one tool, `get_maintenance_status(task)`, which reads the files and does the arithmetic. Both runs used the same model, the same base system prompt and the same five questions, so tool access is the only difference.

**Model used:** *(write your provider and model here, exactly as printed in the banner line when you ran the scripts)*

## 1. Explanation of Concepts

### 1.1 What is a Large Language Model?

A Large Language Model is a neural network trained on a huge amount of text to predict the next token in a sequence. Because that training text contained encyclopedias, manuals, forums and code, the model picks up a lot of general knowledge, and it can explain, summarise, reason and write fluently. In my scenario, that is why a plain LLM can be trusted to explain why engine oil degrades and needs replacing, or what a tyre rotation does: those facts are stable, widely written about, and sit inside its trained knowledge. It answers immediately, from memory, with no way to look anything up.

It starts to go wrong when the answer depends on information it was never trained on or on an exact calculation. My car's odometer, and the reading at which its oil was last changed, exist only in my JSON files. If I ask a plain LLM "How many km until my next oil change?", it has nothing to compute from. In my run the model handled this honestly by asking me for the missing numbers, but that behaviour is not guaranteed: a different model or setting can fill the gap with a plausible-sounding figure, because producing fluent text is what a language model does whether or not it has grounds for the content. Either way, the model alone cannot produce the answer, because the facts are not in its memory.

### 1.2 What is an agent, and how does its answer differ from plain chat?

In the context of LLMs, an agent is an LLM connected to tools, so that it can act instead of only writing text: it reads the question, decides whether outside help is needed, requests a tool, sees the result, and uses that result in its answer. (A full agent also repeats this cycle in a loop until the task is done. This task deliberately covers only the first building block, a single tool call, and leaves the loop out.)

The difference shows up when I ask "Is the Brake Inspection overdue, and by how many km?". The plain chat response came entirely from the model's trained knowledge and the words in my message, so all it could do was ask me for the odometer reading and the mileage of the last brake inspection. The tool-enabled response started differently: the model recognised that this needs my records, requested `get_maintenance_status` with the task "Brake Inspection", received "Brake Inspection: due at 40000 km, 1550 km remaining", and answered that the inspection is not overdue and has about 1,550 km left. The answer came from my data instead of from the model's memory.

### 1.3 What is a tool, what is a tool call, and why does the schema matter?

A tool is an ordinary function in my own code that the model is allowed to request, here `get_maintenance_status(task)`. A tool call is the model's request to run it: a small structured message naming the function and the arguments, such as `get_maintenance_status({'task': 'Engine Oil Change'})`. The model never runs anything itself. It only produces the request, my program runs the function, and the result goes back to the model.

The model can only request a tool it knows about, and what it knows is the tool's schema. The schema has three parts. The name identifies the function. The description says what it does and when to use it; mine says it looks up the owner's private vehicle records and returns the km remaining or overdue for a maintenance task. The parameters say what to pass: a required string `task`, limited to the five task names in my schedule. The model has no other way of knowing that my records exist or what the function does, so the description is what lets it decide "this question is about my vehicle's due dates, so I should use that tool" versus "this is general knowledge, so I will answer directly". A vague description leads to missed calls or wrong arguments, and restricting `task` to the exact names prevents the model from inventing a task that does not exist.

### 1.4 One tool call from start to finish

Take the question "How many more kilometers until the next Engine Oil Change is due?".

1. **User question.** My script sends the question to the model together with the tool schema.
2. **Model decides.** The model sees that the answer depends on private records and returns no text, only a tool call: `get_maintenance_status` with `{'task': 'Engine Oil Change'}`.
3. **Tool runs.** My code reads the call and runs the real function. It looks up the task (interval 5,000 km, last done at 35,000 km), adds them to get 40,000 km, subtracts the current odometer of 38,450 km, and gets 1,550.
4. **Result returns.** The function returns the plain string "Engine Oil Change: due at 40000 km, 1550 km remaining", which is added to the conversation as a tool message linked to the original call.
5. **Final answer.** The model is called again with the whole conversation, reads the tool result and writes the reply: "The next engine oil change is due in 1,550 km."

The model contributes the judgement (whether to call a tool and with which argument) and the wording, while the tool contributes the correct number.

### 1.5 Why should a tool return plain text, even on failure?

A model can only read text, so whatever the tool produces must come back as text in the conversation. If the function raised a Python exception when something went wrong, the program would crash and the model would never see what happened. If it returns a message instead, the model receives that message as an observation and can respond sensibly. In my tool, asking for a task that does not exist, such as "Wheel Alignment", returns "Unknown maintenance task: 'Wheel Alignment'. Valid tasks are: Engine Oil Change, Brake Inspection, Air Filter Replacement, Tyre Rotation, Coolant Replacement". The model can then tell the user that the task is not tracked, or retry with a valid name, instead of the whole assistant dying with a traceback. Returning errors as text turns a failure into information the model can use.

## 2. Comparison Table

| Basis for comparison | Plain LLM prompt (no tool) | LLM with one tool |
| --- | --- | --- |
| Source of the answer | The model's trained knowledge and whatever I type in the message. It has no access to my JSON files, so for the due-date questions it had nothing to draw on. | My actual records, read by `get_maintenance_status`, for the three due-date questions. For the two general questions the model still answered from its own knowledge. |
| Can it fetch or compute information outside its own memory? | No. It can only generate text. In my run it asked me to supply the odometer and last-service mileage instead of looking them up. | Yes, for what the tool covers. The tool reads the files and does the subtraction, so the figure does not depend on the model's memory or arithmetic. |
| Reliability on factual or numeric questions | Reliable for general explanations. For my car's figures it produced no number at all, which is safe but not useful. Its car-specific general claims also varied: it said 5,000 km for oil changes in one answer and 7,500 or 10,000 km in another, and neither comes from my schedule. | All three figures (1,550 km, 1,550 km and 11,550 km) matched my hand calculation, because they came from code and data. The remaining risk is the model choosing the wrong tool or argument, which the schema reduces. |
| Transparency (can you see how the answer was reached?) | Low. I only see the final text and cannot tell what a general statement is based on. | High. The run printed the tool call, its arguments and the raw result, so I can compare them with the final answer line by line. |
| Speed / cost of getting an answer | One model call per question. | Two model calls when the tool is used (one to decide and request, one to write the answer), plus the schema tokens on every call. When no tool was needed (Q4, Q5) it was still a single call. |

## 3. Minimal Implementation

The code is in the repository root. `tool.py` holds the single function `get_maintenance_status(task)` and its JSON schema. `no_tool.py` sends each question to the model with only the system prompt and prints the answer as given. `with_tool.py` sends the same question with the tool available, and if the model requests it, runs the function once, returns the result and prints both the tool call and the final answer. There is no loop and no registry of multiple tools. `config.py` selects the LLM provider and holds the shared question list, and the two runs use the same model and the same base system prompt. The screenshots of both runs are in the `screenshots` folder.

## 4. Observation

I ran the same five questions in both runs. Q1 to Q3 need my private records, and Q4 and Q5 are general knowledge. The current odometer is 38,450 km, so the correct answers for Q1 to Q3 are 1,550 km, "not overdue, 1,550 km remaining", and 11,550 km.

| # | Question | Needs tool? | Plain LLM result | Tool-enabled result |
| --- | --- | --- | --- | --- |
| 1 | Km until next Engine Oil Change | Yes | No answer; asked for odometer and last-change mileage | Called tool correctly; answered 1,550 km (correct) |
| 2 | Is Brake Inspection overdue, by how many km | Yes | No answer; asked for odometer and last-inspection mileage | Called tool correctly; not overdue, 1,550 km left (correct) |
| 3 | Km left before Air Filter Replacement | Yes | No answer; gave a generic interval and asked for the two values | Called tool correctly; 11,550 km left (correct) |
| 4 | Why does engine oil need regular changes | No | Correct, detailed explanation | No tool call; correct explanation |
| 5 | What does a tyre rotation do and why | No | Correct, detailed explanation | No tool call; correct explanation |

**Questions that needed the tool (Q1 to Q3).** The plain LLM did not guess a figure on any of them. On Q1 it said it needed the current odometer reading and the mileage at the last oil change, and added that Honda City models typically use a 5,000 km interval. On Q2 it asked for the same two numbers for the brake inspection and gave no interval at all. On Q3 it said air filters on a Honda City are typically replaced about every 20,000 km or two years, and again asked for the two values. It therefore neither answered correctly nor answered wrongly; it deferred to me, so I would have had to look up my own records and do the subtraction myself. The tool-enabled run did all of this on its own. In each case the model chose `get_maintenance_status`, passed the exact task name (`'Engine Oil Change'`, `'Brake Inspection'`, `'Air Filter Replacement'`), and used the returned line in its answer:

```
TOOL CALL: get_maintenance_status({'task': 'Engine Oil Change'}) -> Engine Oil Change: due at 40000 km, 1550 km remaining
TOOL CALL: get_maintenance_status({'task': 'Brake Inspection'}) -> Brake Inspection: due at 40000 km, 1550 km remaining
TOOL CALL: get_maintenance_status({'task': 'Air Filter Replacement'}) -> Air Filter Replacement: due at 50000 km, 11550 km remaining
```

The final answers (1,550 km; not overdue with about 1,550 km left; 11,550 km) match those tool results and my own calculation. On Q2 the model also read the result correctly as "not overdue" instead of just repeating a number.

**Questions that did not need the tool (Q4 and Q5).** The plain LLM answered both well, with full explanations of lubrication, heat, contaminants and sludge for oil, and even wear, tyre life and handling for rotation. In the tool-enabled run the model correctly called no tool for either question and gave equally good explanations, which shows the tool did not make it call functions unnecessarily. One detail is worth noting. The plain answer to Q4 gave car-specific intervals of 7,500 km for one model-year range and 10,000 km for another, which conflicts with its own Q1 answer of 5,000 km and with the 5,000 km in my schedule. Similarly, its Q5 answer suggested rotating every 5,000 to 8,000 km, while the tool-enabled run said 5,000 to 10,000 km. None of this makes the explanations wrong, but it shows that when a plain LLM gives figures about my particular car, they are general and can change between answers, and they are not taken from my records.

**Overall.** The tool was called on exactly the three questions that needed it and on none of the two that did not, and every tool-backed number was correct.

## 5. Suitability and Conclusion

In my scenario the plain LLM prompt was good enough on its own for the conceptual questions. Explaining why oil is changed and what a tyre rotation does needs only general knowledge, and both runs produced correct, detailed answers with no tool. The plain prompt was not enough for any question about my own car's due dates. Those answers exist only in my private records and need a subtraction on them, so the plain model could do nothing except ask me for the numbers. Giving it one small tool was enough to fix that: the model recognised the question as being about my vehicle, requested the lookup with the right argument, and turned the tool's result into a correct answer. It is true that I could have typed the odometer and last-service values into the prompt myself, but that makes me do the lookup and the checking every time, and it stops working once the records are bigger than a message. The tool moves that work into code.

In general, a plain LLM prompt is enough when the answer lives in the model's trained knowledge or in text I put in the prompt: explaining concepts, summarising, drafting, translating or brainstorming. It is also enough when a small error costs little, since there is nothing to fetch and nothing to verify. A problem needs a tool once the correct answer depends on something the model cannot reliably produce from memory. That includes private data such as my records, information that changes over time, exact calculations, and actions that must actually happen in the world. In those cases the model's fluency does not make it correct, and giving it even one tool changes the job: it stops guessing or asking and starts deciding when to fetch a fact, then explains a fact that came from real data.
