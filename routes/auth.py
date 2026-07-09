"""
auth.py - Authentication routes
Handles: /register, /login, /logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.database import get_db_connection
from utils.i18n import t
from utils.auth_helpers import hash_password, check_password
import re

# Create a Blueprint — modular route grouping
auth_bp = Blueprint('auth', __name__)


# ─── REGISTER ────────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET:  Show registration form
    POST: Validate input, create user account
    """
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # ── Input validation ──────────────────────────────────────────────────
        errors = []

        if not name or len(name) < 2:
            errors.append(t('err_name_short'))

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
            errors.append(t('err_email_invalid'))

        if len(password) < 8:
            errors.append(t('err_password_short'))

        if password != confirm:
            errors.append(t('err_password_mismatch'))

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('register.html', name=name, email=email)

        # ── Check if email already exists ─────────────────────────────────────
        conn = get_db_connection()
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()

        if existing:
            conn.close()
            flash(t('err_email_exists'), 'danger')
            return render_template('register.html', email=email)

        # ── Create new user ───────────────────────────────────────────────────
        hashed_pw = hash_password(password)
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_pw)
        )
        conn.commit()
        conn.close()

        flash(t('msg_account_created'), 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ─── LOGIN ───────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    """
    GET:  Show login form
    POST: Validate credentials, start session
    """
    # Already logged in → go to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash(t('err_fill_all'), 'danger')
            return render_template('login.html')

        # ── Look up user ──────────────────────────────────────────────────────
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if not user or not check_password(password, user['password']):
            flash(t('err_invalid_login'), 'danger')
            return render_template('login.html', email=email)

        # ── Start session ─────────────────────────────────────────────────────
        session.permanent = True
        session['user_id']   = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']

        flash(t('msg_welcome_back', name=user['name']), 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('login.html')


# ─── LOGOUT ──────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash(t('msg_logged_out'), 'info')
    return redirect(url_for('auth.login'))
