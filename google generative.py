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
import time

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AI Math Ultimate",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. FUNGSI LOADER ANIMASI (LOTTIE) ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Animasi dari Internet (Robot & Math)
lottie_robot = load_lottieurl("https://lottie.host/5a8059f1-3226-444a-93f4-0b7305986877/P1sF2Xn3vR.json")
lottie_coding = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")
lottie_success = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_lk80fpsm.json")

# --- 3. CSS "JELLY" & CURSOR EFFECT ---
def inject_custom_css(is_dark):
    # Warna Tema
    if is_dark:
        bg_main = "#0e1117"
        text_color = "#fff"
        card_bg = "linear-gradient(145deg, #1e232f, #161a23)"
        shadow = "5px 5px 10px #0b0d12, -5px -5px 10px #212734" # Neumorphism Dark
        btn_color = "#00DFD8"
    else:
        bg_main = "#e0e5ec"
        text_color = "#333"
        card_bg = "linear-gradient(145deg, #ffffff, #e6e6e6)"
        shadow = "5px 5px 10px #bebebe, -5px -5px 10px #ffffff" # Neumorphism Light
        btn_color = "#007CF0"

    st.markdown(f"""
    <style>
        /* BACKGROUND UTAMA */
        .stApp {{
            background-color: {bg_main};
            color: {text_color};
        }}

        /* TOMBOL "JELLY" (MEMBAL SAAT DIKLIK) */
        .stButton>button {{
            color: {text_color};
            background: {card_bg};
            border: none;
            border-radius: 15px;
            box-shadow: {shadow};
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            font-weight: bold;
        }}
        .stButton>button:hover {{
            transform: translateY(-3px) scale(1.02);
            color: {btn_color};
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        .stButton>button:active {{
            transform: translateY(2px) scale(0.95); /* Efek Membal */
            box-shadow: inset 2px 2px 5px rgba(0,0,0,0.2);
        }}

        /* INPUT TEXT FIELD CUSTOM */
        .stTextInput>div>div>input {{
            border-radius: 12px;
            border: 2px solid transparent;
            background-color: {bg_main};
            box-shadow: inset 3px 3px 6px rgba(0,0,0,0.3), inset -3px -3px 6px rgba(255,255,255,0.05);
            color: {text_color};
            transition: 0.3s;
        }}
        .stTextInput>div>div>input:focus {{
            border-color: {btn_color};
            outline: none;
        }}

        /* KARTU DASHBOARD BERGERAK */
        .hover-card {{
            background: {card_bg};
            padding: 20px;
            border-radius: 20px;
            box-shadow: {shadow};
            text-align: center;
            transition: transform 0.4s ease;
            cursor: pointer;
            height: 100%;
        }}
        .hover-card:hover {{
            transform: scale(1.05) rotate(1deg); /* Miring sedikit saat hover */
            z-index: 10;
        }}

        /* JUDUL GRADIENT BERGERAK */
        .animated-title {{
            background: linear-gradient(90deg, #ff00cc, #333399, #00DFD8);
            background-size: 200% auto;
            color: #fff;
            background-clip: text;
            text-fill-color: transparent;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 3s linear infinite;
            font-size: 3em;
            font-weight: 900;
        }}
        @keyframes shine {{
            to {{ background-position: 200% center; }}
        }}
    </style>
    """, unsafe_allow_html=True)

    # Set Matplotlib Theme
    if is_dark:
        plt.style.use('dark_background')
    else:
        plt.style.use('default')

# --- 4. CONFIG API ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    else:
        st.error("⚠️ API Key belum diatur!")
        st.stop()
except:
    st.error("Error Config API")
    st.stop()

