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
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ASSETS & ANIMASI ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_robot = load_lottieurl("https://lottie.host/5a8059f1-3226-444a-93f4-0b7305986877/P1sF2Xn3vR.json")
lottie_coding = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")

# --- 3. CSS MODERN (FIXED DARK MODE) ---
def inject_custom_css(is_dark):
    # Palet Warna
    if is_dark:
        bg_main = "#0e1117"
        text_color = "#fff"
        input_bg = "#1e232f"
        glow_color = "#00DFD8" # Cyan Neon
        bottom_bg = "#0e1117"  # Warna container bawah (PENTING!)
    else:
        bg_main = "#f0f2f6"
        text_color = "#333"
        input_bg = "#ffffff"
        glow_color = "#007CF0" # Blue Neon
        bottom_bg = "#f0f2f6"

    st.markdown(f"""
    <style>
        /* Background Utama */
        .stApp {{ background-color: {bg_main}; color: {text_color}; }}

        /* --- FIX BAGIAN BAWAH (YANG SEBELUMNYA PUTIH/BUG) --- */
        div[data-testid="stBottom"] {{
            background-color: {bottom_bg} !important;
            border-top: 1px solid {input_bg}; /* Garis tipis pemisah */
        }}
        
        /* Pastikan container input transparan */
        div[data-testid="stChatInput"] {{
            background-color: transparent !important;
        }}

        /* --- STYLE INPUT BAR --- */
        .stChatInput textarea {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border: 2px solid #444;
            border-radius: 15px;
            transition: all 0.3s ease;
        }}
        .stChatInput textarea:focus {{
            border-color: {glow_color} !important;
            box-shadow: 0 0 15px {glow_color}50;
        }}

        /* --- KARTU DASHBOARD --- */
        .hover-card {{
            background-color: {input_bg};
            padding: 20px;
            border-radius: 20px;
            border: 1px solid #333;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .hover-card:hover {{
            transform: translateY(-5px);
            border-color: {glow_color};
            box-shadow: 0 0 20px {glow_color}40;
        }}

        /* --- JUDUL GRADIENT --- */
        .animated-title {{
            background: linear-gradient(90deg, #FF0080, #7928CA, #00DFD8);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 5s linear infinite;
            font-size: 3.5em;
            font-weight: 800;
        }}
        @keyframes shine {{ to {{ background-position: 200% center; }} }}
        
    </style>
    """, unsafe_allow_html=True)
    
    if is_dark: plt.style.use('dark_background')
    else: plt.style.use('default')

# --- 4. API CONFIG ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ API Key hilang!")
        st.stop()
except: st.stop()

model = genai.GenerativeModel('moduls/gemini-2.5-flash')
if "messages" not in st.session_state: st.session_state.messages = []

