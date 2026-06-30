import streamlit as st
import os
import json
import asyncio
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from edge_tts import Communicate

# =========================
# CONFIG & CONSTANTS
# =========================

DB_FILE = "users_db.json"
TRX_FILE = "used_trx.json"
SERVICE_ACCOUNT_FILE = "service_account.json"
SHEET_NAME = "VoiceBotUsers"

DEFAULT_TOTAL_ALLOWED = 5000
DEFAULT_PLAN = "Free Starter"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "FM@12345"

EASYPAISA_NUMBER = "03047149419"
JAZZCASH_NUMBER = "03047149419"
ACCOUNT_TITLE = "Fakhar Mehmood"
WHATSAPP_NUMBER = "923047149419"

PAYMENT_PROOF_FOLDER = "payment_proofs"

PLAN_CATALOG = {
    "Free Starter": {"words": 5000, "price": 0, "description": "Free trial credits"},
    "Plan 1": {"words": 100000, "price": 70, "description": "30 Day - 80 to 100 min audio approx"},
    "Plan 2": {"words": 200000, "price": 137, "description": "30 Day - 166 to 200 min audio approx"},
    "Plan 3": {"words": 300000, "price": 205, "description": "30 Day - 250 to 300 min audio approx"},
    "Plan 4": {"words": 400000, "price": 273, "description": "30 Day - 160 to 450 min audio approx"},
    "Plan 5": {"words": 500000, "price": 337, "description": "30 Day - 350 to 500 min audio approx"},
    "Plan 6": {"words": 1000000, "price": 666, "description": "30 Day - 833 to 1000 min audio approx"},
    "Plan 7": {"words": 5000000, "price": 2970, "description": "30 Day - 4166 to 5000 min audio approx"},
    "Plan 8": {"words": 10000000, "price": 4950, "description": "30 Day - 8333 to 10000 min audio approx"},
}

st.set_page_config(
    page_title="F.M AI Studio - Portal",
    page_icon="🎙️",
    layout="wide"
)

# =========================
# BEAUTIFUL UI CSS
# =========================

