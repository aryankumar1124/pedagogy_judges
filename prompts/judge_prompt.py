"""
Single unified prompt used by ALL THREE judges (OpenAI, Groq, Gemini).
Model diversity (not factor specialization) is the source of independence here.
Each judge sees the full rubric and full transcript, and scores all 6 factors.
"""

from rubrics.pedagogy_rubric import FACTORS, SCORING_SCALE

OUTPUT_SCHEMA_EXAMPLE = """
{
  "PCK": {"score": 4, "confidence": 91, "evidence": ["..."], "reasoning": "...", "strengths": ["..."], "weaknesses": ["..."], "suggestions": ["..."]},
  "Feedback": {...},
  "Modeling": {...},
  "Coaching": {...},
  "Reflection": {...},
  "Engagement": {...}
}
"""


def build_rubric_text() -> str:
    lines = []
    lines.append("SCORING SCALE (applies to every factor):")
    for score, desc in SCORING_SCALE.items():
        lines.append(f"  {score} = {desc}")
    lines.append("")
    lines.append("FACTORS TO EVALUATE:")
    for key, f in FACTORS.items():
        lines.append(f"\n{key} — {f['name']}")
        lines.append(f"Definition: {f['definition']}")
        for score, criteria in f["criteria"].items():
            lines.append(f"  {score}: {criteria}")
    return "\n".join(lines)


def build_system_prompt() -> str:
    rubric_text = build_rubric_text()
    return f"""You are an expert evaluator of teaching quality, grounded in educational research
(Shulman's Pedagogical Content Knowledge, Hattie's Visible Learning, Cognitive Apprenticeship,
and the ICAP framework for student engagement).

Your task is to evaluate a lesson transcript against a 6-factor pedagogy rubric.
You must score ALL SIX factors independently. Do not skip any factor.

RULES:
1. Only evaluate what is present in the transcript. NEVER invent classroom events.
2. If there is not enough evidence to score a factor confidently, explicitly write
   "Insufficient Evidence" in the evidence field for that factor, still provide your
   best-estimate score, and reflect the uncertainty with a LOW confidence value.
3. Every score must be backed by evidence (a short quote or paraphrase from the transcript).
4. Every score must include: reasoning, strengths, weaknesses, and suggestions.
5. Confidence (0-100) should reflect how much clear evidence exists in the transcript,
   not how "good" the teaching is.
6. Return ONLY valid JSON matching the schema below. No preamble, no markdown fences, no extra text.

{rubric_text}

REQUIRED OUTPUT SCHEMA (JSON only):
{OUTPUT_SCHEMA_EXAMPLE}
"""


def build_user_prompt(transcript: str) -> str:
    return f"""Evaluate the following lesson transcript against all 6 pedagogy factors.

TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"

Return your evaluation as JSON only, following the required schema exactly.
"""
