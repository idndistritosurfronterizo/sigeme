def main():
    st.write("🚀 **Función main iniciada**")
    
    # Timeout para conexiones largas
    import socket
    socket.setdefaulttimeout(30)  # 30 segundos de timeout
    
    if not check_password():
        st.write("⏸️ Deteniendo ejecución - usuario no autenticado")
        st.stop()
    
    st.write("✅ Usuario autenticado, continuando con main...")
    
    # Agregar un botón para reconectar manualmente
    if st.button("🔄 Forzar reconexión a Google"):
        st.cache_data.clear()
        st.rerun()