def add_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59,130,246,.22), transparent 28%),
            radial-gradient(circle at top right, rgba(168,85,247,.20), transparent 30%),
            linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #ecfeff 100%);
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1240px;
    }

    h1, h2, h3 { color: #0f172a; font-weight: 800; }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #08111f 0%, #172554 45%, #312e81 100%);
        border-right: 1px solid rgba(255,255,255,.12);
    }

    div[data-testid="stSidebar"] h1,
    div[data-testid="stSidebar"] h2,
    div[data-testid="stSidebar"] h3,
    div[data-testid="stSidebar"] p,
    div[data-testid="stSidebar"] label,
    div[data-testid="stSidebar"] span,
    div[data-testid="stSidebar"] div { color: #fff; }

    .hero-box {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 52%, #db2777 100%);
        padding: 38px;
        border-radius: 28px;
        color: white;
        box-shadow: 0 24px 55px rgba(37,99,235,.28);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .hero-box:before {
        content: '';
        position: absolute;
        width: 240px;
        height: 240px;
        border-radius: 50%;
        background: rgba(255,255,255,.16);
        top: -80px;
        right: -70px;
    }
    .hero-box h1 { color: white; font-size: 44px; margin: 0 0 10px 0; line-height: 1.05; }
    .hero-box p { color: #e0e7ff; font-size: 18px; margin: 0; max-width: 780px; }
    .hero-pill {
        display: inline-block;
        background: rgba(255,255,255,.18);
        border: 1px solid rgba(255,255,255,.25);
        padding: 8px 14px;
        border-radius: 999px;
        color: white;
        font-size: 13px;
        margin-bottom: 16px;
        font-weight: 700;
    }

    .premium-card {
        background: rgba(255,255,255,.94);
        padding: 24px;
        border-radius: 22px;
        box-shadow: 0 12px 30px rgba(15,23,42,.10);
        border: 1px solid rgba(99,102,241,.14);
        margin-bottom: 18px;
    }

    .feature-card {
        background: rgba(255,255,255,.96);
        padding: 22px;
        border-radius: 20px;
        box-shadow: 0 10px 26px rgba(15,23,42,.08);
        border: 1px solid rgba(148,163,184,.24);
        min-height: 145px;
    }
    .feature-card h3 { margin: 0 0 8px 0; font-size: 20px; }
    .feature-card p { margin: 0; color: #475569; font-size: 15px; }

    .glass-card {
        background: rgba(255,255,255,.70);
        backdrop-filter: blur(12px);
        padding: 22px;
        border-radius: 22px;
        box-shadow: 0 14px 32px rgba(15,23,42,.09);
        border: 1px solid rgba(255,255,255,.65);
        margin-bottom: 18px;
    }

    .metric-card {
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color: white;
        padding: 22px;
        border-radius: 20px;
        box-shadow: 0 14px 28px rgba(15,23,42,.25);
        min-height: 120px;
    }
    .metric-card h3 { color: #c7d2fe; margin: 0; font-size: 14px; text-transform: uppercase; letter-spacing: .08em; }
    .metric-card h2 { color: white; margin: 10px 0 0 0; font-size: 30px; }
    .metric-card p { color: #dbeafe; margin: 6px 0 0 0; }

    .sidebar-card {
        background: rgba(255,255,255,.10);
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 20px;
        padding: 18px;
        margin: 12px 0;
        box-shadow: 0 12px 26px rgba(0,0,0,.16);
    }
    .sidebar-card h3 { color: white; margin: 0 0 10px 0; }
    .sidebar-card p { margin: 5px 0; color: #e0e7ff; }

    .payment-box {
        background: linear-gradient(135deg, #fff7ed, #ffedd5);
        border: 1px solid #fed7aa;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 10px 22px rgba(251,146,60,.13);
        margin: 12px 0;
    }

    .plan-card {
        background: white;
        border: 1px solid rgba(99,102,241,.18);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 24px rgba(15,23,42,.08);
        height: 100%;
    }
    .plan-card h3 { color: #3730a3; margin: 0; }
    .price { font-size: 28px; font-weight: 800; color: #db2777; margin: 10px 0; }
    .credits { color: #0f766e; font-weight: 800; }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border: 0;
        border-radius: 14px;
        padding: .78rem 1rem;
        font-weight: 800;
        box-shadow: 0 10px 22px rgba(37,99,235,.24);
        transition: all .18s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #1d4ed8, #6d28d9);
        color: white;
        transform: translateY(-1px);
    }

    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        border-radius: 14px !important;
        border: 1px solid #cbd5e1 !important;
        background: rgba(255,255,255,.92) !important;
    }

    div[data-testid="stSelectbox"] div { border-radius: 14px !important; }

    .footer {
        text-align: center;
        padding: 24px;
        color: #475569;
        font-size: 14px;
    }

    @media (max-width: 768px) {
        .hero-box { padding: 26px; }
        .hero-box h1 { font-size: 31px; }
        .hero-box p { font-size: 15px; }
    }
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# =========================
# SMALL HELPER FUNCTIONS
# =========================

def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def format_number(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


def get_plan_words(plan_name):
    return PLAN_CATALOG.get(plan_name, {}).get("words", DEFAULT_TOTAL_ALLOWED)


def get_plan_price(plan_name):
    return PLAN_CATALOG.get(plan_name, {}).get("price", 0)


def hero(title, subtitle, pill="Professional AI Voice Generator"):
    st.markdown(f"""
    <div class="hero-box">
        <div class="hero-pill">{pill}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def feature_cards():
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="feature-card"><h3>🎧 Natural Voices</h3><p>Urdu, English, Punjabi aur Arabic mein male/female AI voices.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="feature-card"><h3>⚡ Fast MP3</h3><p>Text likhein, voice generate karain aur MP3 download karain.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="feature-card"><h3>🎁 Free Credits</h3><p>New signup par 5000 free credits. Upgrade system built-in.</p></div>', unsafe_allow_html=True)


def show_payment_details():
    st.markdown(f"""
    <div class="payment-box">
        <h3>💳 Payment Details</h3>
        <p><b>Easypaisa:</b> <code>{EASYPAISA_NUMBER}</code></p>
        <p><b>JazzCash:</b> <code>{JAZZCASH_NUMBER}</code></p>
        <p><b>Account Title:</b> <code>{ACCOUNT_TITLE}</code></p>
        <p>Payment ke baad transaction ID aur screenshot submit karain.</p>
        <p><a href="https://wa.me/{WHATSAPP_NUMBER}" target="_blank">📲 WhatsApp Contact</a></p>
    </div>
    """, unsafe_allow_html=True)


def show_plan_cards():
    st.markdown("### 📦 Available Plans")
    items = list(PLAN_CATALOG.items())
    for i in range(0, len(items), 3):
        cols = st.columns(3)
        for col, (plan_name, data) in zip(cols, items[i:i+3]):
            with col:
                st.markdown(f"""
                <div class="plan-card">
                    <h3>{plan_name}</h3>
                    <div class="price">Rs {data['price']}</div>
                    <p class="credits">{format_number(data['words'])} Credits / Words</p>
                    <p>{data['description']}</p>
                </div>
                """, unsafe_allow_html=True)


def show_plan_table():
    plan_rows = []
    for plan_name, data in PLAN_CATALOG.items():
        plan_rows.append({
            "Plan": plan_name,
            "Credits / Words": format_number(data["words"]),
            "Price": f"Rs {data['price']}",
            "Details": data["description"]
        })
    st.table(plan_rows)

# =========================
# GOOGLE SHEET FUNCTIONS
# =========================

def get_sheet():
    try:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            return None

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        ensure_sheet_headers(sheet)
        return sheet
    except Exception:
        return None


def ensure_sheet_headers(sheet):
    headers = ["First Name", "Last Name", "Email", "Username", "Password", "Words Used", "Total Allowed", "Plan"]
    try:
        first_row = sheet.row_values(1)
        if first_row != headers:
            if len(first_row) == 0:
                sheet.append_row(headers)
            else:
                sheet.update("A1:H1", [headers])
    except Exception:
        pass


def load_db_from_sheet():
    sheet = get_sheet()
    if sheet is None:
        return None
    try:
        records = sheet.get_all_records()
        db = {}
        for row in records:
            username = str(row.get("Username", "")).strip()
            if username:
                db[username] = {
                    "first_name": str(row.get("First Name", "")),
                    "last_name": str(row.get("Last Name", "")),
                    "email": str(row.get("Email", "")),
                    "password": str(row.get("Password", "")),
                    "words_used": safe_int(row.get("Words Used", 0), 0),
                    "total_allowed": safe_int(row.get("Total Allowed", DEFAULT_TOTAL_ALLOWED), DEFAULT_TOTAL_ALLOWED),
                    "plan": str(row.get("Plan", DEFAULT_PLAN))
                }
        return db
    except Exception:
        return None


def save_user_to_sheet(username, user_data):
    sheet = get_sheet()
    if sheet is None:
        return False
    try:
        records = sheet.get_all_records()
        row_number = None
        for index, row in enumerate(records, start=2):
            if str(row.get("Username", "")).strip() == username:
                row_number = index
                break

        row_values = [
            user_data.get("first_name", ""),
            user_data.get("last_name", ""),
            user_data.get("email", ""),
            username,
            user_data.get("password", ""),
            safe_int(user_data.get("words_used", 0), 0),
            safe_int(user_data.get("total_allowed", DEFAULT_TOTAL_ALLOWED), DEFAULT_TOTAL_ALLOWED),
            user_data.get("plan", DEFAULT_PLAN)
        ]

        if row_number:
            sheet.update(f"A{row_number}:H{row_number}", [row_values])
        else:
            sheet.append_row(row_values)
        return True
    except Exception:
        return False


def save_all_users_to_sheet(db):
    for username, user_data in db.items():
        save_user_to_sheet(username, user_data)

# =========================
# LOCAL JSON DATABASE FUNCTIONS
# =========================

def load_db_from_local():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_db_to_local(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


def load_db():
    sheet_db = load_db_from_sheet()
    if sheet_db is not None:
        return sheet_db
    return load_db_from_local()


def save_db(db):
    save_db_to_local(db)
    save_all_users_to_sheet(db)

# =========================
# TRANSACTION FUNCTIONS
# =========================

def load_trx():
    if os.path.exists(TRX_FILE):
        try:
            with open(TRX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_trx(trx_list):
    with open(TRX_FILE, "w", encoding="utf-8") as f:
        json.dump(trx_list, f, indent=4, ensure_ascii=False)


def is_duplicate_trx(trx_list, trx_id):
    trx_id = trx_id.strip().lower()
    return any(str(trx.get("trx_id", "")).strip().lower() == trx_id for trx in trx_list)


def save_uploaded_payment_proof(uploaded_file, username):
    if uploaded_file is None:
        return ""
    try:
        if not os.path.exists(PAYMENT_PROOF_FOLDER):
            os.makedirs(PAYMENT_PROOF_FOLDER)
        clean_name = uploaded_file.name.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(PAYMENT_PROOF_FOLDER, f"{username}_{timestamp}_{clean_name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return file_path
    except Exception:
        return ""

# =========================
# LOAD DATABASE
# =========================

db = load_db()
used_trx = load_trx()

# =========================
# SESSION STATE
# =========================

if "generated_audio" not in st.session_state:
    st.session_state.generated_audio = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =========================
# LOGIN / SIGNUP SYSTEM
# =========================

if not st.session_state.logged_in:
    hero("🎙️ F.M AI Studio", "Professional AI Voice Generator for Urdu, English, Punjabi & Arabic. Create account, get free credits, and download MP3 voice.", "Welcome to AI Voice Portal")
    feature_cards()

    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🔐 Sign In", "📝 Create Account", "🔄 Change Password"])

    with tab1:
        st.subheader("Sign In To Your Account")
        user_input = st.text_input("Username", key="login_user")
        pass_input = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login 🔥", use_container_width=True):
            user_input = user_input.strip()
            if user_input == ADMIN_USERNAME and pass_input == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.username = ADMIN_USERNAME
                st.session_state.is_admin = True
                st.success("Admin Panel mein welcome!")
                st.rerun()
            elif user_input in db and db[user_input].get("password", "") == pass_input:
                st.session_state.logged_in = True
                st.session_state.username = user_input
                st.session_state.is_admin = False
                st.success(f"Welcome back {user_input}!")
                st.rerun()
            else:
                st.error("Ghalat username ya password! Dobara koshish karein.")

    with tab2:
        st.subheader("Create New Account")
        c1, c2 = st.columns(2)
        with c1:
            f_name = st.text_input("First Name", key="reg_fname")
            email = st.text_input("Email", key="reg_email")
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        with c2:
            l_name = st.text_input("Last Name", key="reg_lname")
            new_user = st.text_input("Choose Username", key="reg_user")
            st.info("New account par 5000 free credits milain gy.")

        if st.button("Register Account 🚀", use_container_width=True):
            new_user = new_user.strip()
            if new_user == ADMIN_USERNAME:
                st.error("Yeh username reserved hai. Koi aur username choose karain.")
            elif new_user in db:
                st.error("Yeh username pehle se mojood hai!")
            elif new_user == "" or new_pass.strip() == "":
                st.error("Username aur Password khali nahi ho sakte!")
            else:
                db[new_user] = {
                    "first_name": f_name.strip(),
                    "last_name": l_name.strip(),
                    "email": email.strip(),
                    "password": new_pass,
                    "words_used": 0,
                    "total_allowed": DEFAULT_TOTAL_ALLOWED,
                    "plan": DEFAULT_PLAN
                }
                save_db(db)
                st.success("Account kamyabi se ban gaya! Ab Sign In karain.")

    with tab3:
        st.subheader("Change Password")
        c_user = st.text_input("Username", key="chg_user")
        old_pass = st.text_input("Old Password", type="password", key="chg_old")
        c_pass = st.text_input("New Password", type="password", key="chg_new")
        if st.button("Update Password 🔄", use_container_width=True):
            c_user = c_user.strip()
            if c_user in db and db[c_user].get("password", "") == old_pass:
                db[c_user]["password"] = c_pass
                save_db(db)
                st.success("Password kamyabi se badal gaya!")
            else:
                st.error("Username ya purana password ghalat hai!")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">Powered by F.M AI Studio • Professional Text to Voice Platform</div>', unsafe_allow_html=True)

else:
    # =========================
    # ADMIN DASHBOARD
    # =========================
    if st.session_state.get("is_admin", False):
        hero("🛠️ Admin Dashboard", "Users, credits, plans and payment requests manage karain.", "F.M AI Studio Admin Panel")

        total_users = len(db)
        total_pending = len([x for x in used_trx if x.get("status") == "Pending"])

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><h3>Total Users</h3><h2>{total_users}</h2><p>Registered accounts</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><h3>Pending Payments</h3><h2>{total_pending}</h2><p>Waiting approval</p></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><h3>Total Transactions</h3><h2>{len(used_trx)}</h2><p>All requests</p></div>', unsafe_allow_html=True)

        st.write("")
        admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs(["👥 Users Management", "💳 Payment Requests", "📦 Plans", "⚙️ Admin Info"])

        with admin_tab1:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.subheader("👥 Users Management")
            if len(db) == 0:
                st.warning("Abhi koi user create nahi hua.")
            else:
                selected_user = st.selectbox("User select karo:", list(db.keys()))
                selected_data = db[selected_user]
                st.write(f"### Selected User: {selected_user}")

                col_a, col_b = st.columns(2)
                with col_a:
                    new_first_name = st.text_input("First Name", value=selected_data.get("first_name", ""))
                    new_email = st.text_input("Email", value=selected_data.get("email", ""))
                    plan_list = list(PLAN_CATALOG.keys())
                    current_plan = selected_data.get("plan", DEFAULT_PLAN)
                    new_plan = st.selectbox("Plan Name", plan_list, index=plan_list.index(current_plan) if current_plan in plan_list else 0)
                with col_b:
                    new_last_name = st.text_input("Last Name", value=selected_data.get("last_name", ""))
                    new_password = st.text_input("User Password", value=selected_data.get("password", ""))
                    new_total_allowed = st.number_input(
                        "Total Allowed Words / Credits",
                        min_value=0,
                        value=safe_int(selected_data.get("total_allowed", DEFAULT_TOTAL_ALLOWED), DEFAULT_TOTAL_ALLOWED),
                        step=1000
                    )

                new_words_used = st.number_input("Used Words", min_value=0, value=safe_int(selected_data.get("words_used", 0), 0), step=100)

                col_save, col_reset, col_delete = st.columns(3)
                with col_save:
                    if st.button("💾 Save User Changes", use_container_width=True):
                        db[selected_user]["first_name"] = new_first_name
                        db[selected_user]["last_name"] = new_last_name
                        db[selected_user]["email"] = new_email
                        db[selected_user]["password"] = new_password
                        db[selected_user]["plan"] = new_plan
                        db[selected_user]["total_allowed"] = int(new_total_allowed)
                        db[selected_user]["words_used"] = int(new_words_used)
                        save_db(db)
                        st.success("User data successfully update ho gaya!")
                        st.rerun()
                with col_reset:
                    if st.button("🔄 Reset Used Words", use_container_width=True):
                        db[selected_user]["words_used"] = 0
                        save_db(db)
                        st.success("Used words reset ho gaye!")
                        st.rerun()
                with col_delete:
                    if st.button("🗑️ Delete User", use_container_width=True):
                        del db[selected_user]
                        save_db(db)
                        st.warning("User delete ho gaya!")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with admin_tab2:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.subheader("💳 Payment Requests")
            pending_requests = [trx for trx in used_trx if trx.get("status") == "Pending"]
            if len(pending_requests) == 0:
                st.info("Abhi koi pending payment request nahi hai.")
            else:
                request_labels = [f"{trx.get('username')} | {trx.get('plan')} | {trx.get('trx_id')} | Rs {trx.get('price')}" for trx in pending_requests]
                selected_label = st.selectbox("Pending request select karo:", request_labels)
                selected_trx = pending_requests[request_labels.index(selected_label)]

                st.write("### Request Details")
                st.json(selected_trx)
                proof_path = selected_trx.get("proof_path", "")
                if proof_path and os.path.exists(proof_path):
                    st.info(f"Payment proof file saved: {proof_path}")
                    try:
                        st.image(proof_path, caption="Payment Screenshot", use_container_width=True)
                    except Exception:
                        st.warning("Proof image preview nahi ho rahi, lekin file saved hai.")

                col_approve, col_reject = st.columns(2)
                with col_approve:
                    if st.button("✅ Approve Payment & Add Credits", use_container_width=True):
                        username = selected_trx.get("username", "")
                        plan_name = selected_trx.get("plan", DEFAULT_PLAN)
                        if username in db:
                            add_words = get_plan_words(plan_name)
                            old_total = safe_int(db[username].get("total_allowed", DEFAULT_TOTAL_ALLOWED), DEFAULT_TOTAL_ALLOWED)
                            db[username]["total_allowed"] = old_total + add_words
                            db[username]["plan"] = plan_name
                            for trx in used_trx:
                                if trx.get("id") == selected_trx.get("id"):
                                    trx["status"] = "Approved"
                                    trx["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            save_db(db)
                            save_trx(used_trx)
                            st.success(f"{username} ko {format_number(add_words)} credits add ho gaye!")
                            st.rerun()
                        else:
                            st.error("User database mein nahi mila!")
                with col_reject:
                    if st.button("❌ Reject Payment", use_container_width=True):
                        for trx in used_trx:
                            if trx.get("id") == selected_trx.get("id"):
                                trx["status"] = "Rejected"
                                trx["rejected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_trx(used_trx)
                        st.warning("Payment request reject ho gai.")
                        st.rerun()

            st.write("---")
            st.subheader("All Transactions")
            if len(used_trx) > 0:
                st.dataframe(used_trx, use_container_width=True)
            else:
                st.info("Abhi koi transaction nahi.")
            st.markdown('</div>', unsafe_allow_html=True)

        with admin_tab3:
            show_plan_cards()
            show_payment_details()

        with admin_tab4:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.subheader("⚙️ Admin Login Info")
            st.warning("Deploy karne se pehle admin password strong kar lena.")
            st.code(f"Admin Username: {ADMIN_USERNAME}\nAdmin Password: {ADMIN_PASSWORD}")
            st.write("---")
            st.subheader("Google Sheet Info")
            st.info(f"Google Sheet ka naam: {SHEET_NAME}")
            st.markdown("""
            Google Sheet use karni hai to:
            1. Google Sheet ka naam **VoiceBotUsers** rakho.
            2. `service_account.json` mein jo `client_email` hai usko copy karo.
            3. Google Sheet open karo > Share > client_email paste karo.
            4. Permission **Editor** select karo.
            """)
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        if st.button("🚪 Admin Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.is_admin = False
            st.session_state.generated_audio = None
            st.rerun()
        st.stop()

    # =========================
    # NORMAL USER DASHBOARD
    # =========================

    current_user = st.session_state.username
    if current_user not in db:
        st.error("User database mein nahi mila. Dobara login karein.")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.is_admin = False
            st.rerun()
        st.stop()

    user_data = db[current_user]
    words_used = safe_int(user_data.get("words_used", 0), 0)
    total_allowed = safe_int(user_data.get("total_allowed", DEFAULT_TOTAL_ALLOWED), DEFAULT_TOTAL_ALLOWED)
    remaining_words = max(total_allowed - words_used, 0)
    progress_value = min(words_used / total_allowed, 1.0) if total_allowed > 0 else 0

    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-card">
            <h3>💙 Membership</h3>
            <p><b>User:</b> {current_user.upper()}</p>
            <p><b>Plan:</b> {user_data.get('plan', DEFAULT_PLAN)}</p>
            <p><b>Remaining:</b> {format_number(remaining_words)} credits</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progress_value)
        st.caption(f"Used {format_number(words_used)} / {format_number(total_allowed)} credits")

        st.markdown(f"""
        <div class="sidebar-card">
            <h3>💳 New Plan Purchase</h3>
            <p><b>Easypaisa:</b> {EASYPAISA_NUMBER}</p>
            <p><b>JazzCash:</b> {JAZZCASH_NUMBER}</p>
            <p><b>Title:</b> {ACCOUNT_TITLE}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"[📲 WhatsApp Contact](https://wa.me/{WHATSAPP_NUMBER})")

        if user_data.get("plan") in ["Plan 6", "Plan 7", "Plan 8", "VIP Owner"]:
            st.write("---")
            st.markdown("### 🎁 Premium Canva Pro Link")
            st.markdown("[Free Canva Pro Link](https://www.canva.com/)")

        st.write("---")
        st.subheader("F.M AI Studio Services")
        st.markdown("""
        * 11Lab Text to Speech
        * Minimax Voice Clone
        * CapCut Pro
        * Canva Pro yearly offer
        """)
        st.write("---")
        if st.button("🚪 Logout Account", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.is_admin = False
            st.session_state.generated_audio = None
            st.rerun()

    hero("🎙️ Professional AI Voice Generator", "Convert your text into high quality AI voice. Urdu, English, Punjabi & Arabic supported.", "User Voice Studio")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>Total Credits</h3><h2>{format_number(total_allowed)}</h2><p>Your account limit</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><h3>Used Credits</h3><h2>{format_number(words_used)}</h2><p>Already used</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><h3>Remaining</h3><h2>{format_number(remaining_words)}</h2><p>Available credits</p></div>', unsafe_allow_html=True)

    st.write("")
    st.progress(progress_value)
    st.caption(f"Credit usage: {format_number(words_used)} / {format_number(total_allowed)}")

    with st.expander("📦 Plans & Payment Details", expanded=False):
        show_plan_cards()
        show_payment_details()

    with st.expander("💳 Payment Submit / Plan Upgrade Request", expanded=False):
        st.info("Payment karne ke baad yahan transaction ID aur screenshot submit karain. Admin approve karega to credits add ho jayenge.")
        selected_purchase_plan = st.selectbox("Kaunsa plan purchase karna hai?", [p for p in PLAN_CATALOG.keys() if p != "Free Starter"])
        st.write(f"Selected Plan Credits: **{format_number(get_plan_words(selected_purchase_plan))}**")
        st.write(f"Selected Plan Price: **Rs {get_plan_price(selected_purchase_plan)}**")
        trx_id_input = st.text_input("Transaction ID / TID")
        proof_file = st.file_uploader("Payment Screenshot Upload Karain", type=["png", "jpg", "jpeg"])

        if st.button("📩 Submit Payment Request", use_container_width=True):
            trx_id_input = trx_id_input.strip()
            if trx_id_input == "":
                st.error("Transaction ID zaroor likhain.")
            elif is_duplicate_trx(used_trx, trx_id_input):
                st.error("Ye transaction ID pehle se use ho chuki hai.")
            else:
                proof_path = save_uploaded_payment_proof(proof_file, current_user)
                new_request = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "username": current_user,
                    "plan": selected_purchase_plan,
                    "credits": get_plan_words(selected_purchase_plan),
                    "price": get_plan_price(selected_purchase_plan),
                    "trx_id": trx_id_input,
                    "proof_path": proof_path,
                    "status": "Pending",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                used_trx.append(new_request)
                save_trx(used_trx)
                st.success("Payment request submit ho gai. Admin approve karega to credits add ho jayenge.")

    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.subheader("🎙️ Voice Generator")

    lang_choice = st.selectbox("Zubaan Select Karain (Select Language):", ["Urdu (Pakistan)", "English (US/UK)", "Punjabi (India/Pak)", "Arabic"])

    if lang_choice == "Urdu (Pakistan)":
        text_placeholder = "Yahan Urdu likhein ya keyboard ka Mic on kar ke bolain..."
        voice_options = {"Asad (Male)": "ur-PK-AsadNeural", "Uzma (Female)": "ur-PK-UzmaNeural"}
    elif lang_choice == "English (US/UK)":
        text_placeholder = "Type your English text here..."
        voice_options = {
            "Guy (Male)": "en-US-GuyNeural",
            "Jenny (Female)": "en-US-JennyNeural",
            "Aria (Female)": "en-US-AriaNeural",
            "Ryan UK (Male)": "en-GB-RyanNeural",
            "Sonia UK (Female)": "en-GB-SoniaNeural"
        }
    elif lang_choice == "Punjabi (India/Pak)":
        text_placeholder = "Yahan Punjabi text likho..."
        voice_options = {"Ojas (Male)": "pa-IN-OjasNeural", "Vaani (Female)": "pa-IN-VaaniNeural"}
    else:
        text_placeholder = "Uktub al-nas huna..."
        voice_options = {"Hamed (Male)": "ar-SA-HamedNeural", "Zariyah (Female)": "ar-SA-ZariyahNeural"}

    st.info("💡 Voice Typing: Mobile keyboard ka mic daba kar bolain. Laptop par Windows Key + H daba kar bol sakte hain.")
    user_text = st.text_area("Apna Text Yahan Likhein ya Bolain:", placeholder=text_placeholder, height=170)
    voice_name = st.selectbox("Aawaz (Voice Character):", list(voice_options.keys()))

    st.write("---")
    st.subheader("🎛️ Voice Changer Controls")
    col_speed, col_pitch = st.columns(2)
    with col_speed:
        speed_val = st.slider("Speed Control (Tezi)", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
    with col_pitch:
        pitch_val = st.slider("Pitch Control (Aawaz Bhari ya Bareek - Hz)", min_value=-20, max_value=20, value=0, step=1)

    speed_percent = int((speed_val - 1) * 100)
    speed_string = f"+{speed_percent}%" if speed_percent >= 0 else f"{speed_percent}%"
    pitch_string = f"+{pitch_val}Hz" if pitch_val >= 0 else f"{pitch_val}Hz"

    if st.button("🔥 Generate Professional Voice", use_container_width=True):
        current_word_count = len(user_text.split())
        words_used = safe_int(user_data.get("words_used", 0), 0)
        total_allowed = safe_int(user_data.get("total_allowed", DEFAULT_TOTAL_ALLOWED), DEFAULT_TOTAL_ALLOWED)

        if not user_text.strip():
            st.error("Meharbani kar ke pehle text likhain!")
        elif words_used + current_word_count > total_allowed:
            st.error("⚠️ Aap ka credits/words limit khatam ho chuki hai! Naya plan buy karain.")
            show_plan_cards()
            show_payment_details()
        else:
            with st.spinner("F.M AI Studio me audio ban rahi hai..."):
                output_file = "generated_studio_voice.mp3"
                if os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                    except Exception:
                        pass
                try:
                    async def make_voice():
                        communicate = Communicate(
                            text=user_text.strip(),
                            voice=voice_options[voice_name],
                            rate=speed_string,
                            pitch=pitch_string
                        )
                        await communicate.save(output_file)

                    asyncio.run(make_voice())

                    if os.path.exists(output_file):
                        user_data["words_used"] = words_used + current_word_count
                        db[current_user] = user_data
                        save_db(db)
                        st.success("🎉 Audio kamyabi se tayar ho chuki hai!")
                        with open(output_file, "rb") as f:
                            st.session_state.generated_audio = f.read()
                    else:
                        st.error("Audio file create nahi hui. Dobara try karein.")
                except Exception as e:
                    st.error("⚠️ Zubaan aur Character match nahi huay! Dono ko same rakhain.")
                    st.code(str(e))

    if st.session_state.generated_audio is not None:
        st.write("---")
        st.audio(st.session_state.generated_audio, format="audio/mp3")
        st.download_button(
            label="⬇️ Download Professional MP3 File",
            data=st.session_state.generated_audio,
            file_name="fm_ai_studio_voice.mp3",
            mime="audio/mp3",
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">Powered by F.M AI Studio • Professional AI Voice Generator</div>', unsafe_allow_html=True)
