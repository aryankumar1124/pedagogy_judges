"""
Runs all 3 judges (Mistral, Groq, Cohere) on the same transcript,
using the identical unified prompt. Prints each judge's scores,
a naive mean-aggregated pedagogy score, and basic agreement info.

This is intentionally simple — aggregation strategy (mean vs weighted vs
median vs outlier-detection) is the NEXT thing to build once you can see
real disagreement patterns.

Usage:
    Put MISTRAL_API_KEY, GROQ_API_KEY, COHERE_API_KEY in a .env file
    (see .env.example), or export them in your shell, then:
    python main.py path/to/transcript.txt
"""

import os
import sys
import json
import statistics

from dotenv import load_dotenv

load_dotenv()

from judges import mistral_judge, groq_judge, cohere_judge
from rubrics.pedagogy_rubric import FACTORS, interpret_score

JUDGES = {
    "mistral": mistral_judge.score_transcript,
    "groq": groq_judge.score_transcript,
    "cohere": cohere_judge.score_transcript,
}


def run_all_judges(transcript: str) -> dict:
    results = {}
    for name, judge_fn in JUDGES.items():
        print(f"Running {name} judge...")
        try:
            results[name] = judge_fn(transcript)
        except Exception as e:
            results[name] = {"error": str(e)}
    return results


def aggregate(results: dict) -> dict:
    """Naive mean aggregation per factor. Replace with your chosen consensus
    strategy (weighted, median, confidence-weighted, outlier detection) later."""
    factor_scores = {}
    for factor in FACTORS:
        scores = []
        for judge_name, judge_output in results.items():
            if isinstance(judge_output, dict) and factor in judge_output:
                score = judge_output[factor].get("score")
                if isinstance(score, (int, float)):
                    scores.append(score)
        if scores:
            factor_scores[factor] = {
                "mean": round(statistics.mean(scores), 2),
                "individual_scores": scores,
                "agreement_stdev": round(statistics.pstdev(scores), 2) if len(scores) > 1 else 0.0,
            }
    total = sum(v["mean"] for v in factor_scores.values())
    pedagogy_score = round((total / 30) * 100, 1) if factor_scores else 0.0

    return {
        "factor_scores": factor_scores,
        "pedagogy_score": pedagogy_score,
        "interpretation": interpret_score(pedagogy_score),
    }


def print_score_table(results: dict, summary: dict) -> None:
    judge_names = list(results.keys())
    col_width = 10

    header = f"{'Factor':<12}" + "".join(f"{j:<{col_width}}" for j in judge_names) + f"{'Mean':<8}{'Stdev':<8}"
    print(header)
    print("-" * len(header))

    for factor in FACTORS:
        row = f"{factor:<12}"
        for judge in judge_names:
            judge_output = results.get(judge)
            score = judge_output.get(factor, {}).get("score") if isinstance(judge_output, dict) else None
            row += f"{score if score is not None else '—':<{col_width}}"
        factor_summary = summary["factor_scores"].get(factor, {})
        row += f"{factor_summary.get('mean', '—'):<8}{factor_summary.get('agreement_stdev', '—'):<8}"
        print(row)

    print("-" * len(header))
    print(f"Pedagogy Score: {summary['pedagogy_score']} / 100  —  {summary['interpretation']}")


def _print_list(label: str, items) -> None:
    if not items:
        return
    print(f"    {label}:")
    for item in items:
        print(f"      - {item}")


def print_full_detail(results: dict, summary: dict) -> None:
    judge_names = list(results.keys())

    for factor, factor_def in FACTORS.items():
        print(f"\n{factor} — {factor_def['name']}")
        factor_summary = summary["factor_scores"].get(factor, {})
        print(f"  Mean: {factor_summary.get('mean', '—')}   Agreement stdev: {factor_summary.get('agreement_stdev', '—')}")

        for judge in judge_names:
            judge_output = results.get(judge)
            factor_output = judge_output.get(factor) if isinstance(judge_output, dict) else None
            if not factor_output:
                print(f"  {judge}: no output")
                continue

            score = factor_output.get("score", "—")
            confidence = factor_output.get("confidence", "—")
            print(f"  {judge} [score {score}, confidence {confidence}]:")
            print(f"    reasoning: {factor_output.get('reasoning', '—')}")
            _print_list("evidence", factor_output.get("evidence"))
            _print_list("strengths", factor_output.get("strengths"))
            _print_list("weaknesses", factor_output.get("weaknesses"))
            _print_list("suggestions", factor_output.get("suggestions"))


def save_result(transcript_path: str, results: dict, summary: dict) -> str:
    out = {"transcript_path": transcript_path, "judge_results": results, "aggregated": summary}
    stem = os.path.splitext(os.path.basename(transcript_path))[0]
    out_path = f"{stem}_pedagogy_scored.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    return out_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py path/to/transcript.txt")
        sys.exit(1)

    transcript_path = sys.argv[1]
    with open(transcript_path, "r") as f:
        transcript = f.read()

    results = run_all_judges(transcript)
    summary = aggregate(results)

    print("\n=== PEDAGOGY SCORES BY FACTOR ===")
    print_score_table(results, summary)

    print("\n=== FULL DETAIL PER FACTOR ===")
    print_full_detail(results, summary)

    out_path = save_result(transcript_path, results, summary)
    print(f"\nFull result (raw judge outputs + aggregated scores) saved to {out_path}")


if __name__ == "__main__":
    main()
