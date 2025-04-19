import streamlit as st
import requests
from typing import Dict, List, Optional
from datetime import datetime, date

API_BASE_URL = "https://student-calendar-back.onrender.com"

@st.cache_resource
def get_tasks() -> List[Dict]:
    """Obtém a lista de tarefas do usuário."""
    try:
        if not st.session_state.get('token'):
            st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
            return []
        
        headers = {'Authorization': f'Bearer {st.session_state.get("token", "")}'} if st.session_state.get('token') else {}
        response = requests.get(
            f"{API_BASE_URL}/tasks",
            headers=headers
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
        st.error(f"Erro ao obter tarefas: {str(e)}")
        return []

def create_task(task_data: Dict) -> Optional[Dict]:
    """Cria uma nova tarefa."""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.get('token', '')}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_BASE_URL}/tasks",
            json=task_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao criar tarefa: {str(e)}")
        return None

def update_task(task_id: int, task_data: Dict) -> Optional[Dict]:
    """Atualiza uma tarefa existente."""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.get('token', '')}",
            "Content-Type": "application/json"
        }
        response = requests.put(
            f"{API_BASE_URL}/tasks/{task_id}",
            json=task_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao atualizar tarefa: {str(e)}")
        return None

def delete_task(task_id: int) -> bool:
    """Remove uma tarefa."""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.get('token', '')}"
        }
        response = requests.delete(
            f"{API_BASE_URL}/tasks/{task_id}",
            headers=headers
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao excluir tarefa: {str(e)}")
        return False

def render_task_form(existing_data: Optional[Dict] = None) -> Dict:
    """Renderiza o formulário para criar/editar tarefa."""
    title = existing_data.get("title", "") if existing_data else ""
    description = existing_data.get("description", "") if existing_data else ""
    due_date = datetime.strptime(existing_data.get("due_date", date.today().isoformat()), "%Y-%m-%d").date() if existing_data else date.today()
    priority = existing_data.get("priority", "Média") if existing_data else "Média"
    
    with st.form("task_form"):
        title = st.text_input("Título", value=title)
        description = st.text_area("Descrição", value=description)
        due_date = st.date_input("Data de Entrega", value=due_date)
        priority = st.selectbox(
            "Prioridade",
            options=["Baixa", "Média", "Alta"],
            index=["Baixa", "Média", "Alta"].index(priority)
        )
        
        submitted = st.form_submit_button("Salvar")
        
        if submitted:
            return {
                "title": title,
                "description": description,
                "due_date": due_date.isoformat(),
                "priority": priority
            }
    return None

def render_task_list():
    """Renderiza a lista de tarefas com opções de edição e exclusão."""
    tasks = get_tasks()
    
    for task in tasks:
        with st.expander(f"📝 {task['title']} - {task['due_date']}"):
            st.write(f"**Descrição:** {task['description']}")
            st.write(f"**Prioridade:** {task['priority']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Editar", key=f"edit_{task['id']}"):
                    st.session_state["editing_task"] = task['id']
                    st.session_state["task_data"] = task
            with col2:
                if st.button("🗑️ Excluir", key=f"delete_{task['id']}"):
                    if delete_task(task['id']):
                        st.success("Tarefa excluída com sucesso!")
                        st.experimental_rerun()