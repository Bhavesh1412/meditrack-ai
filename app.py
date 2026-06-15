"""
app.py - MediTrack AI Main Application Entry Point
Run with: python app.py
"""

import os
from datetime import timedelta
from flask import Flask
from utils.database import init_db

# ─── Import all route blueprints ─────────────────────────────────────────────
from routes.auth        import auth_bp
from routes.dashboard   import dashboard_bp
from routes.medicines   import medicines_bp
from routes.reminders   import reminders_bp
from routes.side_effects import side_effects_bp
from routes.chatbot     import chatbot_bp
from routes.insights    import insights_bp


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    # ── Security configuration ────────────────────────────────────────────────
    app.secret_key = os.environ.get('SECRET_KEY', 'meditrack-dev-secret-change-in-production')
    app.permanent_session_lifetime = timedelta(days=7)   # Remember login for 7 days

    # ── Register all blueprints (modular routing) ─────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(medicines_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(side_effects_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(insights_bp)

    # ── Initialize database tables on first run ───────────────────────────────
    with app.app_context():
        init_db()

    return app


app = create_app()

if __name__ == '__main__':
    print("🚀 MediTrack AI running at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)