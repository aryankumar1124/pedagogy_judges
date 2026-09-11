import os
import json
from groq import Groq

from prompts.judge_prompt import build_system_prompt, build_user_prompt

MODEL = "openai/gpt-oss-120b"  # swap to whichever Groq model you have access to


def score_transcript(transcript: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

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
