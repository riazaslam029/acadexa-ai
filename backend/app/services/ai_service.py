import json
from typing import Any

from google import genai

from app.core.config import settings

client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
)


def generate_summary(text: str) -> str:
    prompt = f"""
You are an expert study assistant.

Summarize the following document into clear study notes.

Requirements:
- Use headings.
- Use bullet points.
- Keep important definitions.
- Keep important formulas if present.
- Maximum 500 words.

Document:

{text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text


def _generate_document_grounded_content(
    document_text: str,
    instruction: str,
) -> str:
    prompt = f"""
You are an AI study assistant.

Use ONLY the uploaded document to answer.
If information is not in the document, do not fabricate it.

{instruction}

Document:
{document_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return (response.text or "").strip()


def _parse_json_or_text(raw_text: str, fallback_key: str = "content") -> dict[str, Any]:
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
        return {fallback_key: parsed}
    except json.JSONDecodeError:
        return {fallback_key: raw_text}

def chat_with_document(
    document_text: str,
    question: str,
) -> str:
    prompt = f"""
You are an AI study assistant.

Answer ONLY using the information contained in the document below.

If the answer is not present in the document, reply:
"I couldn't find that information in the uploaded document."

Document:

{document_text}

Question:

{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text


def generate_flashcards(document_text: str, count: int = 10) -> dict[str, Any]:
        instruction = f"""
Create {count} flashcards from the document.
Return STRICT JSON with this shape:
{{
    "flashcards": [{{"question": "...", "answer": "..."}}]
}}
"""
        raw = _generate_document_grounded_content(document_text, instruction)
        return _parse_json_or_text(raw, fallback_key="flashcards")


def generate_mcqs(document_text: str, count: int = 10, difficulty: str | None = None) -> dict[str, Any]:
        difficulty_text = difficulty or "medium"
        instruction = f"""
Create {count} multiple-choice questions with difficulty '{difficulty_text}'.
Each question must include a correct answer and explanation.
Return STRICT JSON:
{{
    "mcqs": [
        {{
            "question": "...",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "...",
            "difficulty": "{difficulty_text}",
            "explanation": "..."
        }}
    ]
}}
"""
        raw = _generate_document_grounded_content(document_text, instruction)
        return _parse_json_or_text(raw, fallback_key="mcqs")


def generate_key_points(document_text: str) -> dict[str, Any]:
        instruction = """
Generate concise key points from the document.
Return STRICT JSON: {"key_points": ["...", "..."]}
"""
        raw = _generate_document_grounded_content(document_text, instruction)
        return _parse_json_or_text(raw, fallback_key="key_points")


def generate_study_notes(document_text: str) -> dict[str, Any]:
        instruction = """
Create detailed study notes with headings and bullet points.
Return STRICT JSON: {"study_notes": "..."}
"""
        raw = _generate_document_grounded_content(document_text, instruction)
        return _parse_json_or_text(raw, fallback_key="study_notes")


def generate_quiz(document_text: str, count: int = 10, difficulty: str | None = None) -> dict[str, Any]:
        difficulty_text = difficulty or "medium"
        instruction = f"""
Create a quiz with {count} questions and difficulty '{difficulty_text}'.
Return STRICT JSON:
{{
    "quiz": [
        {{
            "question": "...",
            "answer": "...",
            "difficulty": "{difficulty_text}"
        }}
    ]
}}
"""
        raw = _generate_document_grounded_content(document_text, instruction)
        return _parse_json_or_text(raw, fallback_key="quiz")


def generate_translation(document_text: str, language: str) -> dict[str, Any]:
        instruction = f"""
Translate the document into {language}.
Return STRICT JSON: {{"language": "{language}", "translation": "..."}}
"""
        raw = _generate_document_grounded_content(document_text, instruction)
        return _parse_json_or_text(raw, fallback_key="translation")


def generate_eli5(document_text: str) -> dict[str, Any]:
        instruction = """
Explain the document like I am five years old.
Return STRICT JSON: {"eli5": "..."}
"""
        raw = _generate_document_grounded_content(document_text, instruction)
        return _parse_json_or_text(raw, fallback_key="eli5")


def generate_roadmap(document_text: str) -> dict[str, Any]:
        instruction = """
Create a practical learning roadmap from the document.
Return STRICT JSON:
{
    "roadmap": [
        {"step": 1, "title": "...", "details": "..."}
    ]
}
"""
        raw = _generate_document_grounded_content(document_text, instruction)
        return _parse_json_or_text(raw, fallback_key="roadmap")


def generate_study_plan(document_text: str) -> dict[str, Any]:
        instruction = """
Create a study plan based on document size and complexity.
Return STRICT JSON:
{
    "study_plan": {
        "estimated_days": 0,
        "daily_plan": ["..."]
    }
}
"""
        raw = _generate_document_grounded_content(document_text, instruction)
        return _parse_json_or_text(raw, fallback_key="study_plan")