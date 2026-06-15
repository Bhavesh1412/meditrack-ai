"""
medicines.py - Medicine CRUD routes
Handles: list, add, edit, delete medicines
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import get_db_connection
from utils.auth_helpers import login_required
from datetime import date

medicines_bp = Blueprint('medicines', __name__)


@medicines_bp.route('/medicines')
@login_required
def index():
    """Show all medicines for the current user."""
    user_id = session['user_id']
    conn = get_db_connection()
    medicines = conn.execute("""
        SELECT * FROM medicines
        WHERE user_id = ?
        ORDER BY is_active DESC, name
    """, (user_id,)).fetchall()
    conn.close()
    return render_template('medicines.html', medicines=medicines)


@medicines_bp.route('/medicines/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new medicine."""
    if request.method == 'POST':
        user_id    = session['user_id']
        name       = request.form.get('name', '').strip()
        dosage     = request.form.get('dosage', '').strip()
        frequency  = request.form.get('frequency', '').strip()
        time       = request.form.get('time', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date   = request.form.get('end_date', '').strip() or None
        notes      = request.form.get('notes', '').strip() or None

        # Validation
        if not all([name, dosage, frequency, time, start_date]):
            flash("Please fill in all required fields.", 'danger')
            return render_template('medicines.html', show_modal=True)

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO medicines (user_id, name, dosage, frequency, time, start_date, end_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, dosage, frequency, time, start_date, end_date, notes))

        # Auto-create reminders for each time slot
        med_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        for t in time.split(','):
            t = t.strip()
            if t:
                conn.execute("""
                    INSERT INTO reminders (user_id, medicine_id, reminder_time)
                    VALUES (?, ?, ?)
                """, (user_id, med_id, t))

        conn.commit()
        conn.close()

        flash(f"✅ '{name}' has been added to your medicines.", 'success')
        return redirect(url_for('medicines.index'))

    return redirect(url_for('medicines.index'))


@medicines_bp.route('/medicines/edit/<int:med_id>', methods=['POST'])
@login_required
def edit(med_id):
    """Update an existing medicine."""
    user_id = session['user_id']
    conn = get_db_connection()

    # Security: ensure medicine belongs to this user
    med = conn.execute(
        "SELECT * FROM medicines WHERE id = ? AND user_id = ?", (med_id, user_id)
    ).fetchone()

    if not med:
        conn.close()
        flash("Medicine not found.", 'danger')
        return redirect(url_for('medicines.index'))

    name       = request.form.get('name', '').strip()
    dosage     = request.form.get('dosage', '').strip()
    frequency  = request.form.get('frequency', '').strip()
    time       = request.form.get('time', '').strip()
    start_date = request.form.get('start_date', '').strip()
    end_date   = request.form.get('end_date', '').strip() or None
    notes      = request.form.get('notes', '').strip() or None

    conn.execute("""
        UPDATE medicines
        SET name=?, dosage=?, frequency=?, time=?, start_date=?, end_date=?, notes=?
        WHERE id=? AND user_id=?
    """, (name, dosage, frequency, time, start_date, end_date, notes, med_id, user_id))
    conn.commit()
    conn.close()

    flash(f"✅ '{name}' updated successfully.", 'success')
    return redirect(url_for('medicines.index'))


@medicines_bp.route('/medicines/delete/<int:med_id>', methods=['POST'])
@login_required
def delete(med_id):
    """Soft-delete a medicine (set is_active = 0)."""
    user_id = session['user_id']
    conn = get_db_connection()

    med = conn.execute(
        "SELECT name FROM medicines WHERE id = ? AND user_id = ?", (med_id, user_id)
    ).fetchone()

    if not med:
        conn.close()
        flash("Medicine not found.", 'danger')
        return redirect(url_for('medicines.index'))

    # Soft delete — keeps history intact
    conn.execute(
        "UPDATE medicines SET is_active = 0 WHERE id = ? AND user_id = ?",
        (med_id, user_id)
    )
    conn.commit()
    conn.close()

    flash(f"🗑️ '{med['name']}' has been removed.", 'info')
    return redirect(url_for('medicines.index'))


@medicines_bp.route('/medicines/get/<int:med_id>')
@login_required
def get_medicine(med_id):
    """API endpoint to get medicine data for edit modal (JSON)."""
    user_id = session['user_id']
    conn = get_db_connection()
    med = conn.execute(
        "SELECT * FROM medicines WHERE id = ? AND user_id = ?", (med_id, user_id)
    ).fetchone()
    conn.close()

    if not med:
        return jsonify({'error': 'Not found'}), 404

    return jsonify(dict(med))
