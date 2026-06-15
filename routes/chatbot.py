"""
chatbot.py (route) - AI Health Assistant routes
"""

from flask import Blueprint, render_template, request, jsonify, session
from utils.database import get_db_connection
from utils.auth_helpers import login_required
from utils.chatbot import get_ai_response

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/chatbot')
@login_required
def index():
    """Show chatbot page with chat history."""
    user_id = session['user_id']
    conn    = get_db_connection()
    history = conn.execute("""
        SELECT * FROM chat_history
        WHERE user_id = ?
        ORDER BY created_at ASC
        LIMIT 50
    """, (user_id,)).fetchall()
    conn.close()
    return render_template('chatbot.html', history=history)


@chatbot_bp.route('/chatbot/send', methods=['POST'])
@login_required
def send():
    """
    API endpoint: receive user message, return AI response.
    Saves both messages to chat_history.
    """
    user_id = session['user_id']
    data    = request.get_json()
    user_msg = data.get('message', '').strip()

    if not user_msg:
        return jsonify({'error': 'Empty message'}), 400

    if len(user_msg) > 500:
        return jsonify({'error': 'Message too long (max 500 chars)'}), 400

    # Get recent history for context
    conn = get_db_connection()
    history = conn.execute("""
        SELECT role, message FROM chat_history
        WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 10
    """, (user_id,)).fetchall()

    # Get AI response
    result = get_ai_response(user_msg, [dict(h) for h in reversed(history)])
    bot_reply = result['response']
    source    = result['source']

    # Save both messages
    conn.execute(
        "INSERT INTO chat_history (user_id, role, message) VALUES (?, 'user', ?)",
        (user_id, user_msg)
    )
    conn.execute(
        "INSERT INTO chat_history (user_id, role, message) VALUES (?, 'assistant', ?)",
        (user_id, bot_reply)
    )
    conn.commit()
    conn.close()

    return jsonify({
        'response': bot_reply,
        'source':   source   # 'openai' or 'local' — shown in UI
    })


@chatbot_bp.route('/chatbot/clear', methods=['POST'])
@login_required
def clear():
    """Clear chat history for the current user."""
    user_id = session['user_id']
    conn    = get_db_connection()
    conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
