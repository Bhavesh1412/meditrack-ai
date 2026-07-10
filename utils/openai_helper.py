"""
openai_helper.py - Shared OpenAI configuration (read env at runtime)
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


def get_openai_api_key() -> str:
    """Read API key at call time (works after Render env injection / load_dotenv)."""
    return (os.environ.get('OPENAI_API_KEY') or '').strip()


def get_openai_model() -> str:
    return os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo').strip() or 'gpt-3.5-turbo'


def is_openai_configured() -> bool:
    return OPENAI_AVAILABLE and bool(get_openai_api_key())


def create_openai_client():
    if not is_openai_configured():
        return None
    _http_client = httpx.Client(proxy=None) if httpx else None
    return OpenAI(api_key=get_openai_api_key(), http_client=_http_client)
