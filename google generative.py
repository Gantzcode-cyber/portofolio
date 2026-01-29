import streamlit as st
import google.generativeai as genai
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AI Math Master",
    page_icon="🎓",
    layout="wide" # Layout lebar agar grafik muat
)

# --- 2. KONFIGURASI API KEY (AMAN) ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    else:
        st.error("⚠️ API Key belum diatur! Mohon atur di menu Settings > Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Terjadi kesalahan konfigurasi: {e}")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. INISIALISASI SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya Math Master. Kirim foto, ketik soal, atau gunakan grafik di menu samping."}
    ]

# --- 4. FUNGSI DOWNLOAD ---
def get_chat_history_text():
    chat_text = "📚 CATATAN BELAJAR MATEMATIKA\n\n"
    for msg in st.session_state.messages:
        role = "🤖 AI" if msg["role"] == "assistant" else "👤 SAYA"
        content = msg["content"]
        if isinstance(content, str):
            chat_text += f"{role}:\n{content}\n\n{'-'*30}\n\n"
    return chat_text

# --- 5. SIDEBAR (FITUR LENGKAP) ---
with st.sidebar:
    st.title("🧰 Menu Perkakas")
    
    # === FITUR A: GRAPHING CALCULATOR (BARU!) ===
    st.subheader("📈 Plot Grafik")
    with st.expander("Buka Kalkulator Grafik"):
        st.caption("Contoh: x**2, np.sin(x), x + 2")
        formula = st.text_input("Rumus f(x):", value="x**2")
        x_range = st.slider("Rentang X:", -10, 10, (-5, 5))
        
        if st.button("Gambar Grafik"):
            try:
                x = np.linspace(x_range[0], x_range[1], 100)
                # Tips: Mengganti ^ menjadi ** agar python mengerti pangkat
                safe_formula = formula.replace("^", "**")
                y = eval(safe_formula) # Hati-hati, eval menjalankan kode string
                
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.plot(x, y)
                ax.grid(True)
                ax.set_xlabel("x")
                ax.set_ylabel("f(x)")
                ax.axhline(0, color='black',linewidth=1)
                ax.axvline(0, color='black',linewidth=1)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error rumus: {e}")

    st.divider()

    # === FITUR B: UPLOAD GAMBAR ===
    st.subheader("📸 Scan Soal")
    uploaded_file = st.file_uploader("Upload foto soal", type=["jpg", "png", "jpeg"])
    image_prompt = None
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview", use_container_width=True)
        if st.button("🔍 Bedah Soal Ini"):
            image_prompt = image

    st.divider()

    # === FITUR C: DOWNLOAD ===
    st.download_button(
        label="💾 Download Catatan",
        data=get_chat_history_text(),
        file_name="catatan_matematika.txt",
        mime="text/plain"
    )
    
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 6. AREA CHAT UTAMA ---
st.title("🎓 AI Math Master")
st.caption("Powered by Gemini 1.5 Flash | Support Vision & Graphing")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 7. LOGIKA OTAK AI ---

# Jika user upload gambar
if image_prompt:
    with st.chat_message("user"):
        st.write("Menganalisis gambar...")
    st.session_state.messages.append({"role": "user", "content": "[Mengirim Foto]"})
    
    with st.spinner("Sedang melihat gambar..."):
        try:
            prompt_vision = "Jelaskan solusi matematika dari gambar ini langkah demi langkah dengan format LaTeX."
            response = model.generate_content([prompt_vision, image_prompt])
            st.chat_message("assistant").markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")

# Jika user mengetik teks
if prompt := st.chat_input("Tanyakan soal matematika..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Sedang menghitung..."):
        try:
            # Prompt agar AI pintar matematika
            sys_prompt = "Anda adalah guru matematika. Gunakan notasi LaTeX ($...$) untuk rumus. Jelaskan step-by-step.\nSoal: "
            response = model.generate_content(sys_prompt + prompt)
            
            st.chat_message("assistant").markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
