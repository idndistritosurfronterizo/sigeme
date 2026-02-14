import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import os
import io

# --- CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_CORRECTO = "admin"
PASSWORD_CORRECTO = "ministros2024"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="SIGEME - Distrito Sur Fronterizo",
    page_icon="⛪",
    layout="wide"
)

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    .header-container {
        background: linear-gradient(135deg, #003366 0%, #00509d 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,51,102,0.15);
    }
    .main-title { font-size: 3.5rem; font-weight: 800; margin: 0; letter-spacing: -1px; }
    .sub-title { font-size: 1.2rem; opacity: 0.9; margin-top: 0.5rem; }
    .profile-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 20px;
        margin-top: 10px;
    }
    .content-box {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .img-container {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 3px solid white;
        text-align: center;
        background: #f1f5f9;
    }
    .img-container img {
        width: 100%;
        height: auto;
        display: block;
    }
    .section-header {
        color: #003366;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 800;
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
        st.markdown("<div style='text-align: center; padding: 40px; background: white; border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        st.title("SIGEME")
        with st.form("login_form"):
            user = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Acceder", use_container_width=True):
                if user == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
        st.markdown("</div>", unsafe_allow_html=True)
    return False

def conectar_servicios_google():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if not os.path.exists("credenciales.json"):
        st.error("Archivo credenciales.json no encontrado")
        return None, None
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        # Servicio para Sheets
        client = gspread.authorize(creds)
        spreadsheet = client.open("BD MINISTROS")
        # Servicio para Drive (Fotos)
        drive_service = build('drive', 'v3', credentials=creds)
        
        worksheets = (
            spreadsheet.worksheet("MINISTRO"), 
            spreadsheet.worksheet("IGLESIA"), 
            spreadsheet.worksheet("IGLESIAS"),
            spreadsheet.worksheet("ESTUDIOS TEOLOGICOS"),
            spreadsheet.worksheet("ESTUDIOS ACADEMICOS"),
            spreadsheet.worksheet("Revision")
        )
        return worksheets, drive_service
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

def descargar_foto_drive(drive_service, ruta_appsheet):
    """Busca y descarga la imagen de Drive basándose en la ruta guardada por AppSheet."""
    if not ruta_appsheet or str(ruta_appsheet).strip() == "":
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
    if not check_password(): st.stop()

    res_sheets, drive_service = conectar_servicios_google()
    
    if res_sheets and all(res_sheets):
        sheet_m, sheet_rel, sheet_ig, sheet_est_teo, sheet_est_aca, sheet_rev = res_sheets
        
        # Cargar DataFrames
        df_ministros = pd.DataFrame(sheet_m.get_all_records())
        df_relacion = pd.DataFrame(sheet_rel.get_all_records())
        df_iglesias_cat = pd.DataFrame(sheet_ig.get_all_records())
        df_est_teo_raw = pd.DataFrame(sheet_est_teo.get_all_records())
        df_est_aca_raw = pd.DataFrame(sheet_est_aca.get_all_records())
        df_revisiones_raw = pd.DataFrame(sheet_rev.get_all_records())

        # Limpieza estándar de nombres de columnas
        for df in [df_ministros, df_relacion, df_iglesias_cat, df_est_teo_raw, df_est_aca_raw, df_revisiones_raw]:
            df.columns = [c.strip().upper() for c in df.columns]

        try:
            # Normalización (Tu lógica estable)
            df_relacion['AÑO'] = pd.to_numeric(df_relacion['AÑO'], errors='coerce').fillna(0)
            df_relacion['MINISTRO'] = df_relacion['MINISTRO'].astype(str).str.strip()
            df_relacion['IGLESIA'] = df_relacion['IGLESIA'].astype(str).str.strip()
            df_ministros['ID_MINISTRO'] = df_ministros['ID_MINISTRO'].astype(str).str.strip()
            df_iglesias_cat['ID'] = df_iglesias_cat['ID'].astype(str).str.strip()
            
            df_rel_actual = df_relacion.sort_values(by=['MINISTRO', 'AÑO'], ascending=[True, False]).drop_duplicates(subset=['MINISTRO'])
            df_rel_con_nombre = pd.merge(df_rel_actual, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
            
            df_final = pd.merge(df_ministros, df_rel_con_nombre[['MINISTRO', 'NOMBRE', 'AÑO']], left_on='ID_MINISTRO', right_on='MINISTRO', how='left', suffixes=('', '_REL'))
            df_final['IGLESIA_RESULTADO'] = df_final['NOMBRE_REL'].fillna("Sin Iglesia Asignada")
            df_final['AÑO_ULTIMO'] = df_final['AÑO'].apply(lambda x: int(x) if pd.notnull(x) and x > 0 else "N/A")

        except Exception as e:
            st.error(f"Error procesando datos: {e}")
            df_final = df_ministros.copy()
            df_final['IGLESIA_RESULTADO'] = "Error de Datos"
            df_final['AÑO_ULTIMO'] = "N/A"

        # --- INTERFAZ ---
        st.markdown("<div class='header-container'><h1 class='main-title'>SIGEME</h1><p class='sub-title'>Distrito Sur Fronterizo</p></div>", unsafe_allow_html=True)

        col_busqueda = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_busqueda].unique().tolist())
        
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        seleccion = st.selectbox("Seleccione un Ministro:", ["-- Seleccionar --"] + lista_ministros)

        if seleccion != "-- Seleccionar --":
            data = df_final[df_final[col_busqueda] == seleccion].iloc[0]
            current_id = str(data['ID_MINISTRO'])
            
            c1, c2 = st.columns([1, 3])
            
            with c1:
                st.markdown("### 👤 Fotografía")
                col_foto = next((c for c in data.index if 'FOTO' in c or 'IMAGEN' in c), None)
                
                # --- INTEGRACIÓN DE FOTO REAL ---
                img_data = None
                if col_foto and drive_service:
                    with st.spinner('Cargando foto...'):
                        img_data = descargar_foto_drive(drive_service, data[col_foto])
                
                if img_data:
                    st.markdown("<div class='img-container'>", unsafe_allow_html=True)
                    st.image(img_data, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class='img-container' style='padding: 40px 0;'>
                            <div style='font-size:6rem; color:#cbd5e1;'>👤</div>
                            <p style='color:#64748b; font-size:0.8rem;'>Sin fotografía</p>
                        </div>
                    """, unsafe_allow_html=True)
            
            with c2:
                st.subheader(data[col_busqueda])
                st.markdown(f"""
                <div class="profile-card" style="border-left: 6px solid #fbbf24; background: #fffbeb;">
                    <p style='margin:0; font-size:0.8rem; color:#92400e; font-weight:bold;'>IGLESIA ACTUAL (Gestión {data['AÑO_ULTIMO']})</p>
                    <h3 style='margin:0; color:#78350f;'>{data['IGLESIA_RESULTADO']}</h3>
                </div>
                """, unsafe_allow_html=True)

                excluir = ['ID_MINISTRO', 'NOMBRE', 'IGLESIA', 'MINISTRO', 'NOMBRE_REL', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO', 'ID', col_foto]
                cols_info = st.columns(2)
                visible_fields = [f for f in data.index if f not in excluir and not f.endswith(('_X', '_Y', '_REL'))]
                
                for i, field in enumerate(visible_fields):
                    with cols_info[i % 2]:
                        st.markdown(f"""
                        <div class="profile-card">
                            <small style='color:#64748b; font-weight:600; text-transform:uppercase;'>{field}</small><br>
                            <span style='color:#0f172a; font-weight:500;'>{data[field] if str(data[field]).strip() != "" else "---"}</span>
                        </div>
                        """, unsafe_allow_html=True)

            # --- SECCIONES DE TABLAS (Tu lógica original intacta) ---
            st.markdown("<h3 class='section-header'>📝 HISTORIAL DE REVISIONES</h3>", unsafe_allow_html=True)
            rev_min = df_revisiones_raw[df_revisiones_raw['MINISTRO'].astype(str) == current_id]
            if not rev_min.empty:
                rev_con_nombre = pd.merge(rev_min, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                rev_con_nombre['IGLESIA_DISPLAY'] = rev_con_nombre['NOMBRE'].fillna(rev_con_nombre['IGLESIA'])
                display_rev = rev_con_nombre[['IGLESIA_DISPLAY', 'FEC_REVISION', 'PROX_REVISION', 'STATUS']]
                display_rev.columns = ['IGLESIA', 'FEC_REVISION', 'PROX_REVISION', 'STATUS']
                st.dataframe(display_rev.sort_values(by='FEC_REVISION', ascending=False), use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron registros de revisiones.")

            st.markdown("<h3 class='section-header'>🏛️ HISTORIAL DE GESTIÓN EN IGLESIAS</h3>", unsafe_allow_html=True)
            rel_hist = df_relacion[df_relacion['MINISTRO'].astype(str) == current_id]
            if not rel_hist.empty:
                rel_con_nombre = pd.merge(rel_hist, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                display_rel = rel_con_nombre[['AÑO', 'NOMBRE', 'OBSERVACION']]
                display_rel.columns = ['AÑO', 'NOMBRE DE IGLESIA', 'OBSERVACION']
                st.dataframe(display_rel.sort_values(by='AÑO', ascending=False), use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontró historial de iglesias.")

            # Estudios Teológicos y Académicos
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("<h3 class='section-header'>📚 ESTUDIOS TEOLÓGICOS</h3>", unsafe_allow_html=True)
                df_t = df_est_teo_raw[df_est_teo_raw['MINISTRO'].astype(str) == current_id]
                if not df_t.empty:
                    st.dataframe(df_t[['NIVEL', 'ESCUELA', 'PERIODO', 'CERTIFICADO']], use_container_width=True, hide_index=True)
                else: st.info("Sin registros.")
            
            with col_t2:
                st.markdown("<h3 class='section-header'>🎓 ESTUDIOS ACADÉMICOS</h3>", unsafe_allow_html=True)
                df_a = df_est_aca_raw[df_est_aca_raw['MINISTRO'].astype(str) == current_id]
                if not df_a.empty:
                    st.dataframe(df_a[['NIVEL', 'ESCUELA', 'PERIODO', 'CERTIFICADO']], use_container_width=True, hide_index=True)
                else: st.info("Sin registros.")

        else:
            st.info("Utilice el buscador para localizar un ministro.")
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()