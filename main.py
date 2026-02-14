import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard BD Ministros",
    page_icon="📈",
    layout="wide"
)

# Estilos visuales para mejorar la interfaz (UI)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #f4f7f9;
    }
    .main-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

def conectar_google_sheets():
    # Definir los alcances de seguridad para Google Sheets y Drive
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Diagnóstico 1: Verificar si el archivo de credenciales existe en GitHub
    if not os.path.exists("credenciales.json"):
        st.error("❌ ERROR: El archivo 'credenciales.json' no se encuentra en tu repositorio de GitHub.")
        st.info("Asegúrate de subir el archivo JSON que descargaste de Google Cloud con el nombre exacto: credenciales.json")
        return None

    try:
        # Intentar autenticar con las credenciales
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        
        # --- NOMBRE DEL ARCHIVO (Asegúrate de que coincida con el de Google Drive) ---
        nombre_archivo = "BD MINISTROS" 
        
        # Intentar abrir la primera pestaña (0) del archivo
        sheet = client.open(nombre_archivo).get_worksheet(0)
        return sheet
    
    except gspread.exceptions.SpreadsheetNotFound:
        # Diagnóstico 2: El archivo no se encontró por su nombre
        st.error(f"❌ ERROR: No se encontró el Google Sheet llamado: '{nombre_archivo}'")
        st.warning("Verifica que el nombre en el código sea IDÉNTICO al nombre de tu archivo en Google Drive (revisa espacios y mayúsculas).")
        st.info("Importante: Debes compartir tu Google Sheet con el correo de la 'Cuenta de Servicio' como Editor.")
        return None
    except Exception as e:
        # Diagnóstico 3: Mostrar cualquier otro error técnico
        st.error(f"❌ ERROR DE CONEXIÓN: {str(e)}")
        return None

def main():
    st.title("🚀 Panel de Control: BD Ministros")
    st.caption("Interfaz personalizada sincronizada con AppSheet y Google Sheets")
    st.markdown("---")

    # Intentar obtener la conexión con la hoja
    sheet = conectar_google_sheets()
    
    if sheet:
        try:
            with st.spinner('Cargando datos actualizados desde la nube...'):
                # Obtener todos los datos de la hoja
                data = sheet.get_all_records()
                
            if not data:
                st.warning("⚠️ La conexión fue exitosa, pero la hoja actual parece estar vacía.")
                return

            # Convertir los datos a una tabla de Pandas (DataFrame)
            df = pd.DataFrame(data)

            # --- SECCIÓN DE MÉTRICAS (Resumen rápido) ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="main-card">', unsafe_allow_html=True)
                st.metric("Total de Registros", len(df))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="main-card">', unsafe_allow_html=True)
                st.metric("Columnas en la Base", len(df.columns))
                st.markdown('</div>', unsafe_allow_html=True)

            # --- VISUALIZACIÓN GRÁFICA ---
            st.markdown("### 📊 Gráfico de Resumen Automático")
            
            if len(df.columns) > 0:
                # Toma la primera columna para generar un gráfico de distribución
                col_grafico = df.columns[0]
                fig = px.histogram(df, x=col_grafico, title=f"Frecuencia por: {col_grafico}", 
                                   template="plotly_white", color_discrete_sequence=['#1f77b4'])
                st.plotly_chart(fig, use_container_width=True)

            # --- TABLA DE DATOS INTERACTIVA ---
            st.markdown("### 📋 Vista Detallada de la Tabla")
            st.dataframe(df, use_container_width=True, height=500)

            # --- OPCIÓN DE EXPORTACIÓN ---
            st.markdown("---")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar estos datos (Formato CSV para Excel)",
                data=csv,
                file_name='reporte_bd_ministros.csv',
                mime='text/csv',
            )

        except Exception as e:
            st.error(f"❌ Error al procesar la información de la hoja: {e}")

if __name__ == "__main__":
    main()