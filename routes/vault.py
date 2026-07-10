"""
vault.py - Health Vault routes
Handles: document upload, AI analysis, file serving, vault chat, deletion
"""

import os
import uuid
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    session, flash, jsonify, send_file, current_app
)
from utils.database import get_db_connection
from utils.auth_helpers import login_required
from utils.i18n import t
from utils.vault_ai import analyse_document, vault_chat_response

vault_bp = Blueprint('vault', __name__)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'vault')

FILE_TYPE_ICONS = {
    'prescription': '💊',
    'report': '🩸',
    'xray': '📷',
    'discharge': '📄',
    'other': '📎',
}

MIME_TYPES = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
}


def _allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_upload_dir(user_id):
    """Get (and create if needed) the upload directory for a user."""
    upload_dir = os.path.join(UPLOAD_BASE, str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def _format_file_size(size_bytes):
    """Format bytes into human-readable size string."""
    if not size_bytes:
        return '—'
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    else:
        return f'{size_bytes / (1024 * 1024):.1f} MB'


def _time_ago(dt_string):
    """Convert a datetime string to a relative 'time ago' string."""
    if not dt_string:
        return ''
    try:
        dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            mins = seconds // 60
            return f'{mins} min ago' if mins != 1 else '1 min ago'
        elif seconds < 86400:
            hours = seconds // 3600
            return f'{hours}h ago' if hours != 1 else '1h ago'
        else:
            days = seconds // 86400
            return f'{days}d ago' if days != 1 else '1d ago'
    except (ValueError, TypeError):
        return dt_string


# ─── LIST ALL DOCUMENTS ───────────────────────────────────────────────────────
@vault_bp.route('/vault')
@login_required
def index():
    """Show all uploaded documents for the current user."""
    user_id = session['user_id']
    conn = get_db_connection()

    documents = conn.execute("""
        SELECT * FROM health_vault
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
    """, (user_id,)).fetchall()

    medicines = conn.execute("""
        SELECT name FROM medicines
        WHERE user_id = ? AND is_active = 1
        ORDER BY name
    """, (user_id,)).fetchall()

    total_count = len(documents)
    analysed_count = sum(1 for d in documents if d['ai_summary'])
    pending_count = total_count - analysed_count

    conn.close()

    # Attach helper data to each document
    docs_with_meta = []
    for doc in documents:
        doc_dict = dict(doc)
        doc_dict['icon'] = FILE_TYPE_ICONS.get(doc_dict['file_type'], '📎')
        doc_dict['size_display'] = _format_file_size(doc_dict['file_size'])
        doc_dict['time_ago'] = _time_ago(doc_dict['uploaded_at'])
        doc_dict['analyzed_time_ago'] = _time_ago(doc_dict['ai_analysed_at'])
        docs_with_meta.append(doc_dict)

    return render_template('vault.html',
        documents=docs_with_meta,
        total_count=total_count,
        analysed_count=analysed_count,
        pending_count=pending_count,
        medicines=medicines,
        t=t,
    )


# ─── UPLOAD DOCUMENT ──────────────────────────────────────────────────────────
@vault_bp.route('/vault/upload', methods=['POST'])
@login_required
def upload():
    """Upload a medical document to the vault."""
    user_id = session['user_id']

    # Validate file presence
    if 'file' not in request.files:
        flash(t('vault_upload_error_empty'), 'danger')
        return redirect(url_for('vault.index'))

    file = request.files['file']
    if file.filename == '':
        flash(t('vault_upload_error_empty'), 'danger')
        return redirect(url_for('vault.index'))

    # Validate file extension
    if not _allowed_file(file.filename):
        flash(t('vault_upload_error_type'), 'danger')
        return redirect(url_for('vault.index'))

    # Read file content and validate size
    file_content = file.read()
    if len(file_content) > MAX_FILE_SIZE:
        flash(t('vault_upload_error_size'), 'danger')
        return redirect(url_for('vault.index'))

    # Get form data
    file_type = request.form.get('file_type', 'other').strip()
    notes = request.form.get('notes', '').strip() or None
    original_name = file.filename

    # Generate unique filename
    ext = original_name.rsplit('.', 1)[1].lower()
    safe_name = f"{uuid.uuid4().hex}_{original_name}"

    # Save file to disk
    upload_dir = _get_upload_dir(user_id)
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, 'wb') as f:
        f.write(file_content)

    # Insert record into database
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO health_vault (user_id, file_name, original_name, file_type, file_path, file_size)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, safe_name, original_name, file_type, file_path, len(file_content)))
    vault_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()

    # Trigger AI analysis synchronously
    try:
        _run_analysis(vault_id, user_id)
    except Exception as e:
        print(f"⚠️ Auto-analysis failed for vault {vault_id}: {e}")

    flash(t('vault_upload_success'), 'success')
    return redirect(url_for('vault.index'))


