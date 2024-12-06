import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components
from screeninfo import get_monitors
import time
import os  # Untuk memanipulasi folder dan file
import json  # Untuk menyimpan riwayat dalam format JSON

# Set page config for wide layout
st.set_page_config(
    page_title="Data Analisis Detail Tindakan RANAP",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Mendapatkan ukuran layar (monitor utama)
monitor = get_monitors()[0]
screen_width = monitor.width
screen_height = monitor.height

# Menampilkan judul aplikasi
st.title("Unggah File CSV atau XLSX")

# Fungsi untuk membaca file dengan caching untuk efisiensi
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file.name.endswith("csv"):
        return pd.read_csv(uploaded_file, low_memory=False)  # Disable type inference for speed
    elif uploaded_file.name.endswith("xlsx"):
        return pd.read_excel(uploaded_file, engine='openpyxl')  # Specify engine for faster read

# Fungsi untuk menyimpan file unggahan ke dalam folder 'data'
def save_uploaded_file(uploaded_file):
    folder_path = os.path.abspath(os.path.join(os.getcwd(), "..\data\data"))  # Dapatkan path absolut folder 'data'
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    file_path = os.path.join(folder_path, uploaded_file.name)
    
    # Menyimpan file ke folder 'data'
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())  # Menulis file dalam format binary

    # Menyimpan informasi file yang diunggah dalam log history
    save_upload_history(uploaded_file.name, file_path)

    return file_path

# Fungsi untuk menyimpan riwayat unggahan file ke file JSON
def save_upload_history(file_name, file_path):
    history_file = "upload_history.json"
    
    # Memuat riwayat jika sudah ada, atau buat list kosong jika belum ada
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            upload_history = json.load(f)
    else:
        upload_history = []
    
    # Menambahkan entri riwayat baru
    upload_history.append({
        "file_name": file_name,
        "file_path": file_path,
        "upload_time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Menyimpan kembali riwayat ke dalam file JSON
    with open(history_file, "w") as f:
        json.dump(upload_history, f, indent=4)

# Fungsi untuk menampilkan riwayat file yang diunggah
def display_upload_history():
    history_file = "upload_history.json"
    
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            upload_history = json.load(f)
        
        # Membuat tampilan riwayat di sidebar dengan scroll
        st.sidebar.subheader("Riwayat File yang Diunggah")
        
        # Menambahkan gaya CSS untuk scrollable sidebar
        history_html = "<div style='height: 300px; overflow-y: scroll; padding-right: 10px;'>"
        
        for entry in upload_history:
            history_html += f"<b>{entry['file_name']}</b><br>"
            # history_html += f"Lokasi: {entry['file_path']}<br>"
            history_html += f"Waktu Unggah: {entry['upload_time']}<br>"
            history_html += "<hr>"
        
        history_html += "</div>"

        # Menampilkan HTML dengan scroll
        st.sidebar.markdown(history_html, unsafe_allow_html=True)
    else:
        st.sidebar.info("Belum ada file yang diunggah sebelumnya.")

# Sidebar content for file upload and button
st.sidebar.header("Unggah File")

# Meminta pengguna mengunggah file
uploaded_file = st.sidebar.file_uploader("Pilih file CSV atau XLSX", type=["csv", "xlsx"])

# Tombol untuk menampilkan dashboard menggunakan PyGWalker
view_dashboard = st.sidebar.button("View Dashboard")

# Tombol refresh untuk me-reset aplikasi
refresh_button = st.sidebar.button("Refresh Dashboard")

# Clear cache when refresh button is clicked
if refresh_button:
    st.cache_data.clear()  # Clear cache on refresh

# Menampilkan riwayat file yang diunggah
display_upload_history()

# Menangani file upload dan dashboard view
if uploaded_file is not None:
    # Cek ukuran file (misalnya maksimal 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        st.warning("Ukuran file terlalu besar. Mohon unggah file yang lebih kecil dari 10MB.")
    else:
        # Start the timer to measure loading time
        start_time = time.time()

        # Menyimpan file yang diunggah ke dalam folder 'data'
        saved_file_path = save_uploaded_file(uploaded_file)
        st.success(f"File berhasil diunggah dan disimpan di {saved_file_path}")

        # Membaca data menggunakan fungsi yang sudah dicache
        df = load_data(uploaded_file)

        # Measure the time taken to load data
        load_time = time.time() - start_time
        st.write(f"Data dimuat dalam {load_time:.2f} detik.")

        # Tombol untuk menampilkan dashboard menggunakan PyGWalker
        if view_dashboard:
            st.write("Memuat dashboard PyGWalker...")
            # Gunakan pyg.walk() untuk menghasilkan visualisasi PyGWalker
            html_content = pyg.walk(df).to_html()

            # Menampilkan hasil visualisasi PyGWalker dengan ukuran responsif
            components.html(html_content, height=screen_height, width=screen_width)  # Menetapkan ukuran responsif sesuai ukuran layar

        # Menampilkan data dalam bentuk tabel (menampilkan 100 baris pertama untuk optimisasi)
        st.write("Menampilkan data yang Diunggah :")
        st.dataframe(df)  # Display only top 100 rows to optimize speed
else:
    # Menampilkan pesan jika file belum diunggah
    st.info("Silakan unggah file CSV atau XLSX terlebih dahulu untuk melanjutkan.")
