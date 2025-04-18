import streamlit as st
import requests
from typing import Dict, Optional

API_BASE_URL = "https://student-calendar-back.onrender.com/api"

def login(username: str, password: str) -> Optional[str]:
    """Realiza o login do usuário e retorna o token JWT."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("token")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao realizar login: {str(e)}")
        return None

def check_authentication():
    """Verifica se o usuário está autenticado e exibe o formulário de login se necessário."""
    if "token" not in st.session_state:
        st.warning("Por favor, faça login para continuar")
        
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            
            if st.form_submit_button("Entrar"):
                if token := login(username, password):
                    st.session_state["token"] = token
                    st.success("Login realizado com sucesso!")
                    st.experimental_rerun()
        
        st.stop()

def logout():
    """Realiza o logout do usuário."""
    if "token" in st.session_state:
        del st.session_state["token"]
        st.success("Logout realizado com sucesso!")
        st.experimental_rerun()