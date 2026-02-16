import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import os
import io
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_CORRECTO = "admin"
PASSWORD_CORRECTO = "ministros2024"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="SIGEME ✦ Distrito Sur Fronterizo",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DISEÑO CSS PREMIUM (optimizado para rendimiento) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;500;600;700;800&display=swap');
    
    /* Variables de color premium */
    :root {
        --primary-950: #0a1a2f;
        --primary-900: #0f2b44;
        --primary-800: #1a3f60;
        --primary-700: #25537c;
        --primary-600: #2f6798;
        --gold-400: #e6b422;
        --gold-500: #d4a11e;
        --gold-600: #b3891a;
        --neutral-50: #fafcff;
        --neutral-100: #f2f5fc;
        --neutral-200: #e9eef7;
        --neutral-300: #dce3f0;
        --neutral-400: #b0c0da;
        --neutral-500: #8193b9;
        --neutral-600: #5f7094;
        --neutral-700: #435475;
        --neutral-800: #2f3d58;
        --neutral-900: #1e2840;
        --success: #2ecc71;
        --warning: #f39c12;
        --danger: #e74c3c;
        --info: #3498db;
    }
    
    /* Estilos base */
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(145deg, var(--neutral-50) 0%, var(--neutral-100) 50%, var(--neutral-200) 100%);
        position: relative;
    }
    
    /* Efecto de fondo sutil */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(230, 180, 34, 0.02) 0%, transparent 30%),
            radial-gradient(circle at 80% 70%, rgba(47, 103, 152, 0.02) 0%, transparent 40%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Header espectacular con efecto 3D */
    .hero-premium {
        position: relative;
        background: linear-gradient(165deg, var(--primary-950) 0%, var(--primary-800) 50%, var(--primary-700) 100%);
        padding: 4rem 3rem;
        border-radius: 40px;
        margin-bottom: 3rem;
        overflow: hidden;
        box-shadow: 0 30px 45px -20px rgba(10, 26, 47, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.15);
        transform-style: preserve-3d;
        perspective: 1000px;
    }
    
    .hero-premium::before {
        content: '';
        position: absolute;
        top: -20%;
        left: -10%;
        width: 50%;
        height: 140%;
        background: linear-gradient(90deg, rgba(230, 180, 34, 0.15) 0%, transparent 90%);
        transform: rotate(15deg);
        animation: lightSweep 12s infinite linear;
    }
    
    .hero-premium::after {
        content: '';
        position: absolute;
        bottom: -20%;
        right: -10%;
        width: 50%;
        height: 140%;
        background: linear-gradient(270deg, rgba(255, 255, 255, 0.1) 0%, transparent 90%);
        transform: rotate(-15deg);
        animation: lightSweepReverse 12s infinite linear;
    }
    
    @keyframes lightSweep {
        0% { left: -10%; opacity: 0; }
        50% { opacity: 1; }
        100% { left: 60%; opacity: 0; }
    }
    
    @keyframes lightSweepReverse {
        0% { right: -10%; opacity: 0; }
        50% { opacity: 1; }
        100% { right: 60%; opacity: 0; }
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        text-align: center;
        transform: translateZ(20px);
    }
    
    .hero-title {
        font-size: 6rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #ffffff 0%, var(--gold-400) 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 10px 30px rgba(230, 180, 34, 0.3);
        letter-spacing: -2px;
        animation: titleGlow 3s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(230, 180, 34, 0.3)); }
        50% { filter: drop-shadow(0 0 40px rgba(230, 180, 34, 0.6)); }
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        color: rgba(255, 255, 255, 0.95);
        margin-top: 0.5rem;
        letter-spacing: 4px;
        text-transform: uppercase;
    }
    
    .hero-subtitle span {
        display: inline-block;
        animation: floatText 3s ease-in-out infinite;
    }
    
    @keyframes floatText {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(230, 180, 34, 0.3);
        border-radius: 60px;
        padding: 0.7rem 2rem;
        margin-top: 2rem;
        color: white;
        font-weight: 300;
        font-size: 1rem;
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.3);
    }
    
    /* Tarjetas glassmorphism premium */
    .glass-premium {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 30px;
        padding: 2rem;
        box-shadow: 
            0 20px 40px -15px rgba(10, 26, 47, 0.2),
            0 0 0 1px rgba(230, 180, 34, 0.1) inset;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .glass-premium:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 
            0 30px 50px -20px rgba(47, 103, 152, 0.3),
            0 0 0 2px rgba(230, 180, 34, 0.3) inset;
    }
    
    .glass-premium::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.8) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.6s;
        pointer-events: none;
    }
    
    .glass-premium:hover::before {
        opacity: 0.2;
    }
    
    /* Métricas 3D */
    .metric-3d {
        background: linear-gradient(135deg, var(--primary-800) 0%, var(--primary-950) 100%);
        border-radius: 25px;
        padding: 2rem;
        border: 1px solid rgba(230, 180, 34, 0.4);
        position: relative;
        transform-style: preserve-3d;
        transform: perspective(1000px) rotateX(2deg);
        box-shadow: 
            0 20px 30px -10px rgba(0, 0, 0, 0.4),
            0 -5px 15px -5px rgba(230, 180, 34, 0.2) inset;
    }
    
    .metric-3d::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--gold-400), transparent);
        animation: shimmerMetric 2.5s infinite;
    }
    
    @keyframes shimmerMetric {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .metric-value {
        font-size: 3.2rem;
        font-weight: 800;
        color: white;
        line-height: 1;
        margin-bottom: 0.3rem;
        text-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    .metric-label {
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 300;
    }
    
    /* Avatar 3D giratorio */
    .avatar-3d {
        width: 200px;
        height: 200px;
        border-radius: 35px;
        background: linear-gradient(145deg, var(--primary-600), var(--primary-800));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 5.5rem;
        color: white;
        border: 4px solid var(--gold-400);
        box-shadow: 0 25px 35px -10px rgba(47, 103, 152, 0.5);
        position: relative;
        overflow: hidden;
        animation: avatarFloat 6s ease-in-out infinite;
        transform-style: preserve-3d;
    }
    
    @keyframes avatarFloat {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        25% { transform: translateY(-8px) rotate(2deg); }
        75% { transform: translateY(8px) rotate(-2deg); }
    }
    
    .avatar-3d::after {
        content: '';
        position: absolute;
        top: -30%;
        left: -30%;
        width: 160%;
        height: 160%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        animation: rotateSlow 12s linear infinite;
    }
    
    @keyframes rotateSlow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Spotlight de iglesia */
    .church-spotlight-premium {
        background: linear-gradient(145deg, rgba(230, 180, 34, 0.1) 0%, rgba(230, 180, 34, 0.02) 100%);
        border: 1px solid rgba(230, 180, 34, 0.3);
        border-radius: 35px;
        padding: 2.5rem;
        margin: 2rem 0;
        position: relative;
        backdrop-filter: blur(5px);
        box-shadow: 0 15px 30px -15px rgba(230, 180, 34, 0.3);
    }
    
    .church-spotlight-premium::before {
        content: '⛪';
        position: absolute;
        top: -20px;
        left: 40px;
        font-size: 2.5rem;
        color: var(--gold-400);
        background: var(--neutral-100);
        padding: 0 20px;
        border-radius: 50px;
        box-shadow: 0 5px 15px rgba(230, 180, 34, 0.2);
    }
    
    .church-label {
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 4px;
        color: var(--gold-500);
        margin-bottom: 0.5rem;
        font-weight: 300;
    }
    
    .church-name {
        font-size: 3rem;
        font-weight: 800;
        color: var(--primary-800);
        margin: 0;
        line-height: 1.2;
    }
    
    .church-year {
        display: inline-block;
        background: linear-gradient(135deg, var(--gold-400), var(--gold-600));
        color: var(--primary-950);
        padding: 0.5rem 2rem;
        border-radius: 50px;
        font-weight: 700;
        margin-top: 1.5rem;
        font-size: 1.1rem;
        box-shadow: 0 10px 20px -5px rgba(230, 180, 34, 0.4);
    }
    
    /* Tarjetas de información */
    .info-card-premium {
        background: white;
        border-radius: 25px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.03);
        border: 1px solid var(--neutral-200);
        transition: all 0.3s;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .info-card-premium:hover {
        border-color: var(--gold-400);
        box-shadow: 0 15px 30px -10px rgba(230, 180, 34, 0.15);
        transform: translateY(-5px);
    }
    
    .info-card-premium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 0;
        background: linear-gradient(to bottom, var(--gold-400), var(--primary-600));
        transition: height 0.3s;
    }
    
    .info-card-premium:hover::before {
        height: 100%;
    }
    
    .info-label {
        color: var(--neutral-500);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.3rem;
    }
    
    .info-value {
        color: var(--primary-800);
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* Timeline items */
    .timeline-premium {
        background: white;
        border-radius: 20px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 6px solid var(--gold-400);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.02);
        transition: all 0.3s;
    }
    
    .timeline-premium:hover {
        transform: translateX(8px);
        box-shadow: 0 10px 25px -8px rgba(230, 180, 34, 0.2);
    }
    
    .timeline-year {
        background: var(--primary-700);
        color: white;
        padding: 0.3rem 1.2rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 0.8rem;
    }
    
    /* Badges premium */
    .badge-premium {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 100px;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 5px 10px -3px rgba(0, 0, 0, 0.2);
    }
    
    .badge-completed {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
    }
    
    .badge-pending {
        background: linear-gradient(135deg, #f39c12, #e67e22);
        color: white;
    }
    
    /* Divisor elegante */
    .divider-premium {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 2.5rem 0;
    }
    
    .divider-premium::before,
    .divider-premium::after {
        content: '';
        flex: 1;
        border-bottom: 2px solid rgba(230, 180, 34, 0.2);
    }
    
    .divider-premium span {
        padding: 0 1.5rem;
        color: var(--gold-500);
        font-size: 1.2rem;
        font-weight: 500;
    }
    
    /* Login premium */
    .login-premium {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 50px;
        padding: 3.5rem;
        box-shadow: 
            0 40px 60px -20px var(--primary-950),
            0 0 0 1px rgba(230, 180, 34, 0.2) inset;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    /* Footer premium */
    .footer-premium {
        text-align: center;
        padding: 3rem 2rem 1.5rem;
        color: var(--neutral-500);
        position: relative;
        margin-top: 4rem;
    }
    
    .footer-premium::before {
        content: '⛪';
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 2rem;
        color: var(--gold-400);
        background: var(--neutral-100);
        padding: 0 2rem;
    }
    
    .footer-links {
        display: flex;
        justify-content: center;
        gap: 2.5rem;
        margin-bottom: 2rem;
        font-size: 0.9rem;
    }
    
    .footer-links span {
        transition: all 0.3s;
    }
    
    .footer-links span:hover {
        color: var(--gold-500);
        transform: translateY(-2px);
    }
    
    /* Animación de entrada */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-in {
        animation: fadeInUp 0.8s ease forwards;
    }
    
    /* Welcome message */
    .welcome-premium {
        text-align: center;
        padding: 5rem 2rem;
        animation: fadeInUp 1s ease;
    }
    
    .welcome-icon {
        font-size: 8rem;
        filter: drop-shadow(0 20px 30px rgba(230, 180, 34, 0.3));
        animation: welcomeBounce 4s ease-in-out infinite;
    }
    
    @keyframes welcomeBounce {
        0%, 100% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-20px) scale(1.05); }
    }
    
    .welcome-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-800), var(--primary-600));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 1rem 0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title { font-size: 3.5rem; }
        .church-name { font-size: 2rem; }
        .metric-value { font-size: 2.5rem; }
        .avatar-3d { width: 150px; height: 150px; font-size: 4rem; }
    }
    </style>
