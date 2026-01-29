import streamlit as st
import google.generativeai as genai
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import requests
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import time

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AI Math Ultimate",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ASET & ANIMASI ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Menggunakan animasi robot yang lebih futuristik
lottie_robot = load_lottieurl("https://lottie.host/5a8059f1-3226-444a-93f4-0b7305986877/P1sF2Xn3vR.json")

# --- 3. CSS "CYBER DARK" (HITAM & SILUET BIRU) ---
st.markdown("""
<style>
    /* RESET & BACKGROUND HITAM PEKAT */
    .stApp {
        background-color: #050505;
        color: #E0FFFF;
        font-family: 'Courier New', Courier, monospace; /* Font ala Coding */
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #00E5FF; /* Garis Biru Neon */
    }

    /* TOMBOL "CHAT BARU" & TOMBOL LAINNYA */
    .stButton>button {
        width: 100%;
        border-radius: 0px !important; /* KOTAK TEGAS */
        background-color: #000;
        color: #00E5FF;
        border: 1px solid #00E5FF;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00E5FF;
        color: #000;
        box-shadow: 0 0 20px #00E5FF; /* Efek Cahaya */
    }

    /* CARD DASHBOARD (KOTAK PERSEGI PANJANG) */
    .cyber-card {
        background: #0a0a0a;
        padding: 30px;
        border: 1px solid #333;
        border-radius: 0px; /* HAPUS OVAL */
        text-align: center;
        transition: 0.3s;
        height: 100%;
        border-left: 3px solid #333;
    }
    .cyber-card:hover {
        border-color: #00E5FF;
        border-left: 10px solid #00E5FF; /* Efek geser garis */
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.2);
        transform: translateY(-5px);
    }

    /* INPUT CHAT (BAGIAN BAWAH) */
    .stChatInput textarea {
        background-color: #000 !important;
        color: #00E5FF !important;
        border: 1px solid #333;
        border-radius: 0px !important; /* KOTAK */
    }
    .stChatInput textarea:focus {
        border-color: #00E5FF !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.5);
    }
    
    /* MEMPERBAIKI AREA BAWAH AGAR HITAM */
    div[data-testid="stBottom"] {
        background-color: #050505 !important;
        border-top: 1px solid #00E5FF;
    }

    /* JUDUL GLITCH EFFECT */
    .glitch-title {
        color: #fff;
        font-size: 3em;
        font-weight: bold;
        text-shadow: 2px 2px 0px #00E5FF;
    }
    
    /* HILANGKAN MARGIN ATAS BIAR FULL */
    .block-container {
        padding-top: 2rem;
    }

</style>
""", unsafe_allow_html=True)

# Set Matplotlib agar hitam
plt.style.use('dark_background')

# --- 4. API CONFIG ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ API Key hilang!")
        st.stop()
except: st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')
if "messages" not in st.session_state: st.session_state.messages = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🧬 CONTROL PANEL")
    
    # === FITUR TAMBAH CHAT (CHAT BARU) ===
    if st.button("➕ CHAT BARU", type="primary"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Navigasi Modern (Option Menu)
    selected = option_menu(
        menu_title=None,
        options=["Beranda", "Papan Tulis", "Statistik", "Grafik", "Ujian PDF"],
        icons=["house", "pencil", "bar-chart", "activity", "file-pdf"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#00E5FF", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "5px", "color": "#fff"},
            "nav-link-selected": {"background-color": "#00E5FF", "color": "black", "font-weight": "bold"},
        }
    )
    
    if lottie_robot:
        st_lottie(lottie_robot, height=150, key="sidebar_anim")

# --- 6. LOGIKA FITUR ---

# A. PAPAN TULIS (FULL AREA PERSEGI)
if selected == "Papan Tulis":
    st.markdown("<h2 style='color:#00E5FF'>✏️ CANVAS DIGITAL</h2>", unsafe_allow_html=True)
    
    # Canvas dibuat lebar (width 1000an) dan background hitam pekat
    canvas_result = st_canvas(
        fill_color="rgba(0, 229, 255, 0.3)",
        stroke_width=3,
        stroke_color="#00E5FF", # Tinta Neon
        background_color="#000000", # Kertas Hitam
        height=500, # Tinggi Full
        width=1000, # Lebar Full
        drawing_mode="freedraw",
        key="canvas",
    )
    
    # Tombol kirim full width
    if st.button("KIRIM CORETAN KE AI"):
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype("uint8"))
            st.session_state.messages.append({"role": "user", "content": "[Mengirim Gambar Canvas]"})
            with st.spinner("MEMINDAI DATA VISUAL..."):
                resp = model.generate_content(["Selesaikan soal matematika ini langkah demi langkah:", img])
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
                st.rerun()

