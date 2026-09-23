# Analysis: Direct Prompting vs Chain-of-Thought vs ReAct
### Scenario: Vehicle Maintenance Assistant

**Setup used for these runs:** provider `groq`, model `openai/gpt-oss-120b`.
**Vehicle:** Honda City (2022), odometer 38,450 km, 3 past services, 5
scheduled maintenance tasks (see `data/`).

---

## 3.1 Explanation of each approach

### Direct prompting
Direct prompting answers immediately from the model's own knowledge and
reasoning, with no visible working and no tool access. It either gets a
multi-step problem right in one shot or it doesn't — there's no
intermediate state to inspect.

- **Can answer:** questions where all the needed numbers are stated in
  the prompt and the model's internal reasoning is strong enough to
  combine them correctly without writing anything down.
- **Cannot answer:** anything requiring live data the model wasn't
  given (e.g. the current odometer reading, the actual service
  history) — it would have to guess or hallucinate those figures.
- **How it arrives at an answer:** one forward pass from question to
  answer, no tools, no visible intermediate steps.
- **On this scenario:** with `gpt-oss-120b` (a large, capable model),
  direct prompting actually got **all three** reasoning-only questions
  right (see 3.2). Its limitation only shows up on the tool-needing
  question — asked directly, with no tool access, it would have no way
  to know the vehicle is at 38,450 km or that Rs. 8,500 has been spent
  so far.

### Chain-of-Thought (CoT)
CoT makes the model reason step by step before answering, which gives
it "space" to catch arithmetic and logic errors it might otherwise
make in a single jump. It still cannot fetch a fact it doesn't already
have — it can only reason more carefully over what's already in the
prompt.

- **Can answer:** the same self-contained questions as direct
  prompting, but more reliably on multi-step arithmetic and ordering,
  especially on smaller/weaker models.
- **Cannot answer:** the tool-needing question — no matter how
  carefully it reasons, it still doesn't know the vehicle's live
  odometer or real service history unless a tool tells it.
- **How it arrives at an answer:** the prompt instructs it to number
  its steps, show each calculation, and end with `Final Answer: <x>`;
  the model still answers in one pass, but the pass is longer and
  self-checking.
- **On this scenario:** CoT reasoning was correct and well laid-out on
  all three questions (see screenshots), matching the direct-prompt
  answers exactly. Because `gpt-oss-120b` is already strong at this
  scale of arithmetic, CoT didn't *fix* any wrong answers here — the
  benefit it should show up more clearly on a smaller model like
  `qwen3:4b`, where direct prompting is more likely to slip.

### ReAct
ReAct interleaves Thought, Action, and Observation: it reasons about
what it needs, calls a tool to get it, reads the result, and repeats
until it can give a final answer grounded in real data.

- **Can answer:** questions needing live/private data — exactly the
  tool-needing question in this scenario.
- **Cannot answer (well) on its own:** nothing new here — it's still
  the same underlying LLM reasoning, just with facts injected via
  tools instead of assumed.
- **How it arrives at an answer:** `agent.py`'s loop calls the LLM
  with the tool schemas from `tools.py`; each turn either requests a
  tool call or produces a final answer; tool results are fed back in
  as `role: tool` messages until the model stops calling tools.
- **On this scenario (`react_trace.py` output):** the agent called
  `list_maintenance_tasks`, then `get_maintenance_status` for each of
  the 5 tasks individually, then `get_total_service_cost` — 7 tool
  calls in 7 steps, well under the `max_steps=8` limit. It correctly
  identified Engine Oil Change and Brake Inspection as tied, both due
  in 1,550 km, and correctly summed the total cost as 8,500. One small
  slip: its final answer labeled the total with a `$` sign instead of
  `Rs.` — a presentation/transparency issue, not a reasoning error;
  the underlying number was correct because it came straight from the
  tool.

## 3.2 Comparison table

