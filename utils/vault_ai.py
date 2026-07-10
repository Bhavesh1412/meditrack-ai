"""
vault_ai.py - AI document analysis for Health Vault
Tries OpenAI API first; falls back with clear errors if unavailable.
"""

import json
import re
from typing import Optional

from utils.openai_helper import (
    OPENAI_AVAILABLE,
    chat_completions_create,
    get_groq_model,
    get_openai_model,
    is_groq_configured,
    is_openai_configured,
)

# ─── SYSTEM PROMPT FOR DOCUMENT ANALYSIS ─────────────────────────────────────
ANALYSIS_SYSTEM_PROMPT = """You are a medical document analyser for Nabz AI, an Indian health management platform.
Analyse the provided medical document text and return a JSON object with exactly these keys:

{
"summary": "Plain language summary of the document in 3-4 sentences. Mention key findings, values, or medicines prescribed. Write as if explaining to a patient with no medical background.",
"conflicts": "Any drug conflicts, dangerous combinations, or concerning findings. Cross-reference with the patient's existing medicines list provided. If no conflicts found, write 'No conflicts detected with your current medicines.' Be specific about which medicines conflict and why.",
"suggestions": "2-3 practical health suggestions based on this document. Focus on actionable advice. Always end with: Consult your doctor before making any changes to your treatment."
}

IMPORTANT: Return ONLY valid JSON. No markdown, no explanation, no backticks."""

VAULT_CHAT_SYSTEM_PROMPT = """You are a medical document assistant for Nabz AI, an Indian health management platform.
The user has uploaded a medical document. You receive the document text and/or an AI summary.
You also know the patient's current active medicines.

Your role:
- Answer questions about the uploaded document in simple language
- Explain medical terms, lab values, or diagnoses
- Point out anything the patient should ask their doctor about
- Check for interactions between document medicines and their existing medicines

Always include: This is general information only, not medical advice. Consult your doctor.
Be friendly, empathetic, and concise. Keep responses under 200 words."""

STALE_SUMMARY_MARKERS = (
    'openai api key',
    'ai analysis is currently unavailable',
    'please connect an openai',
    'configure an openai api key',
)


def is_stale_summary(summary: Optional[str]) -> bool:
    """True if summary was saved from the no-API-key fallback."""
    if not summary:
        return True
    lower = summary.lower()
    return any(marker in lower for marker in STALE_SUMMARY_MARKERS)


def _parse_analysis_json(raw: str) -> dict:
    """Parse model JSON, tolerating markdown fences."""
    text = raw.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    return json.loads(text)


def _openai_error_message(exc: Exception, lang: str = 'en') -> str:
    err = str(exc).lower()
    if 'invalid_api_key' in err or 'incorrect api key' in err:
        msg = 'OpenAI rejected the API key. Check OPENAI_API_KEY on Render (no extra spaces).'
    elif 'insufficient_quota' in err or 'billing' in err or 'exceeded' in err:
        msg = 'OpenAI quota or billing issue. Add credits at platform.openai.com/account/billing.'
    elif 'rate_limit' in err:
        msg = 'OpenAI rate limit reached. Wait a minute and try again.'
    else:
        msg = f'OpenAI request failed: {exc}'
    if lang == 'hi':
        return (
            f"AI सेवा अस्थायी रूप से उपलब्ध नहीं है: {msg} "
            "कृपया Render पर API key और OpenAI billing जाँचें। 🩺"
        )
    return f"{msg} Please verify your Render environment variable and OpenAI billing. 🩺"


def analyse_document(extracted_text: str, existing_medicines: list, lang: str = 'en') -> dict:
    """
    Analyse a medical document using OpenAI (or fallback).
    Returns dict: summary, conflicts, suggestions, source, error (optional)
    """
    medicines_str = ", ".join(existing_medicines) if existing_medicines else "No medicines currently recorded."

    if not extracted_text or not extracted_text.strip():
        return {
            'summary': 'No readable text could be extracted from this file. Try a text-based PDF or clearer image.',
            'conflicts': f'Your current medicines: {medicines_str}. Please review manually with your doctor.',
            'suggestions': 'Consult your doctor before making any changes to your treatment.',
            'source': 'local',
        }

    if not is_openai_configured():
        return _local_analysis_fallback(extracted_text, medicines_str, reason='no_key', lang=lang)

    try:
        user_prompt = f"""Analyse this medical document:

--- DOCUMENT TEXT ---
{extracted_text[:4000]}
--- END DOCUMENT ---

Patient's current medicines: {medicines_str}

Return ONLY valid JSON with keys: summary, conflicts, suggestions."""

        response, source = chat_completions_create(
            messages=[
                {'role': 'system', 'content': ANALYSIS_SYSTEM_PROMPT},
                {'role': 'user',   'content': user_prompt},
            ],
            max_tokens=600,
            temperature=0.5,
        )

        raw = response.choices[0].message.content.strip()
        result = _parse_analysis_json(raw)
        result['source'] = source
        return result

    except Exception as e:
        print(f'Vault AI analysis error: {e}')
        return _local_analysis_fallback(
            extracted_text, medicines_str,
            reason='api_error', error=str(e), lang=lang,
        )

        raw = response.choices[0].message.content.strip()
        result = _parse_analysis_json(raw)
        result['source'] = 'openai'
        return result

    except Exception as e:
        print(f'Vault AI analysis error: {e}')
        return _local_analysis_fallback(
            extracted_text, medicines_str,
            reason='api_error', error=str(e), lang=lang,
        )


