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

st.set_page_config(
    page_title="AI Math Ultimate",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_robot = load_lottieurl("https://lottie.host/5a8059f1-3226-444a-93f4-0b7305986877/P1sF2Xn3vR.json")

if "main_nav" not in st.session_state:
    st.session_state["main_nav"] = "Beranda"

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
<style>
    /* RESET GLOBAL */
    .stApp {
        background-color: #000000;
        color: #00E5FF;
        font-family: 'Courier New', monospace;
    }

    /* --- SIDEBAR & MENU --- */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #00E5FF;
    }
    div[data-testid="stSidebarNav"] {
        background-color: #000000 !important;
    }

    /* --- BAR BAWAH (INPUT) --- */
    div[data-testid="stBottom"] {
        background-color: #000000 !important;
        border-top: 1px solid #00E5FF;
        padding-bottom: 20px;
    }
    .stChatInput textarea {
        background-color: #0a0a0a !important;
        color: #00E5FF !important;
        border: 1px solid #333 !important;
    }
    .stChatInput textarea:focus {
        border-color: #00E5FF !important;
        box-shadow: 0 0 10px #00E5FF;
    }

    /* --- TOMBOL UMUM --- */
    .stButton>button {
        width: 100%;
        border-radius: 0px;
        background-color: #050505;
        color: #00E5FF;
        border: 1px solid #00E5FF;
        font-weight: bold;
        transition: 0.3s;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: #00E5FF;
        color: #000;
        box-shadow: 0 0 15px #00E5FF;
    }

    /* --- TOMBOL DASHBOARD BESAR --- */
    div[data-testid="column"] button {
        min-height: 150px; 
        width: 100%;
        font-size: 20px;
        border: 2px solid #333;
    }
    div[data-testid="column"] button:hover {
        border-color: #00E5FF;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

plt.style.use('dark_background')

try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ API Key hilang! Cek Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Error Config: {e}")
    st.stop()

model = genai.GenerativeModel('models/gemini-2.5-flash')

with st.sidebar:
    st.markdown("### 🧬 CONTROL PANEL")
    
    if st.button("➕ CHAT BARU", type="primary"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    selected = option_menu(
        menu_title=None,
        options=["Beranda", "Papan Tulis", "Statistik", "Grafik", "Ujian PDF"],
        icons=["house", "pencil", "bar-chart", "activity", "file-pdf"],
        default_index=0,
        key="main_nav",
        styles={
            "container": {"padding": "0!important", "background-color": "#000000"},
            "icon": {"color": "#00E5FF", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "5px", "color": "#fff", "background-color": "#000000"},
            "nav-link-selected": {"background-color": "#00E5FF", "color": "black", "font-weight": "bold"},
        }
    )
    
    if lottie_robot:
        st_lottie(lottie_robot, height=150, key="anim_sidebar")


if selected == "Papan Tulis":
    st.markdown("<h2 style='color:#00E5FF'>✏️ CANVAS DIGITAL</h2>", unsafe_allow_html=True)
    
    canvas_result = st_canvas(
        fill_color="rgba(0, 229, 255, 0.3)",
        stroke_width=3,
        stroke_color="#00E5FF",
        background_color="#000000",
        height=500,
        width=1200,
        drawing_mode="freedraw",
        key="canvas",
    )
    
    if st.button("KIRIM CORETAN"):
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype("uint8"))
            st.session_state.messages.append({"role": "user", "content": "[Mengirim Canvas]"})
            with st.spinner("ANALISIS VISION..."):
                try: # PENGAMAN
                    resp = model.generate_content(["Jelaskan matematika ini:", img])
                    st.session_state.messages.append({"role": "assistant", "content": resp.text})
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal terhubung ke AI: {e}")

# 
elif selected == "Statistik":
    st.markdown("<h2 style='color:#00E5FF'>📊 DATA ENGINE</h2>", unsafe_allow_html=True)
    file = st.file_uploader("Upload CSV", type=["csv"])
    if file:
        df = pd.read_csv(file)
        st.dataframe(df.head(), use_container_width=True)
        if st.button("ANALISIS DATA"):
            with st.spinner("PROCESSING..."):
                try: # PENGAMAN
                    resp = model.generate_content(f"Analisis data:\n{df.describe().to_string()}")
                    st.session_state.messages.append({"role": "assistant", "content": resp.text})
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal analisis: {e}")

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
        except Exception as e: st.error(f"Rumus Error: {e}")

elif selected == "Ujian PDF":
    st.markdown("<h2 style='color:#00E5FF'>📝 EXAM GENERATOR</h2>", unsafe_allow_html=True)
    topik = st.text_input("Topik:", "Turunan")
    
    if st.button("GENERATE PDF"):
        def create_pdf(text):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 7, text.encode('latin-1', 'replace').decode('latin-1'))
            return pdf.output(dest='S').encode('latin-1')
            
        with st.spinner("CREATING..."):
            try: # PENGAMAN lagi
                # Memanggil API api api
                resp = model.generate_content(f"Buat 3 soal matematika pilihan ganda tentang {topik} beserta kunci jawaban.")
                
                st.download_button(
                    label="DOWNLOAD PDF", 
                    data=create_pdf(resp.text), 
                    file_name="soal_matematika.pdf",
                    mime="application/pdf"
                )
                st.success("PDF Berhasil Dibuat! Silakan Download.")
                
            except Exception as e:
                st.warning("⚠️ Koneksi AI sedang sibuk. Mohon tunggu 10 detik dan coba lagi.")
                st.error(f"Detail Error: {e}")

if selected == "Beranda":
    st.markdown('<h1 style="color:#fff; font-size:3em; margin-bottom: 20px;">AI MATH ULTIMATE</h1>', unsafe_allow_html=True)
    st.write("SISTEM MATEMATIKA CERDAS. SILAKAN PILIH MODUL.")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📸\nVISION SCAN\n(Canvas & Foto)", use_container_width=True):
            st.session_state["main_nav"] = "Papan Tulis" 
            st.rerun()
    with col2:
        if st.button("📈\nAUTO GRAPH\n(Plot Rumus)", use_container_width=True):
            st.session_state["main_nav"] = "Grafik"
            st.rerun()
    with col3:
        if st.button("💾\nDATA ENGINE\n(Analisis CSV)", use_container_width=True):
            st.session_state["main_nav"] = "Statistik"
            st.rerun()
            
if prompt := st.chat_input("COMMAND INPUT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        with st.spinner("CALCULATING..."):
            try:
                resp = model.generate_content("Jawab LaTeX & Singkat: " + prompt)
                
                placeholder.markdown(resp.text)
                
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
            except Exception as e:
                st.error(f"ERROR: {e}")
