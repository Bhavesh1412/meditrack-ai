# 💊 Nabz AI (नब्ज़ AI) — AI-Powered Health Management Platform

> **UN SDG 3: Good Health and Well-Being**
> A full-stack AI-powered web application for managing medications, tracking side effects, uploading medical documents, and consulting an AI health assistant.

---

## 🌟 Features

| Feature | Description |
|---|---|
| 🔐 Authentication | Secure register/login/logout with bcrypt password hashing |
| 📊 Dashboard | Overview of today's medicines, reminders, adherence stats |
| 💊 Medicine Management | Add, edit, delete medicines with full details |
| ⏰ Reminder System | Auto-generated reminders, mark as taken/missed |
| ⚠️ Side Effect Tracker | Report and monitor medication reactions |
| 🤖 AI Health Assistant | OpenAI GPT + local keyword fallback chatbot |
| 📈 Insights Dashboard | Charts: adherence trends, side effects, per-medicine stats |
| 📁 Health Vault | Upload, manage, and get AI analysis on medical documents |
| 📱 Responsive Design | Mobile-friendly sidebar layout |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask 3.0
- **Database:** SQLite (zero setup required)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Charts:** Chart.js 4
- **AI:** OpenAI GPT-3.5-turbo (+ local fallback)
- **Document Processing:** PyPDF2, pytesseract OCR
- **Security:** bcrypt password hashing, session management

---

## 📁 Project Structure

```
nabz-ai/
├── app.py                  # Flask app factory & entry point
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database 
│
├── routes/                 # Blueprint route handlers
│   ├── auth.py             # Login, register, logout
│   ├── dashboard.py        # Main dashboard
│   ├── medicines.py        # CRUD for medicines
│   ├── reminders.py        # Reminder tracking
│   ├── side_effects.py     # Side effect tracker
│   ├── chatbot.py          # AI chatbot routes
│   ├── insights.py         # Analytics & chart data APIs
│   └── vault.py            # Health Vault document management
│
├── utils/                  # Utility modules
│   ├── database.py         # DB connection & schema init
│   ├── auth_helpers.py     # Password hashing, login decorator
│   ├── chatbot.py          # OpenAI + fallback AI logic
│   ├── vault_ai.py         # AI document analysis
│   └── i18n.py             # English/Hindi translations
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Sidebar layout base
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── medicines.html
│   ├── reminders.html
│   ├── sideeffects.html
│   ├── chatbot.html
│   ├── insights.html
│   ├── history.html
│   ├── vault.html
│   └── partials/
│       └── lang_toggle.html
│
└── static/
    └── css/
        └── style.css       # Complete custom stylesheet
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Bhavesh1412/meditrack-ai.git
cd meditrack-ai
```

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment (optional — for OpenAI)

Create a `.env` file in the project root:

```env
SECRET_KEY=your-random-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here
```

> **No OpenAI key?** No problem! The app automatically falls back to a local keyword-based health chatbot.

### 5. Run the application

```bash
python app.py
```

Visit → **http://localhost:5000**

---

## 🚀 First-Time Usage

1. Open `http://localhost:5000`
2. Click **"Create one free"** to register an account
3. Log in with your credentials
4. Add your first medicine via the **Medicines** page
5. Check **Reminders** to mark doses as taken/missed
6. Chat with **NabzBot** on the AI Assistant page
7. Upload documents to your **Health Vault** for AI analysis
8. View your stats on the **Insights** page

---

## 🗄️ Database Schema

```sql
users               -- id, name, email, password (bcrypt), created_at
medicines           -- id, user_id, name, dosage, frequency, time, start/end_date, notes, is_active
reminders           -- id, user_id, medicine_id, reminder_time, is_active
medication_history  -- id, user_id, medicine_id, status (taken/missed/skipped), taken_at
side_effects        -- id, user_id, medicine_id, symptom, severity, description, reported_at
chat_history        -- id, user_id, role (user/assistant), message, created_at
health_vault        -- id, user_id, file_name, original_name, file_type, file_path, ai_summary, ai_conflicts, ai_suggestions
vault_chat          -- id, user_id, vault_id, role (user/assistant), message, created_at
```

---

## 📸 Screenshots

> Add screenshots to a `screenshots/` folder and reference here:

| Page | Preview |
|---|---|
| Dashboard | `screenshots/dashboard.png` |
| Medicines | `screenshots/medicines.png` |
| AI Chat | `screenshots/chatbot.png` |
| Health Vault | `screenshots/vault.png` |
| Insights | `screenshots/insights.png` |

---

## 🔒 Security Features

- ✅ Passwords hashed with **bcrypt** (never stored plain)
- ✅ Flask **session-based** authentication
- ✅ All routes protected with `@login_required`
- ✅ All DB queries use **parameterized statements** (SQL injection safe)
- ✅ User data isolation — users only see their own data
- ✅ CSRF protection via form POST methods
- ✅ Vault files served through protected routes (no direct path exposure)

---

## 📤 GitHub Submission

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: Nabz AI complete project"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/nabz-ai.git
git branch -M main
git push -u origin main
```

Add a `.gitignore`:
```
venv/
database.db
.env
__pycache__/
*.pyc
static/uploads/
```

---

## 🎓 Academic Information

- **Project:** Nabz AI (नब्ज़ AI) – AI-Powered Health Management Platform
- **SDG Alignment:** UN SDG 3 – Good Health and Well-Being
- **Tech Stack:** Python, Flask, SQLite, HTML/CSS/JS, Chart.js, OpenAI API
- **Architecture:** MVC-style, Blueprint-based modular Flask app

---

## ⚠️ Disclaimer

Nabz AI is an academic project. The AI chatbot provides **general health information only** and does **not** replace professional medical advice. Always consult a qualified healthcare provider for medical decisions.

---

*Built with ❤️ for university project submission*
