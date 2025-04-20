import streamlit as st
from typing import Dict, Optional
from database import register_user, login_user, get_user_by_token

def register(username: str, email: Optional[str], password: str) -> Optional[Dict]:
    """Realiza o registro de um novo usuário e retorna os dados do usuário criado."""
    return register_user(username, email, password)

def login(username: str, password: str) -> Optional[str]:
    """Realiza o login do usuário e retorna o token."""
    return login_user(username, password)

def get_current_user() -> Optional[Dict]:
    """Obtém informações do usuário atual usando o token."""
    if not st.session_state.get('token'):
        return None
        
    return get_user_by_token(st.session_state.get('token', ''))

def check_authentication():
    """Verifica se o usuário está autenticado e exibe o formulário de login se necessário."""
    if "token" not in st.session_state:
        st.warning("Por favor, faça login para continuar")
        
        # Tabs para login e registro
        tab1, tab2 = st.tabs(["Login", "Registro"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Usuário")
                password = st.text_input("Senha", type="password")
                
                if st.form_submit_button("Entrar"):
                    if token := login(username, password):
                        st.session_state["token"] = token
                        st.success("Login realizado com sucesso!")
                        st.experimental_rerun()
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Usuário")
                new_email = st.text_input("Email (opcional)")
                new_password = st.text_input("Senha", type="password")
                confirm_password = st.text_input("Confirmar Senha", type="password")
                
                if st.form_submit_button("Registrar"):
                    if new_password != confirm_password:
                        st.error("As senhas não coincidem!")
                    else:
                        if user_data := register(new_username, new_email, new_password):
                            st.success("Registro realizado com sucesso! Faça login para continuar.")
        
        st.stop()
    else:
        # Verificar se o token ainda é válido
        user_data = get_current_user()
        if not user_data:
            # Token inválido, fazer logout
            logout()

def logout():
    """Realiza o logout do usuário."""
    if "token" in st.session_state:
        del st.session_state["token"]
        st.success("Logout realizado com sucesso!")
        st.experimental_rerun()