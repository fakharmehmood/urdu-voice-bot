import streamlit as st
import os
import json
import asyncio
from edge_tts import Communicate

# --- CONFIG & CONSTANTS ---
DB_FILE = "users_db.json"
TRX_FILE = "used_trx.json"

st.set_page_config(
    page_title="F.M AI Studio - Portal",
    page_icon="🎙️",
    layout="wide"
)

# --- DATABASE LOGIC ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "admin": {"password": "admin786", "words_used": 0, "total_allowed": 9999999, "plan": "VIP Owner"},
        "guest": {"password": "guest", "words_used": 0, "total_allowed": 10000, "plan": "Free Trial"}
    }

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def load_trx():
    if os.path.exists(TRX_FILE):
        with open(TRX_FILE, "r") as f:
            return json.load(f)
    return []

def save_trx(trx_list):
    with open(TRX_FILE, "w") as f:
        json.dump(trx_list, f, indent=4)

db = load_db()
used_trx = load_trx()

# --- SESSION STATE ---
if "generated_audio" not in st.session_state:
    st.session_state.generated_audio = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# --- LOGIN & SIGNUP CONTROLLER ---
if not st.session_state.logged_in:
    st.title("🔐 F.M AI Studio - Portal")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Sign In", "📝 Create Account", "🔄 Change Password"])
    
    with tab1:
        st.subheader("Sign In To Your Account")
        user_input = st.text_input("Username", key="login_user")
        pass_input = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login 🔥", use_container_width=True):
            if user_input in db and db[user_input]["password"] == pass_input:
                st.session_state.logged_in = True
                st.session_state.username = user_input
                st.success(f"Welcome back {user_input}!")
                st.rerun()
            else:
                st.error("Ghalat Username ya Password! Dobara koshish karain.")
                
    with tab2:
        st.subheader("Create New Account")
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register Account 🚀", use_container_width=True):
            if new_user in db:
                st.error("Yeh username pehle se majood hai!")
            elif new_user.strip() == "" or new_pass.strip() == "":
                st.error("Username aur Password khali nahi ho sakte!")
            else:
                db[new_user] = {"password": new_pass, "words_used": 0, "total_allowed": 5000, "plan": "Free Starter"}
                save_db(db)
                st.success("Account kamyabi se ban gaya! Ab Sign In karain.")

    with tab3:
        st.subheader("Change Password")
        c_user = st.text_input("Username", key="chg_user")
        old_pass = st.text_input("Old Password", type="password", key="chg_old")
        c_pass = st.text_input("New Password", type="password", key="chg_new")
        if st.button("Update Password 🔄", use_container_width=True):
            if c_user in db and db[c_user]["password"] == old_pass:
                db[c_user]["password"] = c_pass
                save_db(db)
                st.success("Password kamyabi se badal gaya!")
            else:
                st.error("Username ya Purana Password ghalat hai!")
