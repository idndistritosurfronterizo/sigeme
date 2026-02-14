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
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 6px solid #003366;
        height: 100%;
    }
    .metric-label { color: #64748b; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; }
    .metric-value { color: #0f172a; font-size: 2rem; font-weight: 800; }
    .profile-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 20px;
        margin-top: 10px;
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
        return None, None, None
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open("BD MINISTROS")
        return spreadsheet.worksheet("MINISTRO"), spreadsheet.worksheet("IGLESIA"), spreadsheet.worksheet("IGLESIAS")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None, None

def main():
    if not check_password(): st.stop()

    sheet_m, sheet_rel, sheet_ig = conectar_google_sheets()
    
    if sheet_m and sheet_rel and sheet_ig:
        # Cargar DataFrames
        df_ministros = pd.DataFrame(sheet_m.get_all_records())
        df_relacion = pd.DataFrame(sheet_rel.get_all_records())
        df_iglesias_cat = pd.DataFrame(sheet_ig.get_all_records())

        # Limpieza de nombres de columnas
        df_ministros.columns = [c.strip() for c in df_ministros.columns]
        df_relacion.columns = [c.strip() for c in df_relacion.columns]
        df_iglesias_cat.columns = [c.strip() for c in df_iglesias_cat.columns]

        try:
            # 1. Procesar pestaña "IGLESIA" (Relacional) para obtener el año más actual
            # Columnas esperadas: ID_ministro, IGLESIA, AÑO
            df_relacion['AÑO'] = pd.to_numeric(df_relacion['AÑO'], errors='coerce').fillna(0)
            df_relacion = df_relacion.sort_values(by=['ID_ministro', 'AÑO'], ascending=[True, False])
            df_actual = df_relacion.drop_duplicates(subset=['ID_ministro'])

            # 2. Unir con pestaña "IGLESIAS" (Catálogo) para traer el NOMBRE real
            # Columnas esperadas en IGLESIAS: ID, NOMBRE
            df_cat_map = df_iglesias_cat[['ID', 'NOMBRE']].rename(columns={'ID': 'IGLESIA_ID_CAT', 'NOMBRE': 'NOMBRE_REAL_IGLESIA'})
            
            # Asegurar tipos string para el cruce
            df_actual['IGLESIA'] = df_actual['IGLESIA'].astype(str).str.strip()
            df_cat_map['IGLESIA_ID_CAT'] = df_cat_map['IGLESIA_ID_CAT'].astype(str).str.strip()

            df_rel_completa = pd.merge(
                df_actual, 
                df_cat_map, 
                left_on='IGLESIA', 
                right_on='IGLESIA_ID_CAT', 
                how='left'
            )

            # 3. Unir con pestaña "MINISTRO" principal
            # Columnas esperadas en MINISTRO: ID_ministro, NOMBRE, IGLESIA (esta última es la que trae de origen)
            df_ministros['ID_ministro'] = df_ministros['ID_ministro'].astype(str).str.strip()
            df_rel_completa['ID_ministro'] = df_rel_completa['ID_ministro'].astype(str).str.strip()

            df_final = pd.merge(
                df_ministros,
                df_rel_completa[['ID_ministro', 'NOMBRE_REAL_IGLESIA', 'AÑO']],
                on='ID_ministro',
                how='left'
            )

            # Crear columna de visualización final
            df_final['IGLESIA_RESULTADO'] = df_final['NOMBRE_REAL_IGLESIA'].fillna(df_final['IGLESIA'])
            df_final['AÑO_ULTIMO'] = df_final['AÑO'].fillna("N/A")

        except Exception as e:
            st.error(f"Error en el cruce de datos: {e}")
            df_final = df_ministros.copy()
            df_final['IGLESIA_RESULTADO'] = "Error"
            df_final['AÑO_ULTIMO'] = "N/A"

        # --- INTERFAZ ---
        st.markdown("<div class='header-container'><h1 class='main-title'>SIGEME</h1><p class='sub-title'>Distrito Sur Fronterizo</p></div>", unsafe_allow_html=True)

        # Filtro de búsqueda
        col_busqueda = 'NOMBRE' if 'NOMBRE' in df_final.columns else df_final.columns[1]
        lista_ministros = sorted(df_final[col_busqueda].unique().tolist())
        
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        seleccion = st.selectbox("Seleccione un Ministro:", ["-- Seleccionar --"] + lista_ministros)

        if seleccion != "-- Seleccionar --":
            data = df_final[df_final[col_busqueda] == seleccion].iloc[0]
            
            c1, c2 = st.columns([1, 3])
            with c1:
                st.markdown("### 👤 Perfil")
                st.markdown("<div style='background:#f1f5f9; height:180px; border-radius:15px; display:flex; align-items:center; justify-content:center; font-size:4rem;'>👤</div>", unsafe_allow_html=True)
            
            with c2:
                st.subheader(data[col_busqueda])
                
                # Resaltar Iglesia Actual
                st.markdown(f"""
                <div class="profile-card" style="border-left: 6px solid #fbbf24; background: #fffbeb;">
                    <p style='margin:0; font-size:0.8rem; color:#92400e;'>IGLESIA ACTUAL (Gestión {data['AÑO_ULTIMO']})</p>
                    <h3 style='margin:0; color:#78350f;'>{data['IGLESIA_RESULTADO']}</h3>
                </div>
                """, unsafe_allow_html=True)

                # Resto de campos
                excluir = ['ID_ministro', 'NOMBRE', 'IGLESIA', 'NOMBRE_REAL_IGLESIA', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO']
                cols_info = st.columns(2)
                visible_fields = [f for f in data.index if f not in excluir]
                
                for i, field in enumerate(visible_fields):
                    with cols_info[i % 2]:
                        st.markdown(f"""
                        <div class="profile-card">
                            <small style='color:#64748b;'>{field}</small><br>
                            <strong>{data[field] if data[field] != "" else "---"}</strong>
                        </div>
                        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()