model = genai.GenerativeModel('moduls/gemini-2.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. SIDEBAR ---
with st.sidebar:
    # Toggle Dark Mode (Simpan di session state)
    if 'dark_mode' not in st.session_state: st.session_state.dark_mode = True
    dark_mode = st.toggle("🌙 Tema Gelap", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dark_mode
    inject_custom_css(dark_mode) # Inject CSS berdasarkan tema
    
    # Animasi Lottie Kecil di Sidebar
    if lottie_coding:
        st_lottie(lottie_coding, height=150, key="coding")
        
    st.divider()
    menu = st.radio("Navigasi:", ["🏠 Beranda", "✏️ Papan Tulis", "📊 Statistik", "📈 Grafik", "📝 Ujian PDF"])
    st.divider()

    # --- FITUR SIDEBAR ---
    if menu == "✏️ Papan Tulis":
        st.subheader("Canvas Ajaib")
        bg_c = "#000" if dark_mode else "#fff"
        stroke_c = "#fff" if dark_mode else "#000"
        canvas_result = st_canvas(fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color=stroke_c, background_color=bg_c, height=200, width=280, drawing_mode="freedraw", key="canvas")
        if st.button("✨ Kirim Coretan"):
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype("uint8"))
                st.session_state.messages.append({"role": "user", "content": "[Gambar]"})
                with st.spinner("AI sedang melihat..."):
                    resp = model.generate_content(["Jelaskan:", img])
                    st.session_state.messages.append({"role": "assistant", "content": resp.text})
                    st.rerun()

    elif menu == "📊 Statistik":
        file = st.file_uploader("Upload CSV", type=["csv"])
        if file and st.button("🚀 Analisis"):
            df = pd.read_csv(file)
            st.dataframe(df.head())
            with st.spinner("Menganalisis data..."):
                resp = model.generate_content(f"Analisis data ini:\n{df.describe().to_string()}")
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
                st.rerun()

    elif menu == "📈 Grafik":
        rumus = st.text_input("f(x) =", "np.sin(x)*x")
        if st.button("🎨 Gambar"):
            x = np.linspace(-10, 10, 100)
            y = eval(rumus)
            fig, ax = plt.subplots(figsize=(4,3))
            
            # Styling Grafik
            color_line = '#00DFD8' if dark_mode else '#007CF0'
            if dark_mode:
                fig.patch.set_facecolor('#0e1117')
                ax.set_facecolor('#0e1117')
                ax.spines['bottom'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.tick_params(colors='white')
            
            ax.plot(x, y, color=color_line, linewidth=2.5)
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            st.pyplot(fig)

    elif menu == "📝 Ujian PDF":
        def create_pdf(text):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 7, text.encode('latin-1', 'replace').decode('latin-1'))
            return pdf.output(dest='S').encode('latin-1')
        topik = st.text_input("Topik", "Kalkulus")
        if st.button("📄 Generate PDF"):
            resp = model.generate_content(f"Buat 3 soal {topik} & jawaban.")
            st.download_button("Download", create_pdf(resp.text), "soal.pdf")

    if st.button("🗑️ Reset", type="primary"):
        st.session_state.messages = []
        st.rerun()

# --- 6. HERO SECTION (HALAMAN UTAMA) ---

# Kolom Judul & Animasi
col_title, col_anim = st.columns([2, 1])

with col_title:
    st.markdown('<h1 class="animated-title">AI Math Ultimate</h1>', unsafe_allow_html=True)
    st.write("Asisten Matematika Tercanggih dengan Vision, Grafik, dan Analisis Data.")

with col_anim:
    # Menampilkan Robot Bergerak (Lottie)
    if lottie_robot:
        st_lottie(lottie_robot, height=200, key="robot_main")

# --- 7. DASHBOARD CARDS ---
if not st.session_state.messages:
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="hover-card">
            <h2>📸</h2>
            <h3>Vision AI</h3>
            <p>Upload foto soal, AI akan membaca & menjawabnya.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="hover-card">
            <h2>📈</h2>
            <h3>Auto Graph</h3>
            <p>Visualisasi rumus matematika otomatis.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="hover-card">
            <h2>📊</h2>
            <h3>Data Analyst</h3>
            <p>Upload Excel/CSV, dapatkan insight instan.</p>
        </div>
        """, unsafe_allow_html=True)

# --- 8. CHAT AREA ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 9. INPUT & RESPON ---
if prompt := st.chat_input("Ketik pertanyaan matematika..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_msg = st.session_state.messages[-1]["content"]
    with st.chat_message("user"): st.markdown(user_msg)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        # Efek Loading dengan Lottie
        with st.spinner("Sedang memproses..."):
            try:
                sys = "Jawab dengan format LaTeX. Jelaskan step-by-step."
                response = model.generate_content(sys + user_msg)
                
                # Efek mengetik (Simulasi)
                full_resp = response.text
                disp_text = ""
                for char in full_resp.split(" "): # Muncul per kata
                    disp_text += char + " "
                    placeholder.markdown(disp_text + "▌")
                    time.sleep(0.05)
                placeholder.markdown(full_resp)
                
                st.session_state.messages.append({"role": "assistant", "content": full_resp})
            except:
                st.error("Gagal terhubung.")
