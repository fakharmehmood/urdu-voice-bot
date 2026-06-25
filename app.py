import streamlit as st
import asyncio
from edge_tts import Communicate
import os
from datetime import datetime, timedelta

# Page configurations
st.set_page_config(page_title="Dolat Nagar Voice Studio Pro", page_icon="🎙️", layout="centered")

# --- INITIALIZE SESSION STATES ---
if "words_used" not in st.session_state:
    st.session_state.words_used = 0
if "total_allowed_words" not in st.session_state:
    st.session_state.total_allowed_words = 10000  # Default Free Limit
if "is_premium" not in st.session_state:
    st.session_state.is_premium = False
if "plan_type" not in st.session_state:
    st.session_state.plan_type = "Free Trial"

# Calculate remaining words
words_left = max(0, st.session_state.total_allowed_words - st.session_state.words_used)

st.title("🎙️ Dolat Nagar Voiceover Studio Pro")
st.write("Apna text paste karain aur premium quality AI voiceover download karain.")

# --- SIDEBAR: PLANS & SUBSCRIPTION ---
st.sidebar.title("💎 Membership Dashboard")
st.sidebar.write(f"**Current Plan:** {st.session_state.plan_type}")

if st.session_state.plan_type == "Monthly Unlimited Pro":
    st.sidebar.success("♾️ Unlimited Access Active (Valid for 30 Days)")
else:
    st.sidebar.write(f"**Remaining Words:** {words_left:,} / {st.session_state.total_allowed_words:,}")
    progress = min(1.0, st.session_state.words_used / st.session_state.total_allowed_words)
    st.sidebar.progress(progress)

st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Pricing Plans / Packages")
st.sidebar.write("""
1. **Basic Starter:** 100,000 Words = **Rs. 150**
2. **Standard Creator:** 200,000 Words = **Rs. 250**
3. **Mega Script:** 300,000 Words = **Rs. 400**
4. **Monthly Unlimited Pro:** Unlimited = **Rs. 700** (30 Days)
""")

st.sidebar.info("""
🏦 **EasyPaisa / JazzCash:**
* **No:** 0304-7149419
* **Name:** Fakhar Mehmood
""")
st.sidebar.warning("Paise bhej kar **TrxID** aur screenshot WhatsApp (0304-7149419) par send karain.")

st.sidebar.markdown("---")
# --- PROMO CODE / FRIEND ACCESS FUNCTION ---
st.sidebar.subheader("🔑 Activate Package / Promo Code")
promo_input = st.sidebar.text_input("TrxID ya Promo Code likhein:", type="password")

if st.sidebar.button("Verify & Activate"):
    # Secret Friend Promo Code
    if promo_input == "DNL786":
        st.session_state.total_allowed_words = 1000000
        st.session_state.plan_type = "VIP Friend Free Access"
        st.sidebar.success("🎉 VIP Access Activated!")
        st.rerun()
    # Manual TrxID confirmations can be put here or handled via WhatsApp
    elif promo_input == "150_PLAN":
        st.session_state.total_allowed_words += 100000
        st.session_state.plan_type = "Basic Starter"
        st.rerun()
    elif promo_input == "700_PLAN":
        st.session_state.plan_type = "Monthly Unlimited Pro"
        st.rerun()
    else:
        st.sidebar.error("Invalid Code! WhatsApp par contact karain.")

# --- MAIN INTERFACE ---
language = st.radio("Zubaan Select Karain (Select Language):", ("Urdu", "English"), horizontal=True)

if language == "Urdu":
    text_placeholder = "Yahan apna Urdu text paste karain..."
    voice_options = {
        "Asad (Male)": "ur-PK-AsadNeural",
        "Uzma (Female)": "ur-PK-UzmaNeural",
        "Salman (Male Premium)": "ur-IN-SalmanNeural"
    }
else:
    text_placeholder = "Enter your English text here..."
    voice_options = {
        "Ryan (Male - US)": "en-US-RyanNeural",
        "Sonia (Female - US)": "en-US-SoniaNeural",
        "Mitchell (Male - UK)": "en-GB-MitchellNeural",
        "Natasha (Female - UK)": "en-GB-NatashaNeural"
    }

user_text = st.text_area("Text Yahan Likhein:", placeholder=text_placeholder, height=150)
current_word_count = len(user_text.split()) if user_text.strip() else 0
st.write(f"✍️ Total Words in Text: **{current_word_count}**")

col1, col2, col3 = st.columns(3)
with col1:
    voice_selection = st.selectbox("Aawaz (Select Voice):", list(voice_options.keys()))
with col2:
    speed = st.slider("Raftaar (Speed):", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
with col3:
    pitch = st.slider("Bhari-pan (Pitch):", min_value=-50, max_value=50, value=0, step=10)

voice_name = voice_options[voice_selection]
speed_string = f"{'+' if speed >= 1.0 else ''}{int((speed - 1.0) * 100)}%"
pitch_string = f"{'+' if pitch >= 0 else ''}{pitch}Hz"

st.markdown("---")

# Check Word Limits
is_limit_exceeded = False
if st.session_state.plan_type != "Monthly Unlimited Pro":
    if st.session_state.words_used + current_word_count > st.session_state.total_allowed_words:
        is_limit_exceeded = True

if is_limit_exceeded:
    st.error("❌ Aap ki free words ki limit khatam ho chuki hai! Meharbani kar ke Package buy karain ya apna TrxID activate karain.")
    st.button("Generate Audio 🔥", disabled=True, use_container_width=True)
else:
    if st.button("Generate Audio 🔥", use_container_width=True):
        if not user_text.strip():
            st.error("Pehle kuch text likhein!")
        else:
            with st.spinner("AI Professional Voiceover Taiyar Ho Raha Hai..."):
                output_file = "generated_studio_voice.mp3"
                
                if os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                    except:
                        pass
                
                async def make_voice():
                    communicate = Communicate(user_text.strip(), voice_name, rate=speed_string, pitch=pitch_string)
                    await communicate.save(output_file)
                
                asyncio.run(make_voice())
                
                if os.path.exists(output_file):
                    st.session_state.words_used += current_word_count
                    st.success("🎉 Kamyabi! Aap ki professional audio taiyar hai.")
                    
                    with open(output_file, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    st.download_button(
                        label="📥 Download Professional MP3",
                        data=audio_bytes,
                        file_name="premium_voiceover.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
