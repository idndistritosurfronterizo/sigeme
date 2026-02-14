import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
import urllib.parse
import time

# --- CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_CORRECTO = "admin"
PASSWORD_CORRECTO = "ministros2024"

# --- CONFIGURACIÓN APPSHEET ---
# Es vital que el App ID sea el correcto. A veces el nombre de la app es necesario antes del ID.
# Formato sugerido: NombreApp-ID
APPSHEET_APP_ID = "32c8e6c2-fc2a-4dd9-97e7-2d0cdb2af68e" 
APPSHEET_ACCESS_KEY = "V2-aH1dw-B1NeU-AkHMn-VW2ki-X4fcl-rVxWT-pgY26-NT1xZ" 

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
        min-height: 280px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .img-container img {
        width: 100%;
        height: auto;
        max-height: 400px;
        object-fit: contain;
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

def conectar_google_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if not os.path.exists("credenciales.json"):
        st.error("Archivo credenciales.json no encontrado")
        return None
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open("BD MINISTROS")
        return (
            spreadsheet.worksheet("MINISTRO"), 
            spreadsheet.worksheet("IGLESIA"), 
            spreadsheet.worksheet("IGLESIAS"),
            spreadsheet.worksheet("ESTUDIOS TEOLOGICOS"),
            spreadsheet.worksheet("ESTUDIOS ACADEMICOS"),
            spreadsheet.worksheet("Revision")
        )
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def safe_get_dataframe(worksheet):
    data = worksheet.get_all_values()
    if not data: return pd.DataFrame()
    headers = data[0]
    clean_headers = [h.strip().upper() if h.strip() else f"COL_{i}" for i, h in enumerate(headers)]
    return pd.DataFrame(data[1:], columns=clean_headers)

def obtener_url_imagen(ruta_relativa, nombre_tabla):
    """
    Genera la URL pública para AppSheet usando la API de archivos.
    """
    if not APPSHEET_APP_ID or not APPSHEET_ACCESS_KEY:
        return None
    
    ruta_limpia = str(ruta_relativa).strip()
    # Limpiar prefijos de ruta que a veces vienen en el Sheet
    if ruta_limpia.startswith('/'):
        ruta_limpia = ruta_limpia[1:]
        
    if not ruta_limpia or ruta_limpia.lower() in ["0", "nan", "none", "null", ""]:
        return None

    encoded_path = urllib.parse.quote(ruta_limpia)
    
    # URL de la API de AppSheet para recuperación de archivos de tabla
    # Se añade el ID de la app y la tabla correspondiente
    url = (
        f"https://www.appsheet.com/template/gettablefileurl"
        f"?appName={urllib.parse.quote(APPSHEET_APP_ID)}"
        f"&tableName={urllib.parse.quote(nombre_tabla)}"
        f"&fileName={encoded_path}"
        f"&applicationAccessKey={APPSHEET_ACCESS_KEY}"
        f"&v={int(time.time())}" # Versionado para evitar cache
    )
    return url

def main():
    if not check_password(): st.stop()

    res = conectar_google_sheets()
    if res and all(res):
        sheets = list(res)
        df_ministros = safe_get_dataframe(sheets[0])
        df_relacion = safe_get_dataframe(sheets[1])
        df_iglesias_cat = safe_get_dataframe(sheets[2])
        df_est_teo_raw = safe_get_dataframe(sheets[3])
        df_est_aca_raw = safe_get_dataframe(sheets[4])
        df_revisiones_raw = safe_get_dataframe(sheets[5])

        if df_ministros.empty:
            st.error("No se encontraron datos en la tabla MINISTRO.")
            st.stop()

        # Procesamiento de Iglesia Actual
        try:
            df_relacion['AÑO'] = pd.to_numeric(df_relacion['AÑO'], errors='coerce').fillna(0)
            df_rel_actual = df_relacion.sort_values(by=['MINISTRO', 'AÑO'], ascending=[True, False]).drop_duplicates(subset=['MINISTRO'])
            df_rel_con_nombre = pd.merge(df_rel_actual, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
            df_final = pd.merge(df_ministros, df_rel_con_nombre[['MINISTRO', 'NOMBRE', 'AÑO']], left_on='ID_MINISTRO', right_on='MINISTRO', how='left', suffixes=('', '_REL'))
            df_final['IGLESIA_RESULTADO'] = df_final['NOMBRE_REL'].fillna("Sin Iglesia Asignada")
            df_final['AÑO_ULTIMO'] = df_final['AÑO'].apply(lambda x: int(x) if pd.notnull(x) and x > 0 else "N/A")
        except:
            df_final = df_ministros.copy()
            df_final['IGLESIA_RESULTADO'] = "Error al procesar"
            df_final['AÑO_ULTIMO'] = "N/A"

        st.markdown("<div class='header-container'><h1 class='main-title'>SIGEME</h1><p class='sub-title'>Distrito Sur Fronterizo</p></div>", unsafe_allow_html=True)

        col_nombre = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_nombre].unique().tolist())
        
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        seleccion = st.selectbox("Seleccione un Ministro:", ["-- Seleccionar --"] + lista_ministros)

        if seleccion != "-- Seleccionar --":
            data = df_final[df_final[col_nombre] == seleccion].iloc[0]
            current_id = data['ID_MINISTRO']
            
            c1, c2 = st.columns([1, 3])
            
            with c1:
                st.markdown("### 👤 Fotografía")
                # Identificar columna de fotografía
                col_foto = next((c for c in data.index if any(x in c for x in ['FOTO', 'IMAGEN', 'FOTOGRAFIA'])), None)
                
                url_foto = None
                if col_foto:
                    valor_celda = str(data[col_foto]).strip()
                    url_foto = obtener_url_imagen(valor_celda, "MINISTRO")
                
                st.markdown("<div class='img-container'>", unsafe_allow_html=True)
                if url_foto:
                    # En Streamlit, st.image manejará el renderizado
                    st.image(url_foto, use_container_width=True)
                else:
                    st.markdown("<div style='font-size:6rem; color:#cbd5e1;'>👤</div>", unsafe_allow_html=True)
                    st.caption("Imagen no disponible")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with c2:
                st.subheader(data[col_nombre])
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
                        val = str(data[field]).strip()
                        display_val = val if val not in ["", "0", "nan", "None"] else "---"
                        st.markdown(f"""<div class="profile-card"><small style='color:#64748b; font-weight:600; text-transform:uppercase;'>{field}</small><br><span style='color:#0f172a; font-weight:500;'>{display_val}</span></div>""", unsafe_allow_html=True)

            # Historiales
            st.markdown("<h3 class='section-header'>📝 REVISIONES</h3>", unsafe_allow_html=True)
            rev_min = df_revisiones_raw[df_revisiones_raw['MINISTRO'] == current_id]
            if not rev_min.empty:
                rev_con_nombre = pd.merge(rev_min, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                rev_con_nombre['IGLESIA_DISPLAY'] = rev_con_nombre['NOMBRE'].fillna(rev_con_nombre['IGLESIA'])
                st.dataframe(rev_con_nombre[['IGLESIA_DISPLAY', 'FEC_REVISION', 'STATUS']].sort_values(by='FEC_REVISION', ascending=False), use_container_width=True, hide_index=True)
            else: st.info("Sin registros de revisión.")

            st.markdown("<h3 class='section-header'>🏛️ GESTIÓN EN IGLESIAS</h3>", unsafe_allow_html=True)
            rel_min = df_relacion[df_relacion['MINISTRO'] == current_id].copy()
            if not rel_min.empty:
                rel_con_nombre = pd.merge(rel_min, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
                st.dataframe(rel_con_nombre[['AÑO', 'NOMBRE', 'OBSERVACION']].sort_values(by='AÑO', ascending=False), use_container_width=True, hide_index=True)
            else: st.info("Sin historial de iglesias.")

        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()