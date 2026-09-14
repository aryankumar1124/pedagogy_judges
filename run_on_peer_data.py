"""
Runs the pedagogy judges on ONE of Swayam's real teacher-student transcripts.

Usage:
    Put MISTRAL_API_KEY, GROQ_API_KEY, COHERE_API_KEY in a .env file
    (see .env.example), or export them in your shell, then:
    python run_on_peer_data.py /path/to/raw_transcript.json
"""

import sys
import json

from utils.transcript_converter import load_raw_transcript, to_dialogue_text, build_metadata_summary
from main import run_all_judges, aggregate, print_score_table, print_full_detail


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_on_peer_data.py /path/to/raw_transcript.json")
        sys.exit(1)

    raw_path = sys.argv[1]
    data = load_raw_transcript(raw_path)
    metadata = build_metadata_summary(data)
    transcript_text = to_dialogue_text(data)

    print("=== SOURCE METADATA ===")
    print(json.dumps(metadata, indent=2))
    print(f"\nTranscript length: {len(transcript_text)} chars\n")

    results = run_all_judges(transcript_text)
    summary = aggregate(results)

    print("\n=== PEDAGOGY SCORES BY FACTOR ===")
    print_score_table(results, summary)

    print("\n=== FULL DETAIL PER FACTOR ===")
    print_full_detail(results, summary)

    # Save everything to a file for later analysis
    out = {"metadata": metadata, "judge_results": results, "aggregated": summary}
    out_path = raw_path.rsplit("/", 1)[-1].replace(".json", "_pedagogy_scored.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved full result to {out_path}")


if __name__ == "__main__":
    main()
