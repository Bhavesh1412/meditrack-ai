"""
auth_helpers.py - Authentication utility functions
Handles password hashing, session management, and login decorators
"""

import bcrypt
from functools import wraps
from flask import session, redirect, url_for, flash


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    bcrypt automatically salts the hash — never store plain passwords!

    Args:
        plain_password: The password string entered by the user

    Returns:
        A bcrypt-hashed password string (safe to store in DB)
    """
    password_bytes = plain_password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')  # Store as string in SQLite


def check_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its bcrypt hash.

    Args:
        plain_password: Password entered during login
        hashed_password: Stored bcrypt hash from the database

    Returns:
        True if they match, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Usage: @login_required above any route function.

    If user is not logged in, redirects to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id() -> int | None:
    """Return the current logged-in user's ID from session."""
    return session.get('user_id')
