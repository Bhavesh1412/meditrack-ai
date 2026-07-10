"""
vault_ai.py - AI document analysis for Health Vault
Tries OpenAI API first; falls back to local summary if unavailable.
"""

import os
import json

# ─── OPENAI INTEGRATION ──────────────────────────────────────────────────────
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# ─── SYSTEM PROMPT FOR DOCUMENT ANALYSIS ─────────────────────────────────────
ANALYSIS_SYSTEM_PROMPT = """You are a medical document analyser for Nabz AI, an Indian health management platform.
Analyse the provided medical document text and return a JSON object with exactly these keys:

{{
"summary": "Plain language summary of the document in 3-4 sentences. Mention key findings, values, or medicines prescribed. Write as if explaining to a patient with no medical background.",
"conflicts": "Any drug conflicts, dangerous combinations, or concerning findings. Cross-reference with the patient's existing medicines list provided. If no conflicts found, write 'No conflicts detected with your current medicines.' Be specific about which medicines conflict and why.",
"suggestions": "2-3 practical health suggestions based on this document. Focus on actionable advice. Always end with: Consult your doctor before making any changes to your treatment."
}}

IMPORTANT: Return ONLY valid JSON. No markdown, no explanation, no backticks."""

# ─── SYSTEM PROMPT FOR VAULT CHAT ────────────────────────────────────────────
VAULT_CHAT_SYSTEM_PROMPT = """You are a medical document assistant for Nabz AI, an Indian health management platform.
The user has uploaded a medical document and you have access to its AI-generated summary.
You also know the patient's current active medicines.

Your role:
- Answer questions about the uploaded document in simple language
- Explain medical terms, lab values, or diagnoses
- Point out anything the patient should ask their doctor about
- Check for interactions between document medicines and their existing medicines

Always include: This is general information only, not medical advice. Consult your doctor.
Be friendly, empathetic, and concise. Keep responses under 200 words."""


def analyse_document(extracted_text: str, existing_medicines: list) -> dict:
    """
    Analyse a medical document using OpenAI (or fallback).
    
    Args:
        extracted_text: Text extracted from the document (PDF/image)
        existing_medicines: List of medicine names the patient is currently taking
        
    Returns:
        dict with keys: summary, conflicts, suggestions, source
    """
    medicines_str = ", ".join(existing_medicines) if existing_medicines else "No medicines currently recorded."

    # ── TRY OPENAI API ────────────────────────────────────────────────────────
    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)

            user_prompt = f"""Analyse this medical document:

--- DOCUMENT TEXT ---
{extracted_text[:4000]}
--- END DOCUMENT ---

Patient's current medicines: {medicines_str}

Return ONLY valid JSON with keys: summary, conflicts, suggestions."""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=600,
                temperature=0.5
            )

            raw = response.choices[0].message.content.strip()

            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()

            result = json.loads(raw)
            result["source"] = "openai"
            return result

        except Exception as e:
            print(f"⚠️ Vault AI analysis error: {e}. Falling back to local summary.")

    # ── FALLBACK: LOCAL SUMMARY ────────────────────────────────────────────────
    return {
        "summary": (
            f"Document text was received ({len(extracted_text)} characters extracted). "
            "AI analysis is currently unavailable — please connect an OpenAI API key for automated analysis, "
            "or review the document content manually."
        ),
        "conflicts": (
            "Unable to check for drug conflicts automatically. "
            f"Your current medicines: {medicines_str}. "
            "Please cross-check with your doctor."
        ),
        "suggestions": (
            "1. Review this document with your doctor at your next visit.\n"
            "2. Keep a digital copy for your records.\n"
            "3. Consult your doctor before making any changes to your treatment."
        ),
        "source": "local"
    }


def vault_chat_response(user_message: str, document_summary: str,
                        medicines_list: list, chat_history: list = None,
                        lang: str = 'en') -> dict:
    """
    Generate a chat response in context of a specific vault document.
    
    Args:
        user_message: The user's question
        document_summary: AI summary of the document being discussed
        medicines_list: List of patient's active medicine names
        chat_history: Previous vault_chat entries [{role, message}, ...]
        lang: Language code ('en' or 'hi')
        
    Returns:
        dict with 'response' (str) and 'source' ('openai' or 'local')
    """
    medicines_str = ", ".join(medicines_list) if medicines_list else "No medicines currently recorded."
    summary_text = document_summary or "No document summary available."

    system_prompt = VAULT_CHAT_SYSTEM_PROMPT
    if lang == 'hi':
        system_prompt += (
            "\n\nIMPORTANT: Respond entirely in Hindi using Devanagari script. "
            "Keep medicine names in common form. "
            "Always include this disclaimer in Hindi: यह केवल सामान्य जानकारी है, चिकित्सा सलाह नहीं।"
        )

    # ── TRY OPENAI API ────────────────────────────────────────────────────────
    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)

            messages = [{"role": "system", "content": system_prompt}]

            # Add context about the document
            context_msg = (
                f"Document summary: {summary_text}\n\n"
                f"Patient's current medicines: {medicines_str}"
            )
            messages.append({"role": "system", "content": context_msg})

            # Add chat history (last 10 messages for vault context)
            if chat_history:
                for entry in chat_history[-10:]:
                    messages.append({
                        "role": entry['role'],
                        "content": entry['message']
                    })

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )

            return {
                "response": response.choices[0].message.content,
                "source": "openai"
            }

        except Exception as e:
            print(f"⚠️ Vault chat AI error: {e}. Falling back to local response.")

    # ── FALLBACK ───────────────────────────────────────────────────────────────
    if lang == 'hi':
        return {
            "response": (
                "मैं इस दस्तावेज़ के बारे में आपके प्रश्न का उत्तर देना चाहूँगा, लेकिन AI सेवा अभी उपलब्ध नहीं है। "
                "कृपया OpenAI API key कॉन्फ़िगर करें। "
                "तब तक कृपया अपने डॉक्टर से परामर्श करें। 🩺"
            ),
            "source": "local"
        }

    return {
        "response": (
            "I'd like to help with your question about this document, but the AI service "
            "is currently unavailable. Please configure an OpenAI API key for full analysis. "
            "In the meantime, please consult your doctor for medical advice. 🩺"
        ),
        "source": "local"
    }
