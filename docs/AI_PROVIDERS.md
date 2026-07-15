# AI Provider Configuration

This project supports multiple AI providers with automatic fallback.

## OpenRouter (Primary Provider)

Get your free API key at: https://openrouter.ai/keys

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=google/gemini-2.5-flash
```

## Provider Priority

1. **OpenRouter** - Primary (fastest, most reliable)
2. **Google Gemini** - Fallback (if configured)

## Configuration

Edit `.env` file:
```bash
# Primary provider
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=google/gemini-2.5-flash

# Optional fallback
GEMINI_API_KEY=your_gemini_key_here
```

## Rate Limits

- OpenRouter: ~200 tokens/sec (generous free tier)
- Default limit: 30 requests/minute per IP
- Text truncation: 60,000 characters max per document