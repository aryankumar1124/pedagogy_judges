"""
Batch-runs the pedagogy judges on ALL 135 real teacher-student transcripts
from the Swayam dataset. Saves one scored JSON per conversation, plus a
running summary file updated after every conversation (so nothing is lost
if the run is interrupted).
"""

import glob
import json
import os
import time

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

from utils.transcript_converter import load_raw_transcript, to_dialogue_text, build_metadata_summary
from main import run_all_judges, aggregate

RAW_DIR = "swayam_pedagogy_final_v2_results/results/raw/ollama_student_provider_comparison_full_v2"
OUT_DIR = "swayam_pedagogy_final_v2_results/results/pedagogy_scored"
SUMMARY_PATH = "swayam_pedagogy_final_v2_results/results/pedagogy_scored_summary.json"

files = sorted(glob.glob(os.path.join(RAW_DIR, "*.json")))
files = [f for f in files if "failed_runs" not in f]

print(f"Found {len(files)} transcripts to score.")

summary = []
if os.path.exists(SUMMARY_PATH):
    with open(SUMMARY_PATH) as f:
        summary = json.load(f)
already_done = {row["run_id"] for row in summary}

start_time = time.time()

for i, path in enumerate(files, 1):
    run_id = os.path.basename(path).replace(".json", "")
    out_path = os.path.join(OUT_DIR, f"{run_id}_pedagogy_scored.json")

    if run_id in already_done and os.path.exists(out_path):
        print(f"[{i}/{len(files)}] {run_id} - already done, skipping")
        continue

    t0 = time.time()
    try:
        data = load_raw_transcript(path)
        metadata = build_metadata_summary(data)
        transcript_text = to_dialogue_text(data)

        results = run_all_judges(transcript_text)
        agg = aggregate(results)

        out = {"metadata": metadata, "judge_results": results, "aggregated": agg}
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2)

        judge_status = {name: ("ok" if "error" not in r else "error") for name, r in results.items()}
        row = {
            "run_id": run_id,
            "student_model": metadata.get("student_model"),
            "tutor_provider": metadata.get("tutor_provider"),
            "pedagogy_score": agg["pedagogy_score"],
            "interpretation": agg["interpretation"],
            "judge_status": judge_status,
        }
        elapsed = round(time.time() - t0, 1)
        print(f"[{i}/{len(files)}] {run_id} - score={agg['pedagogy_score']} judges={judge_status} ({elapsed}s)")

    except Exception as e:
        row = {"run_id": run_id, "error": str(e)}
        print(f"[{i}/{len(files)}] {run_id} - FAILED: {e}")

    summary = [r for r in summary if r["run_id"] != run_id]
    summary.append(row)
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)

total_elapsed = round((time.time() - start_time) / 60, 1)
print(f"\nDone. {len(summary)} conversations processed in {total_elapsed} minutes.")
print(f"Per-conversation results: {OUT_DIR}/")
print(f"Summary file: {SUMMARY_PATH}")