""", unsafe_allow_html=True)

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]:
        return True
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='login-premium animate-in'>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; margin-bottom: 2.5rem;'>
                <div style='font-size: 5rem; filter: drop-shadow(0 15px 25px var(--gold-400)); animation: floatText 3s ease-in-out infinite;'>⛪</div>
                <h1 style='font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, var(--primary-800), var(--primary-600)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;'>SIGEME</h1>
                <p style='color: var(--neutral-500); letter-spacing: 3px; font-weight: 300;'>Acceso Restringido</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<p style='color: var(--primary-700); font-weight: 500;'>Usuario</p>", unsafe_allow_html=True)
            user = st.text_input("", placeholder="Ingresa tu usuario", label_visibility="collapsed", key="login_user")
            
            st.markdown("<p style='color: var(--primary-700); font-weight: 500; margin-top: 1rem;'>Contraseña</p>", unsafe_allow_html=True)
            password = st.text_input("", placeholder="Ingresa tu contraseña", type="password", label_visibility="collapsed", key="login_pass")
            
            if st.form_submit_button("✦ ACCEDER AL SISTEMA ✦", use_container_width=True):
                if user == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("⛔ Credenciales incorrectas")
        
        st.markdown("</div>", unsafe_allow_html=True)
    return False

def get_as_dataframe(worksheet):
    data = worksheet.get_all_values()
    if not data:
        return pd.DataFrame()
    headers = [str(h).strip().upper() if h else f"COL_{i}" for i, h in enumerate(data[0])]
    final_headers = []
    for i, h in enumerate(headers):
        if h in final_headers:
            final_headers.append(f"{h}_{i}")
        else:
            final_headers.append(h)
    return pd.DataFrame(data[1:], columns=final_headers)

def conectar_servicios_google():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if not os.path.exists("credenciales.json"):
        st.error("📁 Archivo credenciales.json no encontrado")
        return None, None
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open("BD MINISTROS")
        drive_service = build('drive', 'v3', credentials=creds)
        
        worksheets = {
            "MINISTRO": spreadsheet.worksheet("MINISTRO"),
            "RELACION": spreadsheet.worksheet("IGLESIA"),
            "CAT_IGLESIAS": spreadsheet.worksheet("IGLESIAS"),
            "TEOLOGICOS": spreadsheet.worksheet("ESTUDIOS TEOLOGICOS"),
            "ACADEMICOS": spreadsheet.worksheet("ESTUDIOS ACADEMICOS"),
            "REVISION": spreadsheet.worksheet("Revision")
        }
        return worksheets, drive_service
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None, None

def descargar_foto_drive(drive_service, ruta_appsheet):
    if not ruta_appsheet or str(ruta_appsheet).strip() == "" or "n/a" in str(ruta_appsheet).lower():
        return None
    try:
        nombre_archivo = str(ruta_appsheet).split('/')[-1]
        query = f"name = '{nombre_archivo}' and trashed = false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        if items:
            file_id = items[0]['id']
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
            return fh.read()
    except:
        return None
    return None

def main():
    if not check_password(): 
        st.stop()
    
    # Header espectacular
    st.markdown("""
    <div class='hero-premium animate-in'>
        <div class='hero-content'>
            <h1 class='hero-title'>SIGEME</h1>
            <div class='hero-subtitle'>
                <span>D</span><span>I</span><span>S</span><span>T</span><span>R</span><span>I</span><span>T</span><span>O</span>
                <span style='margin:0 10px;'>✦</span>
                <span>S</span><span>U</span><span>R</span>
                <span style='margin:0 10px;'>✦</span>
                <span>F</span><span>R</span><span>O</span><span>N</span><span>T</span><span>E</span><span>R</span><span>I</span><span>Z</span><span>O</span>
            </div>
            <div class='hero-badge'>
                <span>⛪</span> SISTEMA DE GESTIÓN MINISTERIAL <span>⛪</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    sheets, drive_service = conectar_servicios_google()
    
    if not sheets:
        st.error("No se pudo conectar a Google Sheets. Verifica tu conexión y credenciales.")
        st.stop()
    
    with st.spinner('🌟 Cargando datos del ministerio...'):
        df_ministros = get_as_dataframe(sheets["MINISTRO"])
        df_relacion = get_as_dataframe(sheets["RELACION"])
        df_iglesias_cat = get_as_dataframe(sheets["CAT_IGLESIAS"])
        df_est_teo_raw = get_as_dataframe(sheets["TEOLOGICOS"])
        df_est_aca_raw = get_as_dataframe(sheets["ACADEMICOS"])
        df_revisiones_raw = get_as_dataframe(sheets["REVISION"])
    
    try:
        # Procesamiento de datos
        df_relacion['AÑO'] = pd.to_numeric(df_relacion['AÑO'], errors='coerce').fillna(0)
        df_relacion['MINISTRO'] = df_relacion['MINISTRO'].astype(str).str.strip()
        df_relacion['IGLESIA'] = df_relacion['IGLESIA'].astype(str).str.strip()
        df_ministros['ID_MINISTRO'] = df_ministros['ID_MINISTRO'].astype(str).str.strip()
        df_iglesias_cat['ID'] = df_iglesias_cat['ID'].astype(str).str.strip()
        
        # Obtener última iglesia
        df_rel_actual = df_relacion.sort_values(by=['MINISTRO', 'AÑO'], ascending=[True, False]).drop_duplicates(subset=['MINISTRO'])
        df_rel_con_nombre = pd.merge(df_rel_actual, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
        
        df_final = pd.merge(df_ministros, df_rel_con_nombre[['MINISTRO', 'NOMBRE', 'AÑO']], left_on='ID_MINISTRO', right_on='MINISTRO', how='left', suffixes=('', '_REL'))
        df_final['IGLESIA_RESULTADO'] = df_final['NOMBRE_REL'].fillna("Sin Iglesia Asignada")
        df_final['AÑO_ULTIMO'] = df_final['AÑO'].apply(lambda x: int(x) if pd.notnull(x) and x > 0 else "N/A")
        
        # Métricas 3D
        cols = st.columns(4)
        
        with cols[0]:
            st.markdown(f"""
            <div class='metric-3d animate-in' style='animation-delay: 0.1s;'>
                <div class='metric-value'>{len(df_ministros):,}</div>
                <div class='metric-label'>MINISTROS</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            activos = len(df_final[df_final['IGLESIA_RESULTADO'] != "Sin Iglesia Asignada"])
            st.markdown(f"""
            <div class='metric-3d animate-in' style='animation-delay: 0.2s;'>
                <div class='metric-value'>{activos:,}</div>
                <div class='metric-label'>ACTIVOS</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown(f"""
            <div class='metric-3d animate-in' style='animation-delay: 0.3s;'>
                <div class='metric-value'>{df_iglesias_cat['NOMBRE'].nunique()}</div>
                <div class='metric-label'>IGLESIAS</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[3]:
            hoy = datetime.now().strftime("%d/%m/%Y")
            st.markdown(f"""
            <div class='metric-3d animate-in' style='animation-delay: 0.4s;'>
                <div class='metric-value'>{hoy}</div>
                <div class='metric-label'>ACTUALIZADO</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Selector de ministro
        col_nombre = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_nombre].unique().tolist())
        
        st.markdown("<div class='glass-premium animate-in' style='animation-delay: 0.5s;'>", unsafe_allow_html=True)
        
        st.markdown("<p style='color: var(--gold-500); letter-spacing: 3px; margin-bottom: 5px;'>✦ SELECCIONAR MINISTRO ✦</p>", unsafe_allow_html=True)
        seleccion = st.selectbox("", ["—— SELECCIONE ——"] + lista_ministros, label_visibility="collapsed")
        
        if seleccion != "—— SELECCIONE ——":
            data = df_final[df_final[col_nombre] == seleccion].iloc[0]
            current_id = str(data['ID_MINISTRO'])
            
            st.markdown("<div class='divider-premium'><span>⛪</span></div>", unsafe_allow_html=True)
            
            # Perfil del ministro
            col_foto = next((c for c in data.index if 'FOTO' in c or 'IMAGEN' in c), None)
            img_data = descargar_foto_drive(drive_service, data[col_foto]) if col_foto else None
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if img_data:
                    st.image(img_data, use_container_width=True)
                else:
                    st.markdown("""
                    <div class='avatar-3d'>
                        👤
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<h1 style='font-size: 3rem; font-weight: 800; color: var(--primary-800); margin: 0 0 0.5rem 0;'>{data[col_nombre]}</h1>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='church-spotlight-premium'>
                    <div class='church-label'>IGLESIA ACTUAL</div>
                    <div class='church-name'>{data['IGLESIA_RESULTADO']}</div>
                    <div class='church-year'>GESTIÓN {data['AÑO_ULTIMO']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Información personal
            st.markdown("<div class='divider-premium'><span>✦ INFORMACIÓN PERSONAL ✦</span></div>", unsafe_allow_html=True)
            
            excluir = ['ID_MINISTRO', 'NOMBRE', 'IGLESIA', 'MINISTRO', 'NOMBRE_REL', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO', 'ID', col_foto]
            visible_fields = [f for f in data.index if f not in excluir and not f.endswith(('_X', '_Y', '_REL'))]
            
            # Grid de información
            info_cols = st.columns(3)
            for i, field in enumerate(visible_fields):
                val = str(data[field]).strip()
                if val and val != "nan":
                    with info_cols[i % 3]:
                        st.markdown(f"""
                        <div class='info-card-premium'>
                            <div class='info-label'>{field}</div>
                            <div class='info-value'>{val}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Revisiones
            st.markdown("<div class='divider-premium'><span>✦ REVISIONES MINISTERIALES ✦</span></div>", unsafe_allow_html=True)
            
            df_rev = df_revisiones_raw[df_revisiones_raw['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_rev.empty:
                df_rev_show = pd.merge(df_rev, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                df_rev_show['IGLESIA'] = df_rev_show['NOMBRE'].fillna(df_rev_show['IGLESIA'])
                
                for _, row in df_rev_show.sort_values('FEC_REVISION', ascending=False).iterrows():
                    status_class = "badge-completed" if "COMPLETADA" in str(row['STATUS']).upper() else "badge-pending"
                    st.markdown(f"""
                    <div class='timeline-premium'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='font-size: 1.2rem; font-weight: 600; color: var(--primary-700);'>{row['IGLESIA']}</span>
                            <span class='badge-premium {status_class}'>{row['STATUS']}</span>
                        </div>
                        <div style='display: flex; gap: 2rem; margin-top: 0.8rem; color: var(--neutral-600);'>
                            <span>📅 {row['FEC_REVISION']}</span>
                            <span>⏭️ Próxima: {row['PROX_REVISION']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: var(--neutral-500); text-align: center; padding: 2rem;'>📋 No hay revisiones registradas</p>", unsafe_allow_html=True)
            
            # Historial de gestión
            st.markdown("<div class='divider-premium'><span>✦ HISTORIAL DE GESTIÓN ✦</span></div>", unsafe_allow_html=True)
            
            df_hist = df_relacion[df_relacion['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_hist.empty:
                df_hist_show = pd.merge(df_hist, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                
                for _, row in df_hist_show.sort_values('AÑO', ascending=False).iterrows():
                    st.markdown(f"""
                    <div class='timeline-premium'>
                        <span class='timeline-year'>{int(row['AÑO'])}</span>
                        <div style='font-weight: 600; font-size: 1.1rem; margin: 0.3rem 0; color: var(--primary-700);'>{row['NOMBRE']}</div>
                        <div style='color: var(--neutral-600);'>{row['OBSERVACION']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: var(--neutral-500); text-align: center; padding: 2rem;'>📋 No hay historial de gestión</p>", unsafe_allow_html=True)
            
            # Estudios
            st.markdown("<div class='divider-premium'><span>✦ FORMACIÓN ACADÉMICA ✦</span></div>", unsafe_allow_html=True)
            
            col_est1, col_est2 = st.columns(2)
            
            with col_est1:
                st.markdown("""
                <div style='background: linear-gradient(135deg, var(--primary-800), var(--primary-700)); padding: 1.2rem; border-radius: 25px 25px 0 0;'>
                    <h3 style='color: white; margin: 0; text-align: center;'>📖 ESTUDIOS TEOLÓGICOS</h3>
                </div>
                """, unsafe_allow_html=True)
                
                t = df_est_teo_raw[df_est_teo_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not t.empty:
                    for _, row in t.iterrows():
                        st.markdown(f"""
                        <div class='info-card-premium' style='margin: 0.5rem 0; border-radius: 0;'>
                            <div style='font-weight: 600; color: var(--primary-700);'>{row['NIVEL']}</div>
                            <div style='color: var(--neutral-600);'>{row['ESCUELA']} | {row['PERIODO']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: var(--neutral-500); text-align: center; padding: 1rem;'>No registra estudios teológicos</p>", unsafe_allow_html=True)
            
            with col_est2:
                st.markdown("""
                <div style='background: linear-gradient(135deg, var(--gold-600), var(--gold-400)); padding: 1.2rem; border-radius: 25px 25px 0 0;'>
                    <h3 style='color: white; margin: 0; text-align: center;'>🎓 ESTUDIOS ACADÉMICOS</h3>
                </div>
                """, unsafe_allow_html=True)
                
                a = df_est_aca_raw[df_est_aca_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not a.empty:
                    for _, row in a.iterrows():
                        st.markdown(f"""
                        <div class='info-card-premium' style='margin: 0.5rem 0; border-radius: 0;'>
                            <div style='font-weight: 600; color: var(--primary-700);'>{row['NIVEL']}</div>
                            <div style='color: var(--neutral-600);'>{row['ESCUELA']} | {row['PERIODO']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: var(--neutral-500); text-align: center; padding: 1rem;'>No registra estudios académicos</p>", unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div class='welcome-premium'>
                <div class='welcome-icon'>⛪</div>
                <h2 class='welcome-title'>BIENVENIDO AL SISTEMA</h2>
                <p style='color: var(--neutral-500); font-size: 1.2rem; max-width: 500px; margin: 0 auto;'>
                    Seleccione un ministro del listado para visualizar su expediente completo
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer premium
        st.markdown("""
        <div class='footer-premium'>
            <div class='footer-links'>
                <span>⛪ SIGEME</span>
                <span>✦</span>
                <span>DISTRITO SUR FRONTERIZO</span>
                <span>✦</span>
                <span>© 2026</span>
            </div>
            <div style='font-size: 0.9rem; opacity: 0.6;'>
                Sistema de Gestión Ministerial · Todos los derechos reservados
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error procesando datos: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()