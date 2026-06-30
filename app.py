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
    "Free Starter": {
        "words": 5000,
        "price": 0,
        "description": "Free trial credits"
    },
    "Plan 1": {
        "words": 100000,
        "price": 70,
        "description": "30 Day - 80 to 100 mint audio approx"
    },
    "Plan 2": {
        "words": 200000,
        "price": 137,
        "description": "30 Day - 166 to 200 mint audio approx"
    },
    "Plan 3": {
        "words": 300000,
        "price": 205,
        "description": "30 Day - 250 to 300 mint audio approx"
    },
    "Plan 4": {
        "words": 400000,
        "price": 273,
        "description": "30 Day - 160 to 450 mint audio approx"
    },
    "Plan 5": {
        "words": 500000,
        "price": 337,
        "description": "30 Day - 350 to 500 mint audio approx"
    },
    "Plan 6": {
        "words": 1000000,
        "price": 666,
        "description": "30 Day - 833 to 1000 mint audio approx"
    },
    "Plan 7": {
        "words": 5000000,
        "price": 2970,
        "description": "30 Day - 4166 to 5000 mint audio approx"
    },
    "Plan 8": {
        "words": 10000000,
        "price": 4950,
        "description": "30 Day - 8333 to 10000 mint audio approx"
    }
}


st.set_page_config(
    page_title="F.M AI Studio - Portal",
    page_icon="🎙️",
    layout="wide"
)


# =========================
# SMALL HELPER FUNCTIONS
# =========================

def safe_int(value, default=0):
    try:
        return int(value)
    except:
        return default


def format_number(value):
    try:
        return f"{int(value):,}"
    except:
        return str(value)


def get_plan_words(plan_name):
    if plan_name in PLAN_CATALOG:
        return PLAN_CATALOG[plan_name]["words"]
    return DEFAULT_TOTAL_ALLOWED


def get_plan_price(plan_name):
    if plan_name in PLAN_CATALOG:
        return PLAN_CATALOG[plan_name]["price"]
    return 0


def show_payment_details():
    st.markdown(f"""
### 💳 Payment Details

**Easypaisa:** `{EASYPAISA_NUMBER}`  
**JazzCash:** `{JAZZCASH_NUMBER}`  
**Account Title:** `{ACCOUNT_TITLE}`  

Payment ke baad transaction ID aur screenshot submit karain.

[📲 WhatsApp Contact](https://wa.me/{WHATSAPP_NUMBER})
""")


def show_plan_table():
    st.markdown("### 📦 Available Plans")

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
    """
    Google Sheet se connection banata hai.
    Agar service_account.json missing ho ya error aaye to None return karega.
    """
    try:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            return None

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE,
            scope
        )

        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        ensure_sheet_headers(sheet)
        return sheet

    except:
        return None


def ensure_sheet_headers(sheet):
    headers = [
        "First Name",
        "Last Name",
        "Email",
        "Username",
        "Password",
        "Words Used",
        "Total Allowed",
        "Plan"
    ]

    try:
        first_row = sheet.row_values(1)

        if first_row != headers:
            if len(first_row) == 0:
                sheet.append_row(headers)
            else:
                sheet.update("A1:H1", [headers])

    except:
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
                words_used = safe_int(row.get("Words Used", 0), 0)
                total_allowed = safe_int(row.get("Total Allowed", DEFAULT_TOTAL_ALLOWED), DEFAULT_TOTAL_ALLOWED)

                db[username] = {
                    "first_name": str(row.get("First Name", "")),
                    "last_name": str(row.get("Last Name", "")),
                    "email": str(row.get("Email", "")),
                    "password": str(row.get("Password", "")),
                    "words_used": words_used,
                    "total_allowed": total_allowed,
                    "plan": str(row.get("Plan", DEFAULT_PLAN))
                }

        return db

    except:
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

    except:
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
        except:
            return {}

    return {}


