import streamlit as st
import asyncio
from edge_tts import Communicate
import os
import json

# Page configurations
st.set_page_config(page_title="F.M AI Voiceover & Voice Changer", page_icon="🎙️", layout="centered")

DB_FILE = "users_db.json"

# Local Database Helper Functions
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    # Default admin/owner account initialized
    return {
        "admin": {"password": "admin786", "words_used": 0, "total_allowed": 9999999, "plan": "VIP Owner"},
        "guest": {"password": "guest", "words_used": 0, "total_allowed": 10000, "plan": "Free Trial"}
    }

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

# Initialize database
db = load_db()

# --- LOGIN & SIGNUP CONTROLLER ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 F.M AI Studio - Login / Register")
    st.write("Apna account login karain ya naya account banayein.")
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
    
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
                st.error("❌ Galat Username ya Password! Please check karain.")
                
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
                st.success("🎉 Account ban gaya! Ab 'Sign In' wale tab se login karain.")
    st.stop()

# --- POST-LOGIN USER VARIABLES ---
current_user = st.session_state.username
user_data = db[current_user]

words_left = max(0, user_data["total_allowed"] - user_data["words_used"])

# --- CORE APPLICATION INTERFACE ---
st.title("🎙️ F.M AI Voiceover & Voice Changer")
st.write(f"Khush-Amdeed **{current_user.upper()}**! Bol kar type karain aur professional effects download karain.")

# --- SIDEBAR: DASHBOARD & PACKAGES ---
st.sidebar.title("💎 Membership Dashboard")
st.sidebar.write(f"**Current Plan:** {user_data['plan']}")

if "VIP" in user_data["plan"] or "Monthly Pro" in user_data["plan"]:
    st.sidebar.success("♾️ Unlimited Access Active")
else:
    st.sidebar.write(f"**Remaining Words:** {words_left:,} / {user_data['total_allowed']:,}")
    st.sidebar.progress(min(1.0, user_data["words_used"] / user_data["total_allowed"]))

st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Premium Packages")
st.sidebar.write("""
1. **Basic Starter:** 100,000 Words = **Rs. 150**
2. **Standard Creator:** 200,000 Words = **Rs. 250**
3. **Mega Script:** 300,000 Words = **Rs. 400**
4. **Commercial Monthly Pro:** Unlimited = **Rs. 1,500** (30 Days)
""")

st.sidebar.info("🏦 **EasyPaisa / JazzCash:**\n* **No:** 0304-7149419\n* **Name:** Fakhar Mehmood")
st.sidebar.warning("TrxID niche box mein likh kar activate karain ya WhatsApp (0304-7149419) par send karain.")

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Activate Package / Promo Code")
promo_input = st.sidebar.text_input("TrxID ya Promo Code likhein:", type="password")

if st.sidebar.button("Verify & Activate"):
    if promo_input == "DNL786":
        user_data["total_allowed"] = 9999999
        user_data["plan"] = "VIP Owner"
        save_db(db)
        st.sidebar.success("🎉 VIP Access Activated!")
        st.rerun()
    elif promo_input == "150_PLAN":
        user_data["total_allowed"] += 100000
        user_data["plan"] = "Basic Starter"
        save_db(db)
        st.sidebar.success("🎉 1 Lakh words add ho chuke hain!")
        st.rerun()
    elif promo_input == "1500_PLAN":
        user_data["plan"] = "Commercial Monthly Pro (Unlimited)"
        save_db(db)
        st.sidebar.success("🎉 Monthly Pro Active!")
        st.rerun()
    else:
        st.sidebar.error("Invalid TrxID/Code! Please WhatsApp 0304-7149419.")

if st.sidebar.button("🚪 Logout Account"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# --- MAIN SOFTWARE LOGIC ---
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

st.info("💡 **Voice Typing (Bol kar likhna):** Mobile user keyboard ka Mic daba kar bolain. Laptop par `Windows Key + H` daba kar bolna shuru karain, system khud type karega!")
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
    "Aawaz Badlein (Select Voice Changer Effect):",
    ("Original Voice (Standard)", "Cartoon / Kid Voice (High Pitch)", "Deep Heavy Voice (Low Pitch)", "Horror / Ghost Voice (Super Low Pitch)", "Fast / Radio Voice (High Speed)")
)

if effect_choice == "Original Voice (Standard)":
    speed, pitch = 1.0, 0
elif effect_choice == "Cartoon / Kid Voice (High Pitch)":
    speed, pitch = 1.1, 40
elif effect_choice == "Deep Heavy Voice (Low Pitch)":
    speed, pitch = 0.9, -25
elif effect_choice == "Horror / Ghost Voice (Super Low Pitch)":
    speed, pitch = 0.8, -45
else:
    speed, pitch = 1.4, 15

col1, col2 = st.columns(2)
with col1:
    voice_selection = st.selectbox("Aawaz (Voice Character):", list(voice_options.keys()))
with col2:
    st.caption(f"🎯 Speed: {speed}x | Pitch: {pitch}Hz")

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
    st.error("❌ Aap ki free trial limit (10,000 words) khatam ho chuki hai! Agla kaam karne ke liye pehle fee pay karain aur upar box mein TrxID likh kar package active karain.")
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
                        save_db(db)  # Persist changes to file storage
                        st.success("🎉 Audio kamyabi se tayar ho chuki hai!")
                        
                        with open(output_file, "rb") as f:
                            audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        
                        st.download_button(
                            label="📥 Download Professional MP3",
                            data=audio_bytes,
                            file_name="fm_ai_voiceover.mp3",
                            mime="audio/mp3",
                            use_container_width=True
                        )
                        st.rerun()
                except Exception as e:
                    st.error("⚠️ **Zubaan aur Character Match Nahi Huay!**")
                    st.warning("Aap ne jo text likha hai woh aur select ki hui voice different zubaan ki hain. Dono ko same rakhain!")
