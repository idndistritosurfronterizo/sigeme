import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import os
import io
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_CORRECTO = "admin"
PASSWORD_CORRECTO = "ministros2024"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="SIGEME | Distrito Sur Fronterizo",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DISEÑO CSS DE ALTO IMPACTO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
    
    /* Variables de color premium */
    :root {
        --primary-900: #0a1929;
        --primary-800: #0f2a40;
        --primary-700: #1a3b5c;
        --primary-600: #2a4e77;
        --primary-500: #3a6793;
        --primary-400: #4f82b2;
        --accent-gold: #c9a45b;
        --accent-gold-light: #e5c28e;
        --accent-gold-dark: #9e7e48;
        --neutral-50: #f9fafc;
        --neutral-100: #f0f3f8;
        --neutral-200: #e4e9f2;
        --neutral-300: #d3dae9;
        --neutral-400: #a0b0c9;
        --neutral-500: #6f85a8;
        --neutral-600: #4e6384;
        --neutral-700: #354767;
        --neutral-800: #1f2c44;
        --neutral-900: #121a2b;
        --success: #3fb68b;
        --warning: #ffb45b;
        --danger: #ff6b6b;
        --info: #5b8cff;
    }
    
    /* Estilos base */
    html, body, [class*="css"] { 
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--neutral-100) 0%, var(--neutral-200) 100%);
        position: relative;
        overflow-x: hidden;
    }
    
    /* Fondo con partículas (efecto visual) */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: radial-gradient(circle at 30% 40%, rgba(201, 164, 91, 0.03) 0%, transparent 30%),
                          radial-gradient(circle at 70% 60%, rgba(42, 78, 119, 0.03) 0%, transparent 40%),
                          repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 2px, transparent 2px, transparent 10px);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Header espectacular con efecto glassmorphism */
    .hero-section {
        position: relative;
        background: linear-gradient(165deg, var(--primary-900) 0%, var(--primary-700) 40%, var(--primary-600) 100%);
        padding: 4rem 3rem;
        border-radius: 40px 40px 40px 40px;
        margin-bottom: 3rem;
        overflow: hidden;
        box-shadow: 0 30px 40px -20px rgba(10, 25, 41, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -20%;
        width: 70%;
        height: 200%;
        background: radial-gradient(circle, rgba(201, 164, 91, 0.15) 0%, transparent 70%);
        animation: float 15s infinite ease-in-out;
    }
    
    .hero-section::after {
        content: '';
        position: absolute;
        bottom: -30%;
        right: -10%;
        width: 60%;
        height: 150%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%);
        animation: float 20s infinite ease-in-out reverse;
    }
    
    @keyframes float {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(3%, 2%) rotate(2deg); }
        66% { transform: translate(-2%, -3%) rotate(-2deg); }
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        text-align: center;
    }
    
    .hero-title {
        font-size: 5.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #ffffff 0%, var(--accent-gold-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -2px;
        text-transform: uppercase;
        filter: drop-shadow(0 10px 20px rgba(0,0,0,0.3));
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        font-weight: 300;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 0.5rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        position: relative;
        display: inline-block;
    }
    
    .hero-subtitle::before,
    .hero-subtitle::after {
        content: '✦';
        margin: 0 15px;
        color: var(--accent-gold);
        font-size: 1.2rem;
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 100px;
        padding: 0.5rem 1.5rem;
        margin-top: 1.5rem;
        color: white;
        font-weight: 300;
        font-size: 0.9rem;
    }
    
    /* Tarjetas con efecto 3D y glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 30px;
        padding: 1.8rem;
        box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.1),
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.6s;
        pointer-events: none;
    }
    
    .glass-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 45px -12px rgba(42, 78, 119, 0.3),
                    0 0 0 2px rgba(201, 164, 91, 0.3) inset;
    }
    
    .glass-card:hover::before {
        opacity: 0.1;
    }
    
    /* Métricas premium */
    .metric-premium {
        background: linear-gradient(135deg, var(--primary-800) 0%, var(--primary-900) 100%);
        border-radius: 25px;
        padding: 1.8rem;
        border: 1px solid rgba(201, 164, 91, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .metric-premium::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: rgba(255, 255, 255, 0.6);
    }
    
    /* Selector elegante */
    .elegant-select {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(201, 164, 91, 0.2);
        border-radius: 50px;
        padding: 0.5rem 1rem;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    
    .elegant-select:focus {
        border-color: var(--accent-gold);
        box-shadow: 0 0 0 3px rgba(201, 164, 91, 0.2);
    }
    
    /* Perfil del ministro */
    .profile-header {
        display: flex;
        align-items: center;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .profile-avatar {
        width: 150px;
        height: 150px;
        border-radius: 30px;
        background: linear-gradient(135deg, var(--primary-600), var(--primary-800));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
        color: white;
        border: 3px solid var(--accent-gold);
        box-shadow: 0 20px 30px -10px rgba(42, 78, 119, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .profile-avatar::after {
        content: '';
        position: absolute;
        top: -30%;
        left: -30%;
        width: 160%;
        height: 160%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        animation: rotate 8s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .profile-name {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-800), var(--primary-600));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    /* Iglesia actual - diseño destacado */
    .church-spotlight {
        background: linear-gradient(135deg, rgba(201, 164, 91, 0.1) 0%, rgba(201, 164, 91, 0.05) 100%);
        border: 1px solid rgba(201, 164, 91, 0.3);
        border-radius: 30px;
        padding: 2rem;
        margin: 2rem 0;
        position: relative;
        backdrop-filter: blur(5px);
    }
    
    .church-spotlight::before {
        content: '✦';
        position: absolute;
        top: -15px;
        left: 30px;
        font-size: 2rem;
        color: var(--accent-gold);
        background: var(--neutral-100);
        padding: 0 15px;
    }
    
    .church-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: var(--accent-gold);
        margin-bottom: 0.5rem;
    }
    
    .church-name {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-800);
        margin: 0;
    }
    
    .church-year {
        display: inline-block;
        background: var(--accent-gold);
        color: var(--primary-900);
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        margin-top: 1rem;
    }
    
    /* Tablas con diseño moderno */
    .modern-table {
        background: white;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 30px -15px rgba(0,0,0,0.1);
    }
    
    .modern-table table {
        border-collapse: collapse;
        width: 100%;
    }
    
    .modern-table th {
        background: var(--primary-800);
        color: white;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 1px;
        padding: 1rem;
    }
    
    .modern-table td {
        padding: 1rem;
        border-bottom: 1px solid var(--neutral-200);
    }
    
    .modern-table tr:last-child td {
        border-bottom: none;
    }
    
    .modern-table tr:hover td {
        background: rgba(201, 164, 91, 0.05);
    }
    
    /* Badges */
    .badge-premium {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 100px;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    
    .badge-completed {
        background: linear-gradient(135deg, #3fb68b, #2d8a6a);
        color: white;
        box-shadow: 0 4px 10px -2px rgba(63, 182, 139, 0.4);
    }
    
    .badge-pending {
        background: linear-gradient(135deg, #ffb45b, #e6942e);
        color: white;
        box-shadow: 0 4px 10px -2px rgba(255, 180, 91, 0.4);
    }
    
    /* Divisores decorativos */
    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 2rem 0;
    }
    
    .divider::before,
    .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid rgba(201, 164, 91, 0.3);
    }
    
    .divider span {
        padding: 0 1rem;
        color: var(--accent-gold);
        font-size: 1.2rem;
    }
    
    /* Footer */
    .premium-footer {
        text-align: center;
        padding: 3rem 2rem 1rem;
        color: var(--neutral-500);
        position: relative;
    }
    
    .premium-footer::before {
        content: '⛪';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.5rem;
        color: var(--accent-gold);
        background: var(--neutral-100);
        padding: 0 1rem;
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
        with st.container():
            st.markdown("""
            <div style='background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); border-radius: 40px; padding: 3rem; box-shadow: 0 40px 60px -20px var(--primary-900); border: 1px solid rgba(255,255,255,0.5);'>
                <div style='text-align: center; margin-bottom: 2rem;'>
                    <div style='font-size: 5rem; filter: drop-shadow(0 10px 15px var(--accent-gold));'>⛪</div>
                    <h1 style='font-size: 3rem; font-weight: 700; background: linear-gradient(135deg, var(--primary-800), var(--primary-600)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;'>SIGEME</h1>
                    <p style='color: var(--neutral-600); letter-spacing: 2px;'>Acceso Restringido</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                user = st.text_input("", placeholder="USUARIO", key="login_user")
                password = st.text_input("", placeholder="CONTRASEÑA", type="password", key="login_pass")
                
                if st.form_submit_button("✦ ACCEDER ✦", use_container_width=True):
                    if user == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error("⛔ Credenciales incorrectas")
            
            st.markdown("</div>", unsafe_allow_html=True)
    return False

def get_as_dataframe(worksheet):
    """Método robusto para leer hojas evitando errores de encabezados vacíos o duplicados."""
    data = worksheet.get_all_values()
    if not data:
        return pd.DataFrame()
    headers = [str(h).strip().upper() if h else f"COL_{i}" for i, h in enumerate(data[0])]
    # Manejar duplicados en encabezados
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
        with st.spinner("🔄 Estableciendo conexión segura..."):
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
        
        st.success("✅ Conexión establecida con éxito")
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

def crear_grafico_estados(df_rev):
    """Crea un gráfico circular de estados de revisión"""
    if df_rev.empty:
        return None
    
    estados = df_rev['STATUS'].value_counts()
    fig = go.Figure(data=[go.Pie(
        labels=estados.index,
        values=estados.values,
        hole=0.6,
        marker_colors=['#3fb68b', '#ffb45b', '#ff6b6b'],
        textinfo='label+percent',
        textfont=dict(size=14, color='white'),
        marker=dict(line=dict(color='white', width=2))
    )])
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200
    )
    
    return fig

def main():
    if not check_password(): st.stop()

    # Hero Section Espectacular
    st.markdown("""
    <div class='hero-section'>
        <div class='hero-content'>
            <h1 class='hero-title'>SIGEME</h1>
            <div class='hero-subtitle'>Distrito Sur Fronterizo</div>
            <div class='hero-badge'>
                <i class='fas fa-shield-alt'></i> Sistema de Gestión Ministerial
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sheets, drive_service = conectar_servicios_google()
    
    if sheets:
        with st.spinner('🌟 Cargando datos del ministerio...'):
            df_ministros = get_as_dataframe(sheets["MINISTRO"])
            df_relacion = get_as_dataframe(sheets["RELACION"])
            df_iglesias_cat = get_as_dataframe(sheets["CAT_IGLESIAS"])
            df_est_teo_raw = get_as_dataframe(sheets["TEOLOGICOS"])
            df_est_aca_raw = get_as_dataframe(sheets["ACADEMICOS"])
            df_revisiones_raw = get_as_dataframe(sheets["REVISION"])

        try:
            # Normalización de datos para cruces
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

            # Métricas Premium
            st.markdown("<div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 2rem 0;'>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class='metric-premium'>
                    <div class='metric-value'>{len(df_ministros):,}</div>
                    <div class='metric-label'>MINISTROS</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                activos = len(df_final[df_final['IGLESIA_RESULTADO'] != "Sin Iglesia Asignada"])
                st.markdown(f"""
                <div class='metric-premium'>
                    <div class='metric-value'>{activos:,}</div>
                    <div class='metric-label'>ACTIVOS</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                iglesias_unicas = df_iglesias_cat['NOMBRE'].nunique()
                st.markdown(f"""
                <div class='metric-premium'>
                    <div class='metric-value'>{iglesias_unicas}</div>
                    <div class='metric-label'>IGLESIAS</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                hoy = datetime.now().strftime("%d/%m/%Y")
                st.markdown(f"""
                <div class='metric-premium'>
                    <div class='metric-value'>{hoy}</div>
                    <div class='metric-label'>ACTUALIZADO</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error procesando tablas: {e}")
            df_final = df_ministros

        # --- INTERFAZ PRINCIPAL PREMIUM ---
        col_nombre = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_nombre].unique().tolist())
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        
        # Selector elegante
        col_sel1, col_sel2 = st.columns([4, 1])
        with col_sel1:
            st.markdown("<p style='color: var(--neutral-600); margin-bottom: 5px;'>✦ SELECCIONAR MINISTRO</p>", unsafe_allow_html=True)
            seleccion = st.selectbox("", ["—— SELECCIONE ——"] + lista_ministros, label_visibility="collapsed")
        
        with col_sel2:
            if seleccion != "—— SELECCIONE ——":
                st.markdown(f"""
                <div style='background: var(--accent-gold); color: var(--primary-900); padding: 0.5rem 1rem; border-radius: 50px; text-align: center; font-weight: 600; margin-top: 25px;'>
                    ✓ MINISTRO ACTIVO
                </div>
                """, unsafe_allow_html=True)

        if seleccion != "—— SELECCIONE ——":
            data = df_final[df_final[col_nombre] == seleccion].iloc[0]
            current_id = str(data['ID_MINISTRO'])
            
            # Separador decorativo
            st.markdown("<div class='divider'><span>✦</span></div>", unsafe_allow_html=True)
            
            # Perfil del ministro - Diseño premium
            col_foto = next((c for c in data.index if 'FOTO' in c or 'IMAGEN' in c), None)
            img_data = descargar_foto_drive(drive_service, data[col_foto]) if col_foto else None
            
            col_perfil1, col_perfil2 = st.columns([1, 2])
            
            with col_perfil1:
                if img_data:
                    st.image(img_data, use_container_width=True, output_format="auto")
                else:
                    st.markdown(f"""
                    <div class='profile-avatar'>
                        👤
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_perfil2:
                st.markdown(f"<h1 class='profile-name'>{data[col_nombre]}</h1>", unsafe_allow_html=True)
                
                # Iglesia actual con diseño spotlight
                st.markdown(f"""
                <div class='church-spotlight'>
                    <div class='church-label'>IGLESIA ACTUAL</div>
                    <div class='church-name'>{data['IGLESIA_RESULTADO']}</div>
                    <div class='church-year'>GESTIÓN {data['AÑO_ULTIMO']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Información personal en grid elegante
            st.markdown("<div class='divider'><span>✦ INFORMACIÓN PERSONAL ✦</span></div>", unsafe_allow_html=True)
            
            excluir = ['ID_MINISTRO', 'NOMBRE', 'IGLESIA', 'MINISTRO', 'NOMBRE_REL', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO', 'ID', col_foto]
            visible_fields = [f for f in data.index if f not in excluir and not f.endswith(('_X', '_Y', '_REL'))]
            
            # Crear grid de 4 columnas para la información
            cols_info = st.columns(4)
            for i, field in enumerate(visible_fields):
                val = str(data[field]).strip()
                if val and val != "nan":
                    with cols_info[i % 4]:
                        st.markdown(f"""
                        <div class='glass-card' style='padding: 1.2rem;'>
                            <div style='color: var(--accent-gold); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;'>{field}</div>
                            <div style='color: var(--primary-800); font-size: 1.2rem; font-weight: 600; margin-top: 0.3rem;'>{val}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # --- SECCIONES DE HISTORIAL CON DISEÑO PREMIUM ---
            
            # Revisiones con gráfico
            st.markdown("<div class='divider'><span>✦ REVISIONES MINISTERIALES ✦</span></div>", unsafe_allow_html=True)
            
            df_rev = df_revisiones_raw[df_revisiones_raw['MINISTRO'].astype(str).str.strip() == current_id]
            
            col_rev1, col_rev2 = st.columns([2, 1])
            
            with col_rev1:
                if not df_rev.empty:
                    df_rev_show = pd.merge(df_rev, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                    df_rev_show['IGLESIA'] = df_rev_show['NOMBRE'].fillna(df_rev_show['IGLESIA'])
                    
                    # Mostrar tabla con formato mejorado
                    for _, row in df_rev_show.sort_values('FEC_REVISION', ascending=False).iterrows():
                        status_class = "badge-completed" if "COMPLETADA" in str(row['STATUS']).upper() else "badge-pending"
                        st.markdown(f"""
                        <div style='background: white; border-radius: 15px; padding: 1rem; margin-bottom: 0.5rem; border-left: 5px solid var(--accent-gold);'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div><strong>{row['IGLESIA']}</strong></div>
                                <div><span class='badge-premium {status_class}'>{row['STATUS']}</span></div>
                            </div>
                            <div style='display: flex; gap: 2rem; margin-top: 0.5rem; color: var(--neutral-600);'>
                                <div>📅 {row['FEC_REVISION']}</div>
                                <div>⏭️ Próxima: {row['PROX_REVISION']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No hay revisiones registradas")
            
            with col_rev2:
                if not df_rev.empty:
                    fig = crear_grafico_estados(df_rev)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Historial de gestión
            st.markdown("<div class='divider'><span>✦ HISTORIAL DE GESTIÓN ✦</span></div>", unsafe_allow_html=True)
            
            df_hist = df_relacion[df_relacion['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_hist.empty:
                df_hist_show = pd.merge(df_hist, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                
                for _, row in df_hist_show.sort_values('AÑO', ascending=False).iterrows():
                    st.markdown(f"""
                    <div style='display: flex; align-items: center; gap: 2rem; background: rgba(255,255,255,0.5); padding: 1rem; border-radius: 15px; margin-bottom: 0.5rem;'>
                        <div style='background: var(--accent-gold); color: var(--primary-900); padding: 0.5rem 1rem; border-radius: 10px; font-weight: 700;'>{int(row['AÑO'])}</div>
                        <div style='flex: 1;'><strong>{row['NOMBRE']}</strong></div>
                        <div style='color: var(--neutral-600);'>{row['OBSERVACION']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay historial de gestión")
            
            # Estudios en paralelo
            st.markdown("<div class='divider'><span>✦ FORMACIÓN ACADÉMICA ✦</span></div>", unsafe_allow_html=True)
            
            col_est1, col_est2 = st.columns(2)
            
            with col_est1:
                st.markdown("""
                <div style='background: linear-gradient(135deg, var(--primary-800), var(--primary-700)); padding: 1rem; border-radius: 20px 20px 0 0;'>
                    <h3 style='color: white; margin: 0; text-align: center;'>📖 ESTUDIOS TEOLÓGICOS</h3>
                </div>
                """, unsafe_allow_html=True)
                
                t = df_est_teo_raw[df_est_teo_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not t.empty:
                    for _, row in t.iterrows():
                        st.markdown(f"""
                        <div style='background: white; padding: 1rem; border-bottom: 1px solid var(--neutral-200);'>
                            <div style='font-weight: 600;'>{row['NIVEL']}</div>
                            <div style='color: var(--neutral-600); font-size: 0.9rem;'>{row['ESCUELA']} | {row['PERIODO']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No registra estudios teológicos")
            
            with col_est2:
                st.markdown("""
                <div style='background: linear-gradient(135deg, var(--accent-gold-dark), var(--accent-gold)); padding: 1rem; border-radius: 20px 20px 0 0;'>
                    <h3 style='color: white; margin: 0; text-align: center;'>🎓 ESTUDIOS ACADÉMICOS</h3>
                </div>
                """, unsafe_allow_html=True)
                
                a = df_est_aca_raw[df_est_aca_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not a.empty:
                    for _, row in a.iterrows():
                        st.markdown(f"""
                        <div style='background: white; padding: 1rem; border-bottom: 1px solid var(--neutral-200);'>
                            <div style='font-weight: 600;'>{row['NIVEL']}</div>
                            <div style='color: var(--neutral-600); font-size: 0.9rem;'>{row['ESCUELA']} | {row['PERIODO']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No registra estudios académicos")

        else:
            # Mensaje de bienvenida espectacular
            st.markdown("""
            <div style='text-align: center; padding: 5rem 2rem;'>
                <div style='font-size: 8rem; filter: drop-shadow(0 20px 25px rgba(201,164,91,0.3)); animation: float 6s infinite;'>⛪</div>
                <h2 style='color: var(--primary-800); font-size: 2.5rem; margin: 1rem 0;'>BIENVENIDO AL SISTEMA</h2>
                <p style='color: var(--neutral-500); font-size: 1.2rem; max-width: 600px; margin: 0 auto;'>
                    Seleccione un ministro del listado para visualizar su expediente completo
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Footer premium
    st.markdown("""
    <div class='premium-footer'>
        <div style='display: flex; justify-content: center; gap: 2rem; margin-bottom: 2rem;'>
            <span>⛪ SIGEME</span>
            <span>✦</span>
            <span>DISTRITO SUR FRONTERIZO</span>
            <span>✦</span>
            <span>© 2026</span>
        </div>
        <div style='font-size: 0.8rem; opacity: 0.6;'>
            Sistema de Gestión Ministerial · Todos los derechos reservados
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()