import streamlit as st
import google.generativeai as genai

# --- 1. Konfigurasi Halaman ---
st.set_page_config(
    page_title="Math AI Tutor",
    page_icon="🧮",
    layout="centered"
)

st.title("🧮 Gemini Math Tutor")
st.caption("Tanyakan soal matematika, saya akan bantu langkah demi langkah!")

# --- 2. Konfigurasi API Gemini ---
# PENTING: Jangan lupa ganti dengan API Key asli Anda
GEMINI_API_KEY = "AIzaSyCKS9DjnsfyXakrZWQCWsgZhsGYK6oKsXI"
genai.configure(api_key=GEMINI_API_KEY)

# Pilih model (gemini-1.5-flash cepat & hemat, gemini-1.5-pro lebih pintar)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. Inisialisasi Chat History ---
# Agar bot "ingat" percakapan sebelumnya
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 4. Tampilkan Chat di Layar ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. Logika Input & Respon ---
# Saat user mengetik sesuatu:
if prompt := st.chat_input("Contoh: Turunan dari 2x^2 + 5..."):
    
    # Tampilkan pesan user
    st.chat_message("user").write(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Siapkan instruksi khusus (System Prompt) agar jago matematika
    system_instruction = "Kamu adalah guru matematika yang sabar. Gunakan format LaTeX untuk rumus. Jelaskan step-by-step."
    full_prompt = f"{system_instruction}\n\nUser: {prompt}"

    # Kirim ke Gemini
    try:
        response = model.generate_content(full_prompt)
        bot_reply = response.text
        
        # Tampilkan balasan bot
        st.chat_message("assistant").write(bot_reply)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Terjadi kesalahan koneksi: {e}")