"""
Backfills the Groq judge into the conversations that were already scored
before Groq's rate limit / output-token issue was fixed. Merges groq's
score into the existing saved file and recomputes the aggregate.
"""

import glob
import json
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

from judges import groq_judge
from main import aggregate
from utils.transcript_converter import load_raw_transcript, to_dialogue_text

RAW_DIR = "swayam_pedagogy_final_v2_results/results/raw/ollama_student_provider_comparison_full_v2"
OUT_DIR = "swayam_pedagogy_final_v2_results/results/pedagogy_scored"
SUMMARY_PATH = "swayam_pedagogy_final_v2_results/results/pedagogy_scored_summary.json"

files = sorted(glob.glob(os.path.join(OUT_DIR, "*_pedagogy_scored.json")))

with open(SUMMARY_PATH) as f:
    summary = json.load(f)
summary_by_id = {r["run_id"]: r for r in summary}

to_backfill = []
for path in files:
    with open(path) as f:
        d = json.load(f)
    if "error" not in d.get("judge_results", {}).get("groq", {"error": True}):
        continue
    to_backfill.append(path)

print(f"{len(to_backfill)} conversations need Groq backfill.")

for i, path in enumerate(to_backfill, 1):
    run_id = os.path.basename(path).replace("_pedagogy_scored.json", "")
    raw_path = os.path.join(RAW_DIR, run_id + ".json")

    try:
        data = load_raw_transcript(raw_path)
        transcript_text = to_dialogue_text(data)

        with open(path) as f:
            scored = json.load(f)

        groq_result = groq_judge.score_transcript(transcript_text)
        scored["judge_results"]["groq"] = groq_result
        scored["aggregated"] = aggregate(scored["judge_results"])

        with open(path, "w") as f:
            json.dump(scored, f, indent=2)

        status = "ok" if "error" not in groq_result else "error"
        if run_id in summary_by_id:
            summary_by_id[run_id]["judge_status"]["groq"] = status
            summary_by_id[run_id]["pedagogy_score"] = scored["aggregated"]["pedagogy_score"]
            summary_by_id[run_id]["interpretation"] = scored["aggregated"]["interpretation"]

        print(f"[{i}/{len(to_backfill)}] {run_id} - groq={status} new_score={scored['aggregated']['pedagogy_score']}")

    except Exception as e:
        print(f"[{i}/{len(to_backfill)}] {run_id} - BACKFILL FAILED: {e}")

    with open(SUMMARY_PATH, "w") as f:
        json.dump(list(summary_by_id.values()), f, indent=2)

print("Backfill done.")
