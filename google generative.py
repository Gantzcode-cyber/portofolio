import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AI Math Master",
    page_icon="🎓",
    layout="centered"
)

# --- KONFIGURASI API KEY (AMAN) ---
# Mengambil key dari Secrets Streamlit Cloud
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key belum diatur! Mohon atur di menu Settings > Secrets di Streamlit Cloud.")
    st.stop()

# Menggunakan Model yang support Teks & Gambar
model = genai.GenerativeModel('gemini-pro')

# --- INISIALISASI SESSION STATE (MEMORY) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya Math Master. Kirim foto soal atau ketik pertanyaan matematika Anda di sini."}
    ]

# --- FUNGSI DOWNLOAD RIWAYAT CHAT ---
def get_chat_history_text():
    chat_text = "📚 CATATAN BELAJAR MATEMATIKA\n\n"
    for msg in st.session_state.messages:
        role = "🤖 AI" if msg["role"] == "assistant" else "👤 SAYA"
        # Membersihkan pesan dari gambar (jika ada) agar teksnya rapi
        content = msg["content"]
        chat_text += f"{role}:\n{content}\n\n{'-'*30}\n\n"
    return chat_text

# --- SIDEBAR (FITUR TAMBAHAN) ---
with st.sidebar:
    st.header("🧰 Kotak Perkakas")
    
    # 1. Fitur Upload Gambar
    st.subheader("📸 Scan Soal")
    uploaded_file = st.file_uploader("Upload foto soal (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    image_prompt = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview Soal", use_container_width=True)
        
        if st.button("🔍 Bedah Soal Ini"):
            # Flag untuk memproses gambar
            image_prompt = image

    st.divider()

    # 2. Fitur Download
    st.subheader("💾 Simpan Catatan")
    st.download_button(
        label="Download Riwayat Chat (.txt)",
        data=get_chat_history_text(),
        file_name="catatan_matematika.txt",
        mime="text/plain"
    )

    st.divider()
    
    # 3. Reset
    if st.button("🗑️ Hapus Semua Chat"):
        st.session_state.messages = []
        st.rerun()

# --- AREA CHAT UTAMA ---
st.title("🎓 AI Math Tutor")
st.caption("Solusi langkah demi langkah dengan penjelasan LaTeX")

# Menampilkan Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- LOGIKA PEMROSESAN (GAMBAR & TEKS) ---

# Skenario 1: User menekan tombol "Bedah Soal Ini" (Gambar)
if image_prompt:
    with st.chat_message("user"):
        st.write("Menganalisis gambar yang diupload...")
        st.image(image_prompt, width=200)
    
    st.session_state.messages.append({"role": "user", "content": "[Mengirim Foto Soal]"})
    
    with st.spinner("Sedang melihat dan menghitung..."):
        try:
            prompt_khusus = """
            Kamu adalah ahli matematika. Analisis gambar ini:
            1. Tulis ulang soalnya dalam teks.
            2. Jelaskan langkah penyelesaiannya satu per satu.
            3. Gunakan format LaTeX untuk rumus (contoh: $\frac{a}{b}$).
            """
            response = model.generate_content([prompt_khusus, image_prompt])
            bot_reply = response.text
            
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            st.error(f"Error menganalisis gambar: {e}")

# Skenario 2: User mengetik teks biasa
if prompt := st.chat_input("Ketik soal matematika..."):
    # Tampilkan input user
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Proses AI
    with st.spinner("Sedang berpikir..."):
        try:
            # Context agar AI fokus ke matematika
            system_prompt = "Jawablah sebagai guru matematika yang sabar. Gunakan LaTeX untuk rumus. Jelaskan step-by-step.\n\nPertanyaan: "
            response = model.generate_content(system_prompt + prompt)
            bot_reply = response.text
            
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            st.error(f"Error koneksi: {e}")
