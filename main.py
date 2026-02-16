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
    page_title="SIGEME | Distrito Sur Fronterizo",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DISEÑO CSS OPTIMIZADO (espectacular pero ligero) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Variables de color */
    :root {
        --primary: #1e3a5f;
        --primary-light: #2b4c7c;
        --primary-dark: #0f2b44;
        --accent: #c9a959;
        --accent-light: #dbbc7c;
        --accent-dark: #a88b42;
        --success: #2e7d5e;
        --warning: #c97c2e;
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-300: #cbd5e1;
        --gray-600: #475569;
        --gray-700: #334155;
        --gray-800: #1e293b;
        --gray-900: #0f172a;
    }
    
    /* Estilos base */
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--gray-50) 0%, white 100%);
    }
    
    /* Header elegante */
    .header-premium {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 2.5rem 2rem;
        border-radius: 30px;
        margin-bottom: 2rem;
        box-shadow: 0 15px 25px -8px rgba(30,58,95,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header-premium::after {
        content: '';
        position: absolute;
        top: -30%;
        right: -10%;
        width: 40%;
        height: 160%;
        background: radial-gradient(circle, rgba(201,169,89,0.2) 0%, transparent 70%);
    }
    
    .header-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        letter-spacing: -1px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.3rem;
        font-weight: 300;
        letter-spacing: 2px;
    }
    
    .header-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        padding: 0.4rem 1.5rem;
        border-radius: 50px;
        color: white;
        font-size: 0.9rem;
        margin-top: 1rem;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Tarjetas elegantes */
    .card-premium {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        border: 1px solid var(--gray-200);
        transition: all 0.3s ease;
    }
    
    .card-premium:hover {
        border-color: var(--accent);
        box-shadow: 0 12px 24px -12px rgba(201,169,89,0.3);
        transform: translateY(-2px);
    }
    
    /* Métricas */
    .metric-premium {
        background: white;
        border-radius: 18px;
        padding: 1.5rem;
        border-left: 5px solid var(--accent);
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: var(--gray-600);
        letter-spacing: 1px;
    }
    
    /* Avatar */
    .avatar-premium {
        width: 180px;
        height: 180px;
        border-radius: 25px;
        background: linear-gradient(135deg, var(--primary-light), var(--primary));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4.5rem;
        color: white;
        border: 4px solid var(--accent);
        box-shadow: 0 15px 25px -8px rgba(30,58,95,0.3);
    }
    
    /* Iglesia spotlight */
    .church-spotlight {
        background: linear-gradient(135deg, rgba(201,169,89,0.08) 0%, rgba(201,169,89,0.02) 100%);
        border: 1px solid rgba(201,169,89,0.2);
        border-radius: 20px;
        padding: 1.8rem;
        margin: 1.5rem 0;
    }
    
    .church-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: var(--accent);
        letter-spacing: 2px;
    }
    
    .church-name {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        margin: 0.3rem 0;
    }
    
    .church-year {
        display: inline-block;
        background: var(--accent);
        color: white;
        padding: 0.3rem 1.2rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Info cards */
    .info-card {
        background: var(--gray-50);
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid var(--gray-200);
        transition: all 0.2s;
    }
    
    .info-card:hover {
        background: white;
        border-color: var(--accent);
    }
    
    .info-label {
        color: var(--gray-600);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .info-value {
        color: var(--gray-800);
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0.2rem;
    }
    
    /* Timeline */
    .timeline-item {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid var(--accent);
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    
    .timeline-year {
        background: var(--primary);
        color: white;
        padding: 0.2rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 1rem;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-success {
        background: #d5f0e6;
        color: #0b5e42;
    }
    
    .badge-warning {
        background: #fee9d1;
        color: #a45c1e;
    }
    
    /* Login */
    .login-card {
        background: white;
        border-radius: 30px;
        padding: 2.5rem;
        box-shadow: 0 25px 40px -15px rgba(30,58,95,0.3);
        border: 1px solid rgba(201,169,89,0.2);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--gray-600);
        border-top: 1px solid var(--gray-200);
        margin-top: 3rem;
    }
    
    /* Divider */
    .divider {
        display: flex;
        align-items: center;
        margin: 2rem 0;
    }
    
    .divider::before,
    .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid var(--gray-200);
    }
    
    .divider span {
        padding: 0 1rem;
        color: var(--accent);
        font-size: 1rem;
    }
    
    /* Welcome */
    .welcome {
        text-align: center;
        padding: 4rem 2rem;
    }
    
    .welcome-icon {
        font-size: 6rem;
        color: var(--accent);
    }
    
    .welcome-title {
        font-size: 2rem;
        color: var(--primary);
        margin: 1rem 0;
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
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='text-align: center; margin-bottom: 2rem;'>
                <div style='font-size: 4rem;'>⛪</div>
                <h1 style='color: var(--primary); font-size: 2.5rem; margin: 0;'>SIGEME</h1>
                <p style='color: var(--gray-600);'>Sistema de Gestión Ministerial</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            
            if st.form_submit_button("✦ ACCEDER ✦", use_container_width=True):
                if user == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
        
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
    
    # Header
    st.markdown("""
    <div class='header-premium'>
        <div style='position: relative; z-index: 2;'>
            <h1 class='header-title'>SIGEME</h1>
            <div class='header-subtitle'>DISTRITO SUR FRONTERIZO</div>
            <div class='header-badge'>⛪ Sistema de Gestión Ministerial ⛪</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    sheets, drive_service = conectar_servicios_google()
    
    if not sheets:
        st.error("No se pudo conectar a Google Sheets")
        st.stop()
    
    with st.spinner('Cargando datos...'):
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
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-premium'>
                <div class='metric-value'>{len(df_ministros)}</div>
                <div class='metric-label'>Total Ministros</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            activos = len(df_final[df_final['IGLESIA_RESULTADO'] != "Sin Iglesia Asignada"])
            st.markdown(f"""
            <div class='metric-premium'>
                <div class='metric-value'>{activos}</div>
                <div class='metric-label'>Ministros Activos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-premium'>
                <div class='metric-value'>{df_iglesias_cat['NOMBRE'].nunique()}</div>
                <div class='metric-label'>Iglesias</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            hoy = datetime.now().strftime("%d/%m/%Y")
            st.markdown(f"""
            <div class='metric-premium'>
                <div class='metric-value'>{hoy}</div>
                <div class='metric-label'>Fecha</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Selector
        col_nombre = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_nombre].unique().tolist())
        
        st.markdown("<div class='card-premium'>", unsafe_allow_html=True)
        
        st.markdown("<p style='color: var(--accent); font-weight: 600; margin-bottom: 0;'>✦ SELECCIONAR MINISTRO</p>", unsafe_allow_html=True)
        seleccion = st.selectbox("", ["—— SELECCIONE ——"] + lista_ministros, label_visibility="collapsed")
        
        if seleccion != "—— SELECCIONE ——":
            data = df_final[df_final[col_nombre] == seleccion].iloc[0]
            current_id = str(data['ID_MINISTRO'])
            
            st.markdown("<div class='divider'><span>✦</span></div>", unsafe_allow_html=True)
            
            # Perfil
            col_foto = next((c for c in data.index if 'FOTO' in c or 'IMAGEN' in c), None)
            img_data = descargar_foto_drive(drive_service, data[col_foto]) if col_foto else None
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if img_data:
                    st.image(img_data, use_container_width=True)
                else:
                    st.markdown("<div class='avatar-premium'>👤</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<h2 style='color: var(--primary); margin-top: 0;'>{data[col_nombre]}</h2>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='church-spotlight'>
                    <div class='church-label'>Iglesia Actual</div>
                    <div class='church-name'>{data['IGLESIA_RESULTADO']}</div>
                    <div class='church-year'>Gestión {data['AÑO_ULTIMO']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Información personal
            st.markdown("<div class='divider'><span>✦ INFORMACIÓN PERSONAL ✦</span></div>", unsafe_allow_html=True)
            
            excluir = ['ID_MINISTRO', 'NOMBRE', 'IGLESIA', 'MINISTRO', 'NOMBRE_REL', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO', 'ID', col_foto]
            visible_fields = [f for f in data.index if f not in excluir and not f.endswith(('_X', '_Y', '_REL'))]
            
            info_cols = st.columns(3)
            for i, field in enumerate(visible_fields):
                val = str(data[field]).strip()
                if val and val != "nan":
                    with info_cols[i % 3]:
                        st.markdown(f"""
                        <div class='info-card'>
                            <div class='info-label'>{field}</div>
                            <div class='info-value'>{val}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Revisiones
            st.markdown("<div class='divider'><span>✦ REVISIONES MINISTERIALES ✦</span></div>", unsafe_allow_html=True)
            
            df_rev = df_revisiones_raw[df_revisiones_raw['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_rev.empty:
                df_rev_show = pd.merge(df_rev, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                df_rev_show['IGLESIA'] = df_rev_show['NOMBRE'].fillna(df_rev_show['IGLESIA'])
                
                for _, row in df_rev_show.sort_values('FEC_REVISION', ascending=False).iterrows():
                    status_class = "badge-success" if "COMPLETADA" in str(row['STATUS']).upper() else "badge-warning"
                    st.markdown(f"""
                    <div class='timeline-item'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='font-weight: 600; color: var(--primary);'>{row['IGLESIA']}</span>
                            <span class='badge {status_class}'>{row['STATUS']}</span>
                        </div>
                        <div style='margin-top: 0.5rem; color: var(--gray-600);'>
                            📅 {row['FEC_REVISION']} | ⏭️ {row['PROX_REVISION']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay revisiones registradas")
            
            # Historial
            st.markdown("<div class='divider'><span>✦ HISTORIAL DE GESTIÓN ✦</span></div>", unsafe_allow_html=True)
            
            df_hist = df_relacion[df_relacion['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_hist.empty:
                df_hist_show = pd.merge(df_hist, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                
                for _, row in df_hist_show.sort_values('AÑO', ascending=False).iterrows():
                    st.markdown(f"""
                    <div class='timeline-item'>
                        <span class='timeline-year'>{int(row['AÑO'])}</span>
                        <div style='font-weight: 600; margin: 0.5rem 0;'>{row['NOMBRE']}</div>
                        <div style='color: var(--gray-600);'>{row['OBSERVACION']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay historial de gestión")
            
            # Estudios
            st.markdown("<div class='divider'><span>✦ FORMACIÓN ACADÉMICA ✦</span></div>", unsafe_allow_html=True)
            
            col_est1, col_est2 = st.columns(2)
            
            with col_est1:
                st.markdown("<h3 style='color: var(--primary);'>📖 Teológicos</h3>", unsafe_allow_html=True)
                t = df_est_teo_raw[df_est_teo_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not t.empty:
                    for _, row in t.iterrows():
                        st.markdown(f"""
                        <div class='info-card' style='margin-bottom: 0.5rem;'>
                            <div style='font-weight: 600;'>{row['NIVEL']}</div>
                            <div style='color: var(--gray-600);'>{row['ESCUELA']} | {row['PERIODO']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No registra estudios teológicos")
            
            with col_est2:
                st.markdown("<h3 style='color: var(--accent);'>🎓 Académicos</h3>", unsafe_allow_html=True)
                a = df_est_aca_raw[df_est_aca_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not a.empty:
                    for _, row in a.iterrows():
                        st.markdown(f"""
                        <div class='info-card' style='margin-bottom: 0.5rem;'>
                            <div style='font-weight: 600;'>{row['NIVEL']}</div>
                            <div style='color: var(--gray-600);'>{row['ESCUELA']} | {row['PERIODO']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No registra estudios académicos")
        
        else:
            st.markdown("""
            <div class='welcome'>
                <div class='welcome-icon'>⛪</div>
                <h2 class='welcome-title'>Bienvenido al Sistema</h2>
                <p style='color: var(--gray-600);'>Seleccione un ministro para ver su información</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div class='footer'>
            <div style='display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem;'>
                <span>⛪ SIGEME</span>
                <span>✦</span>
                <span>Distrito Sur Fronterizo</span>
                <span>✦</span>
                <span>© 2026</span>
            </div>
            <div style='font-size: 0.8rem; opacity: 0.6;'>
                Sistema de Gestión Ministerial
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()