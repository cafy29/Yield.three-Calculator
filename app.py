import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
from sklearn.linear_model import LinearRegression

# -- SETTINGS --
st.set_page_config(page_title="Yield Textile Calculator", layout="wide")

# -- CUSTOM CSS (PREMIUM INDUSTRIAL DARK) --
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@800&display=swap');/* Sembunyikan Header dan Menu Default Streamlit */
header {visibility: hidden !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}

    /* 1. Base Theme dengan Gambar Kain + Kaca Film Gelap */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(14, 14, 14, 0.88), rgba(14, 14, 14, 0.95)), url('https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77?q=80&w=1000&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    
    /* 2. Tambahan Text-Shadow Biar Tulisan Nyala dan Gak Tenggelam */
    h1, h2, h3, h4, h5, h6, label, p, span {
        color: #E0E0E0 !important;
        font-family: 'Inter', sans-serif !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8) !important; 
    }

    .brand-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 2.8rem; font-weight: 800; color: #FFFFFF !important;
        margin-bottom: 5px; letter-spacing: -1px; text-transform: uppercase;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.9) !important; /* Bayangan ekstra buat judul utama */
    }
    }
    h1, h2, h3, h4, h5, h6, label, p, div, span, .st-emotion-cache-10trblm {
        color: #E0E0E0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    .brand-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 2.8rem; font-weight: 800; color: #FFFFFF !important;
        margin-bottom: 5px; letter-spacing: -1px; text-transform: uppercase;
    }
    .brand-subtitle { color: #888888 !important; font-size: 1rem; margin-bottom: 30px; }

    .solid-card {
        background-color: #1A1A1A; border: 1px solid #333333; border-radius: 6px;
        padding: 24px; margin-bottom: 20px;
    }
    .card-header {
        font-size: 1.1rem; font-weight: 600; border-bottom: 1px solid #333333;
        padding-bottom: 12px; margin-bottom: 20px; color: #FFFFFF !important;
    }
    .metric-value { font-size: 1.8rem; font-weight: 600; color: #FFFFFF !important; }
    .metric-label { font-size: 0.8rem; color: #888888 !important; text-transform: uppercase; margin-bottom: 4px; }
    
    .info-box {
        background-color: #222222; border-left: 3px solid #D92D20; padding: 16px;
        border-radius: 4px; font-size: 0.95rem; margin-top: 20px;
    }
    
    .stButton > button {
        background-color: #D92D20 !important; color: #ffffff !important; border: none !important;
        border-radius: 4px !important; padding: 12px 24px !important; font-weight: 500; width: 100% !important;
    }
    
    .custom-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    .custom-table th { background-color: #222222; color: #A0A0A0; padding: 12px; text-align: left; border-bottom: 1px solid #444444; }
    .custom-table td { padding: 12px; border-bottom: 1px solid #333333; }

    div[data-baseweb="input"], [data-baseweb="select"] { 
        background-color: #1A1A1A !important; border: 1px solid #444444 !important;
    }
    
    .wa-link { text-decoration: none !important; }
    .wa-btn {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #25D366; color: #FFFFFF !important; padding: 10px 20px;
        border-radius: 4px; text-decoration: none !important; font-size: 0.9rem;
        font-weight: 600; transition: background 0.2s; border: none; margin-top: 10px;
    }
    .wa-btn:hover { background-color: #1EBE53; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE PRODUKSI (Stok dalam KG)
# ==========================================
# Konversi standar: 1 Kg Cotton Combed 24s ~ 2.4 - 3 Meter (tergantung setting mesin)
KG_TO_METER = 2.8 

DB_PRODUK_DEWASA = {
    "Kemeja": {
        "ml_kategori": 1,
        "ukuran_base": {"Lebar Dada (cm)": [48, 50, 52, 54, 56], "Panjang Baju (cm)": [68, 70, 72, 74, 76]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 8, "h": 2}, "Boxy Fit": {"w": 12, "h": -3} },
        "rekomendasi_kain": [
            {"nama": "Katun Toyobo Fodu", "harga_kg": 95000, "stok_kg": 484.25, "karakter": "Serat padat, adem. Standar premium."},
            {"nama": "Linen Euro Premium", "harga_kg": 125000, "stok_kg": 85.50, "karakter": "Tekstur natural, sangat breathable."},
            {"nama": "Oxford Premium", "harga_kg": 85000, "stok_kg": 120.00, "karakter": "Kuat, cocok untuk seragam/kemeja kerja."}
        ]
    },
    "Kaos": {
        "ml_kategori": 7,
        "ukuran_base": {"Lebar Dada (cm)": [48, 50, 52, 54, 56], "Panjang Baju (cm)": [68, 70, 72, 74, 76]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 8, "h": 2}, "Boxy Fit": {"w": 12, "h": -3} },
        "rekomendasi_kain": [
            {"nama": "Cotton Combed 24s", "harga_kg": 115000, "stok_kg": 320.75, "karakter": "Standar distro, menyerap keringat."},
            {"nama": "Heavyweight Cotton 16s", "harga_kg": 135000, "stok_kg": 45.25, "karakter": "Tebal & kaku. Terbaik untuk Boxy Fit."},
            {"nama": "Cotton CVC Pique", "harga_kg": 110000, "stok_kg": 210.00, "karakter": "Tekstur pori (bolong-bolong), cocok untuk Polo."}
        ]
    },
    "Celana": {
        "ml_kategori": 2,
        "ukuran_base": {"Lingkar Pinggang (cm)": [76, 80, 84, 88, 92], "Panjang Celana (cm)": [98, 100, 102, 104, 106]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 4, "h": 2}, "Boxy Fit": {"w": 2, "h": 3} },
        "rekomendasi_kain": [
            {"nama": "Twill Stretch", "harga_kg": 110000, "stok_kg": 140.20, "karakter": "Elastis, kuat untuk celana chino."},
            {"nama": "Drill Japan Premium", "harga_kg": 98000, "stok_kg": 250.00, "karakter": "Serat diagonal tebal, awet."},
            {"nama": "Corduroy Light", "harga_kg": 145000, "stok_kg": 35.00, "karakter": "Garis timbul estetik, sangat mewah."}
        ]
    }
}

DB_PRODUK_ANAK = {
    "Kemeja": {
        "ml_kategori": 1,
        "ukuran_base": {"Lebar Dada (cm)": [32, 36, 39, 42], "Panjang Baju (cm)": [42, 48, 52, 56]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 4, "h": 1}, "Boxy Fit": {"w": 6, "h": -2} },
        "rekomendasi_kain": [
            {"nama": "Katun Madinah", "harga_kg": 95000, "stok_kg": 112.45, "karakter": "Sangat lembut, aman untuk kulit anak."},
            {"nama": "Rayon Twill", "harga_kg": 85000, "stok_kg": 88.00, "karakter": "Sangat adem, jatuh, tidak gampang kusut."}
        ]
    },
    "Kaos": {
        "ml_kategori": 7,
        "ukuran_base": {"Lebar Dada (cm)": [32, 36, 39, 42], "Panjang Baju (cm)": [42, 48, 52, 56]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 4, "h": 1}, "Boxy Fit": {"w": 6, "h": -2} },
        "rekomendasi_kain": [
            {"nama": "Cotton Bamboo", "harga_kg": 145000, "stok_kg": 75.30, "karakter": "Anti-bakteri, kualitas premium anak."},
            {"nama": "Cotton Combed 30s", "harga_kg": 110000, "stok_kg": 240.00, "karakter": "Tipis & ringan untuk cuaca panas."},
            {"nama": "Waffle Knit", "harga_kg": 120000, "stok_kg": 50.00, "karakter": "Bertekstur kotak, sangat estetik."}
        ]
    }
}

# -- MODEL --
data_ml = {
    'Tinggi_cm': [160, 170, 165, 180, 150, 175, 160, 155, 185, 168, 170, 160],
    'Berat_kg': [55, 70, 60, 85, 45, 75, 65, 50, 90, 68, 70, 55],
    'Jenis_Baju': [1, 1, 2, 2, 1, 2, 7, 7, 1, 7, 1, 2],
    'Lengan': [0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0], 
    'Cutting': [0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 1],
    'Kebutuhan_Kain': [1.3, 1.6, 1.25, 1.75, 1.4, 1.5, 1.0, 1.2, 1.8, 1.1, 1.5, 1.3]
}
model = LinearRegression().fit(pd.DataFrame(data_ml)[['Tinggi_cm', 'Berat_kg', 'Jenis_Baju', 'Lengan', 'Cutting']].values, pd.DataFrame(data_ml)['Kebutuhan_Kain'].values)

st.markdown("""
<div style="margin-top: 1rem; margin-bottom: 2.5rem;">
    <div class="brand-title">Yield Textile Calculator</div>
    <div class="brand-subtitle">Sistem cerdas untuk mengestimasi kebutuhan kain, efisiensi pemotongan, dan costing produksi garmen secara presisi.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<h4 style='border-bottom: 1px solid #333; padding-bottom: 10px;'>Data Spesifikasi</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    target_pasar = st.radio("Target Pasar:", ["Dewasa", "Anak-anak"])
with c2:
    def_tinggi = 170 if target_pasar == "Dewasa" else 110
    tinggi = st.number_input("Tinggi Badan (cm):", 50, 220, def_tinggi)
with c3:
    def_berat = 65 if target_pasar == "Dewasa" else 20
    berat = st.number_input("Berat Badan (kg):", 10, 150, def_berat)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='border-bottom: 1px solid #333; padding-bottom: 10px;'>Detail Pesanan</h4>", unsafe_allow_html=True)
cc1, cc2, cc3 = st.columns(3)
with cc1:
    jenis = st.selectbox("Jenis Pakaian:", list(DB_PRODUK_DEWASA.keys()) if target_pasar == "Dewasa" else list(DB_PRODUK_ANAK.keys()))
with cc2:
    cutting = st.selectbox("Style Cutting:", ["Regular Fit", "Oversize Fit", "Boxy Fit"])
with cc3:
    jumlah_baju = st.number_input("Kuantitas Produksi:", min_value=1, value=1)

lengan_opt = 0
if jenis not in ["Celana", "Rok"]:
    tampilan_lengan = st.radio("Sleeve / Tipe Lengan:", ["Pendek", "Panjang"], horizontal=True)
    lengan_opt = 1 if tampilan_lengan == "Panjang" else 0

if st.button("Calculate", use_container_width=True):
    DB_AKTIF = DB_PRODUK_ANAK if target_pasar == "Anak-anak" else DB_PRODUK_DEWASA
    ml_kat = DB_AKTIF[jenis]["ml_kategori"]
    cut_val = 0 if cutting == "Regular Fit" else (1 if cutting == "Oversize Fit" else 2)
    
    pred_base = model.predict([[tinggi, berat, ml_kat, lengan_opt, cut_val]])[0]
    pred_unit = max(0.4, pred_base * 0.45) if target_pasar == "Anak-anak" else pred_base
    total_meter = pred_unit * jumlah_baju
    total_yard = total_meter * 1.0936
    total_kg_req = total_meter / KG_TO_METER
    
    res_col1, res_col2 = st.columns([1, 1], gap="large")
    
    with res_col1:
        st.markdown(f"""
        <div class="solid-card">
            <h4 class="card-header">Laporan Material</h4>
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div>
                    <div class="metric-label">Unit Req.</div>
                    <div class="metric-value">{round(pred_unit, 2)} <span style="font-size:1rem; color:#888;">m</span></div>
                </div>
                <div style="text-align: right;">
                    <div class="metric-label">Total Volume</div>
                    <div style="display:flex; gap:15px; justify-content: flex-end; align-items: baseline;">
                        <div class="metric-value">{round(total_meter, 2)} <span style="font-size:1rem; font-weight:400; color:#888;">m</span></div>
                        <div class="metric-value">{round(total_yard, 2)} <span style="font-size:1rem; font-weight:400; color:#888;">yd</span></div>
                    </div>
                </div>
            </div>
            <div class="info-box">
                Estimasi Berat Produksi: <strong>{round(total_kg_req, 2)} Kg</strong>.
            </div>
        </div>
        """.replace('\n', ''), unsafe_allow_html=True)
        
    with res_col2:
        size_base = DB_AKTIF[jenis]["ukuran_base"]
        offsets = DB_AKTIF[jenis]["offset_cutting"][cutting]
        size_labels = ["2-4 Thn", "5-7 Thn", "8-10 Thn", "11-12 Thn"] if target_pasar == "Anak-anak" else ["S", "M", "L", "XL", "XXL"]
        size_data = {"Size": size_labels}
        for kolom, ukuran_list in size_base.items():
            adj = [u + offsets["h"] if "Panjang" in kolom else u + offsets["w"] for u in ukuran_list]
            size_data[kolom] = adj
        table_html = pd.DataFrame(size_data).to_html(index=False, classes="custom-table")
        st.markdown(f'<div class="solid-card" style="padding:0; overflow:hidden;"><div style="padding:24px 24px 10px 24px;"><h4 class="card-header" style="border:none;">Size Chart Reference</h4></div>{table_html}</div>'.replace('\n', ''), unsafe_allow_html=True)

    kain_cards = ""
    for k in DB_AKTIF[jenis]["rekomendasi_kain"]:
        biaya = k['harga_kg'] * total_kg_req
        stok_color = "#12B76A" if k['stok_kg'] >= total_kg_req else "#F04438"
        pesan = urllib.parse.quote(f"Halo, saya mau pesan bahan *{k['nama']}* untuk produksi *{jenis}* ({target_pasar}). Berat kebutuhan *{round(total_kg_req, 2)} kg*. Apakah stok ready?")
        
        kain_cards += f"""
        <div style="border:1px solid #333; padding:16px; border-radius:4px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; background:#151515;">
            <div>
                <div style="font-weight:600; color:#FFF; font-size: 1.05rem;">{k['nama']}</div>
                <div style="color:#888; font-size:0.85rem; margin-top: 4px;">Stok: <strong style="color:{stok_color};">{k['stok_kg']:.2f} kg</strong></div>
            </div>
            <div style="text-align:right;">
                <div style="color:#FFF; font-weight:600; font-size: 1.2rem;">Rp {int(biaya):,}</div>
                <a href="https://wa.me/6285318543702?text={pesan}" target="_blank" class="wa-link">
                    <div class="wa-btn">Order Bahan</div>
                </a>
            </div>
        </div>
        """
    st.markdown(f'<div class="solid-card"><h4 class="card-header">Ketersediaan Stok & Costing</h4>{kain_cards}</div>'.replace('\n', ''), unsafe_allow_html=True)