# --- 5. SIDEBAR ---
with st.sidebar:
    if 'dark_mode' not in st.session_state: st.session_state.dark_mode = True
    dark_mode = st.toggle("🌙 Tema Gelap", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dark_mode
    inject_custom_css(dark_mode) # Panggil CSS Perbaikan
    
    if lottie_coding: st_lottie(lottie_coding, height=120)
    
    selected = option_menu(
        menu_title="Navigasi Utama",
        options=["Beranda", "Papan Tulis", "Statistik", "Grafik", "Ujian PDF"],
        icons=["house", "pencil-square", "bar-chart-line", "graph-up-arrow", "file-earmark-pdf"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "transparent"},
            "icon": {"color": "#00DFD8", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#262730"},
            "nav-link-selected": {"background-color": "#007CF0"},
        }
    )
    
    st.divider()
    if st.button("🗑️ Hapus Chat", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 6. LOGIKA FITUR ---

# A. PAPAN TULIS
if selected == "Papan Tulis":
    st.subheader("✏️ Canvas Digital")
    bg_c = "#000" if dark_mode else "#fff"
    stroke_c = "#fff" if dark_mode else "#000"
    canvas_result = st_canvas(fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color=stroke_c, background_color=bg_c, height=300, width=500, drawing_mode="freedraw", key="canvas")
    if st.button("Kirim Tulisan"):
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype("uint8"))
            st.session_state.messages.append({"role": "user", "content": "[Gambar Tulisan]"})
            with st.spinner("Membaca..."):
                resp = model.generate_content(["Selesaikan:", img])
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
                st.rerun()

# B. STATISTIK
elif selected == "Statistik":
    st.subheader("📊 Data Analyst")
    file = st.file_uploader("Upload CSV", type=["csv"])
    if file and st.button("Analisis"):
        df = pd.read_csv(file)
        st.dataframe(df.head())
        with st.spinner("Menganalisis..."):
            resp = model.generate_content(f"Analisis:\n{df.describe().to_string()}")
            st.session_state.messages.append({"role": "assistant", "content": resp.text})
            st.rerun()

# C. GRAFIK
elif selected == "Grafik":
    st.subheader("📈 Kalkulator Grafik")
    col1, col2 = st.columns([3, 1])
    with col1: rumus = st.text_input("f(x) =", "np.sin(x) * x")
    with col2: 
        if st.button("Plot", use_container_width=True):
            try:
                x = np.linspace(-10, 10, 100)
                y = eval(rumus)
                fig, ax = plt.subplots(figsize=(6, 4))
                line_c = '#00DFD8' if dark_mode else '#007CF0'
                if dark_mode:
                    fig.patch.set_facecolor('#0e1117')
                    ax.set_facecolor('#0e1117')
                    ax.spines['bottom'].set_color('white'); ax.spines['left'].set_color('white')
                    ax.tick_params(colors='white')
                ax.plot(x, y, color=line_c, linewidth=2)
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
            except: st.error("Rumus error")

# D. UJIAN PDF
elif selected == "Ujian PDF":
    st.subheader("📝 Generator Soal")
    topik = st.text_input("Topik", "Kalkulus")
    if st.button("Buat PDF"):
        def create_pdf(text):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 7, text.encode('latin-1', 'replace').decode('latin-1'))
            return pdf.output(dest='S').encode('latin-1')
        resp = model.generate_content(f"Buat 3 soal {topik}.")
        st.download_button("Download PDF", create_pdf(resp.text), "soal.pdf")

# --- 7. HOME & DASHBOARD ---
if selected == "Beranda":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<h1 class="animated-title">AI Math Ultimate</h1>', unsafe_allow_html=True)
        st.write("### Asisten Matematika Cerdas: Vision, Grafik & Analisis.")
    with col2:
        if lottie_robot: st_lottie(lottie_robot, height=200)

    if not st.session_state.messages:
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown('<div class="hover-card"><h1>📸</h1><h3>Vision AI</h3><p>Upload foto soal.</p></div>', unsafe_allow_html=True)
        with c2: st.markdown('<div class="hover-card"><h1>📈</h1><h3>Grafik</h3><p>Visualisasi rumus.</p></div>', unsafe_allow_html=True)
        with c3: st.markdown('<div class="hover-card"><h1>📊</h1><h3>Data</h3><p>Analisis CSV otomatis.</p></div>', unsafe_allow_html=True)

# --- 8. CHAT INTERFACE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 9. INPUT NEON (SUDAH DIPERBAIKI) ---
if prompt := st.chat_input("Ketik pertanyaan matematika..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_msg = st.session_state.messages[-1]["content"]
    with st.chat_message("user"): st.markdown(user_msg)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        with st.spinner("Sedang berpikir..."):
            try:
                sys = "Jawab dengan LaTeX. Jelaskan step-by-step."
                response = model.generate_content(sys + user_msg)
                full_text = ""
                for chunk in response.text.split():
                    full_text += chunk + " "
                    placeholder.markdown(full_text + "▌")
                    time.sleep(0.05)
                placeholder.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
            except: st.error("Error koneksi")