| Basis for comparison | Direct prompting | Chain-of-Thought | ReAct agent |
|---|---|---|---|
| Reasoning depth | None visible — single-shot answer | Explicit, numbered steps with shown calculations | Same step-by-step reasoning as CoT, but interleaved with real tool calls |
| Tool usage | None | None | 6 tool calls across 3 tools (`list_maintenance_tasks`, `get_maintenance_status` ×5, `get_total_service_cost`) |
| Reliability on multi-step questions | High on this model (3/3 correct) but no way to verify *why* it was right | High — reasoning is checkable, and correct on all 3 questions | High — every fact is fetched, not assumed, so it can't drift from the real data |
| Transparency (can you see how it got the answer?) | No — black box | Yes — full worked steps shown | Yes — every tool call and its raw result is printed, plus the reasoning between them |
| Speed / cost | Fastest, cheapest — one short completion | Slower/costlier — longer completion with full working | Slowest/costliest — 7 sequential LLM calls (one per step) plus tool execution time |
| Consistency across repeated runs | Not tested directly, but tends to vary more on harder problems since there's no self-checking step | Tested via self-consistency: all 5 runs on Q1 converged to the same numeric answer (7,480) at `temperature=0.8` | Not repeated in this run, but deterministic tool outputs mean the *facts* stay identical across runs — only phrasing of the final answer would vary |

## 3.3 Self-consistency observation

Ran Question 1 ("12% loyalty discount on Rs. 4,500 + 2,800 + 1,200")
5 times at `temperature=0.8`:

```
run 1: 7,480 rupees.
run 2: 7,480.
run 3: 7,480
run 4: 7,480**
run 5: Rs. 7,480
```

Every run reached the same correct number, **7,480**. However, the
script reported the "majority answer" as only **1 of 5 runs**, because
`Counter` compares the extracted strings exactly, and each run's
`Final Answer:` line was formatted slightly differently (extra
words like "rupees", a trailing `Rs.`, or leftover markdown `**`
characters). This is a genuinely useful finding: the *reasoning*
converged perfectly across all 5 runs, but a naive string-based vote
undercounted that agreement because it wasn't normalizing formatting.
A real self-consistency pipeline would need to strip currency labels
and punctuation before voting — otherwise it can wrongly look like the
model disagreed with itself when it didn't.

At `temperature=0` (as used in `cot_compare.py`), the single
deterministic run also gave 7,480 — consistent with what the 5
higher-temperature runs converged to, so in this case raising the
temperature didn't actually surface any disagreement to vote on; it
would matter more on a harder or more ambiguous question.

## 3.4 Suitability analysis

For this scenario, **ReAct is the most suitable approach**, for one
decisive reason: the central, most useful question a real vehicle
owner would ask — "what's due soonest, and how much have I spent?" —
depends on live data (current odometer, actual service history) that
no LLM has memorized and that changes over time. Direct prompting and
CoT can only reason over facts already present in the prompt; neither
could answer that question without being handed the entire dataset
inline, which doesn't scale as the vehicle accumulates more history.

That said, the comparison table also shows CoT holding its own on the
scenario's *self-contained* reasoning questions (discount arithmetic,
due-date comparison, cost ranking) — on a capable model like
`gpt-oss-120b`, CoT and even direct prompting were both fully correct
here, at a fraction of ReAct's latency and cost. So the practical
takeaway for this assistant is a hybrid: use ReAct when the question
needs current vehicle data, and fall back to direct/CoT prompting for
purely explanatory or self-contained questions where speed matters
more than grounding.

## 3.5 Conclusion

In general:

- **Direct prompting** is the right choice when the question is
  simple, all the information needed is already in the prompt, and
  the model is strong enough for the reasoning involved — it's the
  fastest and cheapest option and it worked fine here on a large
  model, but it offers no transparency and no protection against
  silent errors on harder problems.
- **Chain-of-Thought** is the right choice when a question needs
  several dependent steps of reasoning and you want to see (and
  trust) how the answer was reached, but every fact required is
  already available — it improves reliability on smaller or weaker
  models especially, at the cost of longer, slower responses.
- **ReAct** is the right choice whenever the answer depends on
  information the model doesn't and shouldn't be expected to know in
  advance — live data, private records, anything that can change —
  because it's the only one of the three that can go get that
  information before answering. The trade-off is cost and latency:
  every tool call is another round trip, so it should be reserved for
  questions that genuinely need grounding, not used as a default for
  every question a CoT prompt could already answer correctly.
