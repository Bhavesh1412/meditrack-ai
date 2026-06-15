# 💊 MediTrack AI — Medicine Reminder & Side Effect Tracker

> **UN SDG 3: Good Health and Well-Being**
> A full-stack AI-powered web application for managing medications, tracking side effects, and consulting an AI health assistant.

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
| 📱 Responsive Design | Mobile-friendly sidebar layout |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask 3.0
- **Database:** SQLite (zero setup required)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Charts:** Chart.js 4
- **AI:** OpenAI GPT-3.5-turbo (+ local fallback)
- **Security:** bcrypt password hashing, session management

---

## 📁 Project Structure

```
meditrack/
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
│   └── insights.py         # Analytics & chart data APIs
│
├── utils/                  # Utility modules
│   ├── database.py         # DB connection & schema init
│   ├── auth_helpers.py     # Password hashing, login decorator
│   └── chatbot.py          # OpenAI + fallback AI logic
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
│   └── history.html
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
6. Chat with **MediBot** on the AI Assistant page
7. View your stats on the **Insights** page

---

## 🗄️ Database Schema

```sql
users               -- id, name, email, password (bcrypt), created_at
medicines           -- id, user_id, name, dosage, frequency, time, start/end_date, notes, is_active
reminders           -- id, user_id, medicine_id, reminder_time, is_active
medication_history  -- id, user_id, medicine_id, status (taken/missed/skipped), taken_at
side_effects        -- id, user_id, medicine_id, symptom, severity, description, reported_at
chat_history        -- id, user_id, role (user/assistant), message, created_at
```

---

## 📸 Screenshots

> Add screenshots to a `screenshots/` folder and reference here:

| Page | Preview |
|---|---|
| Dashboard | `screenshots/dashboard.png` |
| Medicines | `screenshots/medicines.png` |
| AI Chat | `screenshots/chatbot.png` |
| Insights | `screenshots/insights.png` |

---

## 🔒 Security Features

- ✅ Passwords hashed with **bcrypt** (never stored plain)
- ✅ Flask **session-based** authentication
- ✅ All routes protected with `@login_required`
- ✅ All DB queries use **parameterized statements** (SQL injection safe)
- ✅ User data isolation — users only see their own data
- ✅ CSRF protection via form POST methods

---

## 📤 GitHub Submission

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: MediTrack AI complete project"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/meditrack-ai.git
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
```

---

## 🎓 Academic Information

- **Project:** MediTrack AI – Medicine Reminder and Side Effect Tracker
- **SDG Alignment:** UN SDG 3 – Good Health and Well-Being
- **Tech Stack:** Python, Flask, SQLite, HTML/CSS/JS, Chart.js, OpenAI API
- **Architecture:** MVC-style, Blueprint-based modular Flask app

---

## ⚠️ Disclaimer

MediTrack AI is an academic project. The AI chatbot provides **general health information only** and does **not** replace professional medical advice. Always consult a qualified healthcare provider for medical decisions.

---

*Built with ❤️ for university project submission*
