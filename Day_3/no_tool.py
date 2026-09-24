"""Day 3, run A: plain LLM prompt. The question goes straight to the model; no tools."""
from config import MODEL, QUESTIONS, SYSTEM_PROMPT, banner, client


def ask_plain(question):
    response = client.chat.completions.create(
        model=MODEL, temperature=0,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": question}])
    return (response.choices[0].message.content or "").strip()


if __name__ == "__main__":
    banner("RUN A: PLAIN LLM (NO TOOL)")
    for number, question in enumerate(QUESTIONS, 1):
        answer = ask_plain(question)
        print(f"Q{number}: {question}\nA{number}: {answer}\n" + "-" * 70)
