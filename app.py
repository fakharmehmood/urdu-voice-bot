import streamlit as st
import asyncio
from edge_tts import Communicate
import os
import json

# Page configurations
st.set_page_config(page_title="F.M AI Voiceover & Voice Changer", page_icon="🎙️", layout="centered")

DB_FILE = "users_db.json"
TRX_FILE = "used_trx.json"

# Load / Save Users Database
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {
        "admin": {"password": "admin786", "words_used": 0, "total_allowed": 9999999, "plan": "VIP Owner"},
        "guest": {"password": "guest", "words_used": 0, "total_allowed": 10000, "plan": "Free Trial"}
    }

def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

# Load / Save Used Transaction IDs (To prevent double usage)
def load_trx():
    if os.path.exists(TRX_FILE):
        with open(TRX_FILE, "r") as f: return json.load(f)
    return []

def save_trx(trx_list):
    with open(TRX_FILE, "w") as f: json.dump(trx_list, f, indent=4)

db = load_db()
used_trx = load_trx()

# --- LOGIN, SIGNUP & PASSWORD CHANGE CONTROLLER ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 F.M AI Studio - Portal")
    
    tab1, tab2, tab3 = st.tabs(["🔑 Sign In", "📝 Create Account", "🔄 Change Password"])
    
    with tab1:
        username_input = st.text_input("Username (Sign In):").strip().lower()
        password_input = st.text_input("Password (Sign In):", type="password").strip()
        if st.button("Login 🔥", use_container_width=True):
            if username_input in db and db[username_input]["password"] == password_input:
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.success("🎉 Welcome Back!")
                st.rerun()
            else:
                st.error("❌ Galat Username ya Password!")
                
    with tab2:
        new_user = st.text_input("Naya Username Chunyein:").strip().lower()
        new_pass = st.text_input("Naya Password Banayein:", type="password").strip()
        if st.button("Register & Get 10,000 Free Words 🚀", use_container_width=True):
            if not new_user or not new_pass:
                st.error("Dono khane pur karain!")
            elif new_user in db:
                st.error("Yeh Username pehle se maujood hai!")
            else:
                db[new_user] = {"password": new_pass, "words_used": 0, "total_allowed": 10000, "plan": "Free Trial"}
                save_db(db)
                st.success("🎉 Account ban gaya! Ab 'Sign In' se login karain.")

    with tab3:
        st.subheader("Apna Password Badlein")
        chg_user = st.text_input("Apna Username Likhein:").strip().lower()
        old_pass = st.text_input("Purana Password Likhein:", type="password").strip()
        new_pass_1 = st.text_input("Naya Password Likhein:", type="password").strip()
        
        if st.button("Password Update Karain 🔄", use_container_width=True):
            if chg_user in db and db[chg_user]["password"] == old_pass:
                if new_pass_1:
                    db[chg_user]["password"] = new_pass_1
                    save_db(db)
                    st.success("💪 Password kamyabi se badal gaya hai! Ab naye password se login karain.")
                else:
                    st.error("Naya password khali nahi ho sakta!")
            else:
                st.error("❌ Username ya Purana Password galat hai!")
    st.stop()

# --- POST-LOGIN LOGIC ---
current_user = st.session_state.username
user_data = db[current_user]
words_left = max(0, user_data["total_allowed"] - user_data["words_used"])

st.title("🎙️ F.M AI Voiceover & Voice Changer")
st.write(f"User: **{current_user.upper()}** | Plan: **{user_data['plan']}**")

# --- SIDEBAR: AUTO PAYMENT SYSTEM ---
st.sidebar.title("💎 Membership Dashboard")
if "VIP" in user_data["plan"] or "Monthly Pro" in user_data["plan"]:
    st.sidebar.success("♾️ Unlimited Access Active")
else:
    st.sidebar.write(f"**Remaining Words:** {words_left:,} / {user_data['total_allowed']:,}")
    st.sidebar.progress(min(1.0, user_data["words_used"] / user_data["total_allowed"]))

