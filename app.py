import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
from sklearn.linear_model import LinearRegression

# -- SETTINGS --
st.set_page_config(page_title="Yield Textile Calculator", layout="wide")

# -- CUSTOM CSS (PREMIUM INDUSTRIAL DARK + RESPONSIVE + CARD SEPARATION) --
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@800&display=swap');

    /* Sembunyikan Elemen Streamlit */
    header {visibility: hidden !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}

    /* Kunci Background Dark Mode */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #0E0E0E !important;
        background-image: linear-gradient(rgba(14, 14, 14, 0.88), rgba(14, 14, 14, 0.95)), url('https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77?q=80&w=1000&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    
    /* Tipografi Utama */
    h1, h2, h3, h4, h5, h6, label, p, .st-emotion-cache-10trblm {
        color: #E0E0E0 !important;
        font-family: 'Inter', sans-serif !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8) !important; 
    }
    span, div { font-family: 'Inter', sans-serif !important; }

    .brand-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 2.5rem; font-weight: 800; color: #FFFFFF !important;
        margin-bottom: 5px; letter-spacing: -1px; text-transform: uppercase;
    }
    .brand-subtitle { color: #888888 !important; font-size: 0.9rem; margin-bottom: 30px; }

    /* Input & Dropdown Fix */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { 
        background-color: #1A1A1A !important; border: 1px solid #444444 !important;
    }
    input, .stSelectbox div { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }

    /* Fix Dropdown Popup */
    div[data-baseweb="popover"] > div, ul[role="listbox"] { background-color: #1A1A1A !important; }
    ul[role="listbox"] li { color: #FFFFFF !important; }
    ul[role="listbox"] span { color: #FFFFFF !important; text-shadow: none !important; }

    /* Kartu Utama (Size Chart & Laporan) */
    .solid-card {
        background-color: #1A1A1A !important; border: 1px solid #333333 !important; border-radius: 8px;
        padding: 24px; margin-bottom: 25px;
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

    /* DESAIN KARTU INVENTORY DIPISAH LEGA */
    .inventory-card {
        background: #181818 !important; 
        border: 1px solid #444 !important; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 30px !important; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.5); 
    }

    .wa-btn {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: transparent !important; color: #FFFFFF !important; 
        padding: 10px 18px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; 
        border: 1px solid #2E7D32 !important; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase;
    }
    .wa-btn:hover { background-color: #2E7D32 !important; }

    .status-badge {
        padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;
        text-transform: uppercase; margin-left: 10px; display: inline-block; vertical-align: middle;
    }

    /* Responsive Mobile HP */
    @media (max-width: 768px) {
        .inventory-card { flex-direction: column; align-items: flex-start; padding: 18px; }
        .card-right { width: 100%; text-align: left; margin-top: 15px; padding-top: 15px; border-top: 1px solid #333; }
        .wa-btn { width: 100%; padding: 12px; margin-top: 10px; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE & ML LOGIC
# ==========================================
KG_TO_METER = 2.8 
DB_PRODUK_DEWASA = {
    "Kemeja": {
        "ml_kategori": 1,
        "ukuran_base": {"Lebar Dada (cm)": [48, 50, 52, 54, 56], "Panjang Baju (cm)": [68, 70, 72, 74, 76]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 8, "h": 2}, "Boxy Fit": {"w": 12, "h": -3} },
        "rekomendasi_kain": [
            {"nama": "KATUN TOYOBO FODU", "harga_kg": 95000, "stok_kg": 484.25, "karakter": "Serat padat, adem. Standar premium."},
            {"nama": "LINEN EURO PREMIUM", "harga_kg": 125000, "stok_kg": 85.50, "karakter": "Tekstur natural, sangat breathable."},
            {"nama": "OXFORD PREMIUM", "harga_kg": 85000, "stok_kg": 120.00, "karakter": "Kuat, cocok untuk seragam/kemeja kerja."}
        ]
    },
    "Kaos": {
        "ml_kategori": 7,
        "ukuran_base": {"Lebar Dada (cm)": [48, 50, 52, 54, 56], "Panjang Baju (cm)": [68, 70, 72, 74, 76]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 8, "h": 2}, "Boxy Fit": {"w": 12, "h": -3} },
        "rekomendasi_kain": [
            {"nama": "COTTON COMBED 24S", "harga_kg": 115000, "stok_kg": 320.75, "karakter": "Standar distro, menyerap keringat."},
            {"nama": "HEAVYWEIGHT COTTON 16S", "harga_kg": 135000, "stok_kg": 45.25, "karakter": "Tebal & kaku. Terbaik untuk Boxy Fit."},
            {"nama": "COTTON CVC PIQUE", "harga_kg": 110000, "stok_kg": 210.00, "karakter": "Tekstur pori, cocok untuk Polo."}
        ]
    },
    "Celana": {
        "ml_kategori": 2,
        "ukuran_base": {"Lingkar Pinggang (cm)": [76, 80, 84, 88, 92], "Panjang Celana (cm)": [98, 100, 102, 104, 106]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 4, "h": 2}, "Boxy Fit": {"w": 2, "h": 3} },
        "rekomendasi_kain": [
            {"nama": "TWILL STRETCH", "harga_kg": 110000, "stok_kg": 140.20, "karakter": "Elastis, kuat untuk celana chino."},
            {"nama": "DRILL JAPAN PREMIUM", "harga_kg": 98000, "stok_kg": 250.00, "karakter": "Serat diagonal tebal, awet."},
            {"nama": "CORDUROY LIGHT", "harga_kg": 145000, "stok_kg": 35.00, "karakter": "Garis timbul estetik, sangat mewah."}
        ]
    }
}
DB_PRODUK_ANAK = {
    "Kemeja": {
        "ml_kategori": 1,
        "ukuran_base": {"Lebar Dada (cm)": [32, 36, 39, 42], "Panjang Baju (cm)": [42, 48, 52, 56]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 4, "h": 1}, "Boxy Fit": {"w": 6, "h": -2} },
        "rekomendasi_kain": [
            {"nama": "KATUN MADINAH", "harga_kg": 95000, "stok_kg": 112.45, "karakter": "Sangat lembut, aman untuk kulit anak."},
            {"nama": "RAYON TWILL", "harga_kg": 85000, "stok_kg": 88.00, "karakter": "Sangat adem, jatuh, tidak gampang kusut."}
        ]
    },
    "Kaos": {
        "ml_kategori": 7,
        "ukuran_base": {"Lebar Dada (cm)": [32, 36, 39, 42], "Panjang Baju (cm)": [42, 48, 52, 56]},
        "offset_cutting": { "Regular Fit": {"w": 0, "h": 0}, "Oversize Fit": {"w": 4, "h": 1}, "Boxy Fit": {"w": 6, "h": -2} },
        "rekomendasi_kain": [
            {"nama": "COTTON BAMBOO", "harga_kg": 145000, "stok_kg": 75.30, "karakter": "Anti-bakteri, kualitas premium anak."},
            {"nama": "COTTON COMBED 30S", "harga_kg": 110000, "stok_kg": 240.00, "karakter": "Tipis & ringan untuk cuaca panas."},
            {"nama": "WAFFLE KNIT", "harga_kg": 120000, "stok_kg": 50.00, "karakter": "Bertekstur kotak, sangat estetik."}
        ]
    }
}

data_ml = {
    'Tinggi_cm': [160, 170, 165, 180, 150, 175, 160, 155, 185, 168, 170, 160],
    'Berat_kg': [55, 70, 60, 85, 45, 75, 65, 50, 90, 68, 70, 55],
    'Jenis_Baju': [1, 1, 2, 2, 1, 2, 7, 7, 1, 7, 1, 2],
    'Lengan': [0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0], 
    'Cutting': [0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 0, 1],
    'Kebutuhan_Kain': [1.3, 1.6, 1.25, 1.75, 1.4, 1.5, 1.0, 1.2, 1.8, 1.1, 1.5, 1.3]
}
model = LinearRegression().fit(pd.DataFrame(data_ml)[['Tinggi_cm', 'Berat_kg', 'Jenis_Baju', 'Lengan', 'Cutting']].values, pd.DataFrame(data_ml)['Kebutuhan_Kain'].values)

# -- HEADER --
st.markdown("""
<div style="margin-top: 1rem; margin-bottom: 2.5rem;">
    <div class="brand-title">Yield Textile Calculator</div>
    <div class="brand-subtitle">Sistem cerdas untuk mengestimasi kebutuhan kain, efisiensi pemotongan, dan costing produksi garmen secara presisi.</div>
</div>
""", unsafe_allow_html=True)

# -- INPUT SECTION --
st.markdown("<h4 style='border-bottom: 1px solid #333; padding-bottom: 10px;'>Data Spesifikasi</h4>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    target_pasar = st.radio("Target Pasar:", ["Dewasa", "Anak-anak"])
with c2:
    tinggi = st.number_input("Tinggi Badan (cm):", 50, 220, 170 if target_pasar == "Dewasa" else 110)
with c3:
    berat = st.number_input("Berat Badan (kg):", 10, 150, 65 if target_pasar == "Dewasa" else 20)

cc1, cc2, cc3 = st.columns(3)
with cc1:
    jenis = st.selectbox("Jenis Pakaian:", list(DB_PRODUK_DEWASA.keys()) if target_pasar == "Dewasa" else list(DB_PRODUK_ANAK.keys()))
with cc2:
    cutting = st.selectbox("Style Cutting:", ["Regular Fit", "Oversize Fit", "Boxy Fit"])
with cc3:
    jumlah_baju = st.number_input("Kuantitas Produksi:", 1, 10000, 1)

# FITUR LENGAN YANG SEMPAT HILANG UDAH BALIK DI SINI
lengan_opt = 0
if jenis not in ["Celana", "Rok"]:
    tampilan_lengan = st.radio("Sleeve / Tipe Lengan:", ["Pendek", "Panjang"], horizontal=True)
    lengan_opt = 1 if tampilan_lengan == "Panjang" else 0

if st.button("Calculate", use_container_width=True):
    DB_AKTIF = DB_PRODUK_ANAK if target_pasar == "Anak-anak" else DB_PRODUK_DEWASA
    ml_kat = DB_AKTIF[jenis]["ml_kategori"]
    cut_val = 0 if cutting == "Regular Fit" else (1 if cutting == "Oversize Fit" else 2)
    
    pred_unit = model.predict([[tinggi, berat, ml_kat, lengan_opt, cut_val]])[0]
    if target_pasar == "Anak-anak": pred_unit *= 0.45
    total_meter = pred_unit * jumlah_baju
    total_kg_req = total_meter / KG_TO_METER
    
    # -- RESULTS --
    res_col1, res_col2 = st.columns(2, gap="large")
    with res_col1:
        st.markdown(f"""
        <div class="solid-card">
            <h4 class="card-header">Laporan Material</h4>
            <div style="display:flex; justify-content:space-between;">
                <div><div class="metric-label">Unit Req.</div><div class="metric-value">{pred_unit:.2f} m</div></div>
                <div style="text-align:right;"><div class="metric-label">Total Volume</div><div class="metric-value">{total_meter:.2f} m</div></div>
            </div>
            <div class="info-box">Estimasi Berat Produksi: <strong>{total_kg_req:.2f} Kg</strong></div>
        </div>""".replace('\n', ''), unsafe_allow_html=True)
    
    with res_col2:
        size_base = DB_AKTIF[jenis]["ukuran_base"]
        offsets = DB_AKTIF[jenis]["offset_cutting"][cutting]
        size_data = {"Size": ["S", "M", "L", "XL", "XXL"] if target_pasar == "Dewasa" else ["2-4", "5-7", "8-10", "11-12"]}
        for col, base in size_base.items():
            size_data[col] = [b + (offsets["h"] if "Panjang" in col else offsets["w"]) for b in base]
        table_html = pd.DataFrame(size_data).to_html(index=False, classes="custom-table")
        st.markdown(f'<div class="solid-card" style="padding:0; overflow:hidden;"><div style="padding:20px;"><h4 class="card-header" style="border:none; margin:0;">Size Chart ({cutting})</h4></div><div style="overflow-x:auto;">{table_html}</div></div>'.replace('\n', ''), unsafe_allow_html=True)

    # -- PROCUREMENT CARDS --
    kain_cards = ""
    for k in DB_AKTIF[jenis]["rekomendasi_kain"]:
        biaya = k['harga_kg'] * total_kg_req
        stok_color = "#81C784" if k['stok_kg'] >= 50 else "#FFB74D"
        stok_status = "Optimal" if k['stok_kg'] >= 50 else "⚠️ Low Stock"
        pesan = urllib.parse.quote(f"Request PO: {k['nama']} ({total_kg_req:.2f} kg)")
        
        kain_cards += f"""
        <div class="inventory-card">
            <div class="card-left">
                <div style="font-weight:700; color:#FFF; font-size:1.1rem;">{k['nama']}</div>
                <div style="margin-top:8px; font-size:0.85rem; color:#AAA;">
                    Available Volume: <strong style="color:{stok_color};">{k['stok_kg']:.2f} kg</strong>
                    <span class="status-badge" style="border:1px solid {stok_color}; color:{stok_color}; background:rgba(0,0,0,0.3);">{stok_status}</span>
                </div>
                <div style="margin-top:6px; font-size:0.75rem; color:#666; font-style:italic;">{k['karakter']}</div>
            </div>
            <div class="card-right" style="text-align:right;">
                <div style="font-size:0.7rem; color:#888; text-transform:uppercase;">Estimated Cost</div>
                <div style="font-size:1.3rem; font-weight:700; color:#FFF;">Rp {int(biaya):,}</div>
                <a href="https://wa.me/6285318543702?text={pesan}" target="_blank" style="text-decoration:none;">
                    <div class="wa-btn">Request Material</div>
                </a>
            </div>
        </div>"""
    
    st.markdown(f"""
    <div style="margin-top:40px;">
        <h3 style="margin-bottom:30px; border-left:4px solid #D92D20; padding-left:15px;">Inventory & Procurement Analysis</h3>
        {kain_cards}
    </div>""".replace('\n', ''), unsafe_allow_html=True)