def save_db_to_local(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


def load_db():
    """
    Pehle Google Sheet se users load karega.
    Agar Google Sheet connect na ho to local users_db.json use karega.
    """
    sheet_db = load_db_from_sheet()

    if sheet_db is not None:
        return sheet_db

    return load_db_from_local()


def save_db(db):
    """
    Local file mein bhi save karega.
    Google Sheet available hui to sheet mein bhi save karega.
    """
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
        except:
            return []

    return []


def save_trx(trx_list):
    with open(TRX_FILE, "w", encoding="utf-8") as f:
        json.dump(trx_list, f, indent=4, ensure_ascii=False)


def is_duplicate_trx(trx_list, trx_id):
    trx_id = trx_id.strip().lower()

    for trx in trx_list:
        if str(trx.get("trx_id", "")).strip().lower() == trx_id:
            return True

    return False


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

    except:
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
    st.title("🔐 F.M AI Studio - Portal")
    st.caption("Login karein ya new account banayein.")

    tab1, tab2, tab3 = st.tabs([
        "🔍 Sign In",
        "📝 Create Account",
        "🔄 Change Password"
    ])

    # -------------------------
    # LOGIN TAB
    # -------------------------
    with tab1:
        st.subheader("Sign In To Your Account")

        user_input = st.text_input("Username", key="login_user")
        pass_input = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login 🔥", use_container_width=True):
            user_input = user_input.strip()

            # Admin Login
            if user_input == ADMIN_USERNAME and pass_input == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.username = ADMIN_USERNAME
                st.session_state.is_admin = True
                st.success("Admin Panel mein welcome!")
                st.rerun()

            # Normal User Login
            elif user_input in db and db[user_input].get("password", "") == pass_input:
                st.session_state.logged_in = True
                st.session_state.username = user_input
                st.session_state.is_admin = False
                st.success(f"Welcome back {user_input}!")
                st.rerun()

            else:
                st.error("Ghalat username ya password! Dobara koshish karein.")

    # -------------------------
    # CREATE ACCOUNT TAB
    # -------------------------
    with tab2:
        st.subheader("Create New Account")

        f_name = st.text_input("First Name", key="reg_fname")
        l_name = st.text_input("Last Name", key="reg_lname")
        email = st.text_input("Email", key="reg_email")
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")

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

    # -------------------------
    # CHANGE PASSWORD TAB
    # -------------------------
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


else:
    # =========================
    # ADMIN DASHBOARD
    # =========================

    if st.session_state.get("is_admin", False):
        st.title("🛠️ Admin Dashboard - F.M AI Studio")
        st.success("Aap admin account se login hain.")

        total_users = len(db)
        total_pending = len([x for x in used_trx if x.get("status") == "Pending"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Users", total_users)

        with col2:
            st.metric("Pending Payments", total_pending)

        with col3:
            st.metric("Total Transactions", len(used_trx))

        st.write("---")

        admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
            "👥 Users Management",
            "💳 Payment Requests",
            "📦 Plans",
            "⚙️ Admin Info"
        ])

        # -------------------------
        # USERS MANAGEMENT
        # -------------------------
        with admin_tab1:
            st.subheader("👥 Users Management")

            if len(db) == 0:
                st.warning("Abhi koi user create nahi hua.")
            else:
                selected_user = st.selectbox("User select karo:", list(db.keys()))
                selected_data = db[selected_user]

                st.write(f"### Selected User: {selected_user}")

                col_a, col_b = st.columns(2)

                with col_a:
                    new_first_name = st.text_input(
                        "First Name",
                        value=selected_data.get("first_name", "")
                    )

                    new_email = st.text_input(
                        "Email",
                        value=selected_data.get("email", "")
                    )

                    new_plan = st.selectbox(
                        "Plan Name",
                        list(PLAN_CATALOG.keys()),
                        index=list(PLAN_CATALOG.keys()).index(
                            selected_data.get("plan", DEFAULT_PLAN)
                        ) if selected_data.get("plan", DEFAULT_PLAN) in PLAN_CATALOG else 0
                    )

                with col_b:
                    new_last_name = st.text_input(
                        "Last Name",
                        value=selected_data.get("last_name", "")
                    )

                    new_password = st.text_input(
                        "User Password",
                        value=selected_data.get("password", "")
                    )

                    new_total_allowed = st.number_input(
                        "Total Allowed Words / Credits",
                        min_value=0,
                        value=safe_int(selected_data.get("total_allowed", DEFAULT_TOTAL_ALLOWED), DEFAULT_TOTAL_ALLOWED),
                        step=1000
                    )

                new_words_used = st.number_input(
                    "Used Words",
                    min_value=0,
                    value=safe_int(selected_data.get("words_used", 0), 0),
                    step=100
                )

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

        # -------------------------
        # PAYMENT REQUESTS
        # -------------------------
        with admin_tab2:
            st.subheader("💳 Payment Requests")

            pending_requests = [trx for trx in used_trx if trx.get("status") == "Pending"]

            if len(pending_requests) == 0:
                st.info("Abhi koi pending payment request nahi hai.")

            else:
                request_labels = []

                for trx in pending_requests:
                    label = f"{trx.get('username')} | {trx.get('plan')} | {trx.get('trx_id')} | Rs {trx.get('price')}"
                    request_labels.append(label)

                selected_label = st.selectbox("Pending request select karo:", request_labels)
                selected_index = request_labels.index(selected_label)
                selected_trx = pending_requests[selected_index]

                st.write("### Request Details")
                st.json(selected_trx)

                proof_path = selected_trx.get("proof_path", "")

                if proof_path and os.path.exists(proof_path):
                    st.info(f"Payment proof file saved: {proof_path}")
                    try:
                        st.image(proof_path, caption="Payment Screenshot", use_container_width=True)
                    except:
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

        # -------------------------
        # PLANS
        # -------------------------
        with admin_tab3:
            show_plan_table()
            st.write("---")
            show_payment_details()

        # -------------------------
        # ADMIN INFO
        # -------------------------
        with admin_tab4:
            st.subheader("⚙️ Admin Login Info")

            st.warning("Ye info sirf testing ke liye hai. Deploy karne se pehle password strong kar lena.")

            st.code(f"""
Admin Username: {ADMIN_USERNAME}
Admin Password: {ADMIN_PASSWORD}
""")

            st.write("---")
            st.subheader("Google Sheet Info")
            st.info(f"Google Sheet ka naam: {SHEET_NAME}")

            st.markdown("""
Agar Google Sheet use karni hai to:

1. Google Sheet ka naam **VoiceBotUsers** rakho.
2. `service_account.json` mein jo `client_email` hai usko copy karo.
3. Google Sheet open karo.
4. Share button dabao.
5. `client_email` paste karo.
6. Permission **Editor** select karo.
7. Share kar do.
""")

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
    remaining_words = total_allowed - words_used

    # -------------------------
    # SIDEBAR
    # -------------------------
    with st.sidebar:
        st.title("💙 Membership Dashboard")

        st.write(f"User: **{current_user.upper()}**")
        st.write(f"Plan: **{user_data.get('plan', DEFAULT_PLAN)}**")

        st.info(f"📄 Total Allowed Words: {format_number(total_allowed)}")
        st.success(f"📈 Used Words: {format_number(words_used)}")
        st.warning(f"🟡 Remaining Words: {format_number(remaining_words)}")

        st.write("---")
        st.subheader("💳 New Plan Purchase")

        st.markdown(f"""
**Easypaisa:** `{EASYPAISA_NUMBER}`  
**JazzCash:** `{JAZZCASH_NUMBER}`  
**Account Title:** `{ACCOUNT_TITLE}`  

Payment ke baad screenshot aur transaction ID submit karain.
""")

        st.markdown(f"[📲 WhatsApp Contact](https://wa.me/{WHATSAPP_NUMBER})")

        if user_data.get("plan") in ["Plan 6", "Plan 7", "Plan 8", "VIP Owner"]:
            st.write("---")
            st.markdown("### 🎁 Premium Canva Pro Link")
            st.markdown("[Free Canva Pro Link](https://www.canva.com/)")

        st.write("---")
        st.subheader("Hi Dolat Nagar e Services")

        st.markdown("""
**Aslam O Alaikum Sir,**

* 11 Lab text to speech & minimax Clone Available
* Capcut for PC
* Private Capcut for mobile
* Canva Pro yearly offer
""")

        st.write("---")

        if st.button("🚪 Logout Account", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.is_admin = False
            st.session_state.generated_audio = None
            st.rerun()

    # -------------------------
    # MAIN INTERFACE
    # -------------------------
    st.title("🎙️ Urdu Professional Voice Bot")
    st.caption("Urdu text ko professional AI voice mein convert karain.")

    # -------------------------
    # PLANS & PAYMENT SECTION
    # -------------------------
    with st.expander("📦 Plans & Payment Details", expanded=False):
        show_plan_table()
        st.write("---")
        show_payment_details()

    with st.expander("💳 Payment Submit / Plan Upgrade Request", expanded=False):
        st.info("Payment karne ke baad yahan transaction ID aur screenshot submit karain. Admin approve karega to credits add ho jayenge.")

        selected_purchase_plan = st.selectbox(
            "Kaunsa plan purchase karna hai?",
            [p for p in PLAN_CATALOG.keys() if p != "Free Starter"]
        )

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

    st.write("---")

    lang_choice = st.selectbox(
        "Zubaan Select Karain (Select Language):",
        [
            "Urdu (Pakistan)",
            "English (US/UK)",
            "Punjabi (India/Pak)",
            "Arabic"
        ]
    )

    # -------------------------
    # LANGUAGE SETTINGS
    # -------------------------
    if lang_choice == "Urdu (Pakistan)":
        text_placeholder = "Yahan Urdu likhein ya keyboard ka Mic on kar ke bolain..."
        voice_options = {
            "Asad (Male)": "ur-PK-AsadNeural",
            "Uzma (Female)": "ur-PK-UzmaNeural"
        }

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
        voice_options = {
            "Ojas (Male)": "pa-IN-OjasNeural",
            "Vaani (Female)": "pa-IN-VaaniNeural"
        }

    else:
        text_placeholder = "Uktub al-nas huna..."
        voice_options = {
            "Hamed (Male)": "ar-SA-HamedNeural",
            "Zariyah (Female)": "ar-SA-ZariyahNeural"
        }

    st.info("💡 Voice Typing: Mobile keyboard ka mic daba kar bolain. Laptop par Windows Key + H daba kar bol sakte hain.")

    user_text = st.text_area(
        "Apna Text Yahan Likhein ya Bolain:",
        placeholder=text_placeholder,
        height=150
    )

    voice_name = st.selectbox(
        "Aawaz (Voice Character):",
        list(voice_options.keys())
    )

    # -------------------------
    # VOICE CHANGER OPTIONS
    # -------------------------
    st.write("---")
    st.subheader("🎛️ Voice Changer Controls")

    speed_val = st.slider(
        "Speed Control (Tezi)",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1
    )

    pitch_val = st.slider(
        "Pitch Control (Aawaz Bhari ya Bareek - Hz)",
        min_value=-20,
        max_value=20,
        value=0,
        step=1
    )

    speed_percent = int((speed_val - 1) * 100)

    if speed_percent >= 0:
        speed_string = f"+{speed_percent}%"
    else:
        speed_string = f"{speed_percent}%"

    if pitch_val >= 0:
        pitch_string = f"+{pitch_val}Hz"
    else:
        pitch_string = f"{pitch_val}Hz"

    # -------------------------
    # GENERATE AUDIO
    # -------------------------
    if st.button("🔥 Generate Professional Voice", use_container_width=True):
        current_word_count = len(user_text.split())

        words_used = safe_int(user_data.get("words_used", 0), 0)
        total_allowed = safe_int(user_data.get("total_allowed", DEFAULT_TOTAL_ALLOWED), DEFAULT_TOTAL_ALLOWED)

        if not user_text.strip():
            st.error("Meharbani kar ke pehle text likhain!")

        elif words_used + current_word_count > total_allowed:
            st.error("⚠️ Aap ka credits/words limit khatam ho chuki hai! Naya plan buy karain.")

            show_plan_table()
            show_payment_details()

        else:
            with st.spinner("F.M AI Studio me audio ban rahi hai..."):
                output_file = "generated_studio_voice.mp3"

                if os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                    except:
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

    # -------------------------
    # AUDIO PLAYER & DOWNLOAD
    # -------------------------
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
