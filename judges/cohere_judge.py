import os
import json
import cohere

from prompts.judge_prompt import build_system_prompt, build_user_prompt

MODEL = "command-a-03-2025"  # swap to whichever Cohere model you have access to


def score_transcript(transcript: str) -> dict:
    client = cohere.ClientV2(api_key=os.environ["COHERE_API_KEY"])

    response = client.chat(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(transcript)},
        ],
    )

    raw_text = response.message.content[0].text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON: {e}", "raw_output": raw_text}


if __name__ == "__main__":
    sample = "Paste a sample transcript here to test."
    result = score_transcript(sample)
    print(json.dumps(result, indent=2))
