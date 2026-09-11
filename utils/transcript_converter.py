"""
Converts a raw transcript JSON (from the teacher-student simulation experiment)
into a plain-text dialogue string that the pedagogy judges can evaluate.

Each raw JSON file = ONE parent conversation, which may span multiple episodes
(multiple assignment questions in sequence). By default this converts the
WHOLE conversation. Use episode_index to pull out just one episode/question
if you want to score them separately.
"""

import json


def load_raw_transcript(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def to_dialogue_text(data: dict, episode_index: int | None = None) -> str:
    """
    episode_index: 1-based episode number (matches episode_id in the JSON).
    If None, includes the full conversation across all episodes.
    """
    messages = data["messages"]

    if episode_index is not None:
        # messages don't carry an explicit episode number directly, but episodes
        # give message index ranges via episode boundaries. Simplest robust way:
        # filter using episode_message_index resetting to 0 as a new-episode signal.
        episodes = data["episodes"]
        target = next((e for e in episodes if e["episode_index"] == episode_index), None)
        if target is None:
            raise ValueError(f"episode_index {episode_index} not found")
        # fall back to full conversation if we can't cleanly slice - safer to
        # just note this as a known limitation.
        raise NotImplementedError(
            "Per-episode slicing needs the exact message range from the source "
            "pipeline; use the full conversation for now (episode_index=None)."
        )

    lines = []
    for m in messages:
        speaker = "Teacher" if m.get("role") == "teacher" else "Student"
        content = m.get("content", "").strip()
        if content:
            lines.append(f"{speaker}: {content}")

    return "\n\n".join(lines)


def build_metadata_summary(data: dict) -> dict:
    """Pulls the ground-truth context worth cross-checking judge scores against."""
    return {
        "run_id": data.get("run_id"),
        "student_model": data.get("student_model"),
        "tutor_provider": data.get("tutor_provider"),
        "tutor_model": data.get("tutor_model"),
        "episode_count": data.get("episode_count"),
        "termination_reason": data.get("termination_reason"),
        "questions": [
            {
                "assignment_id": e.get("assignment_id"),
                "question_id": e.get("question_id"),
                "question_title": e.get("question_title"),
            }
            for e in data.get("episodes", [])
        ],
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    data = load_raw_transcript(path)
    print("=== METADATA ===")
    print(json.dumps(build_metadata_summary(data), indent=2))
    print("\n=== DIALOGUE (first 2000 chars) ===")
    print(to_dialogue_text(data)[:2000])
