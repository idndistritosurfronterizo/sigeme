import streamlit as st

st.set_page_config(page_title="Test Mínimo", page_icon="✅")

st.title("✅ Versión Mínima")
st.write("Si ves esto, Streamlit funciona")

# Probar un poco de lógica
nombre = st.text_input("Escribe algo:")
if nombre:
    st.success(f"Hola {nombre}!")