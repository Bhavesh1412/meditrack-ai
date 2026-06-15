"""
insights.py - Insights & Analytics routes
Provides chart data and statistics for the insights dashboard
"""

from flask import Blueprint, render_template, jsonify, session
from utils.database import get_db_connection
from utils.auth_helpers import login_required
from datetime import date, timedelta

insights_bp = Blueprint('insights', __name__)


@insights_bp.route('/insights')
@login_required
def index():
    """Main insights page."""
    user_id = session['user_id']
    conn    = get_db_connection()

    # ── Summary stats ─────────────────────────────────────────────────────────
    total_medicines = conn.execute(
        "SELECT COUNT(*) as c FROM medicines WHERE user_id=? AND is_active=1",
        (user_id,)
    ).fetchone()['c']

    total_taken = conn.execute(
        "SELECT COUNT(*) as c FROM medication_history WHERE user_id=? AND status='taken'",
        (user_id,)
    ).fetchone()['c']

    total_missed = conn.execute(
        "SELECT COUNT(*) as c FROM medication_history WHERE user_id=? AND status='missed'",
        (user_id,)
    ).fetchone()['c']

    total_side_effects = conn.execute(
        "SELECT COUNT(*) as c FROM side_effects WHERE user_id=?",
        (user_id,)
    ).fetchone()['c']

    total_doses = total_taken + total_missed
    adherence   = round((total_taken / total_doses * 100), 1) if total_doses > 0 else 0

    conn.close()

    return render_template('insights.html',
        total_medicines    = total_medicines,
        total_taken        = total_taken,
        total_missed       = total_missed,
        total_side_effects = total_side_effects,
        adherence          = adherence
    )


@insights_bp.route('/insights/api/adherence')
@login_required
def api_adherence():
    """
    Returns last 14 days of adherence data for Chart.js line chart.
    Format: { labels: [...], taken: [...], missed: [...] }
    """
    user_id = session['user_id']
    conn    = get_db_connection()

    # Generate the last 14 days as labels
    days   = [(date.today() - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    taken_map  = {}
    missed_map = {}

    rows = conn.execute("""
        SELECT DATE(taken_at) as day,
               SUM(CASE WHEN status='taken' THEN 1 ELSE 0 END) as taken,
               SUM(CASE WHEN status='missed' THEN 1 ELSE 0 END) as missed
        FROM medication_history
        WHERE user_id = ? AND taken_at >= date('now', '-14 days')
        GROUP BY DATE(taken_at)
    """, (user_id,)).fetchall()
    conn.close()

    for row in rows:
        taken_map[row['day']]  = row['taken']
        missed_map[row['day']] = row['missed']

    return jsonify({
        'labels': [d[5:] for d in days],   # Show MM-DD only
        'taken':  [taken_map.get(d, 0)  for d in days],
        'missed': [missed_map.get(d, 0) for d in days]
    })


@insights_bp.route('/insights/api/side-effects')
@login_required
def api_side_effects():
    """
    Returns side effect severity breakdown for a doughnut chart.
    """
    user_id = session['user_id']
    conn    = get_db_connection()

    rows = conn.execute("""
        SELECT severity, COUNT(*) as count
        FROM side_effects WHERE user_id = ?
        GROUP BY severity
    """, (user_id,)).fetchall()
    conn.close()

    data = {r['severity']: r['count'] for r in rows}
    return jsonify({
        'labels': ['Mild', 'Moderate', 'Severe'],
        'values': [
            data.get('mild', 0),
            data.get('moderate', 0),
            data.get('severe', 0)
        ]
    })


@insights_bp.route('/insights/api/medicines')
@login_required
def api_medicines():
    """
    Returns per-medicine adherence for a horizontal bar chart.
    """
    user_id = session['user_id']
    conn    = get_db_connection()

    rows = conn.execute("""
        SELECT m.name,
               SUM(CASE WHEN mh.status='taken'  THEN 1 ELSE 0 END) AS taken,
               SUM(CASE WHEN mh.status='missed' THEN 1 ELSE 0 END) AS missed
        FROM medication_history mh
        JOIN medicines m ON mh.medicine_id = m.id
        WHERE mh.user_id = ?
        GROUP BY m.id
        ORDER BY taken DESC
        LIMIT 8
    """, (user_id,)).fetchall()
    conn.close()

    return jsonify({
        'labels': [r['name'] for r in rows],
        'taken':  [r['taken']  for r in rows],
        'missed': [r['missed'] for r in rows]
    })
