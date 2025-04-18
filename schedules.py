import streamlit as st
import requests
from typing import Dict, List, Optional
from datetime import datetime, time

API_BASE_URL = "https://student-calendar-back.onrender.com"

@st.cache_resource
def get_schedules() -> List[Dict]:
    """Obtém a lista de cronogramas do usuário."""
    try:
        if not st.session_state.get('token'):
            st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
            return []
        
        response = requests.get(
            f"{API_BASE_URL}/schedules",
            headers={"Authorization": f"Bearer {st.session_state.get('token', '')}"},
            timeout=10  # Timeout de 10 segundos
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Erro: Tempo limite excedido ao tentar conectar com a API. Por favor, tente novamente.")
        return []
    except requests.exceptions.ConnectionError as e:
        st.error(f"Erro de conexão com a API: {str(e)}\nVerifique sua conexão com a internet e tente novamente.")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter cronogramas: {str(e)}")
        return []

def create_schedule(schedule_data: Dict) -> Optional[Dict]:
    """Cria um novo cronograma."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/schedules",
            headers={
                "Authorization": f"Bearer {st.session_state.get('token', '')}",
                "Content-Type": "application/json"
            },
            json=schedule_data
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao criar cronograma: {str(e)}")
        return None

def update_schedule(schedule_id: int, schedule_data: Dict) -> Optional[Dict]:
    """Atualiza um cronograma existente."""
    try:
        response = requests.put(
            f"{API_BASE_URL}/schedules/{schedule_id}",
            headers={
                "Authorization": f"Bearer {st.session_state.get('token', '')}",
                "Content-Type": "application/json"
            },
            json=schedule_data
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao atualizar cronograma: {str(e)}")
        return None

def delete_schedule(schedule_id: int) -> bool:
    """Remove um cronograma."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {st.session_state.get('token', '')}"}
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao excluir cronograma: {str(e)}")
        return False

def render_schedule_form(existing_data: Optional[Dict] = None) -> Dict:
    """Renderiza o formulário para criar/editar cronograma."""
    title = existing_data.get("title", "") if existing_data else ""
    description = existing_data.get("description", "") if existing_data else ""
    start_time = datetime.strptime(existing_data.get("start_time", "08:00"), "%H:%M").time() if existing_data else time(8, 0)
    end_time = datetime.strptime(existing_data.get("end_time", "18:00"), "%H:%M").time() if existing_data else time(18, 0)
    days = existing_data.get("days", []) if existing_data else []
    
    with st.form("schedule_form"):
        title = st.text_input("Título", value=title)
        description = st.text_area("Descrição", value=description)
        start_time = st.time_input("Horário de Início", value=start_time)
        end_time = st.time_input("Horário de Término", value=end_time)
        
        days_options = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        selected_days = st.multiselect(
            "Dias da Semana",
            options=days_options,
            default=days
        )
        
        submitted = st.form_submit_button("Salvar")
        
        if submitted:
            return {
                "title": title,
                "description": description,
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "days": selected_days
            }
    return None