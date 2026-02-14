import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(
    page_title="Mi Panel de Datos",
    page_icon="📈",
    layout="wide"
)

# Estilos CSS para que se vea más atractivo que AppSheet
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #f0f2f6;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4e73df;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def conectar_google_sheets():
    # Estas son las "llaves" que configuraste en el Paso 1 de la guía
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    try:
        # Intenta cargar el archivo de credenciales que descargaste de Google
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        
        # IMPORTANTE: Cambia "NOMBRE_DE_TU_SHEET" por el nombre real de tu archivo de Google Sheets
        nombre_archivo = "BD MINISTROS" 
        
        sheet = client.open(nombre_archivo).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"Error de conexión: Verifica que el archivo 'credenciales.json' existe y que compartiste el Sheet con el correo de la cuenta de servicio.")
        return None

def main():
    # Barra lateral informativa
    st.sidebar.title("Menú Principal")
    st.sidebar.success("Conectado con AppSheet ✅")
    st.sidebar.write("Esta interfaz lee los mismos datos que tu App móvil.")
    
    # Título de la página
    st.title("🚀 Mi Nueva Interfaz Premium")
    st.caption("Visualización avanzada de datos sincronizada en tiempo real")

    sheet = conectar_google_sheets()
    
    if sheet:
        with st.spinner('Obteniendo datos actualizados...'):
            data = sheet.get_all_records()
            df = pd.DataFrame(data)

        if not df.empty:
            # SECCIÓN DE MÉTRICAS (Resumen rápido)
            st.markdown("### 📌 Resumen General")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Total de Registros", len(df))
                st.markdown('</div>', unsafe_allow_html=True)
            
            # SECCIÓN DE GRÁFICOS (Lo que AppSheet no hace tan bonito)
            st.markdown("---")
            st.markdown("### 📊 Análisis Visual Interactivo")
            
            # Usamos la primera columna para un gráfico de ejemplo
            columna_categoria = df.columns[0] 
            fig = px.bar(df, x=columna_categoria, 
                         title=f"Distribución por {columna_categoria}", 
                         template="plotly_white", 
                         color_discrete_sequence=['#4e73df'])
            
            st.plotly_chart(fig, use_container_width=True)

            # TABLA DE DATOS (Interactiva, permite ordenar y buscar)
            st.markdown("### 📋 Vista de Tabla Completa")
            st.dataframe(df, use_container_width=True)
            
            # BOTÓN PARA DESCARGAR A EXCEL
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar estos datos para Excel (CSV)",
                data=csv,
                file_name='datos_appsheet_export.csv',
                mime='text/csv',
            )
        else:
            st.warning("El archivo de Google Sheets parece estar vacío. Agrega datos desde AppSheet primero.")

if __name__ == "__main__":
    main()