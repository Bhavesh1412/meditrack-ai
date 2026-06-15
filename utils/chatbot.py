"""
chatbot.py - AI Health Assistant logic
Tries OpenAI API first; falls back to local keyword-based responses.
"""

import os
import re

# ─── OPENAI INTEGRATION ──────────────────────────────────────────────────────
# Install with: pip install openai
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# ─── SYSTEM PROMPT FOR THE AI ────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are MediBot, a helpful AI health assistant integrated into MediTrack AI.
Your role is to:
- Answer questions about medications, dosages, and schedules
- Explain common side effects of medicines
- Provide general health and wellness guidance
- Remind users to consult their doctor for serious concerns

Always include the disclaimer: This is general information only, not medical advice.
Be friendly, empathetic, and concise. Keep responses under 150 words.
"""

# ─── LOCAL FALLBACK RESPONSES (keyword-based NLP) ───────────────────────────
# Each entry: (list of keywords, response string)
FALLBACK_RESPONSES = [
    (
        ['side effect', 'side effects', 'reaction', 'adverse'],
        "Common side effects vary by medication. General ones include nausea, "
        "dizziness, headache, or fatigue. Always read your medicine's leaflet "
        "and report severe reactions to your doctor immediately. 🩺"
    ),
    (
        ['miss', 'missed', 'forgot', 'skip', 'skipped'],
        "If you missed a dose, take it as soon as you remember — unless it's "
        "almost time for the next one. Never double-dose. Set reminders in "
        "MediTrack to avoid missing doses in the future! ⏰"
    ),
    (
        ['dosage', 'dose', 'how much', 'how many'],
        "Dosage depends on the specific medicine and your doctor's prescription. "
        "Always follow the prescribed amount. Never adjust dosage without "
        "consulting your healthcare provider. 💊"
    ),
    (
        ['paracetamol', 'panadol', 'acetaminophen', 'tylenol'],
        "Paracetamol (500–1000mg) is used for pain and fever. Max adult dose: "
        "4g/day. Avoid alcohol while taking it. Overdose can cause serious "
        "liver damage — stick to prescribed amounts. 🌡️"
    ),
    (
        ['ibuprofen', 'advil', 'brufen'],
        "Ibuprofen is a common NSAID used for pain, fever, and inflammation. "
        "Take with food to protect your stomach. Avoid if you have kidney "
        "issues or are on blood thinners. Consult your doctor. 💊"
    ),
    (
        ['antibiotic', 'antibiotics', 'amoxicillin', 'azithromycin'],
        "Always complete the full antibiotic course even if you feel better. "
        "Stopping early causes antibiotic resistance. Common side effects: "
        "nausea, diarrhea. Never take someone else's antibiotics. 🦠"
    ),
    (
        ['blood pressure', 'hypertension', 'bp'],
        "High blood pressure often has no symptoms. Take BP medication exactly "
        "as prescribed — don't stop without doctor approval. Lifestyle tips: "
        "reduce salt, exercise regularly, manage stress. 🫀"
    ),
    (
        ['diabetes', 'insulin', 'metformin', 'blood sugar'],
        "Diabetes management involves medication, diet, and monitoring blood "
        "sugar. Never skip doses. Report symptoms of hypoglycemia (shaking, "
        "sweating, confusion) immediately. Work closely with your doctor. 🩸"
    ),
    (
        ['headache', 'migraine', 'pain'],
        "For headaches, ensure hydration, rest, and reduced screen time. "
        "OTC options like paracetamol or ibuprofen help mild cases. "
        "Severe or recurring headaches need medical evaluation. 🧠"
    ),
    (
        ['sleep', 'insomnia', 'tired', 'fatigue'],
        "Good sleep hygiene includes a fixed sleep schedule, avoiding screens "
        "before bed, and limiting caffeine. If fatigue persists despite rest, "
        "consult a doctor to rule out underlying conditions. 😴"
    ),
    (
        ['hello', 'hi', 'hey', 'good morning', 'good evening'],
        "Hello! 👋 I'm MediBot, your AI health assistant. I can help you with "
        "medication questions, side effects, and general health guidance. "
        "What would you like to know today?"
    ),
    (
        ['thank', 'thanks', 'thank you'],
        "You're welcome! 😊 Remember — for serious health concerns, always "
        "consult a qualified healthcare professional. Stay healthy!"
    ),
    (
        ['help', 'what can you do', 'capabilities'],
        "I can help you with: 💊 Medication information, ⚠️ Side effects, "
        "📅 Dose timing advice, 🏥 General health guidance. Just ask me "
        "anything related to your medications or health!"
    ),
]

# Default response when no keywords match
DEFAULT_RESPONSE = (
    "That's a great health question! For accurate and personalized advice, "
    "please consult your doctor or pharmacist. I'm here to provide general "
    "information about medications and wellness. What else can I help with? 😊"
)


def get_fallback_response(user_message: str) -> str:
    """
    Local keyword-based response system.
    Scans the user's message for known health keywords and returns a response.

    This is the fallback when OpenAI API is unavailable.
    """
    message_lower = user_message.lower()

    for keywords, response in FALLBACK_RESPONSES:
        # Check if ANY keyword matches the user message
        if any(keyword in message_lower for keyword in keywords):
            return response

    return DEFAULT_RESPONSE


def get_ai_response(user_message: str, chat_history: list = None) -> dict:
    """
    Main function to get chatbot response.
    Tries OpenAI first → falls back to local NLP if unavailable.

    Args:
        user_message: The user's input message
        chat_history: Previous messages [{role, message}, ...] for context

    Returns:
        dict with 'response' (str) and 'source' ('openai' or 'local')
    """
    # ── TRY OPENAI API ────────────────────────────────────────────────────────
    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)

            # Build message history for context-aware conversation
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add up to last 6 messages for context (keeps API cost low)
            if chat_history:
                for entry in chat_history[-6:]:
                    messages.append({
                        "role": entry['role'],
                        "content": entry['message']
                    })

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )

            return {
                "response": response.choices[0].message.content,
                "source": "openai"
            }

        except Exception as e:
            print(f"⚠️ OpenAI API error: {e}. Falling back to local responses.")

    # ── FALLBACK: LOCAL KEYWORD MATCHING ─────────────────────────────────────
    return {
        "response": get_fallback_response(user_message),
        "source": "local"
    }
