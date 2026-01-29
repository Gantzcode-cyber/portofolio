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
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS CUSTOM (PREMIUM LOOK) ---
st.markdown("""
<style>
    /* Background Utama yang lebih soft (Deep Blue-Black) */
    .stApp {
        background: linear-gradient(to bottom right, #0e1117, #151922);
        color: #E0E0E0;
    }
    
    /* Judul Gradient */
    .title-gradient {
        background: -webkit-linear-gradient(45deg, #007CF0, #00DFD8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 3em;
        padding-bottom: 20px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #11141d;
        border-right: 1px solid #2b313e;
    }

    /* Kartu Dashboard (Container) */
    .dashboard-card {
        background-color: #1e232f;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #2b313e;
        text-align: center;
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .dashboard-card:hover {
        transform: scale(1.02);
        border-color: #007CF0;
    }

    /* Tombol Custom */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Chat Message Styling */
    [data-testid="stChatMessage"] {
        background-color: #1e232f;
        border-radius: 15px;
        border: 1px solid #2b313e;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. KONFIGURASI API KEY ---
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

model = genai.GenerativeModel('moduls/gemini-2.5-flash')

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [] # Kosongkan awal biar bersih

# --- 5. FUNGSI HELPER ---
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

# --- 6. SIDEBAR (NAVIGASI) ---
with st.sidebar:
    st.markdown("### 🧰 Kotak Perkakas")
    
    # Mode Tab untuk Sidebar agar lebih rapi
    menu = st.radio(
        "Pilih Alat:",
        ["🏠 Beranda", "✏️ Papan Tulis", "📊 Statistik", "📈 Grafik", "📝 Ujian PDF"],
        index=0
    )
    
    st.divider()
    
    # --- LOGIKA ALAT ---
    
    # 1. Papan Tulis
    if menu == "✏️ Papan Tulis":
        st.subheader("Canvas Digital")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3, stroke_color="#fff",
            background_color="#000",
            height=200, width=280,
            drawing_mode="freedraw", key="canvas",
        )
        if st.button("Kirim Tulisan"):
            if canvas_result.image_data is not None:
                img_data = canvas_result.image_data.astype("uint8")
                img_pil = Image.fromarray(img_data)
                st.session_state.messages.append({"role": "user", "content": "[Mengirim Tulisan Tangan]"})
                with st.spinner("Membaca tulisan..."):
                    resp = model.generate_content(["Selesaikan:", img_pil])
                    st.session_state.messages.append({"role": "assistant", "content": resp.text})
                    st.rerun()

    # 2. Statistik
    elif menu == "📊 Statistik":
        st.subheader("Data Analyst")
        file_csv = st.file_uploader("Upload CSV", type=["csv"])
        if file_csv and st.button("Analisis"):
            df = pd.read_csv(file_csv)
            info = df.describe().to_string()
            st.dataframe(df.head(3))
            prompt = f"Analisis statistik:\n{info}\nBerikan insight singkat."
            with st.spinner("Menganalisis..."):
                resp = model.generate_content(prompt)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
                st.rerun()

    # 3. Grafik
    elif menu == "📈 Grafik":
        st.subheader("Plotter")
        rumus = st.text_input("f(x) =", "x**2")
        col1, col2 = st.columns(2)
        with col1: x_min = st.number_input("Min", -10)
        with col2: x_max = st.number_input("Max", 10)
        
        if st.button("Gambar"):
            try:
                x = np.linspace(x_min, x_max, 100)
                y = eval(rumus.replace("^", "**"))
                plt.style.use('dark_background')
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.plot(x, y, color='#00DFD8') # Warna Cyan
                ax.grid(True, color='#333', linestyle='--')
                # Hilangkan border kotak grafik agar menyatu
                for spine in ax.spines.values(): spine.set_visible(False)
                st.pyplot(fig)
            except: st.error("Rumus Error")

    # 4. PDF
    elif menu == "📝 Ujian PDF":
        st.subheader("Soal Generator")
        topik = st.text_input("Topik", "Aljabar")
        if st.button("Buat PDF"):
            with st.spinner("Membuat..."):
                resp = model.generate_content(f"Buat 5 soal {topik} & jawaban.")
                st.session_state.messages.append({"role": "assistant", "content": f"Preview:\n{resp.text}"})
                pdf_bytes = create_pdf(resp.text)
                st.download_button("Download", pdf_bytes, "soal.pdf")

    st.divider()
    if st.button("🗑️ Reset Chat", type="primary"):
        st.session_state.messages = []
        st.rerun()

# --- 7. AREA UTAMA (HERO SECTION) ---

# Header dengan Gradient
st.markdown('<h1 class="title-gradient">🧠 AI Math Ultimate</h1>', unsafe_allow_html=True)

# === LAYAR DASHBOARD (Jika chat kosong) ===
if not st.session_state.messages:
    st.markdown("""
    <div style='background-color: #1e232f; padding: 20px; border-radius: 10px; border-left: 5px solid #007CF0;'>
        <h4>👋 Selamat Datang!</h4>
        <p>Saya adalah asisten matematika pribadi Anda. Pilih salah satu alat di sidebar atau ketik soal di bawah.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Spacer
    
    # 3 Kolom Kartu Pintar
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📸 Vision</h3>
            <p>Upload foto soal PR Anda, saya akan menjawabnya.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📈 Grafik</h3>
            <p>Visualisasikan rumus matematika menjadi grafik interaktif.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📝 Ujian</h3>
            <p>Buat latihan soal otomatis dan download sebagai PDF.</p>
        </div>
        """, unsafe_allow_html=True)

# === TAMPILKAN CHAT ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 8. INPUT UTAMA ---
if prompt := st.chat_input("Ketik soal matematika, contoh: Integral dari 2x..."):
    # Hapus dashboard awal saat user mulai mengetik
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Logic pemrosesan (terpisah agar rerun bekerja smooth)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_msg = st.session_state.messages[-1]["content"]
    with st.chat_message("user"):
        st.markdown(user_msg)
        
    with st.chat_message("assistant"):
        with st.spinner("Sedang berpikir..."):
            try:
                # System prompt yang kuat
                sys = "Anda adalah profesor matematika jenius. Jawab dengan LaTeX. Gaya bahasa santai tapi edukatif.\n\nSoal: "
                response = model.generate_content(sys + user_msg)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("Maaf, terjadi kesalahan koneksi.")
