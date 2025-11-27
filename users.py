import streamlit as st

def login(users):
    # Asegurarse de que session_state tenga las claves necesarias
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None

    # Mostrar login si no está autenticado
    if not st.session_state["logged_in"]:
        st.image("Cetl.png", caption="Welcome to the Puerto Rico Data Freight Observatory")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Welcome, {username}!")

                # Redirigir a página deseada (debe estar en /pages)
                st.switch_page("2_AirCargo.py")
            else:
                st.error("Invalid username or password.")

        st.stop()  # Detiene ejecución si no está logueado
