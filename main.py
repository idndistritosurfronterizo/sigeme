import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import sys

st.set_page_config(
    page_title="DIAGNÓSTICO - SIGEME",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 DIAGNÓSTICO DE CONEXIÓN GOOGLE")

# Información básica
st.write("### 📁 Información del sistema")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Directorio actual:** {os.getcwd()}")
    st.write(f"**Python:** {sys.version}")
with col2:
    archivos = os.listdir(".")
    st.write(f"**Archivos en carpeta:** {len(archivos)}")
    json_files = [f for f in archivos if f.endswith('.json')]
    st.write(f"**Archivos JSON:** {json_files}")

# Verificar credenciales
st.write("### 🔐 Verificación de credenciales")

if not os.path.exists("credenciales.json"):
    st.error("❌ No se encuentra el archivo credenciales.json")
    st.stop()
else:
    st.success("✅ Archivo credenciales.json encontrado")
    
    # Mostrar tamaño del archivo
    tamaño = os.path.getsize("credenciales.json")
    st.write(f"**Tamaño:** {tamaño} bytes")

# Probar la conexión
st.write("### 🌐 Prueba de conexión")

if st.button("1️⃣ PROBAR CONEXIÓN A GOOGLE SHEETS"):
    try:
        st.write("Paso 1: Configurando scopes...")
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        st.write("✅ Scopes configurados")
        
        st.write("Paso 2: Cargando credenciales...")
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        st.write(f"✅ Credenciales cargadas - Email: {creds.service_account_email}")
        
        st.write("Paso 3: Autorizando gspread...")
        client = gspread.authorize(creds)
        st.write("✅ gspread autorizado")
        
        st.write("Paso 4: Buscando spreadsheet 'BD MINISTROS'...")
        try:
            spreadsheet = client.open("BD MINISTROS")
            st.success(f"✅ ¡Spreadsheet encontrado!")
            st.write(f"**Título:** {spreadsheet.title}")
            st.write(f"**URL:** {spreadsheet.url}")
            
            # Listar todas las hojas disponibles
            hojas = spreadsheet.worksheets()
            st.write(f"**Hojas disponibles ({len(hojas)}):**")
            for hoja in hojas:
                st.write(f"  - 📄 {hoja.title}")
                
        except Exception as e:
            st.error(f"❌ Error al abrir 'BD MINISTROS': {e}")
            st.write("Posibles causas:")
            st.write("1. El nombre exacto del spreadsheet es diferente")
            st.write("2. No tienes permisos de acceso")
            st.write("3. El spreadsheet no existe")
            
    except Exception as e:
        st.error(f"❌ Error general: {e}")
        import traceback
        st.code(traceback.format_exc())

st.write("---")
st.write("### 📋 Instrucciones:")
st.markdown("""
1. Haz click en el botón **PROBAR CONEXIÓN**
2. Si falla, verifica que:
   - El archivo `credenciales.json` sea el correcto
   - El spreadsheet se llame exactamente **"BD MINISTROS"** (con mayúsculas y espacios)
   - Hayas compartido el spreadsheet con el email de la cuenta de servicio
   
   El email de servicio aparece en el paso 2 de la conexión
""")