from pages import usuarios

MENU_ITEMS = [
    ("usuarios", "👤 Usuários"),
    # ...
]

if st.session_state.pagina == "usuarios":
    usuarios.render(TEMA)
    st.stop()