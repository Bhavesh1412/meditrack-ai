"""
dashboard.py - Dashboard routes
Shows summary stats, today's medicines, upcoming reminders
"""

from flask import Blueprint, render_template, session
from utils.database import get_db_connection
from utils.auth_helpers import login_required
from datetime import date, datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Main dashboard — aggregates data from multiple tables.
    Shows: today's medicines, reminders, side effect count, adherence stats.
    """
    user_id   = session['user_id']
    today_str = date.today().isoformat()   # e.g., "2024-01-15"
    conn      = get_db_connection()

    # ── Today's active medicines ──────────────────────────────────────────────
    today_medicines = conn.execute("""
        SELECT * FROM medicines
        WHERE user_id = ?
          AND is_active = 1
          AND start_date <= ?
          AND (end_date IS NULL OR end_date >= ?)
        ORDER BY time
    """, (user_id, today_str, today_str)).fetchall()

    # ── Upcoming reminders (next 3 active) ───────────────────────────────────
    current_time = datetime.now().strftime('%H:%M')
    reminders = conn.execute("""
        SELECT r.*, m.name AS medicine_name, m.dosage
        FROM reminders r
        JOIN medicines m ON r.medicine_id = m.id
        WHERE r.user_id = ? AND r.is_active = 1
          AND r.reminder_time >= ?
        ORDER BY r.reminder_time
        LIMIT 5
    """, (user_id, current_time)).fetchall()

    # ── Recent side effects (last 5) ─────────────────────────────────────────
    side_effects = conn.execute("""
        SELECT se.*, m.name AS medicine_name
        FROM side_effects se
        LEFT JOIN medicines m ON se.medicine_id = m.id
        WHERE se.user_id = ?
        ORDER BY se.reported_at DESC
        LIMIT 5
    """, (user_id,)).fetchall()

    # ── Adherence stats (last 7 days) ─────────────────────────────────────────
    history = conn.execute("""
        SELECT status, COUNT(*) as count
        FROM medication_history
        WHERE user_id = ?
          AND taken_at >= date('now', '-7 days')
        GROUP BY status
    """, (user_id,)).fetchall()

    taken = sum(r['count'] for r in history if r['status'] == 'taken')
    total = sum(r['count'] for r in history)
    adherence = round((taken / total * 100), 1) if total > 0 else 0

    # ── Total medicine count ──────────────────────────────────────────────────
    total_medicines = conn.execute(
        "SELECT COUNT(*) as cnt FROM medicines WHERE user_id = ? AND is_active = 1",
        (user_id,)
    ).fetchone()['cnt']

    conn.close()

    return render_template('dashboard.html',
        today_medicines  = today_medicines,
        reminders        = reminders,
        side_effects     = side_effects,
        adherence        = adherence,
        total_medicines  = total_medicines,
        taken_count      = taken,
        missed_count     = total - taken,
        today            = today_str,
        user_name        = session.get('user_name', 'User')
    )
