import streamlit as st
import google.generativeai as genai
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AI Math Ultimate",
    page_icon="🧠",
    layout="wide"
)

# --- 2. CSS CUSTOM UNTUK MODE GELAP ---
def inject_custom_css(is_dark_mode):
    if is_dark_mode:
        st.markdown(
            """
            <style>
            /* Warna Latar Belakang Utama */
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            /* Warna Sidebar */
            [data-testid="stSidebar"] {
                background-color: #262730;
                color: #FAFAFA;
            }
            /* Warna Input Text */
            .stTextInput > div > div > input {
                color: #FAFAFA;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        # Set style untuk Matplotlib menjadi gelap
        plt.style.use('dark_background')
    else:
        # Reset ke default (terang)
        plt.style.use('default')

# --- 3. KONFIGURASI API KEY ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    else:
        st.error("⚠️ API Key belum diatur! Mohon atur di menu Settings > Secrets.")
        st.stop()
except Exception:
    st.error("Error konfigurasi API.")
    st.stop()

model = genai.GenerativeModel('models/gemini-2.5-flash')

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya Math Ultimate. Pilih alat di menu sebelah kiri."}
    ]

# --- 5. FUNGSI HELPER PDF ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Latihan Soal Matematika", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 6. SIDEBAR SUPER LENGKAP ---
with st.sidebar:
    st.title("🧰 Menu Perkakas")
    
    # === TOMBOL MODE GELAP (FITUR BARU) ===
    dark_mode = st.toggle("🌙 Mode Gelap", value=True) # Default Nyala
    inject_custom_css(dark_mode) # Panggil fungsi CSS
    st.divider()

    # === A. PAPAN TULIS ===
    st.subheader("✏️ Papan Tulis")
    with st.expander("Buka Canvas"):
        # Warna canvas menyesuaikan mode
        bg_canvas = "#000000" if dark_mode else "#ffffff"
        stroke_canvas = "#ffffff" if dark_mode else "#000000"
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3,
            stroke_color=stroke_canvas, # Tinta putih kalau gelap
            background_color=bg_canvas, # Kertas hitam kalau gelap
            height=200, width=280,
            drawing_mode="freedraw",
            key="canvas",
        )
        if st.button("Kirim Tulisan"):
            if canvas_result.image_data is not None:
                img_data = canvas_result.image_data.astype("uint8")
                img_pil = Image.fromarray(img_data)
                st.session_state.messages.append({"role": "user", "content": "[Mengirim Tulisan Tangan]"})
                with st.spinner("Membaca tulisan..."):
                    resp = model.generate_content(["Selesaikan soal ini:", img_pil])
                    st.session_state.messages.append({"role": "assistant", "content": resp.text})
                    st.rerun()

    st.divider()

    # === B. ANALISIS DATA ===
    st.subheader("📊 Statistik")
    with st.expander("Analisis CSV"):
        file_csv = st.file_uploader("Upload CSV", type=["csv"])
        if file_csv and st.button("Analisis Data"):
            df = pd.read_csv(file_csv)
            info = df.describe().to_string()
            st.dataframe(df.head(3))
            
            prompt = f"Analisis statistik dari data ini:\n{info}\nBerikan insight penting."
            with st.spinner("Menganalisis..."):
                resp = model.generate_content(prompt)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
                st.rerun()

    st.divider()

    # === C. GRAFIK (AUTO DARK MODE) ===
    st.subheader("📈 Kalkulator Grafik")
    with st.expander("Plot Grafik"):
        st.caption("Contoh: x**2, np.sin(x)")
        rumus = st.text_input("f(x) =", value="x**2")
        x_min = st.number_input("Min X", value=-10)
        x_max = st.number_input("Max X", value=10)
        
        if st.button("Gambar Grafik"):
            try:
                x = np.linspace(x_min, x_max, 100)
                y = eval(rumus.replace("^", "**"))
                
                # Membuat figure grafik
                fig, ax = plt.subplots(figsize=(4, 2.5))
                
                # Logic warna grafik mengikuti tema
                if dark_mode:
                    fig.patch.set_facecolor('#0E1117') # Latar belakang luar
                    ax.set_facecolor('#0E1117') # Latar belakang dalam
                    ax.spines['bottom'].set_color('white')
                    ax.spines['top'].set_color('white') 
                    ax.spines['right'].set_color('white')
                    ax.spines['left'].set_color('white')
                    ax.tick_params(axis='x', colors='white')
                    ax.tick_params(axis='y', colors='white')
                    ax.yaxis.label.set_color('white')
                    ax.xaxis.label.set_color('white')
                    ax.title.set_color('white')
                    line_color = '#00ff00' # Hijau neon biar keren di gelap
                    grid_color = '#444444'
                else:
                    line_color = 'blue'
                    grid_color = 'lightgray'

                ax.plot(x, y, color=line_color)
                ax.grid(True, color=grid_color, linestyle='--')
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Rumus Error: {e}")

    st.divider()

    # === D. PDF GENERATOR ===
    st.subheader("📝 Ujian & PDF")
    with st.expander("Buat Soal Latihan"):
        topik = st.text_input("Topik:", "Aljabar Linear")
        jumlah = st.slider("Jumlah Soal", 1, 10, 5)
        
        if st.button("Generate PDF"):
            with st.spinner("Membuat soal..."):
                prompt_pdf = f"Buatkan {jumlah} soal matematika pilihan ganda tentang {topik} beserta kunci jawaban di akhir. Gunakan teks polos."
                resp = model.generate_content(prompt_pdf)
                st.session_state.messages.append({"role": "assistant", "content": f"**Preview Soal PDF:**\n\n{resp.text}"})
                pdf_bytes = create_pdf(resp.text)
                st.download_button("📥 Download File PDF", pdf_bytes, f"Latihan_{topik}.pdf", "application/pdf")

    st.divider()

    # === E. RESET ===
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 7. AREA CHAT UTAMA ---
st.title("🧠 AI Math Ultimate")

# Tampilkan Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 8. INPUT TEXT UTAMA ---
if prompt := st.chat_input("Ketik pertanyaan matematika..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.spinner("Sedang menghitung..."):
        try:
            sys_prompt = "Anda adalah dosen matematika. Gunakan LaTeX ($...$) untuk rumus. Jelaskan langkah demi langkah.\nSoal: "
            resp = model.generate_content(sys_prompt + prompt)
            st.session_state.messages.append({"role": "assistant", "content": resp.text})
            st.chat_message("assistant").markdown(resp.text)
        except Exception as e:
            st.error(f"Terjadi error: {e}")
