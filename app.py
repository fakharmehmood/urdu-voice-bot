import streamlit as st
import asyncio
from edge_tts import Communicate
import os

# Page configurations
st.set_page_config(page_title="Dolat Nagar Ai Voice Studio", page_icon="🎙️", layout="centered")

# --- INITIALIZE SESSION STATES ---
if "words_used" not in st.session_state:
    st.session_state.words_used = 0
if "total_allowed_words" not in st.session_state:
    st.session_state.total_allowed_words = 10000  # Free Limit
if "plan_type" not in st.session_state:
    st.session_state.plan_type = "Free Trial"

words_left = max(0, st.session_state.total_allowed_words - st.session_state.words_used)

st.title("🎙️ Dolat Nagar AI Voiceover & Voice Changer Studio")
st.write("Bol kar type karain, aawaz badlein (Voice Changer Effects) aur professional audio download karain.")

# --- SIDEBAR: PLANS & SUBSCRIPTION ---
st.sidebar.title("💎 Membership Dashboard")
st.sidebar.write(f"**Current Plan:** {st.session_state.plan_type}")

if "Unlimited" in st.session_state.plan_type or "VIP" in st.session_state.plan_type:
    st.sidebar.success("♾️ Unlimited Access Active")
else:
    st.sidebar.write(f"**Remaining Words:** {words_left:,} / {st.session_state.total_allowed_words:,}")
    st.sidebar.progress(min(1.0, st.session_state.words_used / st.session_state.total_allowed_words))

st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Premium Packages")
st.sidebar.write("""
1. **Basic Starter:** 100,000 Words = **Rs. 150**
2. **Standard Creator:** 200,000 Words = **Rs. 250**
3. **Mega Script:** 300,000 Words = **Rs. 400**
4. **Commercial Monthly Pro:** Unlimited = **Rs. 1,500** (30 Days)
""")

st.sidebar.info("🏦 **EasyPaisa / JazzCash:**\n* **No:** 0304-7149419\n* **Name:** Fakhar Mehmood")
st.sidebar.warning("TrxID niche box mein likh kar activate karain ya WhatsApp karain.")

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Activate Package / Promo Code")
promo_input = st.sidebar.text_input("TrxID ya Promo Code likhein:", type="password")

if st.sidebar.button("Verify & Activate"):
    if promo_input == "DNL786":
        st.session_state.total_allowed_words = 9999999
        st.session_state.plan_type = "VIP Owner Free Access"
        st.sidebar.success("🎉 VIP Access Activated!")
        st.rerun()
    elif promo_input == "1500_PLAN":
        st.session_state.plan_type = "Commercial Monthly Pro (Unlimited)"
        st.rerun()
    else:
        st.sidebar.error("Code invalid hai!")

# --- MAIN INTERFACE ---
# Language selection extending to 5 languages
lang_choice = st.selectbox(
    "Zubaan Select Karain (Select Language):",
    ("Urdu (Pakistan)", "English (US/UK)", "Punjabi (India/Pak)", "Arabic (Saudi Arabia)", "Hindi (India)")
)

# Configuration mapping for extended languages and characters
if lang_choice == "Urdu (Pakistan)":
    text_placeholder = "Yahan Urdu likhein ya niche Mic option on kar ke bolain..."
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

# --- ADVANCED MIC (VOICE TYPING) FUNCTION ---
st.subheader("🎤 Voice Typing / Speech to Text")
mic_active = st.toggle("Activate Microphone Guide / Voice Typing Helper")

if mic_active:
    st.success("🤖 **Voice Typing Enabled:** Agar aap Mobile use kar rahe hain to keyboard ka built-in Mic daba kar bolain. Agar Laptop use kar rahe hain to `Windows Key + H` (Mac par `Cmd + Space`) dabra kar bolna shuru karain, system khud hi type karta jayega!")

user_text = st.text_area("Apna Text Yahan Likhein ya Bolain:", placeholder=text_placeholder, height=150)

