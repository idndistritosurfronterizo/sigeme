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
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def conectar_google_sheets():
    # Permisos necesarios para acceder a Sheets y Drive
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Verificar si el archivo de credenciales existe
    if not os.path.exists("credenciales.json"):
        st.error("❌ Archivo 'credenciales.json' no encontrado en el repositorio.")
        return None

    try:
        # Autenticación con el archivo JSON
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        
        # Nombres exactos del archivo y la pestaña
        nombre_archivo = "BD MINISTROS"
        nombre_pestaña = "ministro"
        
        libro = client.open(nombre_archivo)
        
        try:
            sheet = libro.worksheet(nombre_pestaña)
            return sheet
        except gspread.exceptions.WorksheetNotFound:
            hojas_disponibles = [h.title for h in libro.worksheets()]
            st.error(f"❌ No se encontró la pestaña '{nombre_pestaña}'.")
            st.info(f"Hojas disponibles en el archivo: {', '.join(hojas_disponibles)}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error crítico de conexión: {str(e)}")
        return None

def main():
    st.title("🚀 Dashboard: BD Ministros")
    st.markdown("Sincronización automática con Google Sheets")
    st.markdown("---")

    # Intentar obtener la hoja
    sheet = conectar_google_sheets()
    
    if sheet:
        try:
            with st.spinner('Obteniendo datos actualizados...'):
                # Leer todos los registros
                records = sheet.get_all_records()
                
            if not records:
                st.warning("⚠️ La pestaña 'ministro' está conectada pero no tiene datos.")
                return

            # Crear DataFrame
            df = pd.DataFrame(records)

            # --- SECCIÓN DE MÉTRICAS ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Total de Registros", len(df))
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Columnas Detectadas", len(df.columns))
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Estado de Red", "Conectado ✅")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- VISTA DE TABLA ---
            st.markdown("### 📋 Tabla de Datos")
            st.dataframe(df, use_container_width=True)

            # --- SECCIÓN DE GRÁFICOS ---
            st.markdown("---")
            st.markdown("### 📊 Análisis Gráfico")
            
            if not df.empty:
                col_sel = st.selectbox("Elige una columna para visualizar la distribución:", df.columns)
                fig = px.histogram(
                    df, 
                    x=col_sel, 
                    template="plotly_white", 
                    color_discrete_sequence=['#007bff'],
                    title=f"Distribución de: {col_sel}"
                )
                st.plotly_chart(fig, use_container_width=True)

            # --- EXPORTAR ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar datos en CSV", 
                data=csv, 
                file_name='bd_ministros.csv', 
                mime='text/csv'
            )

        except Exception as e:
            st.error(f"❌ Error al procesar los datos de la hoja: {e}")

if __name__ == "__main__":
    main()