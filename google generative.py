import streamlit as st
import google.generativeai as genai
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import pandas as pd
from streamlit_drawable_canvas import st_canvas # Library Papan Tulis

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AI Math Ultimate",
    page_icon="🧠",
    layout="wide"
)

# --- 2. KONFIGURASI API KEY ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    else:
        st.error("⚠️ API Key belum diatur!")
        st.stop()
except Exception:
    st.error("Error konfigurasi API.")
    st.stop()

model = genai.GenerativeModel('models/gemini-2.5-flash')

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Silakan tulis soal di papan tulis, upload foto, atau ketik manual."}
    ]

# --- 4. HELPER PDF ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 5. SIDEBAR SUPER LENGKAP ---
with st.sidebar:
    st.title("🧰 Menu Perkakas")
    
    # === FITUR A: PAPAN TULIS (BARU & KEREN!) ===
    st.subheader("✏️ Papan Tulis")
    with st.expander("Buka Papan Tulis", expanded=True):
        st.caption("Coret rumus di sini:")
        # Membuat Canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Warna isi
            stroke_width=3, # Ketebalan pena
            stroke_color="#000000", # Warna tinta hitam
            background_color="#ffffff", # Kertas putih
            height=200,
            width=280,
            drawing_mode="freedraw",
            key="canvas",
        )
        
        if st.button("Kirim Tulisan Tangan"):
            if canvas_result.image_data is not None:
                # Konversi coretan canvas ke format Gambar yg dimengerti Gemini
                img_data = canvas_result.image_data.astype("uint8")
                img_pil = Image.fromarray(img_data)
                
                # Masukkan ke proses AI
                st.session_state.messages.append({"role": "user", "content": "[Mengirim Tulisan Tangan]"})
                with st.spinner("Membaca tulisan tangan..."):
                    prompt_handwriting = "Baca tulisan matematika ini dan selesaikan langkah demi langkah."
                    response = model.generate_content([prompt_handwriting, img_pil])
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.rerun()

    st.divider()

    # === FITUR B: ANALIS DATA ===
    st.subheader("📊 Statistik")
    with st.expander("Analisis CSV"):
        file_csv = st.file_uploader("Upload CSV", type=["csv"])
        if file_csv and st.button("Analisis"):
            df = pd.read_csv(file_csv)
            info = df.describe().to_string()
            prompt = f"Analisis data ini sebagai Data Scientist:\n{info}"
            resp = model.generate_content(prompt)
            st.session_state.messages.append({"role": "assistant", "content": resp.text})
            st.rerun()

    # === FITUR C: FITUR LAINNYA (Diringkas biar rapi) ===
    st.subheader("Fitur Lain")
    if st.checkbox("Tampilkan Grafik & PDF"):
        # Grafik
        rumus = st.text_input("Grafik f(x):", "x**2")
        if st.button("Plot"):
            x = np.linspace(-10, 10, 100)
            y = eval(rumus.replace("^", "**"))
            fig, ax = plt.subplots(figsize=(4, 2))
            ax.plot(x, y); ax.grid(True)
            st.pyplot(fig)
            
        # PDF
        if st.button("Buat PDF Latihan"):
            resp = model.generate_content("Buat 3 soal matematika random.")
            pdf = create_pdf(resp.text)
            st.download_button("Download PDF", pdf, "soal.pdf")

    st.divider()
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 6. CHAT AREA ---
st.title("🧠 AI Math Ultimate")

# Tampilkan Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 7. INPUT TEXT ---
if prompt := st.chat_input("Ketik sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.spinner("Menghitung..."):
        resp = model.generate_content(prompt)
        st.session_state.messages.append({"role": "assistant", "content": resp.text})
        st.chat_message("assistant").markdown(resp.text)