# B. STATISTIK
elif selected == "Statistik":
    st.markdown("<h2 style='color:#00E5FF'>📊 DATA ANALYST</h2>", unsafe_allow_html=True)
    file = st.file_uploader("Upload CSV", type=["csv"])
    if file:
        df = pd.read_csv(file)
        st.dataframe(df.head(), use_container_width=True)
        if st.button("ANALISIS DATA"):
            with st.spinner("MENGHITUNG DATA..."):
                resp = model.generate_content(f"Analisis data ini:\n{df.describe().to_string()}")
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
                st.rerun()

# C. GRAFIK
elif selected == "Grafik":
    st.markdown("<h2 style='color:#00E5FF'>📈 PLOT GRAFIK</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1: rumus = st.text_input("Fungsi f(x):", "np.sin(x) * x")
    with col2: 
        st.write("")
        st.write("")
        btn_plot = st.button("PLOT")
        
    if btn_plot:
        try:
            x = np.linspace(-10, 10, 100)
            y = eval(rumus)
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Style Grafik Cyberpunk
            fig.patch.set_facecolor('#000')
            ax.set_facecolor('#000')
            ax.spines['bottom'].set_color('#00E5FF')
            ax.spines['left'].set_color('#00E5FF')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(colors='#fff')
            
            ax.plot(x, y, color='#00E5FF', linewidth=3, shadow=True)
            ax.grid(True, color='#333', linestyle='--', alpha=0.5)
            
            st.pyplot(fig)
        except: st.error("SINTAKS ERROR")

# D. UJIAN PDF
elif selected == "Ujian PDF":
    st.markdown("<h2 style='color:#00E5FF'>📝 GENERATOR UJIAN</h2>", unsafe_allow_html=True)
    topik = st.text_input("Topik Matematika:", "Integral")
    if st.button("GENERATE PDF"):
        def create_pdf(text):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 7, text.encode('latin-1', 'replace').decode('latin-1'))
            return pdf.output(dest='S').encode('latin-1')
        
        with st.spinner("MEMBUAT SOAL..."):
            resp = model.generate_content(f"Buat 5 soal {topik}.")
            st.download_button("DOWNLOAD FILE", create_pdf(resp.text), "soal.pdf")

# --- 7. BERANDA (DASHBOARD KOTAK) ---
if selected == "Beranda":
    st.markdown('<h1 class="glitch-title">AI MATH ULTIMATE</h1>', unsafe_allow_html=True)
    st.write("SISTEM MATEMATIKA CERDAS BERBASIS VISION & GENERATIVE AI.")
    
    if not st.session_state.messages:
        st.divider()
        # Kartu Dashboard Full Width & Persegi
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("""
            <div class="cyber-card">
                <h1 style='font-size:50px'>📸</h1>
                <h3>VISION SCAN</h3>
                <p>Upload foto soal, AI akan membedah solusinya.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown("""
            <div class="cyber-card">
                <h1 style='font-size:50px'>📈</h1>
                <h3>AUTO GRAPH</h3>
                <p>Visualisasi rumus matematika instan.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with c3:
            st.markdown("""
            <div class="cyber-card">
                <h1 style='font-size:50px'>💾</h1>
                <h3>DATA ENGINE</h3>
                <p>Analisis file CSV & Statistik otomatis.</p>
            </div>
            """, unsafe_allow_html=True)

# --- 8. CHAT INTERFACE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 9. INPUT AREA ---
if prompt := st.chat_input("MASUKKAN PERINTAH MATEMATIKA..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_msg = st.session_state.messages[-1]["content"]
    with st.chat_message("user"): st.markdown(user_msg)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        with st.spinner("PROCESSING..."):
            try:
                sys = "Jawab dengan LaTeX. Gaya bahasa: Singkat, Padat, Futuristik."
                response = model.generate_content(sys + user_msg)
                
                full_text = ""
                for chunk in response.text.split():
                    full_text += chunk + " "
                    placeholder.markdown(full_text + "▌")
                    time.sleep(0.05)
                placeholder.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
            except: st.error("CONNECTION ERROR")
