import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
from sklearn.linear_model import LinearRegression

# -- SETTINGS --
st.set_page_config(page_title="Yield Textile Calculator", layout="wide")

# -- CUSTOM CSS (PREMIUM INDUSTRIAL DARK + RESPONSIVE + BUG FIXES) --
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@800&display=swap');

    /* 1. Sembunyikan Semua Elemen Bawaan Streamlit */
    header {visibility: hidden !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}

    /* 2. Kunci Mati Background ke Dark Mode */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #0E0E0E !important;
        background-image: linear-gradient(rgba(14, 14, 14, 0.88), rgba(14, 14, 14, 0.95)), url('https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77?q=80&w=1000&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    
    /* 3. Teks Utama (Hilangkan target 'div' global biar dropdown aman) */
    h1, h2, h3, h4, h5, h6, label, p, .st-emotion-cache-10trblm {
        color: #E0E0E0 !important;
        font-family: 'Inter', sans-serif !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8) !important; 
    }
    span, div {
        font-family: 'Inter', sans-serif !important;
    }

    .brand-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 2.5rem; font-weight: 800; color: #FFFFFF !important;
        margin-bottom: 5px; letter-spacing: -1px; text-transform: uppercase;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.9) !important; 
    }
    
    .brand-subtitle { color: #888888 !important; font-size: 0.9rem; margin-bottom: 30px; }

    /* 4. Kunci Mati Kotak Input & Dropdown */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { 
        background-color: #1A1A1A !important; 
        border: 1px solid #444444 !important;
    }
    input, .stSelectbox div {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important; 
    }

    /* === 5. FIX BUG KOTAK PILIHAN DROPDOWN (YANG BURAM TADI) === */
    div[data-baseweb="popover"] > div {
        background-color: #1A1A1A !important;
        border: 1px solid #444444 !important;
    }
    ul[role="listbox"] {
        background-color: #1A1A1A !important;
    }
    ul[role="listbox"] li {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
    }
    ul[role="listbox"] li:hover {
        background-color: #333333 !important;
    }
    ul[role="listbox"] span {
        color: #FFFFFF !important;
        text-shadow: none !important; /* Ini yang bikin buram, kita hilangkan shadow-nya */
    }

    /* 6. Desain Kartu & Elemen Lainnya */
    .solid-card {
        background-color: #1A1A1A !important; border: 1px solid #333333 !important; border-radius: 6px;
        padding: 24px; margin-bottom: 20px;
    }
    .card-header {
        font-size: 1.1rem; font-weight: 600; border-bottom: 1px solid #333333 !important;
        padding-bottom: 12px; margin-bottom: 20px; color: #FFFFFF !important;
    }
    .metric-value { font-size: 1.8rem; font-weight: 600; color: #FFFFFF !important; }
    .metric-label { font-size: 0.8rem; color: #888888 !important; text-transform: uppercase; margin-bottom: 4px; }
    
    .info-box {
        background-color: #222222 !important; border-left: 3px solid #D92D20 !important; padding: 16px;
        border-radius: 4px; font-size: 0.95rem; margin-top: 20px;
    }
    
    .stButton > button {
        background-color: #D92D20 !important; color: #ffffff !important; border: none !important;
        border-radius: 4px !important; padding: 12px 24px !important; font-weight: 500; width: 100% !important;
    }
    
    .custom-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    .custom-table th { background-color: #222222 !important; color: #A0A0A0 !important; padding: 10px; text-align: left; border-bottom: 1px solid #444444 !important; }
    .custom-table td { padding: 10px; border-bottom: 1px solid #333333 !important; color: #E0E0E0 !important; }

    .wa-link { text-decoration: none !important; display: block; width: 100%; }
    
    .wa-btn {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: transparent !important; 
        color: #FFFFFF !important; 
        padding: 8px 15px;
        border-radius: 4px; 
        font-size: 0.75rem;
        font-weight: 700; 
        border: 1px solid #2E7D32 !important; 
        margin-top: 10px;
        letter-spacing: 1px;
        transition: 0.3s ease;
        text-transform: uppercase;
        box-sizing: border-box;
    }
    .wa-btn:hover {
        background-color: #2E7D32 !important;
        border-color: #2E7D32 !important;
        color: #FFFFFF !important;
    }

    .status-badge {
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-left: 8px;
        display: inline-block;
        vertical-align: middle;
    }

    .inventory-card {
        border: 1px solid #333 !important; 
        padding: 20px; 
        border-radius: 8px; 
        margin-bottom: 15px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        background: rgba(25, 25, 25, 0.6) !important; 
        backdrop-filter: blur(10px);
    }
    .card-left { flex: 1; padding-right: 15px; }
    .card-right { text-align: right; min-width: 130px; }

    @media (max-width: 768px) {
        .brand-title { font-size: 2rem; }
        .inventory-card {
            flex-direction: column; 
            align-items: flex-start; 
            padding: 15px;
        }
        .card-left { padding-right: 0; width: 100%; }
        .card-right { 
            text-align: left; 
            width: 100%; 
            margin-top: 15px; 
            padding-top: 15px; 
            border-top: 1px solid #444 !important; 
        }
        .wa-btn { width: 100%; padding: 12px; margin-top: 12px; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE PRODUKSI (Stok dalam KG)
# ==========================================
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
        
        st.markdown(f'<div class="solid-card" style="padding:0; overflow:hidden;"><div style="padding:24px 24px 10px 24px;"><h4 class="card-header" style="border:none;">Size Chart Reference</h4></div><div style="overflow-x:auto;">{table_html}</div></div>'.replace('\n', ''), unsafe_allow_html=True)

    kain_cards = ""
    for k in DB_AKTIF[jenis]["rekomendasi_kain"]:
        biaya = k['harga_kg'] * total_kg_req
        
        # LOGIC ENTERPRISE STOK
        if k['stok_kg'] >= 50:
            stok_color = "#81C784"
            stok_status = "Optimal"
            badge_bg = "rgba(129, 199, 132, 0.15)"
        else:
            stok_color = "#FFB74D"
            stok_status = "⚠️ Low Stock"
            badge_bg = "rgba(255, 183, 77, 0.15)"
            
        pesan = urllib.parse.quote(f"Halo, saya ingin membuat Request Material (PO) untuk bahan *{k['nama']}*. Kebutuhan produksi: *{round(total_kg_req, 2)} kg*. Mohon konfirmasi ketersediaan.")
        
        kain_cards += f"""
        <div class="inventory-card">
            <div class="card-left">
                <div style="font-weight:700; color:#FFFFFF; font-size: 1rem; letter-spacing: 0.5px; text-transform: uppercase;">{k['nama']}</div>
                <div style="color:#AAAAAA; font-size:0.8rem; margin-top: 8px;">
                    Available Volume: <strong style="color:{stok_color}; margin-left:3px; font-size:0.9rem;">{k['stok_kg']:.2f} kg</strong>
                    <span class="status-badge" style="background:{badge_bg}; color:{stok_color}; border: 1px solid {stok_color};">
                        {stok_status}
                    </span>
                </div>
                <div style="color:#777; font-size:0.75rem; margin-top:6px; font-style:italic;">{k['karakter']}</div>
            </div>
            <div class="card-right">
                <div style="color:#888; font-size:0.7rem; text-transform:uppercase; margin-bottom:4px;">Estimated Cost</div>
                <div style="color:#FFFFFF; font-weight:600; font-size: 1.25rem; letter-spacing: -0.5px;">Rp {int(biaya):,}</div>
                <a href="https://wa.me/6285318543702?text={pesan}" target="_blank" class="wa-link">
                    <div class="wa-btn">Request Material</div>
                </a>
            </div>
        </div>
        """
    st.markdown(f'<div class="solid-card" style="background:transparent; border:none; padding:0;"><h4 class="card-header" style="margin-bottom:25px;">Inventory & Procurement Analysis</h4>{kain_cards}</div>'.replace('\n', ''), unsafe_allow_html=True)
