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

# --- DISEÑO CSS PROFESIONAL Y ATRACTIVO ---
st.markdown("""
    <style>
    /* Importación de tipografía moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #f8fafc;
    }
    
    /* Encabezado */
    .header-container {
        background: linear-gradient(135deg, #003366 0%, #00509d 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,51,102,0.15);
    }
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    .sub-title {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    .distrito-tag {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.9rem;
        margin-top: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Tarjetas de métricas interactivas */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        transition: transform 0.2s ease;
        border-left: 6px solid #003366;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        color: #0f172a;
        font-size: 2rem;
        font-weight: 800;
    }

    /* Contenedores */
    .content-box {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    .profile-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 20px;
        margin-top: 10px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if os.path.exists("logoNazareno.png"):
            st.image("logoNazareno.png", width=120)
        
        st.markdown("""
            <div style='background: white; padding: 40px; border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.1); text-align: center;'>
                <h1 style='color: #003366; font-weight: 800; margin-bottom: 10px;'>SIGEME</h1>
                <p style='color: #64748b;'>Sistema de Gestión Ministerial y Eclesiástica</p>
                <hr style='opacity: 0.1; margin: 25px 0;'>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Acceder al Portal", use_container_width=True):
                if user == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Acceso denegado. Verifique sus credenciales.")
    return False

def conectar_google_sheets():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if not os.path.exists("credenciales.json"):
        st.error("❌ Error de sistema: Archivo de credenciales no detectado.")
        return None
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        # Cambia el nombre si el archivo en Drive se llama distinto
        return client.open("BD MINISTROS").worksheet("MINISTRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def main():
    if not check_password():
        st.stop()

    with st.sidebar:
        if os.path.exists("logoNazareno.png"):
            st.image("logoNazareno.png", use_container_width=True)
        st.markdown("<h2 style='text-align: center; color: #003366;'>SIGEME</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión Segura", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()
        st.markdown("### ⚙️ Panel de Filtros")

    sheet = conectar_google_sheets()
    
    if sheet:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Filtros Sidebar
        cols = df.columns.tolist()
        sel_col = st.sidebar.selectbox("Agrupar por:", ["Ver Todo"] + cols)
        df_view = df.copy()
        if sel_col != "Ver Todo":
            vals = df[sel_col].unique().tolist()
            picks = st.sidebar.multiselect(f"Seleccionar {sel_col}:", vals)
            if picks:
                df_view = df[df[sel_col].isin(picks)]

        # --- CABECERA VISUAL ---
        st.markdown("""
            <div class='header-container'>
                <h1 class='main-title'>SIGEME</h1>
                <p class='sub-title'>Sistema de Gestión Ministerial y Eclesiástica</p>
                <span class='distrito-tag'>Distrito Sur Fronterizo</span>
            </div>
        """, unsafe_allow_html=True)

        # --- CÁLCULO DE MÉTRICAS CORREGIDO ---
        # Se busca "PRESBITERO" (sin tilde y mayúsculas) en todo el dataframe
        total_iglesias = df_view['IGLESIA'].nunique() if 'IGLESIA' in df_view.columns else 0
        
        # Función auxiliar para contar categorías ignorando tildes y mayúsculas
        def contar_categoria(dataframe, texto):
            mask = dataframe.apply(lambda x: x.astype(str).str.contains(texto, case=False, na=False)).any(axis=1)
            return len(dataframe[mask])

        num_presbiteros = contar_categoria(df_view, 'PRESBITERO')
        num_licenciados = contar_categoria(df_view, 'LICENCIADO')
        num_laicos = contar_categoria(df_view, 'LAICO')

        # --- PANEL DE MÉTRICAS ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class='metric-card'><div class='metric-label'>Total de Iglesias</div><div class='metric-value'>{total_iglesias}</div></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class='metric-card'><div class='metric-label'>Presbíteros</div><div class='metric-value'>{num_presbiteros}</div></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class='metric-card'><div class='metric-label'>M. Licenciados</div><div class='metric-value'>{num_licenciados}</div></div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class='metric-card'><div class='metric-label'>Ministros Laicos</div><div class='metric-value'>{num_laicos}</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- TABS DE CONTENIDO ---
        t1, t2, t3 = st.tabs(["📋 Registros Ministeriales", "📊 Análisis Estadístico", "🔍 Perfil Individual"])
        
        with t1:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.dataframe(df_view, use_container_width=True, height=450)
            st.markdown("<br>", unsafe_allow_html=True)
            csv = df_view.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Exportar Reporte a Excel/CSV", csv, "reporte_sigeme.csv", "text/csv", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with t2:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            col_chart, col_info = st.columns([2, 1])
            with col_chart:
                col_x = st.selectbox("Visualizar distribución por:", cols)
                fig = px.histogram(
                    df_view, 
                    x=col_x, 
                    color_discrete_sequence=['#003366'], 
                    template="plotly_white",
                    title=f"Concentración de datos por {col_x}"
                )
                fig.update_layout(bargap=0.2, margin=dict(t=50, b=20, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)
            with col_info:
                st.markdown("### Resumen")
                st.info("Utilice los filtros de la izquierda para segmentar los datos por zona, iglesia o categoría específica.")
            st.markdown('</div>', unsafe_allow_html=True)

        with t3:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.subheader("Buscador de Ministro")
            
            # Buscamos la columna de nombres (asumiendo que se llama NOMBRE o similar)
            col_nombre = next((c for c in df.columns if 'NOMBRE' in c.upper()), df.columns[0])
            
            lista_nombres = sorted(df[col_nombre].unique().tolist())
            nombre_sel = st.selectbox("Seleccione un Ministro para ver detalles:", ["-- Seleccionar --"] + lista_nombres)
            
            if nombre_sel != "-- Seleccionar --":
                ministro_data = df[df[col_nombre] == nombre_sel].iloc[0]
                
                st.markdown(f"### Detalle: {nombre_sel}")
                
                # Crear una rejilla para mostrar los datos del ministro
                m_cols = st.columns(3)
                for i, (col_key, col_val) in enumerate(ministro_data.items()):
                    with m_cols[i % 3]:
                        st.markdown(f"""
                        <div class="profile-card">
                            <p style='color: #64748b; font-size: 0.8rem; margin:0;'>{col_key}</p>
                            <p style='color: #003366; font-weight: 600; margin:0;'>{col_val}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Seleccione un nombre del buscador para desplegar su ficha ministerial.")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()