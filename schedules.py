import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime, time
from database import get_user_schedules, create_user_schedule, update_user_schedule, delete_user_schedule

def get_schedules() -> List[Dict]:
    """Obtém a lista de cronogramas do usuário."""
    if not st.session_state.get('token'):
        st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
        return []
    
    return get_user_schedules(st.session_state.get('token', ''))

def create_schedule(schedule_data: Dict) -> Optional[Dict]:
    """Cria um novo cronograma."""
    if not st.session_state.get('token'):
        st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
        return None
    
    return create_user_schedule(st.session_state.get('token', ''), schedule_data)

def update_schedule(schedule_id: int, schedule_data: Dict) -> Optional[Dict]:
    """Atualiza um cronograma existente."""
    if not st.session_state.get('token'):
        st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
        return None
    
    return update_user_schedule(st.session_state.get('token', ''), schedule_id, schedule_data)

def delete_schedule(schedule_id: int) -> bool:
    """Remove um cronograma."""
    if not st.session_state.get('token'):
        st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
        return False
    
    return delete_user_schedule(st.session_state.get('token', ''), schedule_id)

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