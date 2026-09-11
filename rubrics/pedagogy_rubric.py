"""
Locked pedagogy rubric (v1) — 6 factors, 1-5 scale each.
Pedagogy Score = (sum of 6 factor scores / 30) * 100
"""

SCORING_SCALE = {
    1: "Very Poor - The factor is almost absent. The teaching practice rarely supports student learning.",
    2: "Poor - The factor is present occasionally but is inconsistent and ineffective.",
    3: "Average - The factor is present and functional but lacks consistency or depth.",
    4: "Good - The factor is consistently implemented and contributes positively to learning.",
    5: "Excellent - The factor is highly effective, consistently demonstrated, and significantly enhances student learning.",
}

FACTORS = {
    "PCK": {
        "name": "Pedagogical Content Knowledge",
        "definition": "Ability to transform subject matter into forms students can understand — clear explanations, misconceptions addressed, effective examples/analogies.",
        "criteria": {
            1: "Unable to explain concepts clearly. Frequently leaves student misconceptions unresolved.",
            2: "Basic explanations provided but often unclear. Limited use of examples and analogies.",
            3: "Concepts explained adequately. Some examples used. Common misconceptions addressed occasionally.",
            4: "Clear explanations, effective examples, and regular identification of student misconceptions.",
            5: "Exceptional explanations, multiple representations of concepts, proactive identification and correction of misconceptions, strong adaptation to student needs.",
        },
    },
    "Feedback": {
        "name": "Feedback Quality",
        "definition": "How effectively the teacher helps students understand goals, current performance, and next steps.",
        "criteria": {
            1: "Feedback is absent or limited to simple praise or criticism.",
            2: "Feedback identifies errors but rarely provides guidance for improvement.",
            3: "Feedback helps students understand current performance but lacks consistency.",
            4: "Feedback regularly identifies strengths, weaknesses, and next steps.",
            5: "Feedback consistently addresses learning goals, current performance, and future improvement clearly and actionably.",
        },
    },
    "Modeling": {
        "name": "Modeling",
        "definition": "Demonstrating expert thinking and problem-solving processes, not just presenting answers.",
        "criteria": {
            1: "Teacher provides answers without demonstrating thought processes.",
            2: "Occasional demonstrations provided but lack clarity.",
            3: "Teacher demonstrates problem-solving processes for some topics.",
            4: "Teacher regularly models expert thinking and reasoning.",
            5: "Teacher consistently makes expert thinking visible through demonstrations, think-aloud strategies, real-world examples.",
        },
    },
    "Coaching": {
        "name": "Coaching and Scaffolding",
        "definition": "Guidance, hints, structured assistance that fades as student competence grows.",
        "criteria": {
            1: "Little or no support provided during learning activities.",
            2: "Support provided inconsistently and does not meet student needs.",
            3: "Appropriate support provided but not gradually adjusted.",
            4: "Guidance, hints, and support regularly provided and adapted to student progress.",
            5: "Support strategically provided and gradually removed as students become more independent.",
        },
    },
    "Reflection": {
        "name": "Reflection and Articulation",
        "definition": "Extent to which students explain reasoning, reflect on understanding, and communicate thought processes.",
        "criteria": {
            1: "Students rarely asked to explain thinking or reflect on learning.",
            2: "Reflection activities present but superficial.",
            3: "Students occasionally explain reasoning and reflect on understanding.",
            4: "Reflection and explanation regularly incorporated into learning activities.",
            5: "Students consistently articulate reasoning, evaluate understanding, engage in meaningful reflection.",
        },
    },
    "Engagement": {
        "name": "Student Engagement (ICAP)",
        "definition": "Cognitive involvement level: Passive -> Active -> Constructive -> Interactive.",
        "criteria": {
            1: "Learning activities are primarily passive (listening, reading, watching).",
            2: "Activities occasionally require active participation but remain largely passive.",
            3: "Students frequently engage in active learning (note-taking, highlighting).",
            4: "Students regularly engage in constructive activities (self-explaining, questioning, summarizing).",
            5: "Students consistently participate in interactive learning (discussion, collaboration, argumentation, co-construction).",
        },
    },
}

INTERPRETATION_BANDS = [
    (90, 100, "Excellent pedagogy"),
    (80, 89, "Very Good pedagogy"),
    (70, 79, "Good pedagogy"),
    (60, 69, "Fair pedagogy"),
    (0, 59, "Needs significant improvement"),
]


def interpret_score(score: float) -> str:
    for low, high, label in INTERPRETATION_BANDS:
        if low <= score <= high:
            return label
    return "Unknown"
