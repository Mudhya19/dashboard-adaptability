import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components
from screeninfo import get_monitors
import time
import os
import json

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
def load_data(file_path, file_type):
    if file_type == "csv":
        return pd.read_csv(file_path, low_memory=False)
    elif file_type == "xlsx":
        return pd.read_excel(file_path, engine='openpyxl')

# Fungsi untuk menyimpan file unggahan ke dalam folder 'data'
def save_uploaded_file(uploaded_file):
    folder_path = os.path.abspath(os.path.join(os.getcwd(), "data"))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    save_upload_history(uploaded_file.name, file_path)
    return file_path

# Fungsi untuk menyimpan riwayat unggahan file ke file JSON
def save_upload_history(file_name, file_path):
    history_file = "upload_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            upload_history = json.load(f)
    else:
        upload_history = []
    upload_history.append({
        "file_name": file_name,
        "file_path": file_path,
        "upload_time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(history_file, "w") as f:
        json.dump(upload_history, f, indent=4)

# Fungsi untuk memuat file dari riwayat
def load_previous_files():
    history_file = "upload_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            return json.load(f)
    return []

# Menampilkan riwayat file yang diunggah di sidebar
def display_upload_history():
    upload_history = load_previous_files()
    if upload_history:
        st.sidebar.subheader("Riwayat File yang Diunggah")
        history_html = "<div style='height: 300px; overflow-y: scroll; padding-right: 10px;'>"
        for entry in reversed(upload_history):  # Menampilkan file terbaru di atas
            history_html += f"<b>{entry['file_name']}</b><br>"
            history_html += f"Waktu Unggah: {entry['upload_time']}<br>"
            history_html += "<hr>"
        history_html += "</div>"
        st.sidebar.markdown(history_html, unsafe_allow_html=True)
    else:
        st.sidebar.info("Belum ada file yang diunggah sebelumnya.")

# Menampilkan dropdown untuk memilih file dari riwayat
def display_previous_files():
    upload_history = load_previous_files()
    if upload_history:
        st.sidebar.subheader("Pilih File dari Riwayat")
        file_names = ["--Pilih file--"] + [entry["file_name"] for entry in reversed(upload_history)]
        selected_file_name = st.sidebar.selectbox("Pilih file:", file_names)
        if selected_file_name != "--Pilih file--":
            for entry in upload_history:
                if entry["file_name"] == selected_file_name:
                    return entry["file_path"]
    return None

# Sidebar content for file upload and button
st.sidebar.header("Unggah File")
uploaded_file = st.sidebar.file_uploader("Pilih file CSV atau XLSX", type=["csv", "xlsx"])
view_dashboard = st.sidebar.button("View Dashboard")
refresh_button = st.sidebar.button("Refresh Dashboard")

if refresh_button:
    st.cache_data.clear()

# Menampilkan pilihan file dari riwayat
selected_file_path = display_previous_files()

# Menampilkan riwayat unggahan
display_upload_history()

if uploaded_file is not None or selected_file_path is not None:
    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        file_type = "csv" if uploaded_file.name.endswith("csv") else "xlsx"
    else:
        file_path = selected_file_path
        file_type = "csv" if file_path.endswith("csv") else "xlsx"
    
    df = load_data(file_path, file_type)
    st.success(f"File berhasil dimuat: {file_path}")
    
    if view_dashboard:
        st.write("Memuat dashboard PyGWalker...")
        html_content = pyg.walk(df).to_html()
        components.html(html_content, height=screen_height, width=screen_width)
    
    st.write("Menampilkan data yang diunggah:")
    st.dataframe(df)
else:
    st.info("Silakan unggah file CSV atau XLSX terlebih dahulu atau pilih dari riwayat.")
