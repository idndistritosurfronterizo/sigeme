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

# --- DISEÑO CSS MEJORADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Variables globales */
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
        background: linear-gradient(135deg, var(--gray-50) 0%, #ffffff 100%);
    }
    
    /* Header mejorado con animación */
    .header-container {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 3rem 2rem;
        border-radius: 30px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 30px -10px rgba(0,51,102,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shine 8s infinite linear;
    }
    
    @keyframes shine {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .main-title { 
        font-size: 4rem; 
        font-weight: 800; 
        margin: 0; 
        letter-spacing: -2px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .sub-title { 
        font-size: 1.3rem; 
        opacity: 0.95; 
        margin-top: 0.5rem;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Tarjetas mejoradas */
    .profile-card {
        background: #ffffff;
        border: 1px solid var(--gray-200);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .profile-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px -8px rgba(0,51,102,0.15);
        border-color: var(--primary-light);
    }
    
    /* Tarjeta especial para iglesia actual */
    .church-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-left: 6px solid var(--secondary);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 15px -6px rgba(251,191,36,0.3);
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
        letter-spacing: 0.5px;
        margin: 0;
    }
    
    /* Contenedor de contenido */
    .content-box {
        background: white;
        padding: 2.5rem;
        border-radius: 30px;
        box-shadow: 0 4px 6px -2px rgba(0,0,0,0.05), 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    /* Contenedor de imagen mejorado */
    .img-container {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 12px 25px -8px rgba(0,51,102,0.2);
        border: 4px solid white;
        background: linear-gradient(135deg, var(--gray-100) 0%, var(--gray-200) 100%);
        aspect-ratio: 1/1;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.3s ease;
    }
    
    .img-container:hover {
        transform: scale(1.02);
    }
    
    /* Secciones con encabezados decorativos */
    .section-header {
        color: var(--primary);
        border-bottom: 3px solid var(--secondary);
        padding-bottom: 0.75rem;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-header::before {
        content: '';
        width: 4px;
        height: 28px;
        background: var(--secondary);
        border-radius: 4px;
        display: inline-block;
    }
    
    /* Badges y etiquetas */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .badge-success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .badge-warning {
        background: #fed7aa;
        color: #92400e;
    }
    
    /* Login container mejorado */
    .login-container {
        background: white;
        padding: 3rem;
        border-radius: 32px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
        text-align: center;
        border: 1px solid var(--gray-100);
    }
    
    /* DataFrames personalizados */
    .dataframe-container {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--gray-200);
        margin: 1rem 0;
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease forwards;
    }
    
    /* Estilos para métricas */
    .metric-card {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 16px -4px rgba(0,51,102,0.3);
    }
    
    .metric-card .value {
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1;
    }
    
    .metric-card .label {
        font-size: 0.875rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-title { font-size: 2.5rem; }
        .header-container { padding: 2rem 1rem; }
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
        with st.container():
            st.markdown("<div class='login-container fade-in'>", unsafe_allow_html=True)
            
            # Logo o icono
            st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <div style='font-size: 4rem;'>⛪</div>
                <h1 style='color: #003366; font-weight: 800; margin: 0;'>SIGEME</h1>
                <p style='color: #64748b; margin: 0;'>Sistema de Gestión Ministerial</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                user = st.text_input("Usuario", placeholder="Ingresa tu usuario")
                password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
                
                if st.form_submit_button("Acceder al Sistema", use_container_width=True, type="primary"):
                    if user == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas. Por favor, intenta de nuevo.")
            
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
        with st.spinner("🔄 Conectando con Google Drive..."):
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
        
        st.success("✅ Conexión exitosa con Google Drive")
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

def mostrar_estadisticas(df_ministros):
    """Muestra estadísticas rápidas en la parte superior"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="value">{}</div>
            <div class="label">Total Ministros</div>
        </div>
        """.format(len(df_ministros)), unsafe_allow_html=True)
    
    with col2:
        # Ministros activos (con iglesia asignada)
        activos = len(df_ministros[df_ministros['IGLESIA_RESULTADO'] != "Sin Iglesia Asignada"]) if 'IGLESIA_RESULTADO' in df_ministros.columns else 0
        st.markdown("""
        <div class="metric-card">
            <div class="value">{}</div>
            <div class="label">Ministros Activos</div>
        </div>
        """.format(activos), unsafe_allow_html=True)
    
    with col3:
        # Última actualización
        hoy = datetime.now().strftime("%d/%m/%Y")
        st.markdown("""
        <div class="metric-card">
            <div class="value">{}</div>
            <div class="label">Fecha</div>
        </div>
        """.format(hoy), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="value">⛪</div>
            <div class="label">Distrito Sur</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    if not check_password(): st.stop()

    # Header principal
    st.markdown("""
    <div class='header-container'>
        <h1 class='main-title'>SIGEME</h1>
        <p class='sub-title'>Sistema de Gestión Ministerial - Distrito Sur Fronterizo</p>
    </div>
    """, unsafe_allow_html=True)

    sheets, drive_service = conectar_servicios_google()
    
    if sheets:
        with st.spinner('🔄 Cargando datos desde la nube...'):
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

            # Mostrar estadísticas
            mostrar_estadisticas(df_final)

        except Exception as e:
            st.error(f"❌ Error procesando tablas: {e}")
            df_final = df_ministros

        # --- INTERFAZ PRINCIPAL ---
        col_nombre = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_nombre].unique().tolist())
        
        st.markdown("<div class='content-box fade-in'>", unsafe_allow_html=True)
        
        # Selector mejorado
        st.markdown("### 👥 Selección de Ministro")
        col1, col2 = st.columns([3, 1])
        with col1:
            seleccion = st.selectbox("", ["-- Seleccionar un ministro --"] + lista_ministros, label_visibility="collapsed")
        with col2:
            if seleccion != "-- Seleccionar un ministro --":
                st.markdown(f"<div style='text-align: right; padding-top: 8px;'><span class='badge badge-success'>✓ Ministro Seleccionado</span></div>", unsafe_allow_html=True)

        if seleccion != "-- Seleccionar un ministro --":
            data = df_final[df_final[col_nombre] == seleccion].iloc[0]
            current_id = str(data['ID_MINISTRO'])
            
            # Separador visual
            st.markdown("<hr style='margin: 2rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
            
            # Perfil del ministro
            c1, c2 = st.columns([1, 3])
            
            with c1:
                st.markdown("### 📸 Fotografía")
                col_foto = next((c for c in data.index if 'FOTO' in c or 'IMAGEN' in c), None)
                
                img_data = descargar_foto_drive(drive_service, data[col_foto]) if col_foto else None
                
                if img_data:
                    st.markdown("<div class='img-container'>", unsafe_allow_html=True)
                    st.image(img_data, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class='img-container' style='background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);'>
                        <div style='font-size: 5rem;'>👤</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with c2:
                st.markdown(f"<h2 style='color: #003366; margin-top: 0;'>{data[col_nombre]}</h2>", unsafe_allow_html=True)
                
                # Iglesia actual
                st.markdown(f"""
                <div class='church-card'>
                    <p>IGLESIA ACTUAL</p>
                    <h3>{data['IGLESIA_RESULTADO']}</h3>
                    <div style='margin-top: 0.5rem;'>
                        <span class='badge badge-warning'>Gestión {data['AÑO_ULTIMO']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Información adicional en grid
                excluir = ['ID_MINISTRO', 'NOMBRE', 'IGLESIA', 'MINISTRO', 'NOMBRE_REL', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO', 'ID', col_foto]
                visible_fields = [f for f in data.index if f not in excluir and not f.endswith(('_X', '_Y', '_REL'))]
                
                st.markdown("### 📋 Información Personal")
                cols_info = st.columns(2)
                for i, field in enumerate(visible_fields):
                    with cols_info[i % 2]:
                        val = str(data[field]).strip()
                        st.markdown(f"""
                        <div class='profile-card'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <span style='color:#64748b; font-weight:600; text-transform:uppercase; font-size:0.8rem;'>{field}</span>
                            </div>
                            <div style='color:#0f172a; font-weight:500; font-size:1.1rem; margin-top:0.5rem;'>
                                {val if val and val != "nan" else "—"}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # --- TABLAS HISTÓRICAS CON MEJOR PRESENTACIÓN ---
            st.markdown("<h3 class='section-header'>📝 HISTORIAL DE REVISIONES</h3>", unsafe_allow_html=True)
            df_rev = df_revisiones_raw[df_revisiones_raw['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_rev.empty:
                df_rev_show = pd.merge(df_rev, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                df_rev_show['IGLESIA'] = df_rev_show['NOMBRE'].fillna(df_rev_show['IGLESIA'])
                
                # Aplicar colores según STATUS
                def color_status(val):
                    if 'COMPLETADA' in str(val).upper():
                        return 'background-color: #d1fae5; color: #065f46'
                    elif 'PENDIENTE' in str(val).upper():
                        return 'background-color: #fed7aa; color: #92400e'
                    return ''
                
                st.dataframe(
                    df_rev_show[['IGLESIA', 'FEC_REVISION', 'PROX_REVISION', 'STATUS']]
                    .sort_values('FEC_REVISION', ascending=False)
                    .style.applymap(color_status, subset=['STATUS']),
                    use_container_width=True,
                    hide_index=True
                )
            else: 
                st.info("📭 No hay revisiones registradas para este ministro.")

            st.markdown("<h3 class='section-header'>🏛️ HISTORIAL DE GESTIÓN EN IGLESIAS</h3>", unsafe_allow_html=True)
            df_hist = df_relacion[df_relacion['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_hist.empty:
                df_hist_show = pd.merge(df_hist, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                st.dataframe(
                    df_hist_show[['AÑO', 'NOMBRE', 'OBSERVACION']]
                    .sort_values('AÑO', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
            else: 
                st.info("📭 No hay historial de gestión registrado.")

            # Estudios en columnas mejoradas
            st.markdown("<h3 class='section-header'>📚 ESTUDIOS REALIZADOS</h3>", unsafe_allow_html=True)
            
            col_teo, col_aca = st.columns(2)
            
            with col_teo:
                st.markdown("#### 📖 Estudios Teológicos")
                t = df_est_teo_raw[df_est_teo_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not t.empty:
                    st.dataframe(
                        t[['NIVEL', 'ESCUELA', 'PERIODO', 'CERTIFICADO']],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No registra estudios teológicos")

            with col_aca:
                st.markdown("#### 🎓 Estudios Académicos")
                a = df_est_aca_raw[df_est_aca_raw['MINISTRO'].astype(str).str.strip() == current_id]
                if not a.empty:
                    st.dataframe(
                        a[['NIVEL', 'ESCUELA', 'PERIODO', 'CERTIFICADO']],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No registra estudios académicos")

        else:
            # Mensaje de bienvenida cuando no hay selección
            st.markdown("""
            <div style='text-align: center; padding: 4rem 2rem; background: #f8fafc; border-radius: 20px;'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>👋</div>
                <h3 style='color: #003366;'>Bienvenido al Sistema de Gestión Ministerial</h3>
                <p style='color: #64748b;'>Seleccione un ministro del listado para ver su información detallada</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style='text-align: center; margin-top: 3rem; padding: 1rem; color: #64748b; font-size: 0.8rem;'>
        <hr style='opacity: 0.1; margin-bottom: 1rem;'>
        <p>© 2024 SIGEME - Sistema de Gestión Ministerial | Distrito Sur Fronterizo</p>
        <p style='opacity: 0.6;'>Desarrollado para la administración eficiente del ministerio</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()