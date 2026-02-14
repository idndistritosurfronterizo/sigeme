import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os

# 1. Configuración mínima
st.set_page_config(page_title="Test Conexión")
st.title("Diagnóstico de Conexión")

# 2. Verificar archivos en el servidor
st.write("### Verificando archivos en GitHub:")
archivos = os.listdir('.')
st.write(archivos)

if "credenciales.json" not in archivos:
    st.error("Archivo 'credenciales.json' NO DETECTADO")
else:
    st.success("Archivo 'credenciales.json' detectado")

# 3. Intento de conexión directo
def conectar():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        
        # Intentar abrir el archivo y la hoja
        # Verifica que el nombre sea exacto en tu Google Drive
        doc = client.open("BD MINISTROS")
        sheet = doc.worksheet("ministro")
        return sheet
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return None

# 4. Mostrar datos
hoja = conectar()
if hoja:
    st.success("¡Conectado a la pestaña 'ministro'!")
    df = pd.DataFrame(hoja.get_all_records())
    st.dataframe(df)