import streamlit as st
import google.generativeai as genai
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AI Math Master",
    page_icon="🎓",
    layout="wide"
)

# --- 2. KONFIGURASI API KEY ---
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
        {"role": "assistant", "content": "Halo! Saya siap membantu. Cek menu samping untuk Grafik dan Mode Ujian."}
    ]

# --- 4. FUNGSI PEMBUAT PDF ---
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Latihan Soal Matematika", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Dibuat oleh AI Math Master", ln=True, align='C')
    pdf.ln(10)
    
    # Content (Sanitasi teks agar tidak error di FPDF)
    # FPDF standar tidak support emoji/simbol matematika rumit, jadi kita bersihkan
    clean_text = text_content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    
    # Output string bytes
    return pdf.output(dest='S').encode('latin-1')

# --- 5. SIDEBAR (MENU PERKAKAS) ---
with st.sidebar:
    st.title("🧰 Menu Perkakas")
    
    # === FITUR A: UJIAN GENERATOR (BARU!) ===
    st.subheader("📝 Generator Ujian")
    with st.expander("Buat Soal Latihan"):
        topik = st.text_input("Topik (misal: Aljabar)", "Trigonometri")
        jumlah_soal = st.slider("Jumlah Soal:", 1, 10, 5)
        tingkat = st.selectbox("Tingkat Kesulitan:", ["Mudah", "Sedang", "Sulit/Olimpiade"])
        
        if st.button("Buat PDF Soal"):
            with st.spinner("Sedang meracik soal..."):
                try:
                    prompt_ujian = f"""
                    Buatkan {jumlah_soal} soal latihan matematika tentang {topik} dengan tingkat kesulitan {tingkat}.
                    Format output:
                    1. Soal 1...
                    2. Soal 2...
                    
                    --- Kunci Jawaban ---
                    1. Jawaban...
                    
                    Tolong jangan gunakan simbol LaTeX yang rumit, gunakan teks biasa agar mudah dicetak ke PDF.
                    """
                    response = model.generate_content(prompt_ujian)
                    ujian_text = response.text
                    
                    # Tampilkan di chat utama juga
                    st.session_state.messages.append({"role": "assistant", "content": f"**Mode Ujian: {topik}**\n\n{ujian_text}"})
                    
                    # Buat PDF
                    pdf_bytes = create_pdf(ujian_text)
                    st.success("Soal siap!")
                    
                    # Tombol Download PDF
                    st.download_button(
                        label="📥 Download PDF Soal",
                        data=pdf_bytes,
                        file_name=f"Soal_{topik}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Gagal membuat soal: {e}")

    st.divider()

    # === FITUR B: GRAPHING CALCULATOR ===
    st.subheader("📈 Plot Grafik")
    with st.expander("Buka Kalkulator Grafik"):
        st.caption("Contoh: x**2, np.sin(x)")
        formula = st.text_input("Rumus f(x):", value="np.sin(x)")
        
        if st.button("Gambar Grafik"):
            try:
                x = np.linspace(-10, 10, 100)
                safe_formula = formula.replace("^", "**")
                y = eval(safe_formula)
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.plot(x, y)
                ax.grid(True)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error rumus: {e}")

    st.divider()

    # === FITUR C: UPLOAD GAMBAR ===
    st.subheader("📸 Scan Soal")
    uploaded_file = st.file_uploader("Upload foto", type=["jpg", "png", "jpeg"])
    image_prompt = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview", use_container_width=True)
        if st.button("🔍 Bedah Soal Ini"):
            image_prompt = image

    st.divider()
    
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 6. AREA CHAT UTAMA ---
st.title("🎓 AI Math Master Pro")
st.caption("All-in-One: Chat, Vision, Graphing, Exam PDF")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 7. LOGIKA UTAMA ---

# Jika ada gambar
if image_prompt:
    st.session_state.messages.append({"role": "user", "content": "[Mengirim Foto]"})
    with st.spinner("Menganalisis..."):
        response = model.generate_content(["Selesaikan soal matematika di gambar ini langkah demi langkah.", image_prompt])
        st.chat_message("assistant").markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# Jika ada teks
if prompt := st.chat_input("Ketik soal matematika..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Sedang berpikir..."):
        try:
            sys_prompt = "Anda adalah guru matematika. Gunakan LaTeX ($) untuk rumus. Jelaskan step-by-step.\nSoal: "
            response = model.generate_content(sys_prompt + prompt)
            st.chat_message("assistant").markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
# --- TEMPEL INI DI PALING BAWAH KODE UNTUK CEK MODEL ---
try:
    st.write("Mengecek daftar model yang tersedia...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name) # Ini akan muncul di log hitam (terminal)
            st.write(f"- {m.name}") # Ini akan muncul di layar website
except Exception as e:
    st.error(f"Error listing models: {e}")
