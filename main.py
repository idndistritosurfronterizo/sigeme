import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import os
import io
import sys
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

# Mostrar información de depuración en un expander
with st.expander("🔧 DEPURACIÓN (click para ver errores)"):
    st.write("**Versión de Python:**", sys.version)
    st.write("**Streamlit versión:**", st.__version__)
    st.write("**Pandas versión:**", pd.__version__)
    st.write("**Archivo credenciales.json existe:**", os.path.exists("credenciales.json"))
    st.write("**Directorio actual:**", os.getcwd())
    st.write("**Archivos en carpeta:**", os.listdir("."))

# --- DISEÑO CSS (simplificado por ahora) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    </style>
""", unsafe_allow_html=True)

def check_password():
    st.write("🔑 **Función check_password ejecutándose**")
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if st.session_state["authenticated"]:
        st.write("✅ Usuario ya autenticado")
        return True
    
    st.write("❌ Usuario no autenticado, mostrando login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 SIGEME - Login")
        
        with st.form("login_form"):
            user = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Ingresar"):
                st.write("🔍 Intentando login...")
                if user == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
                    st.write("✅ Login exitoso")
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
                    st.write("❌ Login falló")
    return False

def get_as_dataframe(worksheet):
    """Método robusto para leer hojas"""
    try:
        data = worksheet.get_all_values()
        st.write(f"📊 Hoja cargada: {len(data)} filas")
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
    except Exception as e:
        st.error(f"Error en get_as_dataframe: {e}")
        return pd.DataFrame()

def conectar_servicios_google():
    st.write("🔄 **Conectando a Google Services...**")
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    if not os.path.exists("credenciales.json"):
        st.error("❌ Archivo credenciales.json NO encontrado")
        return None, None
    
    try:
        st.write("📁 Leyendo credenciales.json...")
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        st.write("✅ Credenciales OK")
        
        client = gspread.authorize(creds)
        st.write("✅ Autorización gspread OK")
        
        st.write("📊 Abriendo spreadsheet 'BD MINISTROS'...")
        spreadsheet = client.open("BD MINISTROS")
        st.write("✅ Spreadsheet abierto OK")
        
        st.write("🔌 Conectando a Drive...")
        drive_service = build('drive', 'v3', credentials=creds)
        st.write("✅ Drive OK")
        
        worksheets = {}
        hojas = ["MINISTRO", "IGLESIA", "IGLESIAS", "ESTUDIOS TEOLOGICOS", "ESTUDIOS ACADEMICOS", "Revision"]
        
        for hoja in hojas:
            try:
                st.write(f"  - Cargando hoja: {hoja}")
                worksheets[hoja] = spreadsheet.worksheet(hoja)
                st.write(f"    ✅ {hoja} cargada")
            except Exception as e:
                st.error(f"    ❌ Error con hoja {hoja}: {e}")
        
        return worksheets, drive_service
    except Exception as e:
        st.error(f"❌ Error de conexión general: {e}")
        import traceback
        st.code(traceback.format_exc())
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
    except Exception as e:
        st.warning(f"Error descargando foto: {e}")
        return None
    return None

def main():
    st.write("🚀 **Función main iniciada**")
    
    if not check_password():
        st.write("⏸️ Deteniendo ejecución - usuario no autenticado")
        st.stop()
    
    st.write("✅ Usuario autenticado, continuando con main...")
    
    st.markdown("# ⛪ SIGEME")
    st.markdown("### Distrito Sur Fronterizo")
    
    sheets, drive_service = conectar_servicios_google()
    
    if not sheets:
        st.error("❌ No se pudieron cargar las hojas. Verifica:")
        st.error("1. Que el archivo credenciales.json esté en la carpeta correcta")
        st.error("2. Que el spreadsheet 'BD MINISTROS' exista y sea accesible")
        st.error("3. Que las hojas tengan los nombres exactos")
        st.stop()
    
    try:
        with st.spinner('Cargando datos...'):
            st.write("📥 Cargando MINISTRO...")
            df_ministros = get_as_dataframe(sheets["MINISTRO"])
            st.write(f"   → {len(df_ministros)} registros")
            
            st.write("📥 Cargando RELACION...")
            df_relacion = get_as_dataframe(sheets["IGLESIA"])
            st.write(f"   → {len(df_relacion)} registros")
            
            st.write("📥 Cargando CAT_IGLESIAS...")
            df_iglesias_cat = get_as_dataframe(sheets["IGLESIAS"])
            st.write(f"   → {len(df_iglesias_cat)} registros")
            
            st.write("📥 Cargando TEOLOGICOS...")
            df_est_teo_raw = get_as_dataframe(sheets["ESTUDIOS TEOLOGICOS"])
            st.write(f"   → {len(df_est_teo_raw)} registros")
            
            st.write("📥 Cargando ACADEMICOS...")
            df_est_aca_raw = get_as_dataframe(sheets["ESTUDIOS ACADEMICOS"])
            st.write(f"   → {len(df_est_aca_raw)} registros")
            
            st.write("📥 Cargando REVISION...")
            df_revisiones_raw = get_as_dataframe(sheets["Revision"])
            st.write(f"   → {len(df_revisiones_raw)} registros")
        
        st.write("🔄 Procesando datos...")
        
        # Mostrar las primeras filas de cada dataframe para verificar
        with st.expander("Vista previa de datos cargados"):
            st.write("MINISTRO:", df_ministros.head())
            st.write("RELACION:", df_relacion.head())
            st.write("IGLESIAS:", df_iglesias_cat.head())
        
        # Normalización de datos
        df_relacion['AÑO'] = pd.to_numeric(df_relacion['AÑO'], errors='coerce').fillna(0)
        df_relacion['MINISTRO'] = df_relacion['MINISTRO'].astype(str).str.strip()
        df_relacion['IGLESIA'] = df_relacion['IGLESIA'].astype(str).str.strip()
        df_ministros['ID_MINISTRO'] = df_ministros['ID_MINISTRO'].astype(str).str.strip()
        df_iglesias_cat['ID'] = df_iglesias_cat['ID'].astype(str).str.strip()
        
        # Obtener última iglesia
        st.write("📊 Procesando relaciones...")
        df_rel_actual = df_relacion.sort_values(by=['MINISTRO', 'AÑO'], ascending=[True, False]).drop_duplicates(subset=['MINISTRO'])
        df_rel_con_nombre = pd.merge(df_rel_actual, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
        
        df_final = pd.merge(df_ministros, df_rel_con_nombre[['MINISTRO', 'NOMBRE', 'AÑO']], left_on='ID_MINISTRO', right_on='MINISTRO', how='left', suffixes=('', '_REL'))
        df_final['IGLESIA_RESULTADO'] = df_final['NOMBRE_REL'].fillna("Sin Iglesia Asignada")
        df_final['AÑO_ULTIMO'] = df_final['AÑO'].apply(lambda x: int(x) if pd.notnull(x) and x > 0 else "N/A")
        
        st.write(f"✅ Datos procesados: {len(df_final)} ministros")
        
        # Métricas simples
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Ministros", len(df_ministros))
        activos = len(df_final[df_final['IGLESIA_RESULTADO'] != "Sin Iglesia Asignada"])
        col2.metric("Ministros Activos", activos)
        col3.metric("Iglesias", df_iglesias_cat['NOMBRE'].nunique())
        
        # Selector de ministro
        col_nombre = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_nombre].unique().tolist())
        
        seleccion = st.selectbox("Seleccione un Ministro:", ["-- Seleccionar --"] + lista_ministros)
        
        if seleccion != "-- Seleccionar --":
            data = df_final[df_final[col_nombre] == seleccion].iloc[0]
            
            st.subheader(f"📋 Información de {seleccion}")
            st.write("Iglesia actual:", data['IGLESIA_RESULTADO'])
            
            # Mostrar toda la información disponible
            for campo, valor in data.items():
                if pd.notna(valor) and str(valor).strip():
                    st.write(f"**{campo}:** {valor}")
        
    except Exception as e:
        st.error(f"❌ Error en el procesamiento: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()