else:
    # --- LOGGED IN USER CONTEXT ---
    current_user = st.session_state.username
    user_data = db[current_user]
    
    # --- SIDEBAR: NEW RATES & PACKAGES ---
    with st.sidebar:
        st.title("💎 Membership Dashboard")
        st.write(f"User: **{current_user.upper()}** | Plan: **{user_data['plan']}**")
        st.info(f"📋 Total Allowed Words: {user_data['total_allowed']}")
        st.success(f"📈 Used Words: {user_data['words_used']}")
        
        st.write("---")
        st.subheader("Hi Dolat Nagar e Services, welcome to AI TOOLS FLOW")
        st.markdown("""
        **Aslam O Alaikum Sir,**
        * 11 Lab text to speech & minimax Clone Available in **175**
        * Capcut for pc **500** single device(shared QR)
        * Private capcut for mobile and pc 2 device **800**
        
        🎁 **Free Canva pro yearly Offer:**
        *1 Million Credit lene par Canva yearly free Hasil krain!*
        """)
        
        st.write("---")
        st.markdown("### 📊 11LAB Text to speech only English")
        st.caption("⚠️ (ye access 11Lab official pay ni hmary portal pay mily ga)")
        
        plans_text = """
        **---Plan 1------**
        Credit : *1 lakh* | Price : *70*
        *30 Day , 80 to 100 Mint audio*
        
        **---Plan 2------**
        Credit : *2 lakh* | Price : *137*
        *30 Day , 166 to 200 Mint audio*
        
        **---Plan 3------**
        Credit : *3 lakh* | Price : *205*
        *30 Day , 250 to 300 Mint audio*
        
        **---Plan 4------**
        Credit : *4 lakh* | Price : *273*
        *30 Day , 160 to 450 Mint audio*
        
        **---Plan 5------**
        Credit : *5 lakh* | Price : *337*
        *30 Day , 350 to 500 Mint audio*
        
        **---Plan 6------**
        Credit : *10 lakh(1M)* | Price : *666*
        *30 Day , 833 to 1000 Mint audio*
        
        **---Plan 7------**
        Credit : *50 lakh(5M)* | Price : *2970*
        *30 Day , 4166 to 5000 Mint audio*
        
        **---Plan 8------**
        Credit : *100 lakh(10M)* | Price : *4950*
        *30 Day , 8333 to 10000 Mint audio*
        """
        st.markdown(plans_text)
        
        st.write("---")
        st.warning("""
        * Elevenlabs charge 3X On other(non English) Language 
        * Minimax voice cloning in All language charge 1.2x characters
        * *Test before purchase After purchase No refund. Issue will solve as soon as possible.*
        """)
        
        st.write("---")
        if st.button("🚪 Logout Account", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.generated_audio = None
            st.rerun()

    # --- MAIN INTERFACE ENGINE ---
    st.title("🎙️ Urdu Professional Voice Bot")
    st.caption("Urdu text ko professional AI voice mein convert karain.")
    
    lang_choice = st.selectbox(
        "Zubaan Select Karain (Select Language):",
        ["Urdu (Pakistan)", "English (US/UK)", "Punjabi (India/Pak)", "Arabic"]
    )
    
    # Language setups
    if lang_choice == "Urdu (Pakistan)":
        text_placeholder = "Yahan Urdu likhein ya keyboard ka Mic on kar ke bolain..."
        voice_options = {"Asad (Male)": "ur-PK-AsadNeural", "Uzma (Female)": "ur-PK-UzmaNeural"}
    elif lang_choice == "English (US/UK)":
        text_placeholder = "Type your English text here..."
        voice_options = {"Brian (Male)": "en-US-BrianNeural", "Emma (Female)": "en-US-EmmaNeural"}
    elif lang_choice == "Punjabi (India/Pak)":
        text_placeholder = "Yahan Punjabi text likho..."
        voice_options = {"Mandeep (Male)": "pa-IN-MandeepNeural"}
    else:
        text_placeholder = "Uktub al-nas huna..."
        voice_options = {"Hamed (Male)": "ar-SA-HamedNeural"}

    st.info("💡 **Voice Typing:** Mobile keyboard ka Mic daba kar bolain. Laptop par `Windows Key + H` dabra kar bolna shuru karain!")
    
    user_text = st.text_area("Apna Text Yahan Likhain ya Bolain:", placeholder=text_placeholder, height=150)
    voice_name = st.selectbox("Aawaz (Voice Character):", list(voice_options.keys()))
    
    # Speed & Pitch options block
    speed_val = st.slider("Speed Control", 0.5, 2.0, 1.0, 0.1)
    pitch_val = st.slider("Pitch Control (Hz)", -20, 20, 0, 1)
    
    speed_string = f"{'+' if speed_val >= 1.0 else ''}{int((speed_val-1)*100)}%"
    pitch_string = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"

    if st.button("🔥 Generate Professional Voice", use_container_width=True):
        current_word_count = len(user_text.split())
        
        if not user_text.strip():
            st.error("Meharbani kar ke pehle text likhain!")
        elif user_data["words_used"] + current_word_count > user_data["total_allowed"]:
            st.error("⚠️ Aap ka Credits/Words Limit khatam ho chuka hai! Naya plan buy karain.")
        else:
            with st.spinner("F.M AI Studio Me Audio Ban Rahi Hai..."):
                output_file = "generated_studio_voice.mp3"
                if os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                    except:
                        pass
                
                try:
                    async def make_voice():
                        communicate = Communicate(
                            user_text.strip(), 
                            voice_options[voice_name],
                            rate=speed_string,
                            pitch=pitch_string
                        )
                        await communicate.save(output_file)
                    
                    asyncio.run(make_voice())
                    
                    if os.path.exists(output_file):
                        user_data["words_used"] += current_word_count
                        save_db(db)
                        st.success("🎉 Audio kamyabi se tayar ho chuki hai!")
                        
                        with open(output_file, "rb") as f:
                            st.session_state.generated_audio = f.read()
                            
                except Exception as e:
                    st.error("⚠️ Zubaan aur Character Match Nahi Huay! Dono ko same rakhain!")

    # --- FREEZELESS DOWNLOAD SYSTEM ---
    if st.session_state.generated_audio is not None:
        st.write("---")
        st.audio(st.session_state.generated_audio, format="audio/mp3")
        st.download_button(
            label="📥 Download Professional MP3 File",
            data=st.session_state.generated_audio,
            file_name="fm_ai_studio_voice.mp3",
            mime="audio/mp3",
            use_container_width=True
        )