st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Automatic Packages Activation")
st.sidebar.write("""
1. **Basic Starter (100k words):** Rs. 150
2. **Standard Creator (200k words):** Rs. 250
3. **Mega Script (300k words):** Rs. 400
4. **Commercial Monthly Pro (Unlimited):** Rs. 1,500
""")

st.sidebar.info("🏦 **EasyPaisa / JazzCash:**\n* **No:** 0304-7149419\n* **Name:** Fakhar Mehmood")

# --- INSTANT AUTOMATIC PAYMENT GATEWAY ---
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Auto-Activate Via TrxID")
selected_plan = st.sidebar.selectbox("Kaun sa plan buy kiya h?", ["Basic Starter (Rs.150)", "Standard Creator (Rs.250)", "Mega Script (Rs.400)", "Commercial Monthly Pro (Rs.1500)"])
user_trx = st.sidebar.text_input("EasyPaisa/JazzCash ki TrxID likhein:", placeholder="e.g. 40123456789").strip()

if st.sidebar.button("Verify & Activate Instant 🔥"):
    if not user_trx:
        st.sidebar.error("Pehle Transaction ID (TrxID) likhein!")
    elif user_trx in used_trx:
        st.sidebar.error("❌ Yeh TrxID pehle se istemal ho chuki hai!")
    elif len(user_trx) < 10:
        st.sidebar.error("❌ TrxID invalid hai (Bohat choti hai)!")
    else:
        # Secret promo code override for owner testing
        if user_trx == "DNL786":
            user_data["total_allowed"] = 9999999
            user_data["plan"] = "VIP Owner"
            save_db(db)
            st.sidebar.success("🎉 VIP Active!")
            st.rerun()
            
        # Automatic allocation based on selection
        used_trx.append(user_trx)
        save_trx(used_trx)
        
        if "Rs.150" in selected_plan:
            user_data["total_allowed"] += 100000
            user_data["plan"] = "Basic Starter"
        elif "Rs.250" in selected_plan:
            user_data["total_allowed"] += 200000
            user_data["plan"] = "Standard Creator"
        elif "Rs.400" in selected_plan:
            user_data["total_allowed"] += 300000
            user_data["plan"] = "Mega Script"
        elif "Rs.1500" in selected_plan:
            user_data["plan"] = "Commercial Monthly Pro (Unlimited)"
            user_data["total_allowed"] = 9999999

        save_db(db)
        st.sidebar.success(f"🎉 Shukriya! Aap ka '{selected_plan}' instant automatic active ho gaya hai.")
        st.rerun()

