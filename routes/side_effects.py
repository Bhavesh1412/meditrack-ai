"""
side_effects.py - Side Effect Tracker routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.database import get_db_connection
from utils.auth_helpers import login_required

side_effects_bp = Blueprint('side_effects', __name__)


@side_effects_bp.route('/side-effects')
@login_required
def index():
    user_id = session['user_id']
    conn    = get_db_connection()

    effects = conn.execute("""
        SELECT se.*, m.name AS medicine_name
        FROM side_effects se
        LEFT JOIN medicines m ON se.medicine_id = m.id
        WHERE se.user_id = ?
        ORDER BY se.reported_at DESC
    """, (user_id,)).fetchall()

    # Get user's medicines for the dropdown
    medicines = conn.execute(
        "SELECT id, name FROM medicines WHERE user_id = ? AND is_active = 1",
        (user_id,)
    ).fetchall()

    # Stats: group by severity
    stats = conn.execute("""
        SELECT severity, COUNT(*) as count
        FROM side_effects WHERE user_id = ?
        GROUP BY severity
    """, (user_id,)).fetchall()

    conn.close()

    severity_map = {r['severity']: r['count'] for r in stats}
    return render_template('sideeffects.html',
        effects    = effects,
        medicines  = medicines,
        mild_count = severity_map.get('mild', 0),
        mod_count  = severity_map.get('moderate', 0),
        sev_count  = severity_map.get('severe', 0)
    )


@side_effects_bp.route('/side-effects/add', methods=['POST'])
@login_required
def add():
    user_id     = session['user_id']
    symptom     = request.form.get('symptom', '').strip()
    severity    = request.form.get('severity', '').strip()
    medicine_id = request.form.get('medicine_id') or None
    description = request.form.get('description', '').strip() or None
    reported_at = request.form.get('reported_at', '').strip() or None

    if not symptom or severity not in ('mild', 'moderate', 'severe'):
        flash("Please fill in all required fields.", 'danger')
        return redirect(url_for('side_effects.index'))

    conn = get_db_connection()
    if reported_at:
        conn.execute("""
            INSERT INTO side_effects (user_id, medicine_id, symptom, severity, description, reported_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, medicine_id, symptom, severity, description, reported_at))
    else:
        conn.execute("""
            INSERT INTO side_effects (user_id, medicine_id, symptom, severity, description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, medicine_id, symptom, severity, description))

    conn.commit()
    conn.close()

    flash(f"✅ Side effect '{symptom}' reported.", 'success')
    return redirect(url_for('side_effects.index'))


@side_effects_bp.route('/side-effects/delete/<int:se_id>', methods=['POST'])
@login_required
def delete(se_id):
    user_id = session['user_id']
    conn    = get_db_connection()
    conn.execute(
        "DELETE FROM side_effects WHERE id = ? AND user_id = ?",
        (se_id, user_id)
    )
    conn.commit()
    conn.close()
    flash("Side effect record deleted.", 'info')
    return redirect(url_for('side_effects.index'))
