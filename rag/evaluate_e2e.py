import json
import time
from rag.evaluate import load_eval_set
from rag.service import answer_question
from rag.prompt import NO_ANSWER

if __name__ == "__main__":
    eval_set = load_eval_set()
    results = []

    for item in eval_set:
        start = time.time()
        out = answer_question(item["question"])
        elapsed = time.time() - start

        refused = NO_ANSWER in out["answer"]
        decision_ok = (not refused) == item["should_answer"]
        top_source = out["sources"][0]["source"] if out["sources"] else None
        source_ok = (top_source == item["expected_source"]) if item["should_answer"] else None

        results.append({
            "question": item["question"],
            "should_answer": item["should_answer"],
            "refused": refused,
            "decision_ok": decision_ok,
            "source_ok": source_ok,
            "seconds": round(elapsed, 2),
            "answer": out["answer"],
        })
        status = "OK  " if decision_ok else "FAIL"
        print(f"{status} | {elapsed:4.1f}s | {item['question']}")

    answerable = [r for r in results if r["should_answer"]]
    unanswerable = [r for r in results if not r["should_answer"]]

    print("\n===== Scorecard =====")
    print(f"Correct decisions:      {sum(r['decision_ok'] for r in results)}/{len(results)}")
    print(f"Answerable answered:    {sum(not r['refused'] for r in answerable)}/{len(answerable)}")
    print(f"Unanswerable refused:   {sum(r['refused'] for r in unanswerable)}/{len(unanswerable)}")
    print(f"Correct source cited:   {sum(bool(r['source_ok']) for r in answerable)}/{len(answerable)}")
    print(f"Average latency:        {sum(r['seconds'] for r in results)/len(results):.1f}s per question")

    print("\n===== Failures (full answers) =====")
    for r in results:
        if not r["decision_ok"]:
            print(f"\nQ: {r['question']}\nA: {r['answer']}")

    with open("rag/eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        