if st.sidebar.button("🚪 Logout Account"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# --- MAIN ENGINE LOGIC ---
lang_choice = st.selectbox(
    "Zubaan Select Karain (Select Language):",
    ("Urdu (Pakistan)", "English (US/UK)", "Punjabi (India/Pak)", "Arabic (Saudi Arabia)", "Hindi (India)")
)

if lang_choice == "Urdu (Pakistan)":
    text_placeholder = "Yahan Urdu likhein ya keyboard ka Mic on kar ke bolain..."
    voice_options = {"Asad (Male)": "ur-PK-AsadNeural", "Uzma (Female)": "ur-PK-UzmaNeural", "Salman (Premium Male)": "ur-IN-SalmanNeural"}
elif lang_choice == "English (US/UK)":
    text_placeholder = "Type or dictate English text here..."
    voice_options = {"Ryan (Male - US)": "en-US-RyanNeural", "Sonia (Female - US)": "en-US-SoniaNeural", "Natasha (Female - UK)": "en-GB-NatashaNeural", "Mitchell (Male - UK)": "en-GB-MitchellNeural"}
elif lang_choice == "Punjabi (India/Pak)":
    text_placeholder = "ایتھے پنجابی لکھو یا بولو..."
    voice_options = {"Mandeep (Female Punjabi)": "pa-IN-MandeepNeural", "Gurpreet (Male Punjabi)": "pa-IN-GurpreetNeural"}
elif lang_choice == "Arabic (Saudi Arabia)":
    text_placeholder = "اكتب النص العربي هنا..."
    voice_options = {"Hamed (Male)": "ar-SA-HamedNeural", "Zariyah (Female)": "ar-SA-ZariyahNeural"}
else:
    text_placeholder = "यहाँ हिंदी टेक्स्ट लिखें..."
    voice_options = {"Madhur (Male)": "hi-IN-MadhurNeural", "Swara (Female)": "hi-IN-SwaraNeural"}

st.info("💡 **Voice Typing:** Mobile keyboard ka Mic daba kar bolain. Laptop par `Windows Key + H` dabra kar bolna shuru karain!")
user_text = st.text_area("Apna Text Yahan Likhein ya Bolain:", placeholder=text_placeholder, height=150)

if st.button("🪄 Auto-Clean & Fix Text"):
    if user_text.strip():
        user_text = " ".join(user_text.split())
        st.success("✨ Formatting bilkul durust kar di gayi hai!")

current_word_count = len(user_text.split()) if user_text.strip() else 0
st.write(f"✍️ Total Words: **{current_word_count}**")

# --- VOICE CHANGER SECTION ---
st.subheader("🎛️ AI Voice Changer Effects")
effect_choice = st.selectbox(
    "Aawaz Badlein:",
    ("Original Voice (Standard)", "Cartoon / Kid Voice (High Pitch)", "Deep Heavy Voice (Low Pitch)", "Horror / Ghost Voice (Super Low Pitch)", "Fast / Radio Voice (High Speed)")
)

if effect_choice == "Original Voice (Standard)": speed, pitch = 1.0, 0
elif effect_choice == "Cartoon / Kid Voice (High Pitch)": speed, pitch = 1.1, 40
elif effect_choice == "Deep Heavy Voice (Low Pitch)": speed, pitch = 0.9, -25
elif effect_choice == "Horror / Ghost Voice (Super Low Pitch)": speed, pitch = 0.8, -45
else: speed, pitch = 1.4, 15

col1, col2 = st.columns(2)
with col1: voice_selection = st.selectbox("Aawaz (Voice Character):", list(voice_options.keys()))
with col2: st.caption(f"🎯 Speed: {speed}x | Pitch: {pitch}Hz")

voice_name = voice_options[voice_selection]
speed_string = f"{'+' if speed >= 1.0 else ''}{int((speed - 1.0) * 100)}%"
pitch_string = f"{'+' if pitch >= 0 else ''}{pitch}Hz"

st.markdown("---")

# Limit Gates
is_limit_exceeded = False
if "Unlimited" not in user_data["plan"] and "VIP" not in user_data["plan"]:
    if user_data["words_used"] + current_word_count > user_data["total_allowed"]:
        is_limit_exceeded = True

if is_limit_exceeded:
    st.error("❌ Aap ki free trial limit khatam ho chuki hai! Agla kaam karne ke liye pehle niche TrxID dal kar automatic activate karain.")
    st.button("Generate Audio 🔥", disabled=True, use_container_width=True)
else:
    if st.button("Generate Audio 🔥", use_container_width=True):
        if not user_text.strip():
            st.error("Pehle kuch text input karain!")
        else:
            with st.spinner("F.M AI Studio Me Audio Ban Rahi Hai..."):
                output_file = "generated_studio_voice.mp3"
                if os.path.exists(output_file):
                    try: os.remove(output_file)
                    except: pass
                
                try:
                    async def make_voice():
                        communicate = Communicate(user_text.strip(), voice_name, rate=speed_string, pitch=pitch_string)
                        await communicate.save(output_file)
                    asyncio.run(make_voice())
                    
                    if os.path.exists(output_file):
                        user_data["words_used"] += current_word_count
                        save_db(db)
                        st.success("🎉 Audio kamyabi se tayar ho chuki hai!")
                        
                        with open(output_file, "rb") as f: audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        st.download_button(label="📥 Download Professional MP3", data=audio_bytes, file_name="fm_ai_voiceover.mp3", mime="audio/mp3", use_container_width=True)
                        st.rerun()
                except Exception as e:
                    st.error("⚠️ Zubaan aur Character Match Nahi Huay! Dono ko same rakhain!")
