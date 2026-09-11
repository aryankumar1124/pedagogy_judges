# Pedagogy Judges

An LLM-ensemble pipeline that scores teacher-student lesson transcripts against a
research-grounded pedagogy rubric, using three independent model providers as
"judges" and measuring how much they agree.

## Idea

Rather than trusting a single LLM's opinion of teaching quality, this project asks
three different models (OpenAI, Groq, Gemini) to independently score the same
transcript against the identical rubric and prompt. Model diversity — not prompt
specialization — is the source of independence: every judge sees the same
instructions, so disagreement between them reflects genuine judgment differences
rather than prompt variation.

## Rubric

Scoring is based on a locked, 6-factor rubric (1-5 scale per factor), grounded in
established pedagogy research:

| Factor | Grounded in | What it measures |
|---|---|---|
| **PCK** | Shulman's Pedagogical Content Knowledge | Clear explanations, misconceptions addressed, effective examples |
| **Feedback** | Hattie's Visible Learning | Whether feedback helps students understand goals, performance, and next steps |
| **Modeling** | Cognitive Apprenticeship | Teacher makes expert thinking visible (think-alouds, worked examples) |
| **Coaching** | Cognitive Apprenticeship | Scaffolding that adapts and fades as competence grows |
| **Reflection** | Cognitive Apprenticeship | Students explain reasoning and articulate their thinking |
| **Engagement** | ICAP framework | Passive → Active → Constructive → Interactive student participation |

`Pedagogy Score = (sum of 6 factor scores / 30) × 100`

See `rubrics/pedagogy_rubric.py` for full scoring criteria at each level, and
`prompts/judge_prompt.py` for the exact prompt sent to every judge.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# then fill in OPENAI_API_KEY, GROQ_API_KEY, GOOGLE_API_KEY in .env
```

## Usage

Score a plain-text transcript:

```bash
python main.py sample_transcript.txt
```

This prints a per-factor score table (one column per judge, plus mean and
agreement stdev), full reasoning/evidence/strengths/weaknesses/suggestions for
every factor, and saves the complete result to `<transcript>_pedagogy_scored.json`.

Score one of the real teacher-student transcripts from the experiment dataset:

```bash
python run_on_peer_data.py path/to/raw_transcript.json
```

## Project structure

```
judges/            One module per LLM provider — each calls its API and parses the JSON response
prompts/            Single unified prompt shared by all judges
rubrics/            The locked 6-factor pedagogy rubric and scoring bands
utils/              Converts raw teacher-student JSON transcripts into judge-readable dialogue text
main.py             Runs all 3 judges on a transcript, aggregates, prints, saves
run_on_peer_data.py Same pipeline, wired to the real Swayam experiment transcripts
swayam_pedagogy_final_v2_results/  Prior experiment data (student-model × tutor-provider comparison)
```

## Current status & limitations

This is a working v1, not a validated research result. Known gaps, in order of
importance:

1. **No human ground-truth comparison yet.** The pipeline shows the three judges
   *agree* with each other on this sample transcript (exact agreement on PCK,
   Feedback, and Coaching; within 1 point on the rest). It does not yet show they
   are *correct* — that requires comparing judge scores against real human expert
   ratings, which hasn't been done.
2. **Aggregation is a plain mean**, not confidence-weighted or outlier-resistant.
   Each judge already outputs a `confidence` score per factor (reflecting how much
   evidence was in the transcript), but the aggregation step currently ignores it
   and treats every judge equally. A single misfiring judge can pull the mean
   without any resistance.
3. **Episode-level slicing is unimplemented.** `utils/transcript_converter.py` can
   only score a whole multi-episode conversation at once; pulling out a single
   episode raises `NotImplementedError` by design, pending the exact message-range
   data from the source pipeline.

### Next steps
- Collect human expert scores on a held-out set of transcripts and measure
  judge-vs-human agreement (not just judge-vs-judge).
- Add confidence-weighted aggregation as an alternative to the naive mean, and
  compare the two.
- Implement per-episode transcript slicing.
