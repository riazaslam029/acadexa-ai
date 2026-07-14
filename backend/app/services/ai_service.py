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