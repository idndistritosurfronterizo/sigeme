import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import os
import re

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
    .profile-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 20px;
        margin-top: 10px;
    }
    .content-box {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .img-container {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 3px solid white;
    }
    .section-header {
        color: #003366;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 800;
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
        return None
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open("BD MINISTROS")
        return (
            spreadsheet.worksheet("MINISTRO"), 
            spreadsheet.worksheet("IGLESIA"), 
            spreadsheet.worksheet("IGLESIAS"),
            spreadsheet.worksheet("ESTUDIOS TEOLOGICOS"),
            spreadsheet.worksheet("ESTUDIOS ACADEMICOS"),
            spreadsheet.worksheet("Revision")
        )
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def main():
    if not check_password(): st.stop()

    res = conectar_google_sheets()
    if res and all(res):
        sheet_m, sheet_rel, sheet_ig, sheet_est_teo, sheet_est_aca, sheet_rev = res
        
        # Cargar DataFrames
        df_ministros = pd.DataFrame(sheet_m.get_all_records())
        df_relacion = pd.DataFrame(sheet_rel.get_all_records())
        df_iglesias_cat = pd.DataFrame(sheet_ig.get_all_records())
        df_est_teo_raw = pd.DataFrame(sheet_est_teo.get_all_records())
        df_est_aca_raw = pd.DataFrame(sheet_est_aca.get_all_records())
        df_revisiones_raw = pd.DataFrame(sheet_rev.get_all_records())

        # Limpieza estándar de nombres de columnas (Todo a MAYÚSCULAS)
        df_ministros.columns = [c.strip().upper() for c in df_ministros.columns]
        df_relacion.columns = [c.strip().upper() for c in df_relacion.columns]
        df_iglesias_cat.columns = [c.strip().upper() for c in df_iglesias_cat.columns]
        df_est_teo_raw.columns = [c.strip().upper() for c in df_est_teo_raw.columns]
        df_est_aca_raw.columns = [c.strip().upper() for c in df_est_aca_raw.columns]
        df_revisiones_raw.columns = [c.strip().upper() for c in df_revisiones_raw.columns]

        try:
            # Normalizar tipos de datos para cruces
            df_relacion['AÑO'] = pd.to_numeric(df_relacion['AÑO'], errors='coerce').fillna(0)
            df_relacion['MINISTRO'] = df_relacion['MINISTRO'].astype(str).str.strip()
            df_relacion['IGLESIA'] = df_relacion['IGLESIA'].astype(str).str.strip()
            
            df_ministros['ID_MINISTRO'] = df_ministros['ID_MINISTRO'].astype(str).str.strip()
            
            df_iglesias_cat['ID'] = df_iglesias_cat['ID'].astype(str).str.strip()
            df_iglesias_cat['NOMBRE'] = df_iglesias_cat['NOMBRE'].astype(str).str.strip()
            
            df_est_teo_raw['MINISTRO'] = df_est_teo_raw['MINISTRO'].astype(str).str.strip()
            df_est_aca_raw['MINISTRO'] = df_est_aca_raw['MINISTRO'].astype(str).str.strip()
            
            df_revisiones_raw['MINISTRO'] = df_revisiones_raw['MINISTRO'].astype(str).str.strip()
            df_revisiones_raw['IGLESIA'] = df_revisiones_raw['IGLESIA'].astype(str).str.strip()

            # 1. Obtener el registro con el MAX(AÑO) por cada ministro (para el perfil principal)
            df_rel_ordenada = df_relacion.sort_values(by=['MINISTRO', 'AÑO'], ascending=[True, False])
            df_rel_actual = df_rel_ordenada.drop_duplicates(subset=['MINISTRO'])

            # 2. Unir la relación actual con el catálogo para obtener el NOMBRE de la iglesia
            df_rel_con_nombre = pd.merge(
                df_rel_actual,
                df_iglesias_cat[['ID', 'NOMBRE']],
                left_on='IGLESIA',
                right_on='ID',
                how='left'
            )

            # 3. Unir con la tabla principal de MINISTRO
            df_final = pd.merge(
                df_ministros,
                df_rel_con_nombre[['MINISTRO', 'NOMBRE', 'AÑO']],
                left_on='ID_MINISTRO',
                right_on='MINISTRO',
                how='left',
                suffixes=('', '_REL')
            )

            # Definir resultados finales de visualización del perfil
            df_final['IGLESIA_RESULTADO'] = df_final['NOMBRE_REL'].fillna("Sin Iglesia Asignada")
            df_final['AÑO_ULTIMO'] = df_final['AÑO'].apply(lambda x: int(x) if pd.notnull(x) and x > 0 else "N/A")

        except Exception as e:
            st.error(f"Error procesando datos: {e}")
            df_final = df_ministros.copy()
            df_final['IGLESIA_RESULTADO'] = "Error de Datos"
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
            current_id = data['ID_MINISTRO']
            
            c1, c2 = st.columns([1, 3])
            
            with c1:
                st.markdown("### 👤 Fotografía")
                col_foto = next((c for c in data.index if 'FOTO' in c or 'IMAGEN' in c), None)
                
                if col_foto and str(data[col_foto]).strip() != "":
                    foto_path = str(data[col_foto])
                    st.markdown(f"<div class='img-container'>", unsafe_allow_html=True)
                    st.markdown("<div style='background:#f1f5f9; height:250px; display:flex; align-items:center; justify-content:center; font-size:6rem;'>👤</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.caption(f"Ref: {foto_path.split('/')[-1]}")
                else:
                    st.markdown("<div style='background:#f1f5f9; height:250px; border-radius:15px; display:flex; align-items:center; justify-content:center; font-size:6rem;'>👤</div>", unsafe_allow_html=True)
            
            with c2:
                st.subheader(data[col_busqueda])
                
                # Iglesia Actual
                st.markdown(f"""
                <div class="profile-card" style="border-left: 6px solid #fbbf24; background: #fffbeb;">
                    <p style='margin:0; font-size:0.8rem; color:#92400e; font-weight:bold;'>IGLESIA ACTUAL (Gestión {data['AÑO_ULTIMO']})</p>
                    <h3 style='margin:0; color:#78350f;'>{data['IGLESIA_RESULTADO']}</h3>
                </div>
                """, unsafe_allow_html=True)

                # Campos a excluir de las tarjetas de info general
                excluir = [
                    'ID_MINISTRO', 'NOMBRE', 'IGLESIA', 'MINISTRO', 
                    'NOMBRE_REL', 'AÑO', 'IGLESIA_RESULTADO', 'AÑO_ULTIMO', 'ID',
                    'ESTUDIOS TEOLOGICOS', 'ESTUDIOS ACADEMICOS', col_foto
                ]
                
                cols_info = st.columns(2)
                visible_fields = [f for f in data.index if f not in excluir and not f.endswith(('_X', '_Y', '_REL'))]
                
                for i, field in enumerate(visible_fields):
                    with cols_info[i % 2]:
                        st.markdown(f"""
                        <div class="profile-card">
                            <small style='color:#64748b; font-weight:600; text-transform:uppercase;'>{field}</small><br>
                            <span style='color:#0f172a; font-weight:500;'>{data[field] if str(data[field]).strip() != "" else "---"}</span>
                        </div>
                        """, unsafe_allow_html=True)

            # --- SECCIÓN: HISTORIAL DE IGLESIAS ---
            st.markdown("<h3 class='section-header'>🏛️ HISTORIAL DE GESTIÓN EN IGLESIAS</h3>", unsafe_allow_html=True)
            
            # Filtrar por el ministro actual en la pestaña IGLESIA (df_relacion)
            rel_min = df_relacion[df_relacion['MINISTRO'] == current_id].copy()
            if not rel_min.empty:
                # Unir con catálogo de iglesias para obtener el NOMBRE
                rel_con_nombre = pd.merge(
                    rel_min,
                    df_iglesias_cat[['ID', 'NOMBRE']],
                    left_on='IGLESIA',
                    right_on='ID',
                    how='left'
                )
                
                actual_cols = rel_con_nombre.columns.tolist()
                
                # Identificar la columna de nombre (Pandas suele dejarla como 'NOMBRE' o 'NOMBRE_y' tras el merge)
                col_nombre_iglesia = 'NOMBRE' if 'NOMBRE' in actual_cols else 'NOMBRE_Y'
                
                try:
                    # Seleccionamos solo AÑO, el NOMBRE (iglesia) y OBSERVACION en el orden pedido
                    display_rel_hist = rel_con_nombre[['AÑO', col_nombre_iglesia, 'OBSERVACION']].copy()
                    
                    # Renombrar para estética en el Dashboard
                    display_rel_hist.columns = ['AÑO', 'NOMBRE DE IGLESIA', 'OBSERVACION']
                    
                    # Mostrar tabla ordenada por año
                    st.dataframe(
                        display_rel_hist.sort_values(by='AÑO', ascending=False), 
                        use_container_width=True, 
                        hide_index=True
                    )
                except KeyError:
                    # Fallback de seguridad: si falla la selección, mostrar lo que hay pero filtrado
                    st.warning("Estructura de columnas inesperada. Mostrando datos disponibles.")
                    st.dataframe(rel_con_nombre, use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron registros históricos de iglesias para este ministro.")

            # --- SECCIÓN: ESTUDIOS TEOLÓGICOS ---
            st.markdown("<h3 class='section-header'>📚 ESTUDIOS TEOLÓGICOS</h3>", unsafe_allow_html=True)
            
            est_teo_min = df_est_teo_raw[df_est_teo_raw['MINISTRO'] == current_id]
            if not est_teo_min.empty:
                display_teo = est_teo_min[['NIVEL', 'ESCUELA', 'PERIODO', 'CERTIFICADO']].copy()
                st.dataframe(display_teo, use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron registros de estudios teológicos para este ministro.")

            # --- SECCIÓN: ESTUDIOS ACADÉMICOS ---
            st.markdown("<h3 class='section-header'>🎓 ESTUDIOS ACADÉMICOS</h3>", unsafe_allow_html=True)
            
            est_aca_min = df_est_aca_raw[df_est_aca_raw['MINISTRO'] == current_id]
            if not est_aca_min.empty:
                display_aca = est_aca_min[['NIVEL', 'ESCUELA', 'PERIODO', 'CERTIFICADO']].copy()
                st.dataframe(display_aca, use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron registros de estudios académicos para este ministro.")

            # --- SECCIÓN: REVISIÓN ---
            st.markdown("<h3 class='section-header'>📝 HISTORIAL DE REVISIONES</h3>", unsafe_allow_html=True)
            
            rev_min = df_revisiones_raw[df_revisiones_raw['MINISTRO'] == current_id]
            if not rev_min.empty:
                # Conversión de ID de Iglesia a Nombre para la tabla de revisiones
                rev_con_nombre = pd.merge(
                    rev_min,
                    df_iglesias_cat[['ID', 'NOMBRE']],
                    left_on='IGLESIA',
                    right_on='ID',
                    how='left',
                    suffixes=('_REV', '_CAT')
                )
                
                rev_con_nombre['IGLESIA_DISPLAY'] = rev_con_nombre['NOMBRE'].fillna(rev_con_nombre['IGLESIA'])
                
                display_rev = rev_con_nombre[['ID_REVISION', 'IGLESIA_DISPLAY', 'FEC_REVISION', 'PROX_REVISION', 'STATUS']].copy()
                display_rev.columns = ['ID_REVISION', 'IGLESIA', 'FEC_REVISION', 'PROX_REVISION', 'STATUS']
                
                st.dataframe(display_rev.sort_values(by='FEC_REVISION', ascending=False), use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron registros de revisiones para este ministro.")

        else:
            st.info("Utilice el buscador para localizar un ministro y ver su historial de gestión.")
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()