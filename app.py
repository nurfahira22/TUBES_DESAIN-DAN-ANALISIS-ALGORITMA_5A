import streamlit as st
import pandas as pd
import time

# --- SETUP HALAMAN (TAMPILAN) ---
st.set_page_config(
    page_title="Log Analyzer Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        color: white;
        background-color: #007bff; /* Warna Biru Profesional */
        border-radius: 10px;
        height: 50px; 
        width: 100%;
    }
    .reportview-container .markdown-text-container {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BAGIAN 1: LOGIKA ALGORITMA KMP ---
def compute_lps_array(pattern, M, lps):
    length = 0
    lps[0] = 0
    i = 1
    while i < M:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

def kmp_search(text, pattern):
    # --- CASE INSENSITIVE ---
    text_cmp = text.lower()
    pattern_cmp = pattern.lower()

    M = len(pattern_cmp)
    N = len(text_cmp)
    
    lps = [0] * M
    
    # Hitung LPS menggunakan pattern yang sudah dikecilkan
    compute_lps_array(pattern_cmp, M, lps)
    
    i = 0 
    j = 0 
    while i < N:
        # Bandingkan menggunakan variabel _cmp (yang huruf kecil)
        if pattern_cmp[j] == text_cmp[i]:
            i += 1
            j += 1
        
        if j == M:
            return True
            j = lps[j-1]
        elif i < N and pattern_cmp[j] != text_cmp[i]:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
    return False

# --- BAGIAN 2: UI/UX (TAMPILAN WEB) ---

# Header Utama
st.title("🔍 Sistem Deteksi Anomali Log")
st.markdown("### Menggunakan Algoritma String Matching (KMP)")
st.markdown("---")

# Sidebar (Menu Kiri)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2920/2920349.png", width=100)
    st.header("Panel Kontrol")
    
    # Upload File
    st.info("Langkah 1: Upload Data")
    uploaded_file = st.file_uploader("Pilih file log (.txt/.log)", type=["txt", "log"])
    
    # Input Keyword
    st.info("Langkah 2: Tentukan Pola")
    # Saya tambahkan catatan kecil di placeholder bahwa ini tidak case sensitive
    keyword = st.text_input("Kata Kunci Error", value="ERROR", placeholder="Misal: fatal (huruf besar/kecil sama saja)")
    
    # Tombol Eksekusi
    st.write("")
    tombol = st.button("🔍 JALANKAN ANALISIS")

# Area Utama
col1, col2 = st.columns([2, 1])

if uploaded_file is not None and tombol:
    # Baca Konten File
    content = uploaded_file.getvalue().decode("utf-8").splitlines()
    total_lines = len(content)
    
    with col1:
        st.success(f"📂 File berhasil dimuat! Total: {total_lines} baris data.")
        
        # Proses KMP dengan Loading Bar
        progress_text = "Sedang memindai pola..."
        my_bar = st.progress(0, text=progress_text)
        
        results = []
        start_time = time.time()
        
        for index, line in enumerate(content):
            # Animasi loading bar
            if index % (total_lines // 100 + 1) == 0:
                my_bar.progress((index + 1) / total_lines)
                
            # Logika Pencarian
            # kmp_search sekarang sudah menangani huruf besar/kecil di dalamnya
            if kmp_search(line, keyword):
                # Kita simpan 'line' yang ASLI (agar tampilan tetap original)
                results.append({"No": index + 1, "Isi Log Error": line.strip()})
        
        my_bar.empty() # Hilangkan loading bar setelah selesai
        end_time = time.time()
        
        # Tampilkan Hasil
        if len(results) > 0:
            st.markdown(f"### ✅ Ditemukan {len(results)} Masalah")
            st.markdown(f"⏱️ Waktu proses: **{end_time - start_time:.4f} detik**")
            
            df = pd.DataFrame(results)
            st.dataframe(
                df, 
                column_config={
                    "No": st.column_config.NumberColumn("Baris Ke-", width="small"),
                    "Isi Log Error": st.column_config.TextColumn("Detail Pesan Log", width="large")
                },
                use_container_width=True,
                height=400
            )
        else:
            st.balloons()
            st.success("🎉 Tidak ditemukan error! Sistem aman.")

    with col2:
        # Statistik Ringkas
        st.markdown("### 📊 Ringkasan")
        st.metric(label="Total Baris Diperiksa", value=total_lines)
        st.metric(label="Jumlah Error Ditemukan", value=len(results), delta_color="inverse")

elif uploaded_file is None:
    # Tampilan Awal jika belum upload
    st.warning("⚠️ Belum ada file yang diupload.")
    st.markdown("""
    **Panduan Penggunaan:**
    1. Siapkan file log server (Apache/Nginx/System).
    2. Upload melalui menu di sebelah kiri.
    3. Masukkan kata kunci (contoh: `ERROR`, `WARNING`, `FAIL`).
    4. Klik tombol **Jalankan Analisis**.
    """)