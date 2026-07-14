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