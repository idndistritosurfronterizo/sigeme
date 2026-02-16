import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os

st.set_page_config(
    page_title="DIAGNÓSTICO DATOS - SIGEME",
    page_icon="📊",
    layout="wide"
)

st.title("📊 DIAGNÓSTICO DE DATOS")

def get_as_dataframe(worksheet):
    """Método para leer hojas"""
    try:
        data = worksheet.get_all_values()
        if not data:
            return pd.DataFrame()
        headers = [str(h).strip().upper() if h else f"COL_{i}" for i, h in enumerate(data[0])]
        final_headers = []
        for i, h in enumerate(headers):
            if h in final_headers:
                final_headers.append(f"{h}_{i}")
            else:
                final_headers.append(h)
        return pd.DataFrame(data[1:], columns=final_headers)
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# Conectar a Google
st.write("### 🔌 Conectando a Google...")

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
client = gspread.authorize(creds)
spreadsheet = client.open("BD MINISTROS")

st.success("✅ Conectado a Google Sheets")

# Cargar cada hoja individualmente con control de errores
st.write("### 📥 Cargando hojas...")

hojas_a_cargar = {
    "MINISTRO": "MINISTRO",
    "RELACION": "IGLESIA", 
    "CAT_IGLESIAS": "IGLESIAS",
    "TEOLOGICOS": "ESTUDIOS TEOLOGICOS",
    "ACADEMICOS": "ESTUDIOS ACADEMICOS",
    "REVISION": "Revision"
}

dataframes = {}

for key, nombre_hoja in hojas_a_cargar.items():
    st.write(f"**Cargando {key} ({nombre_hoja})...**")
    try:
        worksheet = spreadsheet.worksheet(nombre_hoja)
        df = get_as_dataframe(worksheet)
        dataframes[key] = df
        st.success(f"✅ {key} cargada - {len(df)} filas, {len(df.columns)} columnas")
        
        # Mostrar vista previa
        with st.expander(f"Vista previa de {key}"):
            if not df.empty:
                st.write("Primeras 3 filas:")
                st.dataframe(df.head(3))
                st.write("Columnas:", list(df.columns))
            else:
                st.warning("DataFrame vacío")
                
    except Exception as e:
        st.error(f"❌ Error cargando {key}: {e}")
        dataframes[key] = pd.DataFrame()

# Probar el procesamiento de datos
st.write("### 🔄 Probando procesamiento de datos...")

try:
    if all(key in dataframes for key in ["MINISTRO", "RELACION", "CAT_IGLESIAS"]):
        df_ministros = dataframes["MINISTRO"]
        df_relacion = dataframes["RELACION"]
        df_iglesias_cat = dataframes["CAT_IGLESIAS"]
        
        st.write("**Datos disponibles para procesamiento:**")
        st.write(f"- Ministros: {len(df_ministros)} registros")
        st.write(f"- Relaciones: {len(df_relacion)} registros")
        st.write(f"- Iglesias: {len(df_iglesias_cat)} registros")
        
        # Verificar columnas necesarias
        st.write("**Verificando columnas:**")
        
        if 'ID_MINISTRO' in df_ministros.columns:
            st.success(f"✅ Columna ID_MINISTRO en MINISTROS")
        else:
            st.error(f"❌ No se encuentra ID_MINISTRO en MINISTROS. Columnas: {list(df_ministros.columns)}")
            
        if 'MINISTRO' in df_relacion.columns:
            st.success(f"✅ Columna MINISTRO en RELACION")
        else:
            st.error(f"❌ No se encuentra MINISTRO en RELACION. Columnas: {list(df_relacion.columns)}")
            
        if 'IGLESIA' in df_relacion.columns:
            st.success(f"✅ Columna IGLESIA en RELACION")
        else:
            st.error(f"❌ No se encuentra IGLESIA en RELACION. Columnas: {list(df_relacion.columns)}")
            
        if 'ID' in df_iglesias_cat.columns:
            st.success(f"✅ Columna ID en IGLESIAS")
        else:
            st.error(f"❌ No se encuentra ID en IGLESIAS. Columnas: {list(df_iglesias_cat.columns)}")
            
        if 'NOMBRE' in df_iglesias_cat.columns:
            st.success(f"✅ Columna NOMBRE en IGLESIAS")
        else:
            st.error(f"❌ No se encuentra NOMBRE en IGLESIAS. Columnas: {list(df_iglesias_cat.columns)}")
        
        # Intentar el merge paso a paso
        st.write("**Probando merge de datos:**")
        
        # Paso 1: Normalizar
        df_relacion['AÑO'] = pd.to_numeric(df_relacion['AÑO'], errors='coerce').fillna(0)
        df_relacion['MINISTRO'] = df_relacion['MINISTRO'].astype(str).str.strip()
        df_relacion['IGLESIA'] = df_relacion['IGLESIA'].astype(str).str.strip()
        df_ministros['ID_MINISTRO'] = df_ministros['ID_MINISTRO'].astype(str).str.strip()
        df_iglesias_cat['ID'] = df_iglesias_cat['ID'].astype(str).str.strip()
        
        # Paso 2: Última iglesia
        if not df_relacion.empty:
            df_rel_actual = df_relacion.sort_values(by=['MINISTRO', 'AÑO'], ascending=[True, False]).drop_duplicates(subset=['MINISTRO'])
            st.success(f"✅ Últimas relaciones calculadas: {len(df_rel_actual)} registros")
            
            # Paso 3: Merge con iglesias
            df_rel_con_nombre = pd.merge(df_rel_actual, df_iglesias_cat[['ID', 'NOMBRE']], left_on='IGLESIA', right_on='ID', how='left')
            st.success(f"✅ Merge con iglesias completado: {len(df_rel_con_nombre)} registros")
            
            # Paso 4: Merge final
            df_final = pd.merge(df_ministros, df_rel_con_nombre[['MINISTRO', 'NOMBRE', 'AÑO']], left_on='ID_MINISTRO', right_on='MINISTRO', how='left', suffixes=('', '_REL'))
            df_final['IGLESIA_RESULTADO'] = df_final['NOMBRE_REL'].fillna("Sin Iglesia Asignada")
            st.success(f"✅ Merge final completado: {len(df_final)} registros")
            
            # Mostrar resultado
            st.write("**Muestra del resultado final:**")
            columnas_mostrar = ['ID_MINISTRO', 'NOMBRE', 'IGLESIA_RESULTADO'] + [col for col in df_final.columns if col not in ['ID_MINISTRO', 'NOMBRE', 'IGLESIA_RESULTADO', 'MINISTRO', 'NOMBRE_REL']][:5]
            st.dataframe(df_final[columnas_mostrar].head(10))
            
        else:
            st.error("❌ DataFrame RELACION vacío")
            
except Exception as e:
    st.error(f"❌ Error en procesamiento: {e}")
    import traceback
    st.code(traceback.format_exc())

st.write("---")
st.write("### 📋 Resumen")
st.write("Si ves errores en las columnas, necesitamos ajustar los nombres en el código")
st.write("Los nombres de columnas deben coincidir exactamente con los que ves en Google Sheets")