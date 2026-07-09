"""
i18n.py - English / Hindi translations for MediTrack AI
"""

from flask import session, has_request_context

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
}

DEFAULT_LANG = 'en'


def get_lang():
    if not has_request_context():
        return DEFAULT_LANG
    lang = session.get('lang', DEFAULT_LANG)
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANG


def t(key, **kwargs):
    lang = get_lang()
    text = TRANSLATIONS.get(lang, {}).get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_LANG].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def t_status(status):
    key = f'status_{status}'
    return t(key) if key in TRANSLATIONS['en'] else (status.title() if status else '')


def t_severity(severity):
    key = f'severity_{severity}'
    return t(key) if key in TRANSLATIONS['en'] else severity.title()


def t_freq(freq):
    mapping = {
        'Once daily': 'freq_once_daily',
        'Twice daily': 'freq_twice_daily',
        'Three times daily': 'freq_thrice_daily',
        'Four times daily': 'freq_four_daily',
        'As needed': 'freq_as_needed',
        'Weekly': 'freq_weekly',
    }
    key = mapping.get(freq)
    return t(key) if key else freq


# ─── TRANSLATION STRINGS ─────────────────────────────────────────────────────

TRANSLATIONS = {
    'en': {
        # Nav
        'nav_main': 'Main',
        'nav_track': 'Track',
        'nav_ai': 'AI',
        'nav_dashboard': 'Dashboard',
        'nav_medicines': 'Medicines',
        'nav_reminders': 'Reminders',
        'nav_side_effects': 'Side Effects',
        'nav_insights': 'Insights',
        'nav_ai_assistant': 'AI Assistant',
        'nav_health_management': 'Health Management',
        'nav_logout': 'Logout',
        'lang_switched': 'Language changed to English.',

        # Common
        'active': 'Active',
        'inactive': 'Inactive',
        'cancel': 'Cancel',
        'save_changes': 'Save Changes',
        'add': 'Add',
        'all': 'All',
        'edit': 'Edit',
        'remove': 'Remove',
        'general': 'General',
        'records': 'records',
        'medicine': 'Medicine',
        'status': 'Status',
        'time': 'Time',
        'notes': 'Notes',
        'description': 'Description',
        'date': 'Date',
        'action': 'Action',
        'symptom': 'Symptom',
        'severity': 'Severity',
        'scheduled': 'Scheduled',
        'logged_at': 'Logged At',
        'full_report': 'Full Report',
        'send': 'Send',
        'you': 'You',
        'medibot': 'MediBot',
        'medibot_ai': 'MediBot (AI)',
        'ai_assistant': 'AI Assistant',

        # Status & severity
        'status_taken': 'Taken',
        'status_missed': 'Missed',
        'status_skipped': 'Skipped',
        'severity_mild': 'Mild',
        'severity_moderate': 'Moderate',
        'severity_severe': 'Severe',

        # Frequency
        'freq_once_daily': 'Once daily',
        'freq_twice_daily': 'Twice daily',
        'freq_thrice_daily': 'Three times daily',
        'freq_four_daily': 'Four times daily',
        'freq_as_needed': 'As needed',
        'freq_weekly': 'Weekly',
        'select_frequency': 'Select frequency',

        # Auth
        'auth_welcome_back': 'Welcome back',
        'auth_sign_in_sub': 'Sign in to your MediTrack account',
        'auth_create_account': 'Create Account',
        'auth_create_sub': 'Start managing your health today',
        'auth_email': 'Email Address',
        'auth_password': 'Password',
        'auth_full_name': 'Full Name',
        'auth_confirm_password': 'Confirm Password',
        'auth_sign_in': 'Sign In',
        'auth_no_account': "Don't have an account?",
        'auth_create_free': 'Create one free',
        'auth_has_account': 'Already have an account?',
        'auth_log_in': 'Log in',
        'auth_brand_headline': 'Your health, organized beautifully',
        'auth_brand_headline_hi_span': 'organized beautifully',
        'auth_brand_desc': 'Track medications, monitor side effects, and get AI-powered health guidance — all in one elegant dashboard.',
        'auth_feature_reminders': 'Smart medication reminders',
        'auth_feature_insights': 'Adherence insights & analytics',
        'auth_feature_ai': 'AI health assistant on demand',
        'auth_register_headline': 'Start your health journey today',
        'auth_register_span': 'health journey',
        'auth_register_desc': 'Join thousands managing their wellness with intelligent reminders, side effect tracking, and personalized AI guidance.',
        'auth_feature_secure': 'Secure, encrypted accounts',
        'auth_feature_never_miss': 'Never miss a dose again',
        'auth_feature_track': 'Track reactions in real time',
        'auth_pw_match': 'Passwords match',
        'auth_pw_no_match': 'Passwords do not match',
        'auth_smart_companion': 'Your smart health companion',

        # Auth errors & flashes
        'err_name_short': 'Name must be at least 2 characters.',
        'err_email_invalid': 'Please enter a valid email address.',
        'err_password_short': 'Password must be at least 8 characters.',
        'err_password_mismatch': 'Passwords do not match.',
        'err_email_exists': 'An account with this email already exists.',
        'msg_account_created': 'Account created successfully! Please log in.',
        'err_fill_all': 'Please fill in all fields.',
        'err_invalid_login': 'Invalid email or password.',
        'msg_welcome_back': 'Welcome back, {name}! 👋',
        'msg_logged_out': "You've been logged out successfully.",
        'err_required_fields': 'Please fill in all required fields.',
        'msg_medicine_added': "✅ '{name}' has been added to your medicines.",
        'msg_medicine_not_found': 'Medicine not found.',
        'msg_medicine_updated': "✅ '{name}' updated successfully.",
        'msg_medicine_removed': "🗑️ '{name}' has been removed.",
        'msg_side_effect_reported': "✅ Side effect '{symptom}' reported.",
        'msg_side_effect_deleted': 'Side effect record deleted.',
        'msg_marked_as': 'Marked as {status}!',

        # Dashboard
        'dash_title': 'Dashboard',
        'dash_welcome': '👋 Welcome back, {name}!',
        'dash_subtitle': "Here's your health overview for today — {today}",
        'stat_active_medicines': 'Active Medicines',
        'stat_taken_7d': 'Taken (7 days)',
        'stat_missed_7d': 'Missed (7 days)',
        'stat_adherence': 'Adherence Rate',
        'weekly_adherence': 'Weekly Adherence',
        'adherence_summary': '{pct}% — {taken} taken out of {total} scheduled doses',
        'today_medicines': "Today's Medicines",
        'upcoming_reminders': 'Upcoming Reminders',
        'recent_side_effects': 'Recent Side Effects',
        'quick_actions': 'Quick Actions',
        'add_new_medicine': 'Add New Medicine',
        'report_side_effect': 'Report Side Effect',
        'ask_ai': 'Ask AI Assistant',
        'view_insights': 'View Insights',
        'empty_no_medicines': 'No medicines yet',
        'empty_add_first_med': 'Add your first medicine to get started',
        'empty_no_reminders': 'No upcoming reminders',
        'empty_reminders_auto': 'Reminders are created automatically when you add medicines',
        'empty_no_side_effects': 'No side effects reported',
        'empty_track_reactions': 'Track any reactions you experience',

        # Medicines
        'med_page_title': 'My Medicines',
        'med_page_sub': 'Manage your medication schedule',
        'add_medicine': 'Add Medicine',
        'add_new_medicine_modal': 'Add New Medicine',
        'edit_medicine': 'Edit Medicine',
        'medicine_name': 'Medicine Name',
        'dosage': 'Dosage',
        'frequency': 'Frequency',
        'times': 'Time(s)',
        'times_hint': '(comma-separated)',
        'start_date': 'Start Date',
        'end_date': 'End Date',
        'empty_no_meds': 'No medicines added yet',
        'empty_click_add': 'Click "Add Medicine" to start tracking your medications',
        'confirm_remove': 'Remove {name}?',

        # Reminders
        'rem_page_title': 'Reminders & Tracking',
        'rem_page_sub': 'Mark doses as taken or missed · Today: {today}',
        'stat_taken_30d': 'Taken (30 days)',
        'stat_missed_30d': 'Missed (30 days)',
        'today_schedule': "Today's Schedule",
        'today_log': "Today's Log",
        'empty_no_reminders_now': 'No reminders for now',
        'empty_add_for_reminders': 'Add medicines to generate reminders automatically',
        'empty_no_doses_today': 'No doses logged today',
        'empty_mark_doses': 'Mark doses as taken or missed to track here',
        'toast_error': 'Something went wrong. Try again.',

        # Side effects
        'se_page_title': 'Side Effect Tracker',
        'se_page_sub': 'Report and monitor reactions to your medicines',
        'report_side_effect_btn': 'Report Side Effect',
        'all_reported': 'All Reported Side Effects',
        'report_modal_title': 'Report Side Effect',
        'symptom_reaction': 'Symptom / Reaction',
        'related_medicine': 'Related Medicine',
        'not_linked': 'Not linked to a medicine',
        'date_reported': 'Date Reported',
        'select_severity': 'Select severity',
        'sev_mild_opt': 'Mild – minor discomfort',
        'sev_mod_opt': 'Moderate – affects daily life',
        'sev_sev_opt': 'Severe – needs attention',
        'report_effect': 'Report Effect',
        'empty_se_detail': 'Report any symptoms or reactions you experience from your medications',
        'confirm_delete_se': 'Delete this record?',

        # Insights
        'insights_title': 'Health Insights',
        'insights_sub': 'Analytics and patterns from your medication history',
        'stat_total_taken': 'Total Doses Taken',
        'stat_total_missed': 'Total Doses Missed',
        'stat_overall_adherence': 'Overall Adherence',
        'stat_se_reported': 'Side Effects Reported',
        'chart_14day': '14-Day Adherence Trend',
        'chart_severity': 'Side Effect Severity',
        'chart_per_med': 'Per-Medicine Adherence',
        'overall_progress': 'Overall Adherence Progress',
        'excellent': 'Excellent',
        'good': 'Good',
        'needs_improvement': 'Needs Improvement',
        'doses_summary': 'You took {taken} out of {total} scheduled doses',
        'chart_taken': 'Taken',
        'chart_missed': 'Missed',
        'empty_chart_history': 'No history yet',
        'empty_chart_mark': 'Mark doses to see per-medicine data',

        # Chatbot
        'chat_title': 'AI Health Assistant',
        'chat_sub': 'Ask MediBot about medications, side effects, and general health',
        'clear_chat': 'Clear Chat',
        'chat_disclaimer': 'Disclaimer: MediBot provides general health information only. This chatbot does not replace professional medical advice. Always consult a qualified healthcare provider for medical decisions.',
        'chat_welcome': "Hi! I'm MediBot, your AI health assistant.",
        'chat_can_help': 'I can help with:',
        'chat_help_meds': 'Medication questions',
        'chat_help_se': 'Side effect information',
        'chat_help_dose': 'Dosage and timing advice',
        'chat_help_health': 'General health guidance',
        'chat_placeholder': 'Ask about your medicines, side effects, dosage...',
        'try_asking': 'Try asking:',
        'chat_error': 'Sorry, I ran into an issue. Please try again. 😕',
        'confirm_clear_chat': 'Clear all chat history?',
        'quick_q1': 'What are common side effects of ibuprofen?',
        'quick_q2': 'What should I do if I missed a dose?',
        'quick_q3': 'How does paracetamol work?',
        'quick_q4': 'What is the maximum daily dose of paracetamol?',
        'quick_q5': 'Can I take antibiotics with food?',

        # History
        'history_title': 'Medication History',
        'history_sub': 'Full record of all logged doses',
        'back_reminders': '← Back to Reminders',
        'page_of': 'Page {page} of {total}',
        'prev': '← Prev',
        'next': 'Next →',
        'empty_history': 'No history yet',
        'empty_history_sub': 'Mark medicines as taken or missed to build your history',
    },

    'hi': {
        # Nav
        'nav_main': 'मुख्य',
        'nav_track': 'ट्रैक',
        'nav_ai': 'AI',
        'nav_dashboard': 'डैशबोर्ड',
        'nav_medicines': 'दवाइयाँ',
        'nav_reminders': 'रिमाइंडर',
        'nav_side_effects': 'दुष्प्रभाव',
        'nav_insights': 'विश्लेषण',
        'nav_ai_assistant': 'AI सहायक',
        'nav_health_management': 'स्वास्थ्य प्रबंधन',
        'nav_logout': 'लॉग आउट',
        'lang_switched': 'भाषा हिंदी में बदल गई।',

        # Common
        'active': 'सक्रिय',
        'inactive': 'निष्क्रिय',
        'cancel': 'रद्द करें',
        'save_changes': 'बदलाव सहेजें',
        'add': 'जोड़ें',
        'all': 'सभी',
        'edit': 'संपादित',
        'remove': 'हटाएँ',
        'general': 'सामान्य',
        'records': 'रिकॉर्ड',
        'medicine': 'दवा',
        'status': 'स्थिति',
        'time': 'समय',
        'notes': 'नोट्स',
        'description': 'विवरण',
        'date': 'तारीख',
        'action': 'कार्रवाई',
        'symptom': 'लक्षण',
        'severity': 'गंभीरता',
        'scheduled': 'निर्धारित',
        'logged_at': 'लॉग समय',
        'full_report': 'पूरी रिपोर्ट',
        'send': 'भेजें',
        'you': 'आप',
        'medibot': 'मेडीबॉट',
        'medibot_ai': 'मेडीबॉट (AI)',
        'ai_assistant': 'AI सहायक',

        # Status & severity
        'status_taken': 'लिया',
        'status_missed': 'छूटा',
        'status_skipped': 'छोड़ा',
        'severity_mild': 'हल्का',
        'severity_moderate': 'मध्यम',
        'severity_severe': 'गंभीर',

        # Frequency
        'freq_once_daily': 'दिन में एक बार',
        'freq_twice_daily': 'दिन में दो बार',
        'freq_thrice_daily': 'दिन में तीन बार',
        'freq_four_daily': 'दिन में चार बार',
        'freq_as_needed': 'ज़रूरत अनुसार',
        'freq_weekly': 'साप्ताहिक',
        'select_frequency': 'आवृत्ति चुनें',

        # Auth
        'auth_welcome_back': 'वापसी पर स्वागत है',
        'auth_sign_in_sub': 'अपने MediTrack खाते में साइन इन करें',
        'auth_create_account': 'खाता बनाएँ',
        'auth_create_sub': 'आज से अपना स्वास्थ्य प्रबंधन शुरू करें',
        'auth_email': 'ईमेल पता',
        'auth_password': 'पासवर्ड',
        'auth_full_name': 'पूरा नाम',
        'auth_confirm_password': 'पासवर्ड की पुष्टि',
        'auth_sign_in': 'साइन इन',
        'auth_no_account': 'खाता नहीं है?',
        'auth_create_free': 'मुफ़्त में बनाएँ',
        'auth_has_account': 'पहले से खाता है?',
        'auth_log_in': 'लॉग इन',
        'auth_brand_headline': 'आपका स्वास्थ्य, सुंदर ढंग से व्यवस्थित',
        'auth_brand_desc': 'दवाइयाँ ट्रैक करें, दुष्प्रभाव निगरानी करें, और एक सुंदर डैशबोर्ड में AI स्वास्थ्य मार्गदर्शन पाएँ।',
        'auth_feature_reminders': 'स्मार्ट दवा रिमाइंडर',
        'auth_feature_insights': 'अनुपालन विश्लेषण',
        'auth_feature_ai': 'ऑन-डिमांड AI स्वास्थ्य सहायक',
        'auth_register_headline': 'आज ही अपनी स्वास्थ्य यात्रा शुरू करें',
        'auth_register_desc': 'हज़ारों लोगों के साथ जुड़ें जो रिमाइंडर, दुष्प्रभाव ट्रैकिंग और AI मार्गदर्शन से अपना स्वास्थ्य संभालते हैं।',
        'auth_feature_secure': 'सुरक्षित, एन्क्रिप्टेड खाते',
        'auth_feature_never_miss': 'कोई खुराक कभी न छूटे',
        'auth_feature_track': 'प्रतिक्रियाएँ रियल-टाइम ट्रैक करें',
        'auth_pw_match': 'पासवर्ड मेल खाते हैं',
        'auth_pw_no_match': 'पासवर्ड मेल नहीं खाते',
        'auth_smart_companion': 'आपका स्मार्ट स्वास्थ्य साथी',

        # Auth errors & flashes
        'err_name_short': 'नाम कम से कम 2 अक्षर का होना चाहिए।',
        'err_email_invalid': 'कृपया मान्य ईमेल पता दर्ज करें।',
        'err_password_short': 'पासवर्ड कम से कम 8 अक्षर का होना चाहिए।',
        'err_password_mismatch': 'पासवर्ड मेल नहीं खाते।',
        'err_email_exists': 'इस ईमेल से पहले से खाता मौजूद है।',
        'msg_account_created': 'खाता सफलतापूर्वक बनाया गया! कृपया लॉग इन करें।',
        'err_fill_all': 'कृपया सभी फ़ील्ड भरें।',
        'err_invalid_login': 'अमान्य ईमेल या पासवर्ड।',
        'msg_welcome_back': 'वापसी पर स्वागत है, {name}! 👋',
        'msg_logged_out': 'आप सफलतापूर्वक लॉग आउट हो गए।',
        'err_required_fields': 'कृपया सभी आवश्यक फ़ील्ड भरें।',
        'msg_medicine_added': "✅ '{name}' आपकी दवाओं में जोड़ी गई।",
        'msg_medicine_not_found': 'दवा नहीं मिली।',
        'msg_medicine_updated': "✅ '{name}' सफलतापूर्वक अपडेट हुई।",
        'msg_medicine_removed': "🗑️ '{name}' हटा दी गई।",
        'msg_side_effect_reported': "✅ दुष्प्रभाव '{symptom}' दर्ज किया गया।",
        'msg_side_effect_deleted': 'दुष्प्रभाव रिकॉर्ड हटाया गया।',
        'msg_marked_as': '{status} के रूप में चिह्नित!',

        # Dashboard
        'dash_title': 'डैशबोर्ड',
        'dash_welcome': '👋 वापसी पर स्वागत है, {name}!',
        'dash_subtitle': 'आज का आपका स्वास्थ्य अवलोकन — {today}',
        'stat_active_medicines': 'सक्रिय दवाइयाँ',
        'stat_taken_7d': 'लिया (7 दिन)',
        'stat_missed_7d': 'छूटा (7 दिन)',
        'stat_adherence': 'अनुपालन दर',
        'weekly_adherence': 'साप्ताहिक अनुपालन',
        'adherence_summary': '{pct}% — {total} निर्धारित खुराक में से {taken} ली',
        'today_medicines': 'आज की दवाइयाँ',
        'upcoming_reminders': 'आगामी रिमाइंडर',
        'recent_side_effects': 'हाल के दुष्प्रभाव',
        'quick_actions': 'त्वरित कार्य',
        'add_new_medicine': 'नई दवा जोड़ें',
        'report_side_effect': 'दुष्प्रभाव दर्ज करें',
        'ask_ai': 'AI सहायक से पूछें',
        'view_insights': 'विश्लेषण देखें',
        'empty_no_medicines': 'अभी कोई दवा नहीं',
        'empty_add_first_med': 'शुरू करने के लिए अपनी पहली दवा जोड़ें',
        'empty_no_reminders': 'कोई आगामी रिमाइंडर नहीं',
        'empty_reminders_auto': 'दवा जोड़ने पर रिमाइंडर अपने आप बनते हैं',
        'empty_no_side_effects': 'कोई दुष्प्रभाव दर्ज नहीं',
        'empty_track_reactions': 'अनुभव की गई किसी भी प्रतिक्रिया को ट्रैक करें',

        # Medicines
        'med_page_title': 'मेरी दवाइयाँ',
        'med_page_sub': 'अपनी दवा अनुसूची प्रबंधित करें',
        'add_medicine': 'दवा जोड़ें',
        'add_new_medicine_modal': 'नई दवा जोड़ें',
        'edit_medicine': 'दवा संपादित करें',
        'medicine_name': 'दवा का नाम',
        'dosage': 'खुराक',
        'frequency': 'आवृत्ति',
        'times': 'समय',
        'times_hint': '(अल्पविराम से अलग)',
        'start_date': 'शुरू की तारीख',
        'end_date': 'समाप्ति तारीख',
        'empty_no_meds': 'अभी कोई दवा नहीं जोड़ी',
        'empty_click_add': 'दवाइयाँ ट्रैक करने के लिए "दवा जोड़ें" पर क्लिक करें',
        'confirm_remove': '{name} हटाएँ?',

        # Reminders
        'rem_page_title': 'रिमाइंडर और ट्रैकिंग',
        'rem_page_sub': 'खुराक लिया/छूटा चिह्नित करें · आज: {today}',
        'stat_taken_30d': 'लिया (30 दिन)',
        'stat_missed_30d': 'छूटा (30 दिन)',
        'today_schedule': 'आज का शेड्यूल',
        'today_log': 'आज का लॉग',
        'empty_no_reminders_now': 'अभी कोई रिमाइंडर नहीं',
        'empty_add_for_reminders': 'रिमाइंडर के लिए दवाइयाँ जोड़ें',
        'empty_no_doses_today': 'आज कोई खुराक लॉग नहीं',
        'empty_mark_doses': 'यहाँ ट्रैक करने के लिए खुराक लिया/छूटा चिह्नित करें',
        'toast_error': 'कुछ गलत हुआ। फिर से प्रयास करें।',

        # Side effects
        'se_page_title': 'दुष्प्रभाव ट्रैकर',
        'se_page_sub': 'अपनी दवाओं की प्रतिक्रियाएँ दर्ज और निगरानी करें',
        'report_side_effect_btn': 'दुष्प्रभाव दर्ज करें',
        'all_reported': 'सभी दर्ज दुष्प्रभाव',
        'report_modal_title': 'दुष्प्रभाव दर्ज करें',
        'symptom_reaction': 'लक्षण / प्रतिक्रिया',
        'related_medicine': 'संबंधित दवा',
        'not_linked': 'किसी दवा से लिंक नहीं',
        'date_reported': 'दर्ज की तारीख',
        'select_severity': 'गंभीरता चुनें',
        'sev_mild_opt': 'हल्का – मामूली असुविधा',
        'sev_mod_opt': 'मध्यम – दैनिक जीवन प्रभावित',
        'sev_sev_opt': 'गंभीर – ध्यान देने योग्य',
        'report_effect': 'प्रभाव दर्ज करें',
        'empty_se_detail': 'अपनी दवाओं से अनुभव किए गए लक्षण या प्रतिक्रियाएँ दर्ज करें',
        'confirm_delete_se': 'यह रिकॉर्ड हटाएँ?',

        # Insights
        'insights_title': 'स्वास्थ्य विश्लेषण',
        'insights_sub': 'आपके दवा इतिहास से विश्लेषण और पैटर्न',
        'stat_total_taken': 'कुल खुराक ली',
        'stat_total_missed': 'कुल खुराक छूटी',
        'stat_overall_adherence': 'कुल अनुपालन',
        'stat_se_reported': 'दुष्प्रभाव दर्ज',
        'chart_14day': '14-दिन अनुपालन रुझान',
        'chart_severity': 'दुष्प्रभाव गंभीरता',
        'chart_per_med': 'प्रति-दवा अनुपालन',
        'overall_progress': 'कुल अनुपालन प्रगति',
        'excellent': 'उत्कृष्ट',
        'good': 'अच्छा',
        'needs_improvement': 'सुधार की ज़रूरत',
        'doses_summary': 'आपने {total} निर्धारित खुराक में से {taken} ली',
        'chart_taken': 'लिया',
        'chart_missed': 'छूटा',
        'empty_chart_history': 'अभी कोई इतिहास नहीं',
        'empty_chart_mark': 'प्रति-दवा डेटा के लिए खुराक चिह्नित करें',

        # Chatbot
        'chat_title': 'AI स्वास्थ्य सहायक',
        'chat_sub': 'मेडीबॉट से दवाइयों, दुष्प्रभाव और सामान्य स्वास्थ्य के बारे में पूछें',
        'clear_chat': 'चैट साफ़ करें',
        'chat_disclaimer': 'अस्वीकरण: मेडीबॉट केवल सामान्य स्वास्थ्य जानकारी देता है। यह चैटबॉट पेशेवर चिकित्सा सलाह का विकल्प नहीं है। चिकित्सा निर्णयों के लिए हमेशा योग्य स्वास्थ्य प्रदाता से परामर्श लें।',
        'chat_welcome': 'नमस्ते! मैं मेडीबॉट, आपका AI स्वास्थ्य सहायक हूँ।',
        'chat_can_help': 'मैं इनमें मदद कर सकता हूँ:',
        'chat_help_meds': 'दवा संबंधी प्रश्न',
        'chat_help_se': 'दुष्प्रभाव जानकारी',
        'chat_help_dose': 'खुराक और समय सलाह',
        'chat_help_health': 'सामान्य स्वास्थ्य मार्गदर्शन',
        'chat_placeholder': 'अपनी दवाइयों, दुष्प्रभाव, खुराक के बारे में पूछें...',
        'try_asking': 'पूछने का प्रयास करें:',
        'chat_error': 'क्षमा करें, समस्या हुई। कृपया फिर से प्रयास करें। 😕',
        'confirm_clear_chat': 'सारा चैट इतिहास साफ़ करें?',
        'quick_q1': 'इबुप्रोफेन के सामान्य दुष्प्रभाव क्या हैं?',
        'quick_q2': 'अगर मैंने खुराक छोड़ दी तो क्या करूँ?',
        'quick_q3': 'पैरासिटामोल कैसे काम करता है?',
        'quick_q4': 'पैरासिटामोल की अधिकतम दैनिक खुराक क्या है?',
        'quick_q5': 'क्या एंटीबायोटिक्स भोजन के साथ ले सकते हैं?',

        # History
        'history_title': 'दवा इतिहास',
        'history_sub': 'सभी लॉग की गई खुराक का पूरा रिकॉर्ड',
        'back_reminders': '← रिमाइंडर पर वापस',
        'page_of': 'पृष्ठ {page} / {total}',
        'prev': '← पिछला',
        'next': 'अगला →',
        'empty_history': 'अभी कोई इतिहास नहीं',
        'empty_history_sub': 'इतिहास बनाने के लिए दवाइयाँ लिया/छूटा चिह्नित करें',
    },
}
