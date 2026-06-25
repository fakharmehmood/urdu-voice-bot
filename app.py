import streamlit as st
import asyncio
from edge_tts import Communicate
import os

# Page configurations
st.set_page_config(page_title="Multi-Language Voice Studio Pro", page_icon="🎙️", layout="centered")

# Initialize word counter in user's browser session
if "words_used" not in st.session_state:
    st.session_state.words_used = 0

FREE_LIMIT = 10000
words_left = max(0, FREE_LIMIT - st.session_state.words_used)

st.title("🎙️ International Voiceover Studio Pro")
st.write("Apna Text likhein aur professional AI voiceover download karain (Urdu & English).")

# --- SIDEBAR: Payment & Account Details ---
st.sidebar.title("💎 Premium Subscription")
st.sidebar.write(f"**Free Words Left:** {words_left:,} / {FREE_LIMIT:,}")

# Word progress bar
progress = min(1.0, st.session_state.words_used / FREE_LIMIT)
st.sidebar.progress(progress)

st.sidebar.markdown("---")
st.sidebar.subheader("🚀 Upgrade to Unlimited")
st.sidebar.write("Life-time unlimited access ke liye niche diye gaye accounts par **Rs. 500** send karain:")

st.sidebar.info("""
🏦 **EasyPaisa Account:**
* **No:** 0304-7149419
* **Name:** Fakhar Mehmood

📱 **JazzCash Account:**
* **No:** 0304-7149419
* **Name:** Fakhar Mehmood
""")

st.sidebar.warning("Paise bhejney ke baad apni **Transaction ID (TrxID)** aur Email hamare WhatsApp (0304-7149419) par send karain!")

# --- MAIN INTERFACE ---
# Language Selection
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

# Calculate words in current text
current_word_count = len(user_text.split()) if user_text.strip() else 0
st.write(f"✍️ Total Words: **{current_word_count}**")

col1, col2, col3 = st.columns(3)

with col1:
    voice_selection = st.selectbox("Aawaz (Select Voice):", list(voice_options.keys()))

with col2:
    speed = st.slider("Raftaar (Speed):", min_value=0.5, max_value=1.5, value=1.0, step=0.1)

with col3:
    pitch = st.slider("Bhari-pan (Pitch):", min_value=-50, max_value=50, value=0, step=10, help="Minus (-) se aawaz bhari hogi, Plus (+) se patli hogi.")

# Technical configuration mapping
voice_name = voice_options[voice_selection]
speed_string = f"{'+' if speed >= 1.0 else ''}{int((speed - 1.0) * 100)}%"
pitch_string = f"{'+' if pitch >= 0 else ''}{pitch}Hz"

st.markdown("---")

# Check if user has exceeded the limit
if st.session_state.words_used + current_word_count > FREE_LIMIT:
    st.error("❌ Aap ki 10,000 free words ki limit khatam ho chuki hai! Premium account activate karwayein.")
    st.button("Generate Audio 🔥", disabled=True, use_container_width=True)
else:
    if st.button("Generate Audio 🔥", use_container_width=True):
        if not user_text.strip():
            st.error("Meharbani kar ke pehle kuch text likhein!")
        else:
            with st.spinner("AI Professional Voiceover Taiyar Ho Raha Hai..."):
                output_file = "generated_studio_voice.mp3"
                
                # Deleting old file if exists to avoid caching bugs
                if os.path.exists(output_file):
                    os.remove(output_file)
                
                async def make_voice():
                    communicate = Communicate(user_text.strip(), voice_name, rate=speed_string, pitch=pitch_string)
                    await communicate.save(output_file)
                
                asyncio.run(make_voice())
                
                if os.path.exists(output_file):
                    # Update word counter safely
                    st.session_state.words_used += current_word_count
                    
                    st.success("🎉 Kamyabi! Aap ki professional audio taiyar hai.")
                    
                    # Play Audio
                    with open(output_file, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    # Download Button
                    st.download_button(
                        label="📥 Download Professional MP3",
                        data=audio_bytes,
                        file_name="premium_voiceover.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
