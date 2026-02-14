import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import os
import io
import urllib.parse
import time
import re

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
        margin-top: 10px;
        display: block;
    }
    .img-container img {
        width: 100%;
        height: auto;
        object-fit: cover;
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

def obtener_servicios():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if not os.path.exists("credenciales.json"):
        st.error("Archivo credenciales.json no encontrado")
        return None, None
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        drive_service = build('drive', 'v3', credentials=creds)
        spreadsheet = client.open("BD MINISTROS")
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

def safe_get_dataframe(worksheet):
    try:
        data = worksheet.get_all_values()
        if not data: return pd.DataFrame()
        headers = data[0]
        clean_headers = [str(h).strip().upper() if h.strip() else f"COL_{i}" for i, h in enumerate(headers)]
        df = pd.DataFrame(data[1:], columns=clean_headers)
        # Convertimos todo a string para evitar conflictos de tipos en las comparaciones
        return df.apply(lambda x: x.astype(str).str.strip() if x.dtype == "object" else x.astype(str))
    except:
        return pd.DataFrame()

def descargar_imagen_bytes(drive_service, ruta_appsheet):
    texto = str(ruta_appsheet).strip()
    if not texto or texto.lower() in ["0", "nan", "none", "null", ""]:
        return None

    try:
        nombre_archivo = texto.split('/')[-1]
        query = f"name = '{nombre_archivo}' and trashed = false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            id_prefijo = nombre_archivo.split('.')[0]
            query_parcial = f"name contains '{id_prefijo}' and trashed = false"
            results = drive_service.files().list(q=query_parcial, fields="files(id, name)").execute()
            items = results.get('files', [])

        if items:
            file_id = items[0]['id']
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.seek(0)
            return fh.read()
    except:
        return None
    return None

def main():
    if not check_password(): st.stop()

    sheets, drive_service = obtener_servicios()
    if sheets and all(sheets):
        df_ministros = safe_get_dataframe(sheets[0])
        df_relacion = safe_get_dataframe(sheets[1])
        df_iglesias_cat = safe_get_dataframe(sheets[2])
        df_est_teo_raw = safe_get_dataframe(sheets[3])
        df_est_aca_raw = safe_get_dataframe(sheets[4])
        df_revisiones_raw = safe_get_dataframe(sheets[5])

        if df_ministros.empty:
            st.error("No se encontraron datos en la tabla MINISTRO.")
            st.stop()

        id_col = 'ID_MINISTRO' if 'ID_MINISTRO' in df_ministros.columns else df_ministros.columns[0]
        col_nombre = 'NOMBRE' if 'NOMBRE' in df_ministros.columns else df_ministros.columns[1]

        try:
            df_relacion['AÑO'] = pd.to_numeric(df_relacion['AÑO'], errors='coerce').fillna(0)
            rel_min_col = 'MINISTRO' if 'MINISTRO' in df_relacion.columns else df_relacion.columns[0]
            df_rel_actual = df_relacion.sort_values(by=[rel_min_col, 'AÑO'], ascending=[True, False]).drop_duplicates(subset=[rel_min_col])
            
            df_rel_con_nombre = pd.merge(df_rel_actual, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
            df_final = pd.merge(df_ministros, df_rel_con_nombre[[rel_min_col, 'NOMBRE', 'AÑO']], left_on=id_col, right_on=rel_min_col, how='left', suffixes=('', '_REL'))
            df_final['IGLESIA_RESULTADO'] = df_final['NOMBRE_REL'].fillna("Sin Iglesia Asignada")
            df_final['AÑO_ULTIMO'] = df_final['AÑO'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and str(x) != '0.0' and str(x) != '0' else "N/A")
        except:
            df_final = df_ministros.copy()
            df_final['IGLESIA_RESULTADO'] = "Error al procesar"
            df_final['AÑO_ULTIMO'] = "N/A"

        st.markdown("<div class='header-container'><h1 class='main-title'>SIGEME</h1><p class='sub-title'>Distrito Sur Fronterizo</p></div>", unsafe_allow_html=True)

        lista_ministros = sorted(df_final[col_nombre].unique().tolist())
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        seleccion = st.selectbox("Seleccione un Ministro:", ["-- Seleccionar --"] + lista_ministros)

        if seleccion != "-- Seleccionar --":
            data = df_final[df_final[col_nombre] == seleccion].iloc[0]
            current_id = str(data[id_col]).strip()
            
            c1, c2 = st.columns([1, 3])
            
            with c1:
                st.markdown("### 👤 Fotografía")
                col_foto = next((c for c in data.index if any(x in c for x in ['FOTO', 'IMAGEN', 'FOTOGRAFIA'])), None)
                
                img_bytes = None
                if col_foto and drive_service:
                    with st.spinner('Cargando...'):
                        img_bytes = descargar_imagen_bytes(drive_service, data[col_foto])
                
                if img_bytes:
                    st.markdown("<div class='img-container'>", unsafe_allow_html=True)
                    st.image(img_bytes, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='img-container' style='padding: 50px 0;'><div style='font-size:6rem; color:#cbd5e1;'>👤</div><br><small style='color:#64748b;'>Imagen no encontrada</small></div>", unsafe_allow_html=True)
            
            with c2:
                st.subheader(data[col_nombre])
                st.markdown(f"""
                <div class="profile-card" style="border-left: 6px solid #fbbf24; background: #fffbeb;">
                    <p style='margin:0; font-size:0.8rem; color:#92400e; font-weight:bold;'>IGLESIA ACTUAL (Gestión {data['AÑO_ULTIMO']})</p>
                    <h3 style='margin:0; color:#78350f;'>{data['IGLESIA_RESULTADO']}</h3>
                </div>
                """, unsafe_allow_html=True)

                excluir = [id_col, 'NOMBRE', 'IGLESIA', 'MINISTRO', 'NOMBRE_REL', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO', 'ID', col_foto]
                cols_info = st.columns(2)
                visible_fields = [f for f in data.index if f not in excluir and not f.endswith(('_X', '_Y', '_REL'))]
                
                for i, field in enumerate(visible_fields):
                    with cols_info[i % 2]:
                        val = str(data[field]).strip()
                        display_val = val if val not in ["", "0", "nan", "None", "0.0"] else "---"
                        st.markdown(f"""<div class="profile-card"><small style='color:#64748b; font-weight:600; text-transform:uppercase;'>{field}</small><br><span style='color:#0f172a; font-weight:500;'>{display_val}</span></div>""", unsafe_allow_html=True)

            st.markdown("<h3 class='section-header'>🎓 FORMACIÓN ACADÉMICA Y TEOLÓGICA</h3>", unsafe_allow_html=True)
            est_col1, est_col2 = st.columns(2)
            
            with est_col1:
                st.markdown("**Estudios Teológicos**")
                id_col_teo = next((c for c in df_est_teo_raw.columns if any(x in c for x in ['ID_MINISTRO', 'MINISTRO', 'ID'])), None)
                if id_col_teo:
                    # Filtro robusto convirtiendo ambos a string
                    df_teo = df_est_teo_raw[df_est_teo_raw[id_col_teo].astype(str).str.strip() == current_id]
                    if not df_teo.empty:
                        cols_mostrar = [c for c in ['NIVEL', 'INSTITUCION', 'ESTADO'] if c in df_teo.columns]
                        st.dataframe(df_teo[cols_mostrar], use_container_width=True, hide_index=True)
                    else: st.info("Sin registros teológicos.")
                else: st.warning("Columna de ID no encontrada.")

            with est_col2:
                st.markdown("**Estudios Académicos**")
                id_col_aca = next((c for c in df_est_aca_raw.columns if any(x in c for x in ['ID_MINISTRO', 'MINISTRO', 'ID'])), None)
                if id_col_aca:
                    df_aca = df_est_aca_raw[df_est_aca_raw[id_col_aca].astype(str).str.strip() == current_id]
                    if not df_aca.empty:
                        cols_mostrar = [c for c in ['NIVEL', 'TITULO', 'ESTADO'] if c in df_aca.columns]
                        st.dataframe(df_aca[cols_mostrar], use_container_width=True, hide_index=True)
                    else: st.info("Sin registros académicos.")
                else: st.warning("Columna de ID no encontrada.")

            st.markdown("<h3 class='section-header'>📝 REVISIONES</h3>", unsafe_allow_html=True)
            id_col_rev = next((c for c in df_revisiones_raw.columns if any(x in c for x in ['ID_MINISTRO', 'MINISTRO', 'ID'])), None)
            if id_col_rev:
                rev_min = df_revisiones_raw[df_revisiones_raw[id_col_rev].astype(str).str.strip() == current_id]
                if not rev_min.empty:
                    rev_con_nombre = pd.merge(rev_min, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                    rev_con_nombre['IGLESIA_DISPLAY'] = rev_con_nombre['NOMBRE'].fillna(rev_con_nombre['IGLESIA'])
                    st.dataframe(rev_con_nombre[['IGLESIA_DISPLAY', 'FEC_REVISION', 'STATUS']].sort_values(by='FEC_REVISION', ascending=False), use_container_width=True, hide_index=True)
                else: st.info("Sin registros de revisión.")

            st.markdown("<h3 class='section-header'>🏛️ GESTIÓN EN IGLESIAS</h3>", unsafe_allow_html=True)
            rel_min_col_hist = next((c for c in df_relacion.columns if any(x in c for x in ['ID_MINISTRO', 'MINISTRO', 'ID'])), None)
            if rel_min_col_hist:
                rel_min = df_relacion[df_relacion[rel_min_col_hist].astype(str).str.strip() == current_id].copy()
                if not rel_min.empty:
                    rel_con_nombre = pd.merge(rel_min, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                    st.dataframe(rel_con_nombre[['AÑO', 'NOMBRE', 'OBSERVACION']].sort_values(by='AÑO', ascending=False), use_container_width=True, hide_index=True)
                else: st.info("Sin historial de iglesias.")

        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()