def _local_analysis_fallback(extracted_text, medicines_str, reason='no_key', error=None, lang='en'):
    preview = extracted_text[:500].strip()
    if len(extracted_text) > 500:
        preview += '…'

    if reason == 'api_error':
        summary = _openai_error_message(Exception(error or 'unknown'), lang)
    elif lang == 'hi':
        summary = (
            f'दस्तावेज़ से {len(extracted_text)} अक्षर निकाले गए। '
            'AI विश्लेषण के लिए Render पर OPENAI_API_KEY सेट करें, फिर Re-analyze दबाएँ।'
        )
    else:
        summary = (
            f'Extracted {len(extracted_text)} characters from the document. '
            'Set OPENAI_API_KEY in Render Environment, redeploy, then click Re-analyze.'
        )

    return {
        'summary': summary,
        'conflicts': (
            f'Unable to check conflicts automatically. Current medicines: {medicines_str}.'
        ),
        'suggestions': (
            f'Document preview:\n{preview}\n\n'
            'Review this document with your doctor.'
        ),
        'source': 'local',
        'error': error,
    }


def vault_chat_response(
    user_message: str,
    document_summary: str = None,
    document_text: str = None,
    medicines_list: list = None,
    chat_history: list = None,
    lang: str = 'en',
) -> dict:
    """Generate vault chat response with document context."""
    medicines_list = medicines_list or []
    medicines_str = ', '.join(medicines_list) if medicines_list else 'No medicines currently recorded.'

    # Prefer live document text over stale placeholder summary
    context_parts = []
    if document_text and document_text.strip():
        context_parts.append(f'--- DOCUMENT TEXT ---\n{document_text[:3500]}\n--- END ---')
    if document_summary and not is_stale_summary(document_summary):
        context_parts.append(f'Document summary: {document_summary}')
    elif document_summary and is_stale_summary(document_summary) and not document_text:
        context_parts.append(
            'Note: Document was not yet analysed by AI. Use any extracted text if present.'
        )

    context_block = '\n\n'.join(context_parts) if context_parts else 'No document content available.'
    context_block += f'\n\nPatient current medicines: {medicines_str}'

    system_prompt = VAULT_CHAT_SYSTEM_PROMPT
    if lang == 'hi':
        system_prompt += (
            '\n\nIMPORTANT: Respond entirely in Hindi (Devanagari). '
            'Disclaimer: यह केवल सामान्य जानकारी है, चिकित्सा सलाह नहीं।'
        )

    if not (is_openai_configured() or is_groq_configured()):
        if lang == 'hi':
            return {
                'response': (
                    'AI चैट के लिए OPENAI_API_KEY या GROQ_API_KEY Render Environment में सेट करें और redeploy करें। '
                    'फिर दस्तावेज़ पर Re-analyze दबाएँ। 🩺'
                ),
                'source': 'local',
            }
        return {
            'response': (
                'Health Vault AI needs OPENAI_API_KEY or GROQ_API_KEY in Render → Environment. '
                'After saving, wait for redeploy, then click Re-analyze on your document. 🩺'
            ),
            'source': 'local',
        }

    try:
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'system', 'content': context_block},
        ]

        if chat_history:
            for entry in chat_history[-10:]:
                messages.append({'role': entry['role'], 'content': entry['message']})

        messages.append({'role': 'user', 'content': user_message})

        response, source = chat_completions_create(
            messages=messages,
            max_tokens=400,
            temperature=0.7,
        )

        return {
            'response': response.choices[0].message.content,
            'source': source,
        }

    except Exception as e:
        print(f'Vault chat AI error: {e}')
        return {
            'response': _openai_error_message(e, lang),
            'source': 'local',
            'error': str(e),
        }