# Clean Text Function (Simple punctuation and spacing automatic handler)
if st.button("🪄 Auto-Clean & Fix Text (Alfaz Durust Karain)"):
    if user_text.strip():
        cleaned = " ".join(user_text.split())
        user_text = cleaned
        st.success("✨ System ne aap ke text ki formatting aur spacing bilkul durust kar di hai!")
    else:
        st.error("Pehle text area mein kuch likhein ya bolain!")

current_word_count = len(user_text.split()) if user_text.strip() else 0
st.write(f"✍️ Total Words: **{current_word_count}**")

# --- VOICE CHANGER EFFECTS SECTION ---
st.subheader("🎛️ AI Voice Changer & Speed Studio")
effect_choice = st.selectbox(
    "Aawaz Badlein (Select Voice Changer Effect):",
    ("Original Voice (Standard)", "Cartoon / Kid Voice (High Pitch)", "Deep Heavy Voice (Low Pitch)", "Horror / Ghost Voice (Super Low Pitch)", "Fast / Radio Voice (High Speed)")
)

# Custom adjustments based on Voice Changer Selection
if effect_choice == "Original Voice (Standard)":
    speed, pitch = 1.0, 0
elif effect_choice == "Cartoon / Kid Voice (High Pitch)":
    speed, pitch = 1.1, 40
elif effect_choice == "Deep Heavy Voice (Low Pitch)":
    speed, pitch = 0.9, -25
elif effect_choice == "Horror / Ghost Voice (Super Low Pitch)":
    speed, pitch = 0.8, -45
else: # Fast / Radio Voice
    speed, pitch = 1.4, 15

# Manual overrides fine-tuning sliders
col1, col2 = st.columns(2)
with col1:
    voice_selection = st.selectbox("Aawaz (Voice Character):", list(voice_options.keys()))
with col2:
    st.caption(f"🎯 Current Preset: **{effect_choice}** (Speed: {speed}x, Pitch: {pitch}Hz)")

voice_name = voice_options[voice_selection]
speed_string = f"{'+' if speed >= 1.0 else ''}{int((speed - 1.0) * 100)}%"
pitch_string = f"{'+' if pitch >= 0 else ''}{pitch}Hz"

st.markdown("---")

# Limit Checks
is_limit_exceeded = False
if "Unlimited" not in st.session_state.plan_type and "VIP" not in st.session_state.plan_type:
    if st.session_state.words_used + current_word_count > st.session_state.total_allowed_words:
        is_limit_exceeded = True

if is_limit_exceeded:
    st.error("❌ Aap ki free words ki limit khatam ho chuki hai! Bara-e-maherbani package active karwayein.")
    st.button("Generate Audio 🔥", disabled=True, use_container_width=True)
else:
    if st.button("Generate Audio 🔥", use_container_width=True):
        if not user_text.strip():
            st.error("Pehle kuch text input karain!")
        else:
            with st.spinner("AI Professional Voiceover Studio Me Audio Ban Rahi Hai..."):
                output_file = "generated_studio_voice.mp3"
                
                if os.path.exists(output_file):
                    try: os.remove(output_file)
                    except: pass
                
                # --- CRASH PROTECTION TRY-EXCEPT BLOCK ---
                try:
                    async def make_voice():
                        communicate = Communicate(user_text.strip(), voice_name, rate=speed_string, pitch=pitch_string)
                        await communicate.save(output_file)
                    
                    asyncio.run(make_voice())
                    
                    if os.path.exists(output_file):
                        st.session_state.words_used += current_word_count
                        st.success("🎉 Audio kamyabi se tayar ho chuki hai!")
                        
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
                except Exception as e:
                    st.error("⚠️ **Zubaan aur Character Match Nahi Huay!**")
                    st.warning(f"Aap ne jo text likha hai woh '{lang_choice}' ka hai jabki voice character koi aur chun liya hai. Meharbani kar ke upar select ki hui zubaan ke mutabiq hi aawaz (Voice character) select karain!")
