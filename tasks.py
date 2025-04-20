import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime, date
from database import get_user_tasks, create_user_task, update_user_task, delete_user_task

def get_tasks() -> List[Dict]:
    """Obtém a lista de tarefas do usuário."""
    if not st.session_state.get('token'):
        st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
        return []
    
    return get_user_tasks(st.session_state.get('token', ''))

def create_task(task_data: Dict) -> Optional[Dict]:
    """Cria uma nova tarefa."""
    if not st.session_state.get('token'):
        st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
        return None
    
    return create_user_task(st.session_state.get('token', ''), task_data)

def update_task(task_id: int, task_data: Dict) -> Optional[Dict]:
    """Atualiza uma tarefa existente."""
    if not st.session_state.get('token'):
        st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
        return None
    
    return update_user_task(st.session_state.get('token', ''), task_id, task_data)

def delete_task(task_id: int) -> bool:
    """Remove uma tarefa."""
    if not st.session_state.get('token'):
        st.error("Erro: Token de autenticação não encontrado. Por favor, faça login novamente.")
        return False
    
    return delete_user_task(st.session_state.get('token', ''), task_id)

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