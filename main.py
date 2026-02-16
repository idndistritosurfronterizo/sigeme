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
    page_title="SIGEME - Distrito Sur Fronterizo",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DISEÑO CSS (optimizado para evitar pantalla en blanco) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Variables de color */
    :root {
        --primary: #003366;
        --primary-light: #00509d;
        --primary-dark: #001f3f;
        --secondary: #fbbf24;
        --secondary-light: #fcd34d;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
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
        background: linear-gradient(135deg, var(--gray-50) 0%, #ffffff 100%);
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 2.5rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,51,102,0.2);
    }
    
    .main-title { 
        font-size: 3.5rem; 
        font-weight: 800; 
        margin: 0; 
        letter-spacing: -1px;
    }
    
    .sub-title { 
        font-size: 1.2rem; 
        opacity: 0.9; 
        margin-top: 0.5rem;
    }
    
    /* Tarjetas */
    .profile-card {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 15px;
        padding: 1.2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
    }
    
    .profile-card:hover {
        border-color: var(--primary-light);
        box-shadow: 0 8px 15px rgba(0,51,102,0.1);
    }
    
    /* Iglesia actual */
    .church-card {
        background: #fffbeb;
        border-left: 6px solid var(--secondary);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .church-card h3 {
        color: #78350f;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0 0 0;
    }
    
    .church-card p {
        color: #92400e;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85rem;
        margin: 0;
    }
    
    /* Contenedor principal */
    .content-box {
        background: white;
        padding: 2rem;
        border-radius: 25px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Contenedor de imagen */
    .img-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 3px solid white;
        background: var(--gray-100);
        aspect-ratio: 1/1;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Secciones */
    .section-header {
        color: var(--primary);
        border-bottom: 2px solid var(--gray-200);
        padding-bottom: 0.75rem;
        margin: 2rem 0 1.5rem 0;
        font-weight: 700;
        font-size: 1.4rem;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .badge-warning {
        background: #fed7aa;
        color: #92400e;
    }
    
    /* Login */
    .login-container {
        background: white;
        padding: 2.5rem;
        border-radius: 25px;
        box-shadow: 0 20px 30px -10px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    /* Métricas */
    .metric-card {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.8rem;
        opacity: 0.9;
        text-transform: uppercase;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-title { font-size: 2.5rem; }
        .header-container { padding: 1.5rem; }
        .content-box { padding: 1.5rem; }
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
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <div style='font-size: 4rem;'>⛪</div>
                <h1 style='color: #003366; font-weight: 800; margin: 0;'>SIGEME</h1>
                <p style='color: #64748b;'>Sistema de Gestión Ministerial</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            
            if st.form_submit_button("Acceder", use_container_width=True, type="primary"):
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
    <div class='header-container'>
        <h1 class='main-title'>SIGEME</h1>
        <p class='sub-title'>Distrito Sur Fronterizo</p>
    </div>
    """, unsafe_allow_html=True)
    
    sheets, drive_service = conectar_servicios_google()
    
    if not sheets:
        st.error("No se pudo conectar a Google Sheets. Verifica tu conexión y credenciales.")
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
            <div class='metric-card'>
                <div class='metric-value'>{len(df_ministros)}</div>
                <div class='metric-label'>Total Ministros</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            activos = len(df_final[df_final['IGLESIA_RESULTADO'] != "Sin Iglesia Asignada"])
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{activos}</div>
                <div class='metric-label'>Ministros Activos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{df_iglesias_cat['NOMBRE'].nunique()}</div>
                <div class='metric-label'>Iglesias</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            hoy = datetime.now().strftime("%d/%m/%Y")
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{hoy}</div>
                <div class='metric-label'>Fecha</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Selector de ministro
        col_nombre = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_nombre].unique().tolist())
        
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        seleccion = st.selectbox("Seleccione un Ministro:", ["-- Seleccionar --"] + lista_ministros)
        
        if seleccion != "-- Seleccionar --":
            data = df_final[df_final[col_nombre] == seleccion].iloc[0]
            current_id = str(data['ID_MINISTRO'])
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown("### Fotografía")
                col_foto = next((c for c in data.index if 'FOTO' in c or 'IMAGEN' in c), None)
                img_data = descargar_foto_drive(drive_service, data[col_foto]) if col_foto else None
                
                if img_data:
                    st.markdown("<div class='img-container'>", unsafe_allow_html=True)
                    st.image(img_data, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='img-container'><div style='font-size: 5rem;'>👤</div></div>", unsafe_allow_html=True)
            
            with col2:
                st.subheader(data[col_nombre])
                st.markdown(f"""
                <div class='church-card'>
                    <p>IGLESIA ACTUAL (Gestión {data['AÑO_ULTIMO']})</p>
                    <h3>{data['IGLESIA_RESULTADO']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Información adicional
                excluir = ['ID_MINISTRO', 'NOMBRE', 'IGLESIA', 'MINISTRO', 'NOMBRE_REL', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO', 'ID', col_foto]
                visible_fields = [f for f in data.index if f not in excluir and not f.endswith(('_X', '_Y', '_REL'))]
                
                cols_info = st.columns(2)
                for i, field in enumerate(visible_fields):
                    val = str(data[field]).strip()
                    with cols_info[i % 2]:
                        st.markdown(f"""
                        <div class='profile-card'>
                            <small style='color:#64748b; font-weight:600; text-transform:uppercase;'>{field}</small><br>
                            <span style='color:#0f172a; font-weight:500;'>{val if val and val != "nan" else "---"}</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Revisiones
            st.markdown("<h3 class='section-header'>📝 HISTORIAL DE REVISIONES</h3>", unsafe_allow_html=True)
            df_rev = df_revisiones_raw[df_revisiones_raw['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_rev.empty:
                df_rev_show = pd.merge(df_rev, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                df_rev_show['IGLESIA'] = df_rev_show['NOMBRE'].fillna(df_rev_show['IGLESIA'])
                
                for _, row in df_rev_show.sort_values('FEC_REVISION', ascending=False).iterrows():
                    status_class = "badge-success" if "COMPLETADA" in str(row['STATUS']).upper() else "badge-warning"
                    st.markdown(f"""
                    <div class='profile-card' style='margin-bottom: 0.5rem;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <strong>{row['IGLESIA']}</strong>
                            <span class='badge {status_class}'>{row['STATUS']}</span>
                        </div>
                        <div style='color: #64748b;'>📅 {row['FEC_REVISION']} | ⏭️ {row['PROX_REVISION']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay revisiones registradas.")
            
            # Historial de gestión
            st.markdown("<h3 class='section-header'>🏛️ HISTORIAL DE GESTIÓN</h3>", unsafe_allow_html=True)
            df_hist = df_relacion[df_relacion['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_hist.empty:
                df_hist_show = pd.merge(df_hist, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                
                for _, row in df_hist_show.sort_values('AÑO', ascending=False).iterrows():
                    st.markdown(f"""
                    <div class='profile-card' style='margin-bottom: 0.5rem;'>
                        <div><span style='background: #003366; color: white; padding: 0.2rem 0.8rem; border-radius: 10px;'>{int(row['AÑO'])}</span></div>
                        <div><strong>{row['NOMBRE']}</strong></div>
                        <div style='color: #64748b;'>{row['OBSERVACION']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay historial de gestión.")
            
            # Estudios
            col_est1, col_est2 = st.columns(2)
            
            with col_est1:
                st.markdown("<h3 class='section-header'>📚 ESTUDIOS TEOLÓGICOS</h3>", unsafe_allow_html=True)
                t = df_est_teo_raw[df_est_teo_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not t.empty:
                    for _, row in t.iterrows():
                        st.markdown(f"""
                        <div class='profile-card' style='margin-bottom: 0.5rem;'>
                            <strong>{row['NIVEL']}</strong><br>
                            <span style='color: #64748b;'>{row['ESCUELA']} | {row['PERIODO']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No registra estudios teológicos")
            
            with col_est2:
                st.markdown("<h3 class='section-header'>🎓 ESTUDIOS ACADÉMICOS</h3>", unsafe_allow_html=True)
                a = df_est_aca_raw[df_est_aca_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not a.empty:
                    for _, row in a.iterrows():
                        st.markdown(f"""
                        <div class='profile-card' style='margin-bottom: 0.5rem;'>
                            <strong>{row['NIVEL']}</strong><br>
                            <span style='color: #64748b;'>{row['ESCUELA']} | {row['PERIODO']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No registra estudios académicos")
        
        else:
            st.info("Seleccione un ministro para ver su información.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div style='text-align: center; margin-top: 2rem; color: #64748b; font-size: 0.8rem;'>
            <hr style='opacity: 0.2;'>
            <p>© 2024 SIGEME - Sistema de Gestión Ministerial | Distrito Sur Fronterizo</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error procesando datos: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()