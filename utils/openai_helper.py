"""
openai_helper.py - Multi-provider AI configuration (OpenAI / Groq)
Reads env at runtime. Groq acts as free fallback when OpenAI quota/billing fails.
"""

import os

try:
    from openai import OpenAI
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None
    httpx = None


# ─── ENV READERS ───────────────────────────────────────────────────────────────

def get_openai_api_key() -> str:
    return (os.environ.get('OPENAI_API_KEY') or '').strip()

def get_groq_api_key() -> str:
    return (os.environ.get('GROQ_API_KEY') or '').strip()

def get_openai_model() -> str:
    return os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo').strip() or 'gpt-3.5-turbo'

def get_groq_model() -> str:
    return os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile').strip() or 'llama-3.3-70b-versatile'


# ─── CLIENT FACTORIES ─────────────────────────────────────────────────────────

def _http_client():
    if httpx:
        return httpx.Client(proxy=None)
    return None


def create_openai_client():
    if not get_openai_api_key():
        return None
    return OpenAI(api_key=get_openai_api_key(), http_client=_http_client())


def create_groq_client():
    if not get_groq_api_key():
        return None
    return OpenAI(
        api_key=get_groq_api_key(),
        base_url='https://api.groq.com/openai/v1',
        http_client=_http_client(),
    )


# ─── CHAT COMPLETIONS WITH FALLBACK ───────────────────────────────────────────

def is_groq_configured() -> bool:
    return OPENAI_AVAILABLE and bool(get_groq_api_key())


def is_openai_configured() -> bool:
    return OPENAI_AVAILABLE and bool(get_openai_api_key())


def chat_completions_create(messages, max_tokens=200, temperature=0.7):
    """
    Try OpenAI first. On quota/billing/rate-limit errors, fall back to Groq.
    Returns (response, source) where source is 'openai' or 'groq'.
    Raises only if both providers fail.
    """
    # 1) Try OpenAI
    if is_openai_configured():
        try:
            client = create_openai_client()
            resp = client.chat.completions.create(
                model=get_openai_model(),
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp, 'openai'
        except Exception as exc:
            err = str(exc).lower()
            quota_errors = [
                'insufficient_quota', 'billing', 'quota', 'exceeded',
                'rate_limit', '429',
            ]
            if any(k in err for k in quota_errors) and is_groq_configured():
                print(f"[AI] OpenAI quota/billing error, falling back to Groq: {exc}")
            else:
                raise

    # 2) Fall back to Groq
    if is_groq_configured():
        client = create_groq_client()
        resp = client.chat.completions.create(
            model=get_groq_model(),
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp, 'groq'

    raise RuntimeError('No AI provider configured. Set OPENAI_API_KEY or GROQ_API_KEY.')
