"""
app.py - MediTrack AI Main Application Entry Point
Run with: python app.py
"""

import os
from datetime import timedelta
from flask import Flask
from dotenv import load_dotenv
from utils.database import init_db
from utils.i18n import get_lang, t, t_freq, t_severity, t_status, SUPPORTED_LANGUAGES

load_dotenv()

# ─── Import all route blueprints ─────────────────────────────────────────────
from routes.auth        import auth_bp
from routes.dashboard   import dashboard_bp
from routes.medicines   import medicines_bp
from routes.reminders   import reminders_bp
from routes.side_effects import side_effects_bp
from routes.chatbot     import chatbot_bp
from routes.insights    import insights_bp
from routes.language    import language_bp
from routes.vault       import vault_bp


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    # ── Security configuration ────────────────────────────────────────────────
    app.secret_key = os.environ.get('SECRET_KEY', 'meditrack-dev-secret-change-in-production')
    app.permanent_session_lifetime = timedelta(days=7)

    # ── i18n: inject translation helpers into all templates ─────────────────
    @app.context_processor
    def inject_i18n():
        return dict(
            t=t,
            t_freq=t_freq,
            t_severity=t_severity,
            t_status=t_status,
            current_lang=get_lang(),
            languages=SUPPORTED_LANGUAGES,
        )

    # ── Register all blueprints ─────────────────────────────────────────────
    app.register_blueprint(language_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(medicines_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(side_effects_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(vault_bp)

    # ── Initialize database tables on first run ───────────────────────────────
    with app.app_context():
        init_db()

    return app


app = create_app()

if __name__ == '__main__':
    print("MediTrack AI running at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
