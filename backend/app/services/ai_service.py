from abc import ABC, abstractmethod
import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

MAX_DOCUMENT_CHARS = 60_000


class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    pass


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def generate_summary(self, text: str) -> str:
        pass

    @abstractmethod
    def chat_with_document(self, document_text: str, question: str) -> str:
        pass

    @abstractmethod
    def generate_flashcards(self, document_text: str, count: int = 10) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_mcqs(self, document_text: str, count: int = 10, difficulty: str | None = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_key_points(self, document_text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_study_notes(self, document_text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_quiz(self, document_text: str, count: int = 10, difficulty: str | None = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_translation(self, document_text: str, language: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_eli5(self, document_text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_roadmap(self, document_text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_study_plan(self, document_text: str) -> Dict[str, Any]:
        pass


class BaseAIProvider(AIProvider):
    """Base implementation with common functionality."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    def _truncate_text(self, text: str, max_chars: int = MAX_DOCUMENT_CHARS) -> str:
        if not text:
            return ""
        text = text.strip()
        if len(text) <= max_chars:
            return text
        logger.warning("ai_text_truncated", chars=len(text), max=max_chars)
        return text[:max_chars] + "\n\n[...content truncated for length...]"

    def _parse_json_or_yield(self, raw_text: str, fallback_key: str = "content") -> Dict[str, Any]:
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


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter AI provider implementation."""

    def __init__(self):
        super().__init__(settings.OPENROUTER_MODEL)
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = settings.OPENROUTER_API_KEY

    def _make_request(self, payload: dict) -> httpx.Response:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        return httpx.post(self.api_url, json=payload, headers=headers, timeout=60.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        reraise=True,
        retry=retry_if_exception_type((httpx.RequestError,)),
    )
    def _call_api(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1024) -> str:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        response = self._make_request(payload)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

    def generate_summary(self, text: str) -> str:
        truncated = self._truncate_text(text)
        prompt = f"""You are an expert study assistant.

Summarize the following document into clear study notes.
Requirements:
- Use headings.
- Use bullet points.
- Keep important definitions.
- Keep important formulas if present.
- Maximum 500 words.

Document:
{truncated}"""
        try:
            return self._call_api(
                [{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )
        except Exception as exc:
            logger.error("openrouter_summary_failed", error=str(exc))
            raise AIProviderError("Failed to generate document summary.") from exc

    def chat_with_document(self, document_text: str, question: str) -> str:
        truncated = self._truncate_text(document_text)
        prompt = f"""You are an AI study assistant.

Answer ONLY using the information contained in the document below.

If the answer is not present in the document, reply:
"I couldn't find that information in the uploaded document."

Document:
{truncated}

Question:
{question}"""
        try:
            return self._call_api(
                [{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )
        except Exception as exc:
            logger.error("openrouter_chat_failed", error=str(exc))
            raise AIProviderError("Failed to get response from AI model.") from exc

    def _generate_grounded_content(self, document_text: str, instruction: str) -> str:
        truncated = self._truncate_text(document_text)
        prompt = f"""You are an AI study assistant.

Use ONLY the uploaded document to answer.
If information is not in the document, do not fabricate it.

{instruction}

Document:
{truncated}"""
        try:
            return self._call_api(
                [{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1000,
            )
        except Exception as exc:
            logger.error("openrouter_grounded_content_failed", error=str(exc))
            raise AIProviderError("Failed to generate grounded content.") from exc

    def generate_flashcards(self, document_text: str, count: int = 10) -> Dict[str, Any]:
        instruction = f"""Create {count} flashcards from the document.
Return STRICT JSON with this shape:
{{"flashcards": [{{"question": "...", "answer": "..."}}]}}"""
        raw = self._generate_grounded_content(document_text, instruction)
        return self._parse_json_or_yield(raw, fallback_key="flashcards")

    def generate_mcqs(self, document_text: str, count: int = 10, difficulty: str | None = None) -> Dict[str, Any]:
        difficulty_text = difficulty or "medium"
        instruction = f"""Create {count} multiple-choice questions with difficulty '{difficulty_text}'.
Each question must include correct answer and explanation.
Return STRICT JSON:
{{"mcqs": [
    {{
        "question": "...",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "...",
        "difficulty": "{difficulty_text}",
        "explanation": "..."
    }}
]}}"""
        raw = self._generate_grounded_content(document_text, instruction)
        return self._parse_json_or_yield(raw, fallback_key="mcqs")

    def generate_key_points(self, document_text: str) -> Dict[str, Any]:
        instruction = """Generate concise key points from the document.
Return STRICT JSON: {"key_points": ["...", "..."]}"""
        raw = self._generate_grounded_content(document_text, instruction)
        return self._parse_json_or_yield(raw, fallback_key="key_points")

    def generate_study_notes(self, document_text: str) -> Dict[str, Any]:
        instruction = """Create detailed study notes with headings and bullet points.
Return STRICT JSON: {"study_notes": "..."}"""
        raw = self._generate_grounded_content(document_text, instruction)
        return self._parse_json_or_yield(raw, fallback_key="study_notes")

    def generate_quiz(self, document_text: str, count: int = 10, difficulty: str | None = None) -> Dict[str, Any]:
        difficulty_text = difficulty or "medium"
        instruction = f"""Create a quiz with {count} questions and difficulty '{difficulty_text}'.
Return STRICT JSON:
{{"quiz": [
    {{
        "question": "...",
        "answer": "...",
        "difficulty": "{difficulty_text}"
    }}
]}}"""
        raw = self._generate_grounded_content(document_text, instruction)
        return self._parse_json_or_yield(raw, fallback_key="quiz")

    def generate_translation(self, document_text: str, language: str) -> Dict[str, Any]:
        instruction = f"""Translate the document into {language}.
Return STRICT JSON: {{"language": "{language}", "translation": "..."}}"""
        raw = self._generate_grounded_content(document_text, instruction)
        return self._parse_json_or_yield(raw, fallback_key="translation")

    def generate_eli5(self, document_text: str) -> Dict[str, Any]:
        instruction = """Explain the document like I am five years old.
Return STRICT JSON: {"eli5": "..."}"""
        raw = self._generate_grounded_content(document_text, instruction)
        return self._parse_json_or_yield(raw, fallback_key="eli5")

    def generate_roadmap(self, document_text: str) -> Dict[str, Any]:
        instruction = """Create a practical learning roadmap from the document.
Return STRICT JSON:
{
    "roadmap": [
        {"step": 1, "title": "...", "details": "..."}
    ]
}"""
        raw = self._generate_grounded_content(document_text, instruction)
        return self._parse_json_or_yield(raw, fallback_key="roadmap")

    def generate_study_plan(self, document_text: str) -> Dict[str, Any]:
        instruction = """Create a study plan based on document size and complexity.
Return STRICT JSON:
{
    "study_plan": {
        "estimated_days": 0,
        "daily_plan": ["..."]
    }
}"""
        raw = self._generate_grounded_content(document_text, instruction)
        return self._parse_json_or_yield(raw, fallback_key="study_plan")


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider implementation (fallback)."""

    def __init__(self):
        super().__init__("gemini-2.5-flash")
        from google import genai
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def _truncate_text(self, text: str, max_chars: int = MAX_DOCUMENT_CHARS) -> str:
        if not text:
            return ""
        text = text.strip()
        if len(text) <= max_chars:
            return text
        logger.warning("gemini_text_truncated", chars=len(text), max=max_chars)
        return text[:max_chars] + "\n\n[...content truncated for length...]"

    def generate_summary(self, text: str) -> str:
        # Implementation would use Gemini API
        # For brevity, we'll raise NotImplementedError to fall back to next provider
        raise NotImplementedError("Gemini provider not fully implemented in this example")

    # Other methods would follow similar pattern...
    # For this example, we'll make it raise NotImplementedError to trigger fallback
    def chat_with_document(self, document_text: str, question: str) -> str:
        raise NotImplementedError("Gemini provider not fully implemented")

    def generate_flashcards(self, document_text: str, count: int = 10) -> Dict[str, Any]:
        raise NotImplementedError("Gemini provider not fully implemented")

    def generate_mcqs(self, document_text: str, count: int = 10, difficulty: str | None = None) -> Dict[str, Any]:
        raise NotImplementedError("Gemini provider not fully implemented")

    def generate_key_points(self, document_text: str) -> Dict[str, Any]:
        raise NotImplementedError("Gemini provider not fully implemented")

    def generate_study_notes(self, document_text: str) -> Dict[str, Any]:
        raise NotImplementedError("Gemini provider not fully implemented")

    def generate_quiz(self, document_text: str, count: int = 10, difficulty: str | None = None) -> Dict[str, Any]:
        raise NotImplementedError("Gemini provider not fully implemented")

    def generate_translation(self, document_text: str, language: str) -> Dict[str, Any]:
        raise NotImplementedError("Gemini provider not fully implemented")

    def generate_eli5(self, document_text: str) -> Dict[str, Any]:
        raise NotImplementedError("Gemini provider not fully implemented")

    def generate_roadmap(self, document_text: str) -> Dict[str, Any]:
        raise NotImplementedError("Gemini provider not fully implemented")

    def generate_study_plan(self, document_text: str) -> Dict[str, Any]:
        raise NotImplementedError("Gemini provider not fully implemented")


class MultiProviderAIService:
    """AI service that tries multiple providers with fallback."""

    def __init__(self):
        self.providers: List[AIProvider] = []
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available providers in order of preference."""
        # Try to add OpenRouter (primary)
        try:
            if hasattr(settings, 'OPENROUTER_API_KEY') and settings.OPENROUTER_API_KEY:
                self.providers.append(OpenRouterProvider())
                logger.info("Initialized OpenRouter provider")
        except Exception as e:
            logger.warning("Failed to initialize OpenRouter provider", error=str(e))

        # Try to add Gemini (fallback)
        try:
            if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
                self.providers.append(GeminiProvider())
                logger.info("Initialized Gemini provider")
        except Exception as e:
            logger.warning("Failed to initialize Gemini provider", error=str(e))

        # Ensure we have at least one provider
        if not self.providers:
            logger.error("No AI providers available!")
            raise RuntimeError("No AI providers configured")

    def _try_provider(self, method_name: str, *args, **kwargs):
        """Try the method on each provider until one succeeds."""
        last_exception = None
        for provider in self.providers:
            try:
                method = getattr(provider, method_name)
                return method(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Provider {provider.__class__.__name__} failed for {method_name}", error=str(e))
                last_exception = e
                continue
        
        # If all providers failed, raise the last exception
        raise last_exception or AIProviderError("All AI providers failed")

    # Delegate all methods to the provider chain
    def generate_summary(self, text: str) -> str:
        return self._try_provider("generate_summary", text)

    def chat_with_document(self, document_text: str, question: str) -> str:
        return self._try_provider("chat_with_document", document_text, question)

    def generate_flashcards(self, document_text: str, count: int = 10) -> Dict[str, Any]:
        return self._try_provider("generate_flashcards", document_text, count)

    def generate_mcqs(self, document_text: str, count: int = 10, difficulty: str | None = None) -> Dict[str, Any]:
        return self._try_provider("generate_mcqs", document_text, count, difficulty)

    def generate_key_points(self, document_text: str) -> Dict[str, Any]:
        return self._try_provider("generate_key_points", document_text)

    def generate_study_notes(self, document_text: str) -> Dict[str, Any]:
        return self._try_provider("generate_study_notes", document_text)

    def generate_quiz(self, document_text: str, count: int = 10, difficulty: str | None = None) -> Dict[str, Any]:
        return self._try_provider("generate_quiz", document_text, count, difficulty)

    def generate_translation(self, document_text: str, language: str) -> Dict[str, Any]:
        return self._try_provider("generate_translation", document_text, language)

    def generate_eli5(self, document_text: str) -> Dict[str, Any]:
        return self._try_provider("generate_eli5", document_text)

    def generate_roadmap(self, document_text: str) -> Dict[str, Any]:
        return self._try_provider("generate_roadmap", document_text)

    def generate_study_plan(self, document_text: str) -> Dict[str, Any]:
        return self._try_provider("generate_study_plan", document_text)


# Singleton instance
ai_service = MultiProviderAIService()