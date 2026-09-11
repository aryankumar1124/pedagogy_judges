import os
import json
import google.generativeai as genai

from prompts.judge_prompt import build_system_prompt, build_user_prompt

MODEL = "gemini-3.5-flash"  # swap to whichever Gemini model you have access to


def score_transcript(transcript: str) -> dict:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=build_system_prompt(),
        generation_config={"response_mime_type": "application/json"},
    )

    response = model.generate_content(build_user_prompt(transcript))
    raw_text = response.text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON: {e}", "raw_output": raw_text}


if __name__ == "__main__":
    sample = "Paste a sample transcript here to test."
    result = score_transcript(sample)
    print(json.dumps(result, indent=2))
