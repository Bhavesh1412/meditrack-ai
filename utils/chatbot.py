"""
chatbot.py - AI Health Assistant logic
Tries OpenAI API first; falls back to local keyword-based responses.
"""

import re

from utils.openai_helper import chat_completions_create, get_groq_model, is_groq_configured, is_openai_configured

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


def get_system_prompt(lang: str = 'en') -> str:
    prompt = SYSTEM_PROMPT.strip()
    if lang == 'hi':
        prompt += (
            "\n\nIMPORTANT: Respond entirely in Hindi using Devanagari script. "
            "Keep medicine names in common form. "
            "Always include this disclaimer in Hindi: यह केवल सामान्य जानकारी है, चिकित्सा सलाह नहीं।"
        )
    return prompt


# Hindi fallback responses (same keyword triggers)
FALLBACK_RESPONSES_HI = [
    (
        ['side effect', 'side effects', 'reaction', 'adverse', 'dushprabhav', 'प्रभाव'],
        "दुष्प्रभाव दवा के अनुसार अलग होते हैं। सामान्य में मितली, चक्कर, सिरदर्द या थकान शामिल हैं। "
        "दवा की पर्ची पढ़ें और गंभीर प्रतिक्रिया पर तुरंत डॉक्टर को बताएँ। 🩺"
    ),
    (
        ['miss', 'missed', 'forgot', 'skip', 'skipped', 'bhool', 'chhod'],
        "अगर खुराक छूट गई हो तो याद आते ही लें — जब तक अगली खुराक का समय न हो। "
        "कभी दोहरी खुराक न लें। MediTrack में रिमाइंडर सेट करें! ⏰"
    ),
    (
        ['dosage', 'dose', 'how much', 'khurak', 'खुराक'],
        "खुराक विशिष्ट दवा और डॉक्टर के नुस्खे पर निर्भर करती है। "
        "हमेशा निर्धारित मात्रा लें। बिना डॉक्टर की सलाह के खुराक न बदलें। 💊"
    ),
    (
        ['hello', 'hi', 'hey', 'namaste', 'नमस्ते'],
        "नमस्ते! 👋 मैं मेडीबॉट, आपका AI स्वास्थ्य सहायक हूँ। "
        "दवा, दुष्प्रभाव और सामान्य स्वास्थ्य मार्गदर्शन में मदद कर सकता हूँ। "
        "आज क्या जानना चाहेंगे?"
    ),
    (
        ['thank', 'thanks', 'dhanyavad', 'धन्यवाद'],
        "आपका स्वागत है! 😊 गंभीर स्वास्थ्य चिंताओं के लिए हमेशा योग्य डॉक्टर से परामर्श लें। स्वस्थ रहें!"
    ),
    (
        ['help', 'madad', 'मदद'],
        "मैं मदद कर सकता हूँ: 💊 दवा जानकारी, ⚠️ दुष्प्रभाव, 📅 खुराक समय, 🏥 सामान्य स्वास्थ्य मार्गदर्शन। बस पूछें!"
    ),
]

DEFAULT_RESPONSE_HI = (
    "यह एक अच्छा स्वास्थ्य प्रश्न है! सटीक और व्यक्तिगत सलाह के लिए "
    "डॉक्टर या फार्मासिस्ट से परामर्श करें। मैं दवाओं और कल्याण की सामान्य जानकारी देने के लिए यहाँ हूँ। "
    "और क्या मदद करूँ? 😊"
)


def get_fallback_response(user_message: str, lang: str = 'en') -> str:
    """
    Local keyword-based response system.
    Scans the user's message for known health keywords and returns a response.
    """
    message_lower = user_message.lower()
    responses = FALLBACK_RESPONSES_HI if lang == 'hi' else FALLBACK_RESPONSES

    for keywords, response in responses:
        if any(keyword in message_lower for keyword in keywords):
            return response

    return DEFAULT_RESPONSE_HI if lang == 'hi' else DEFAULT_RESPONSE


def get_ai_response(user_message: str, chat_history: list = None, lang: str = 'en') -> dict:
    """
    Main function to get chatbot response.
    Tries OpenAI first → falls back to local NLP if unavailable.

    Args:
        user_message: The user's input message
        chat_history: Previous messages [{role, message}, ...] for context

    Returns:
        dict with 'response' (str) and 'source' ('openai' or 'local')
    """
    # ── TRY AI (OpenAI first, Groq as free fallback) ─────────────────────────
    if is_openai_configured() or is_groq_configured():
        try:
            messages = [{"role": "system", "content": get_system_prompt(lang)}]

            if chat_history:
                for entry in chat_history[-6:]:
                    messages.append({
                        "role": entry['role'],
                        "content": entry['message']
                    })

            messages.append({"role": "user", "content": user_message})

            response, source = chat_completions_create(
                messages,
                max_tokens=200,
                temperature=0.7,
            )

            return {
                "response": response.choices[0].message.content,
                "source": source   # 'openai' or 'groq'
            }

        except Exception as e:
            print(f"⚠️ AI API error: {e}. Falling back to local responses.")

    # ── FALLBACK: LOCAL KEYWORD MATCHING ─────────────────────────────────────
    return {
        "response": get_fallback_response(user_message, lang),
        "source": "local"
    }
