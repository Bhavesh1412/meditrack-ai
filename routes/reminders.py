"""
reminders.py - Reminder and medication tracking routes
Handles marking medicines as taken/missed and showing history
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import get_db_connection
from utils.auth_helpers import login_required
from datetime import date, datetime

reminders_bp = Blueprint('reminders', __name__)


@reminders_bp.route('/reminders')
@login_required
def index():
    """Show all reminders and today's medication schedule."""
    user_id   = session['user_id']
    today_str = date.today().isoformat()
    conn      = get_db_connection()

    # All active reminders with medicine details
    reminders = conn.execute("""
        SELECT r.*, m.name AS medicine_name, m.dosage, m.frequency, m.notes
        FROM reminders r
        JOIN medicines m ON r.medicine_id = m.id
        WHERE r.user_id = ? AND r.is_active = 1
          AND m.is_active = 1
        ORDER BY r.reminder_time
    """, (user_id,)).fetchall()

    # Today's medication history
    today_history = conn.execute("""
        SELECT mh.*, m.name AS medicine_name, m.dosage
        FROM medication_history mh
        JOIN medicines m ON mh.medicine_id = m.id
        WHERE mh.user_id = ?
          AND DATE(mh.taken_at) = ?
        ORDER BY mh.taken_at DESC
    """, (user_id, today_str)).fetchall()

    # Adherence data for last 30 days
    adherence_data = conn.execute("""
        SELECT DATE(taken_at) as day,
               SUM(CASE WHEN status='taken' THEN 1 ELSE 0 END) as taken,
               SUM(CASE WHEN status='missed' THEN 1 ELSE 0 END) as missed
        FROM medication_history
        WHERE user_id = ? AND taken_at >= date('now', '-30 days')
        GROUP BY DATE(taken_at)
        ORDER BY day
    """, (user_id,)).fetchall()

    total_taken  = sum(r['taken']  for r in adherence_data)
    total_missed = sum(r['missed'] for r in adherence_data)
    total_all    = total_taken + total_missed
    adherence_pct = round((total_taken / total_all * 100), 1) if total_all > 0 else 0

    conn.close()

    return render_template('reminders.html',
        reminders      = reminders,
        today_history  = today_history,
        adherence_pct  = adherence_pct,
        total_taken    = total_taken,
        total_missed   = total_missed,
        today          = today_str
    )


@reminders_bp.route('/reminders/mark', methods=['POST'])
@login_required
def mark():
    """
    Mark a medicine as 'taken' or 'missed'.
    Expects JSON: { medicine_id, status, scheduled_time }
    """
    user_id = session['user_id']
    data    = request.get_json()

    medicine_id    = data.get('medicine_id')
    status         = data.get('status')          # 'taken' or 'missed'
    scheduled_time = data.get('scheduled_time', '')
    notes          = data.get('notes', '')

    # Validate status
    if status not in ('taken', 'missed', 'skipped'):
        return jsonify({'error': 'Invalid status'}), 400

    conn = get_db_connection()

    # Verify medicine belongs to user
    med = conn.execute(
        "SELECT id FROM medicines WHERE id = ? AND user_id = ?",
        (medicine_id, user_id)
    ).fetchone()

    if not med:
        conn.close()
        return jsonify({'error': 'Medicine not found'}), 404

    conn.execute("""
        INSERT INTO medication_history (user_id, medicine_id, status, scheduled_time, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, medicine_id, status, scheduled_time, notes))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'Marked as {status}!'})


@reminders_bp.route('/reminders/history')
@login_required
def history():
    """Show full medication history with pagination."""
    user_id = session['user_id']
    page    = int(request.args.get('page', 1))
    per_page = 20
    offset  = (page - 1) * per_page

    conn = get_db_connection()

    records = conn.execute("""
        SELECT mh.*, m.name AS medicine_name
        FROM medication_history mh
        JOIN medicines m ON mh.medicine_id = m.id
        WHERE mh.user_id = ?
        ORDER BY mh.taken_at DESC
        LIMIT ? OFFSET ?
    """, (user_id, per_page, offset)).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) as cnt FROM medication_history WHERE user_id = ?",
        (user_id,)
    ).fetchone()['cnt']
    conn.close()

    return render_template('history.html',
        records    = records,
        page       = page,
        total_pages = (total + per_page - 1) // per_page
    )
