import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_CORRECTO = "admin"
PASSWORD_CORRECTO = "ministros2024"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="SIGEME - Distrito Sur Fronterizo",
    page_icon="⛪",
    layout="wide"
)

# --- DISEÑO CSS PERSONALIZADO (AZULES Y ELEGANCIA) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f4f8;
    }
    
    /* Títulos y Subtítulos */
    .main-title {
        color: #003366;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        margin-bottom: 0px;
        text-align: center;
    }
    .sub-title {
        color: #00509d;
        font-size: 1.2rem;
        text-align: center;
        margin-top: -10px;
        font-weight: 400;
    }
    .distrito-text {
        color: #666;
        font-size: 1rem;
        text-align: center;
        font-style: italic;
        margin-bottom: 20px;
    }

    /* Tarjetas de métricas */
    .metric-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-bottom: 5px solid #003366;
        text-align: center;
    }
    
    /* Contenedores de contenido */
    .content-box {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }

    /* Botones y Sidebar */
    .stButton>button {
        background-color: #003366;
        color: white;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    # Login Visual
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        # Intentar cargar logo en login
        if os.path.exists("logoNazareno.png"):
            st.image("logoNazareno.png", width=150)
        
        st.markdown("""
            <div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border-top: 5px solid #003366;'>
                <h1 style='text-align: center; color: #003366;'>SIGEME</h1>
                <p style='text-align: center; color: #666;'>Sistema de Gestión Ministerial y Eclesiástica</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar al Sistema", use_container_width=True):
                if user == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    return False

def conectar_google_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if not os.path.exists("credenciales.json"):
        st.error("❌ Falta credenciales.json")
        return None
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        return client.open("BD MINISTROS").worksheet("MINISTRO")
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def main():
    if not check_password():
        st.stop()

    # --- BARRA LATERAL ---
    with st.sidebar:
        if os.path.exists("logoNazareno.png"):
            st.image("logoNazareno.png", use_container_width=True)
        st.title("SIGEME")
        st.info("Gestión Ministerial")
        if st.button("🚪 Salir"):
            st.session_state["authenticated"] = False
            st.rerun()
        st.markdown("---")
        st.markdown("### 🛠️ Filtros")

    sheet = conectar_google_sheets()
    
    if sheet:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Filtros Sidebar
        cols = df.columns.tolist()
        sel_col = st.sidebar.selectbox("Filtrar por:", ["Todos"] + cols)
        df_view = df.copy()
        if sel_col != "Todos":
            vals = df[sel_col].unique().tolist()
            picks = st.sidebar.multiselect(f"Seleccionar {sel_col}:", vals)
            if picks:
                df_view = df[df[sel_col].isin(picks)]

        # --- ENCABEZADO PERSONALIZADO ---
        st.markdown("<h1 class='main-title'>SIGEME</h1>", unsafe_allow_html=True)
        st.markdown("<p class='sub-title'>Sistema de Gestión Ministerial y Eclesiástica</p>", unsafe_allow_html=True)
        st.markdown("<p class='distrito-text'>Distrito Sur Fronterizo</p>", unsafe_allow_html=True)

        # --- MÉTRICAS ---
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><p style="color:#666">Ministros</p><h2>{len(df_view)}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><p style="color:#666">Base de Datos</p><h2 style="color:#28a745">Activa</h2></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><p style="color:#666">Distrito</p><h2 style="font-size:1.2rem; color:#003366">SUR FRONTERIZO</h2></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- PANELES ---
        t1, t2 = st.tabs(["📋 Base de Datos", "📊 Gráficos de Análisis"])
        
        with t1:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.dataframe(df_view, use_container_width=True, height=400)
            csv = df_view.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Reporte CSV", csv, "sigeme_reporte.csv", "text/csv")
            st.markdown('</div>', unsafe_allow_html=True)

        with t2:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            col_x = st.selectbox("Selecciona columna para analizar:", cols)
            fig = px.histogram(df_view, x=col_x, color_discrete_sequence=['#003366'], template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()