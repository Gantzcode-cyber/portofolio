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

lottie_robot = load_lottieurl("https://lottie.host/5a8059f1-3226-444a-93f4-0b7305986877/P1sF2Xn3vR.json")

# --- 3. CSS "CYBER DARK" (ANTI-BOCOR PUTIH) ---
st.markdown("""
<style>
    /* RESET GLOBAL */
    .stApp {
        background-color: #000000;
        color: #00E5FF;
        font-family: 'Courier New', monospace;
    }

    /* --- PERBAIKAN SIDEBAR (AGAR TIDAK ADA KOTAK PUTIH) --- */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #00E5FF;
    }
    
    /* Memaksa container menu opsi menjadi hitam */
    div[data-testid="stSidebarNav"] {
        background-color: #000000 !important;
    }

    /* --- PERBAIKAN BAR BAWAH (INPUT CHAT) --- */
    /* Target container paling bawah */
    div[data-testid="stBottom"] {
        background-color: #000000 !important; /* Paksa Hitam */
        border-top: 1px solid #00E5FF;
        padding-bottom: 20px;
    }
    /* Target area input text */
    .stChatInput textarea {
        background-color: #0a0a0a !important;
        color: #00E5FF !important;
        border: 1px solid #333 !important;
    }
    .stChatInput textarea:focus {
        border-color: #00E5FF !important;
        box-shadow: 0 0 10px #00E5FF;
    }

    /* --- TOMBOL --- */
    .stButton>button {
        width: 100%;
        border-radius: 0px;
        background-color: #000;
        color: #00E5FF;
        border: 1px solid #00E5FF;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00E5FF;
        color: #000;
        box-shadow: 0 0 15px #00E5FF;
    }

    /* --- KARTU DASHBOARD --- */
    .cyber-card {
        background: #050505;
        border: 1px solid #333;
        padding: 20px;
        text-align: center;
        transition: 0.3s;
        border-left: 3px solid #333;
    }
    .cyber-card:hover {
        border-color: #00E5FF;
        border-left: 10px solid #00E5FF;
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.2);
    }

    /* --- FIX CANVAS AGAR FULL (TIDAK ADA BACKGROUND PUTIH) --- */
    iframe[title="streamlit_drawable_canvas.st_canvas"] {
        background-color: #000000;
    }

</style>
""", unsafe_allow_html=True)

# Set Grafik jadi Gelap
plt.style.use('dark_background')

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
    st.markdown("### 🧬 CONTROL PANEL")
    
    if st.button("➕ CHAT BARU", type="primary"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # PERBAIKAN MENU: Background Container diset ke HITAM (#000000)
    selected = option_menu(
        menu_title=None,
        options=["Beranda", "Papan Tulis", "Statistik", "Grafik", "Ujian PDF"],
        icons=["house", "pencil", "bar-chart", "activity", "file-pdf"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#000000"}, # INI KUNCINYA
            "icon": {"color": "#00E5FF", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "5px", "color": "#fff", "background-color": "#000000"},
            "nav-link-selected": {"background-color": "#00E5FF", "color": "black", "font-weight": "bold"},
        }
    )
    
    if lottie_robot:
        st_lottie(lottie_robot, height=150, key="anim_sidebar")

# --- 6. LOGIKA FITUR ---

# A. PAPAN TULIS (FULL & MENYATU)
if selected == "Papan Tulis":
    st.markdown("<h2 style='color:#00E5FF'>✏️ CANVAS DIGITAL</h2>", unsafe_allow_html=True)
    st.caption("Coret rumus matematika di area hitam di bawah ini.")
    
    # Canvas Lebar & Hitam
    canvas_result = st_canvas(
        fill_color="rgba(0, 229, 255, 0.3)",
        stroke_width=3,
        stroke_color="#00E5FF",
        background_color="#000000", # Pastikan Hitam
        height=500,
        width=1200, # Lebar maksimal agar pas di laptop
        drawing_mode="freedraw",
        key="canvas",
    )
    
    if st.button("KIRIM CORETAN"):
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype("uint8"))
            st.session_state.messages.append({"role": "user", "content": "[Mengirim Canvas]"})
            with st.spinner("MEMBACA CORETAN..."):
                resp = model.generate_content(["Jelaskan matematika ini:", img])
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
                st.rerun()

# B. STATISTIK
elif selected == "Statistik":
    st.markdown("<h2 style='color:#00E5FF'>📊 DATA ENGINE</h2>", unsafe_allow_html=True)
    file = st.file_uploader("Upload CSV", type=["csv"])
    if file:
        df = pd.read_csv(file)
        st.dataframe(df.head(), use_container_width=True)
        if st.button("ANALISIS"):
            with st.spinner("PROCESSING..."):
                resp = model.generate_content(f"Analisis data:\n{df.describe().to_string()}")
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
                st.rerun()

# C. GRAFIK
elif selected == "Grafik":
    st.markdown("<h2 style='color:#00E5FF'>📈 PLOT SYSTEM</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1: rumus = st.text_input("f(x):", "np.sin(x)*x")
    with col2: 
        st.write("")
        st.write("")
        btn = st.button("PLOT")
        
    if btn:
        try:
            x = np.linspace(-10, 10, 100)
            y = eval(rumus)
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor('#000')
            ax.set_facecolor('#000')
            ax.spines['bottom'].set_color('#00E5FF'); ax.spines['left'].set_color('#00E5FF')
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            ax.tick_params(colors='#fff')
            ax.plot(x, y, color='#00E5FF', linewidth=3)
            ax.grid(True, color='#333', linestyle='--')
            st.pyplot(fig)
        except: st.error("ERROR")

# D. PDF
elif selected == "Ujian PDF":
    st.markdown("<h2 style='color:#00E5FF'>📝 EXAM GENERATOR</h2>", unsafe_allow_html=True)
    topik = st.text_input("Topik:", "Turunan")
    if st.button("GENERATE"):
        def create_pdf(text):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 7, text.encode('latin-1', 'replace').decode('latin-1'))
            return pdf.output(dest='S').encode('latin-1')
        with st.spinner("CREATING..."):
            resp = model.generate_content(f"Buat 3 soal {topik}.")
            st.download_button("DOWNLOAD", create_pdf(resp.text), "soal.pdf")

# --- 7. DASHBOARD ---
if selected == "Beranda":
    st.markdown('<h1 style="color:#fff; font-size:3em;">AI MATH ULTIMATE</h1>', unsafe_allow_html=True)
    st.write("SYSTEM READY. WAITING FOR INPUT.")
    
    if not st.session_state.messages:
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown('<div class="cyber-card"><h1>📸</h1><h3>VISION</h3></div>', unsafe_allow_html=True)
        with c2: st.markdown('<div class="cyber-card"><h1>📈</h1><h3>GRAPH</h3></div>', unsafe_allow_html=True)
        with c3: st.markdown('<div class="cyber-card"><h1>💾</h1><h3>DATA</h3></div>', unsafe_allow_html=True)

# --- 8. CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 9. INPUT BAWAH (FIXED BLACK) ---
if prompt := st.chat_input("COMMAND INPUT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_msg = st.session_state.messages[-1]["content"]
    with st.chat_message("user"): st.markdown(user_msg)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        with st.spinner("CALCULATING..."):
            try:
                resp = model.generate_content("Jawab LaTeX & Singkat: " + user_msg)
                placeholder.markdown(resp.text)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
            except: st.error("ERROR")