# ─── SERVE FILE ───────────────────────────────────────────────────────────────
@vault_bp.route('/vault/file/<int:vault_id>')
@login_required
def serve_file(vault_id):
    """Serve a vault document with security check."""
    user_id = session['user_id']
    conn = get_db_connection()

    doc = conn.execute(
        "SELECT * FROM health_vault WHERE id = ? AND user_id = ?",
        (vault_id, user_id)
    ).fetchone()
    conn.close()

    if not doc:
        flash(t('vault_file_error_not_found'), 'danger')
        return redirect(url_for('vault.index'))

    file_path = doc['file_path']
    if not os.path.exists(file_path):
        flash(t('vault_file_error_not_found'), 'danger')
        return redirect(url_for('vault.index'))

    ext = doc['original_name'].rsplit('.', 1)[1].lower() if '.' in doc['original_name'] else 'pdf'
    mime_type = MIME_TYPES.get(ext, 'application/octet-stream')

    return send_file(file_path, mimetype=mime_type, as_attachment=False)


# ─── RUN AI ANALYSIS ─────────────────────────────────────────────────────────
@vault_bp.route('/vault/analyse/<int:vault_id>', methods=['POST'])
@login_required
def analyse(vault_id):
    """Run or re-run AI analysis on a document."""
    user_id = session['user_id']
    result = _run_analysis(vault_id, user_id)

    if result is None:
        return jsonify({'success': False, 'error': 'Document not found'}), 404

    return jsonify({'success': True, **result})


@vault_bp.route('/vault/ai-status')
@login_required
def ai_status():
    """Debug endpoint: check if OpenAI is configured (does not expose full key)."""
    from utils.openai_helper import get_openai_api_key, get_openai_model, is_openai_configured

    key = get_openai_api_key()
    return jsonify({
        'openai_configured': is_openai_configured(),
        'key_hint': f'{key[:7]}…' if len(key) > 7 else ('set' if key else 'missing'),
        'model': get_openai_model(),
    })


def _run_analysis(vault_id, user_id):
    """
    Internal helper: extract text from document, run AI analysis, update DB.
    Returns analysis dict or None if document not found.
    """
    conn = get_db_connection()
    doc = conn.execute(
        "SELECT * FROM health_vault WHERE id = ? AND user_id = ?",
        (vault_id, user_id)
    ).fetchone()

    if not doc:
        conn.close()
        return None

    # Get user's active medicines
    medicines = conn.execute(
        "SELECT name FROM medicines WHERE user_id = ? AND is_active = 1",
        (user_id,)
    ).fetchall()
    medicines_list = [m['name'] for m in medicines]

    # Get language preference for analysis
    from utils.i18n import get_lang
    lang = get_lang()

    # Extract text from document
    extracted_text = _extract_text(doc['file_path'], doc['original_name'])

    # Run AI analysis
    analysis = analyse_document(extracted_text, medicines_list, lang=lang)

    # Update database with results
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute("""
        UPDATE health_vault
        SET ai_summary = ?, ai_conflicts = ?, ai_suggestions = ?, ai_analysed_at = ?
        WHERE id = ? AND user_id = ?
    """, (
        analysis.get('summary', ''),
        analysis.get('conflicts', ''),
        analysis.get('suggestions', ''),
        now,
        vault_id, user_id
    ))
    conn.commit()
    conn.close()

    return {
        'summary': analysis.get('summary', ''),
        'conflicts': analysis.get('conflicts', ''),
        'suggestions': analysis.get('suggestions', ''),
        'source': analysis.get('source', 'local'),
        'analysed_at': now,
    }


def _extract_text(file_path, original_name):
    """Extract text content from a PDF or image file."""
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''

    # PDF text extraction
    if ext == 'pdf':
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return '\n'.join(text_parts) if text_parts else 'No text could be extracted from this PDF.'
        except Exception as e:
            print(f"⚠️ PDF extraction error: {e}")
            return 'Unable to extract text from this PDF. The file may be encrypted or image-based.'

    # Image OCR
    if ext in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
        try:
            import pytesseract
            from PIL import Image
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip() if text.strip() else 'No text could be extracted from this image.'
        except ImportError:
            return (
                'Image text extraction requires Tesseract OCR. '
                'Install Tesseract on your system for image analysis support. '
                'Meanwhile, please upload a PDF for best results.'
            )
        except Exception as e:
            print(f"⚠️ OCR extraction error: {e}")
            return 'Unable to extract text from this image.'

    return 'Unsupported file type for text extraction.'


