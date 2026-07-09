"""
language.py - Language toggle routes (English / Hindi)
"""

from flask import Blueprint, redirect, request, session, flash, url_for
from utils.i18n import SUPPORTED_LANGUAGES, TRANSLATIONS

language_bp = Blueprint('language', __name__)


@language_bp.route('/set-language/<lang>')
def set_language(lang):
    """Set UI language and redirect back to the previous page."""
    if lang in SUPPORTED_LANGUAGES:
        session.permanent = True
        session['lang'] = lang
        flash(TRANSLATIONS[lang]['lang_switched'], 'info')

    referrer = request.referrer
    if referrer and not referrer.endswith('/set-language/en') and not referrer.endswith('/set-language/hi'):
        return redirect(referrer)

    return redirect(url_for('auth.login'))
