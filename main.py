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
        margin-bottom: 1rem;
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
        st.error("Archivo credenciales.json no encontrado")
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
        st.error(f"Error de conexión: {e}")
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
    if not check_password(): st.stop()

    sheets, drive_service = conectar_servicios_google()
    
    if sheets:
        with st.spinner('Cargando datos desde la nube...'):
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

        except Exception as e:
            st.error(f"Error procesando tablas: {e}")
            df_final = df_ministros

        # --- INTERFAZ ---
        st.markdown("<div class='header-container'><h1 class='main-title'>SIGEME</h1><p class='sub-title'>Distrito Sur Fronterizo</p></div>", unsafe_allow_html=True)

        col_nombre = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_nombre].unique().tolist())
        
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        seleccion = st.selectbox("Seleccione un Ministro:", ["-- Seleccionar --"] + lista_ministros)

        if seleccion != "-- Seleccionar --":
            data = df_final[df_final[col_nombre] == seleccion].iloc[0]
            current_id = str(data['ID_MINISTRO'])
            
            c1, c2 = st.columns([1, 3])
            
            with c1:
                st.markdown("### 👤 Fotografía")
                col_foto = next((c for c in data.index if 'FOTO' in c or 'IMAGEN' in c), None)
                
                img_data = descargar_foto_drive(drive_service, data[col_foto]) if col_foto else None
                
                if img_data:
                    st.markdown("<div class='img-container'>", unsafe_allow_html=True)
                    st.image(img_data, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='img-container' style='padding:40px 0; font-size:6rem;'>👤</div>", unsafe_allow_html=True)
            
            with c2:
                st.subheader(data[col_nombre])
                st.markdown(f"""
                <div class="profile-card" style="border-left: 6px solid #fbbf24; background: #fffbeb;">
                    <p style='margin:0; font-size:0.8rem; color:#92400e; font-weight:bold;'>IGLESIA ACTUAL (Gestión {data['AÑO_ULTIMO']})</p>
                    <h3 style='margin:0; color:#78350f;'>{data['IGLESIA_RESULTADO']}</h3>
                </div>
                """, unsafe_allow_html=True)

                excluir = ['ID_MINISTRO', 'NOMBRE', 'IGLESIA', 'MINISTRO', 'NOMBRE_REL', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO', 'ID', col_foto]
                visible_fields = [f for f in data.index if f not in excluir and not f.endswith(('_X', '_Y', '_REL'))]
                
                cols_info = st.columns(2)
                for i, field in enumerate(visible_fields):
                    with cols_info[i % 2]:
                        val = str(data[field]).strip()
                        st.markdown(f"""
                        <div class="profile-card">
                            <small style='color:#64748b; font-weight:600; text-transform:uppercase;'>{field}</small><br>
                            <span style='color:#0f172a; font-weight:500;'>{val if val and val != "nan" else "---"}</span>
                        </div>
                        """, unsafe_allow_html=True)

            # --- TABLAS HISTÓRICAS ---
            st.markdown("<h3 class='section-header'>📝 HISTORIAL DE REVISIONES</h3>", unsafe_allow_html=True)
            df_rev = df_revisiones_raw[df_revisiones_raw['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_rev.empty:
                df_rev_show = pd.merge(df_rev, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                df_rev_show['IGLESIA'] = df_rev_show['NOMBRE'].fillna(df_rev_show['IGLESIA'])
                st.dataframe(df_rev_show[['IGLESIA', 'FEC_REVISION', 'PROX_REVISION', 'STATUS']].sort_values('FEC_REVISION', ascending=False), use_container_width=True, hide_index=True)
            else: st.info("No hay revisiones registradas.")

            st.markdown("<h3 class='section-header'>🏛️ HISTORIAL DE GESTIÓN EN IGLESIAS</h3>", unsafe_allow_html=True)
            df_hist = df_relacion[df_relacion['MINISTRO'].astype(str).str.strip() == current_id]
            if not df_hist.empty:
                df_hist_show = pd.merge(df_hist, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                st.dataframe(df_hist_show[['AÑO', 'NOMBRE', 'OBSERVACION']].sort_values('AÑO', ascending=False), use_container_width=True, hide_index=True)
            else: st.info("No hay historial de gestión.")

            # --- SECCIÓN DE ESTUDIOS (REORDENADA: UNO DEBAJO DEL OTRO) ---
            st.markdown("<h3 class='section-header'>📚 ESTUDIOS TEOLÓGICOS</h3>", unsafe_allow_html=True)
            t = df_est_teo_raw[df_est_teo_raw['MINISTRO'].astype(str).str.strip() == current_id]
            if not t.empty:
                st.dataframe(t[['NIVEL', 'ESCUELA', 'PERIODO', 'CERTIFICADO']], use_container_width=True, hide_index=True)
            else:
                st.info("No se registran estudios teológicos.")

            st.markdown("<h3 class='section-header'>🎓 ESTUDIOS ACADÉMICOS</h3>", unsafe_allow_html=True)
            a = df_est_aca_raw[df_est_aca_raw['MINISTRO'].astype(str).str.strip() == current_id]
            if not a.empty:
                st.dataframe(a[['NIVEL', 'ESCUELA', 'PERIODO', 'CERTIFICADO']], use_container_width=True, hide_index=True)
            else:
                st.info("No se registran estudios académicos.")

        else:
            st.info("Seleccione un ministro para ver su información.")
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()