Aquí tienes el código completo y listo para copiar directamente. He configurado la línea 46 para que busque específicamente el archivo "BD MINISTROS" y la línea 49 para que entre directamente a la pestaña llamada "ministro".

Copia todo este bloque de texto y pégalo en tu archivo main.py en GitHub:

Python
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

# Estilos visuales personalizados
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
    }
    .metric-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

def conectar_google_sheets():
    # Definir los permisos para Google Drive y Sheets
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Verificar si el archivo de credenciales existe
    if not os.path.exists("credenciales.json"):
        st.error("❌ Archivo 'credenciales.json' no encontrado en el repositorio de GitHub.")
        return None

    try:
        # Autenticación con el archivo JSON
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        
        # 1. Nombre del archivo de Google Sheets
        nombre_archivo = "BD MINISTROS"
        
        # 2. Nombre exacto de la pestaña
        nombre_pestaña = "ministro"
        
        # Abrir el libro de trabajo
        libro = client.open(nombre_archivo)
        
        # Intentar abrir la pestaña específica por su nombre
        try:
            sheet = libro.worksheet(nombre_pestaña)
            return sheet
        except gspread.exceptions.WorksheetNotFound:
            # Si no encuentra la pestaña, muestra las que sí existen para ayudar
            hojas_disponibles = [h.title for h in libro.worksheets()]
            st.error(f"❌ No se encontró la pestaña '{nombre_pestaña}'.")
            st.info(f"Pestañas encontradas en tu archivo: {', '.join(hojas_disponibles)}")
            return None
            
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"❌ No se encontró el archivo de Google Sheets llamado '{nombre_archivo}'.")
        st.info("Revisa que el nombre sea exacto y que hayas compartido el archivo con el correo de la cuenta de servicio.")
        return None
    except Exception as e:
        st.error(f"❌ Error de conexión: {str(e)}")
        return None

def main():
    st.title("🚀 Dashboard: BD Ministros")
    st.markdown(f"Visualización de datos sincronizada con la pestaña **'{ "ministro" }'**")
    st.markdown("---")

    # Intentar obtener la conexión
    sheet = conectar_google_sheets()
    
    if sheet:
        try:
            with st.spinner('Sincronizando datos...'):
                # Obtener todos los registros de la pestaña
                records = sheet.get_all_records()
                
            if not records:
                st.warning(f"⚠️ La pestaña '{ "ministro" }' está conectada pero parece estar vacía.")
                return

            # Crear el DataFrame (Tabla)
            df = pd.DataFrame(records)

            # --- SECCIÓN DE MÉTRICAS ---
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Total de Registros", len(df))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Columnas Detectadas", len(df.columns))
                st.markdown('</div>', unsafe_allow_html=True)

            # --- VISTA DE TABLA ---
            st.markdown("### 📋 Tabla de Datos Interactiva")
            st.dataframe(df, use_container_width=True)

            # --- ANÁLISIS GRÁFICO ---
            st.markdown("---")
            st.markdown("### 📊 Gráfico de Distribución")
            
            if not df.empty:
                # Usar la primera columna para un gráfico rápido
                eje_x = df.columns[0]
                fig = px.histogram(
                    df, 
                    x=eje_x, 
                    title=f"Registros por {eje_x}",
                    template="plotly_white",
                    color_discrete_sequence=['#007bff']
                )
                st.plotly_chart(fig, use_container_width=True)

            # --- BOTÓN DE DESCARGA ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Reporte (CSV)",
                data=csv,
                file_name='reporte_ministros.csv',
                mime='text/csv',
            )

        except Exception as e:
            st.error(f"❌ Error al procesar los datos: {e}")

if __name__ == "__main__":
    main()