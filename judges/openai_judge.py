import os
import json
from openai import OpenAI

from prompts.judge_prompt import build_system_prompt, build_user_prompt

MODEL = "gpt-5-mini"  # swap to gpt-4.1 / gpt-5 / whichever you have access to


def score_transcript(transcript: str) -> dict:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(transcript)},
        ],
    )

    raw_text = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON: {e}", "raw_output": raw_text}


if __name__ == "__main__":
    sample = "Paste a sample transcript here to test."
    result = score_transcript(sample)
    print(json.dumps(result, indent=2))