# ─── VAULT CHAT ───────────────────────────────────────────────────────────────
@vault_bp.route('/vault/chat', methods=['POST'])
@login_required
def chat():
    """Chat about a specific document or general health."""
    user_id = session['user_id']
    data = request.get_json()

    if not data or not data.get('message', '').strip():
        return jsonify({'response': 'Please enter a message.', 'source': 'local'})

    message = data['message'].strip()
    vault_id = data.get('vault_id')

    conn = get_db_connection()

    # Load document context if vault_id provided
    doc_summary = None
    doc_text = None
    if vault_id:
        doc = conn.execute(
            "SELECT ai_summary, file_path, original_name FROM health_vault WHERE id = ? AND user_id = ?",
            (vault_id, user_id)
        ).fetchone()
        if doc:
            doc_summary = doc['ai_summary']
            doc_text = _extract_text(doc['file_path'], doc['original_name'])

    # Load user's active medicines
    medicines = conn.execute(
        "SELECT name FROM medicines WHERE user_id = ? AND is_active = 1",
        (user_id,)
    ).fetchall()
    medicines_list = [m['name'] for m in medicines]

    # Load chat history for this vault document (last 10 messages)
    chat_history = []
    if vault_id:
        history = conn.execute("""
            SELECT role, message FROM vault_chat
            WHERE user_id = ? AND vault_id = ?
            ORDER BY id DESC LIMIT 10
        """, (user_id, vault_id)).fetchall()
        chat_history = list(reversed(history))

    # Get language preference
    from utils.i18n import get_lang
    lang = get_lang()

    # Save user message
    conn.execute("""
        INSERT INTO vault_chat (user_id, vault_id, role, message)
        VALUES (?, ?, 'user', ?)
    """, (user_id, vault_id, message))
    conn.commit()

    # Get AI response
    result = vault_chat_response(
        user_message=message,
        document_summary=doc_summary,
        document_text=doc_text,
        medicines_list=medicines_list,
        chat_history=chat_history,
        lang=lang
    )

    # Save assistant response
    conn.execute("""
        INSERT INTO vault_chat (user_id, vault_id, role, message)
        VALUES (?, ?, 'assistant', ?)
    """, (user_id, vault_id, result['response']))
    conn.commit()
    conn.close()

    return jsonify({
        'response': result['response'],
        'source': result['source']
    })


# ─── CHAT HISTORY ─────────────────────────────────────────────────────────────
@vault_bp.route('/vault/chat-history/<int:vault_id>')
@login_required
def chat_history(vault_id):
    """Get chat history for a specific vault document."""
    user_id = session['user_id']
    conn = get_db_connection()

    # Verify document ownership
    doc = conn.execute(
        "SELECT id FROM health_vault WHERE id = ? AND user_id = ?",
        (vault_id, user_id)
    ).fetchone()

    if not doc:
        conn.close()
        return jsonify([])

    messages = conn.execute("""
        SELECT role, message, created_at FROM vault_chat
        WHERE user_id = ? AND vault_id = ?
        ORDER BY id ASC
    """, (user_id, vault_id)).fetchall()
    conn.close()

    return jsonify([dict(m) for m in messages])


# ─── DELETE DOCUMENT ──────────────────────────────────────────────────────────
@vault_bp.route('/vault/delete/<int:vault_id>', methods=['POST'])
@login_required
def delete(vault_id):
    """Delete a vault document and its physical file."""
    user_id = session['user_id']
    conn = get_db_connection()

    doc = conn.execute(
        "SELECT * FROM health_vault WHERE id = ? AND user_id = ?",
        (vault_id, user_id)
    ).fetchone()

    if not doc:
        conn.close()
        flash(t('vault_file_error_not_found'), 'danger')
        return redirect(url_for('vault.index'))

    # Delete physical file
    file_path = doc['file_path']
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"⚠️ Could not delete file {file_path}: {e}")

    # Delete database record (cascade handles vault_chat)
    conn.execute("DELETE FROM health_vault WHERE id = ? AND user_id = ?", (vault_id, user_id))
    conn.commit()
    conn.close()

    flash(f"Document deleted.", 'success')
    return redirect(url_for('vault.index'))
