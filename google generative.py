import streamlit as st
import google.generativeai as genai
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import time

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AI Math Ultimate",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. LOGIKA ANIMASI & CSS CANGGIH ---
def inject_custom_css(is_dark):
    # Tentukan warna berdasarkan mode
    if is_dark:
        bg_color = "#0e1117"
        text_color = "#E0E0E0"
        card_bg = "#1e232f"
        border_color = "#2b313e"
        accent_color = "#00DFD8" # Cyan Neon
        shadow = "rgba(0,0,0,0.5)"
    else:
        bg_color = "#ffffff"
        text_color = "#000000"
        card_bg = "#f0f2f6"
        border_color = "#dce0e6"
        accent_color = "#007CF0" # Blue
        shadow = "rgba(0,0,0,0.1)"

    # Inject CSS dengan Animasi
    st.markdown(f"""
    <style>
        /* 1. Animasi Masuk (Fade In) */
        @keyframes fadeIn {{
            0% {{ opacity: 0; transform: translateY(20px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            animation: fadeIn 0.8s ease-out;
        }}

        /* 2. Tombol yang 'Membal' saat diklik */
        .stButton>button {{
            transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border-radius: 12px;
            border: 2px solid transparent;
        }}
        .stButton>button:hover {{
            transform: scale(1.05);
            border-color: {accent_color};
            box-shadow: 0 5px 15px {shadow};
            color: {accent_color};
        }}
        .stButton>button:active {{
            transform: scale(0.95);
        }}

        /* 3. Kartu Dashboard Melayang */
        .dashboard-card {{
            background-color: {card_bg};
            padding: 25px;
            border-radius: 20px;
            border: 1px solid {border_color};
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 4px 6px {shadow};
        }}
        .dashboard-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 10px 20px {shadow};
            border-color: {accent_color};
        }}

        /* 4. Judul Gradient Animasi */
        .title-animate {{
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            font-size: 3.5em;
        }}
        @keyframes gradient {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        /* 5. Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {bg_color};
            border-right: 1px solid {border_color};
        }}
        
    </style>
    
    <script>
    const cursor = document.createElement('div');
    cursor.style.width = '20px';
    cursor.style.height = '20px';
    cursor.style.border = '2px solid {accent_color}';
    cursor.style.borderRadius = '50%';
    cursor.style.position = 'fixed';
    cursor.style.pointerEvents = 'none';
    cursor.style.zIndex = '9999';
    cursor.style.transition = 'transform 0.1s';
    document.body.appendChild(cursor);

    document.addEventListener('mousemove', (e) => {{
        cursor.style.left = e.clientX - 10 + 'px';
        cursor.style.top = e.clientY - 10 + 'px';
    }});
    
    document.addEventListener('mousedown', () => {{
        cursor.style.transform = 'scale(0.8)';
        cursor.style.background = '{accent_color}';
        cursor.style.opacity = '0.5';
    }});
    
    document.addEventListener('mouseup', () => {{
        cursor.style.transform = 'scale(1)';
        cursor.style.background = 'transparent';
        cursor.style.opacity = '1';
    }});
    </script>
    """, unsafe_allow_html=True)
    
    # Set Matplotlib Theme
    if is_dark:
        plt.style.use('dark_background')
    else:
        plt.style.use('default')

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

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan")
    
    # === SWITCH MODE TERANG/GELAP (YANG ANDA MINTA) ===
    # Kita simpan state di session agar tidak reset saat refresh
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    
    dark_mode = st.toggle("🌙 Mode Gelap / Terang", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dark_mode # Update state
    
    # PANGGIL FUNGSI CSS DI SINI
    inject_custom_css(dark_mode)
    
    st.divider()
    st.markdown("### 🧰 Menu Alat")
    
    menu = st.radio(
        "Navigasi:",
        ["🏠 Beranda", "✏️ Papan Tulis", "📊 Statistik", "📈 Grafik", "📝 Ujian PDF"],
        index=0
    )
    
    st.divider()
    
    # === FITUR-FITUR SIDEBAR ===
    # 1. Papan Tulis
    if menu == "✏️ Papan Tulis":
        st.subheader("Canvas Digital")
        # Warna canvas menyesuaikan mode
        c_bg = "#000" if dark_mode else "#fff"
        c_stroke = "#fff" if dark_mode else "#000"
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3, stroke_color=c_stroke,
            background_color=c_bg,
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
                fig, ax = plt.subplots(figsize=(4, 3))
                
                # Warna Grafik Custom
                line_c = '#00DFD8' if dark_mode else '#007CF0'
                grid_c = '#444' if dark_mode else '#ddd'
                
                if dark_mode:
                    fig.patch.set_facecolor('#0e1117')
                    ax.set_facecolor('#0e1117')
                    ax.spines['bottom'].set_color('white')
                    ax.spines['left'].set_color('white')
                    ax.tick_params(colors='white')
                
                ax.plot(x, y, color=line_c, linewidth=2)
                ax.grid(True, color=grid_c, linestyle='--', alpha=0.5)
                # Hilangkan border atas/kanan
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                st.pyplot(fig)
            except: st.error("Rumus Error")

    # 4. PDF
    elif menu == "📝 Ujian PDF":
        def create_pdf(text):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            clean_text = text.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 7, clean_text)
            return pdf.output(dest='S').encode('latin-1')
            
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

# --- 5. AREA UTAMA (HERO SECTION ANIMATED) ---

# Judul dengan Animasi Gradient Bergerak
st.markdown('<h1 class="title-animate">✨ AI Math Ultimate</h1>', unsafe_allow_html=True)

# === LAYAR DASHBOARD (Jika chat kosong) ===
if not st.session_state.messages:
    # Kartu Intro
    st.markdown(f"""
    <div style='background-color: {"#1e232f" if dark_mode else "#f0f2f6"}; padding: 20px; border-radius: 15px; border-left: 5px solid {"#00DFD8" if dark_mode else "#007CF0"}; animation: fadeIn 1s ease-out;'>
        <h4>👋 Halo, Master Matematika!</h4>
        <p>Saya siap membantu. Coba hover mouse ke kartu di bawah untuk melihat efeknya.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("") 
    
    # 3 Kolom Kartu Pintar (Floating Cards)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h1>📸</h1>
            <h3>Vision AI</h3>
            <p>Upload foto soal, saya baca.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h1>📈</h1>
            <h3>Auto Graph</h3>
            <p>Plot rumus matematika indah.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="dashboard-card">
            <h1>📝</h1>
            <h3>Exam Gen</h3>
            <p>Bikin soal ujian + PDF.</p>
        </div>
        """, unsafe_allow_html=True)

# === TAMPILKAN CHAT ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. INPUT UTAMA ---
if prompt := st.chat_input("Ketik soal matematika..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Proses AI
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_msg = st.session_state.messages[-1]["content"]
    with st.chat_message("user"):
        st.markdown(user_msg)
        
    with st.chat_message("assistant"):
        with st.spinner("Sedang berpikir..."):
            try:
                sys = "Anda adalah asisten matematika jenius. Jawab dengan LaTeX ($$). Jelaskan step-by-step."
                response = model.generate_content(sys + user_msg)
                
                # Efek mengetik (Typing Effect) sederhana
                placeholder = st.empty()
                full_response = response.text
                
                # Menampilkan langsung (streaming effect di Streamlit butuh code khusus, kita tampilkan langsung agar cepat)
                placeholder.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error("Maaf, terjadi kesalahan koneksi.")
