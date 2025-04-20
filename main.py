import streamlit as st
from typing import Dict, List, Optional
from auth import check_authentication, logout, get_current_user
from tasks import get_tasks, create_task, update_task, delete_task, render_task_form
from schedules import get_schedules, create_schedule, update_schedule, delete_schedule, render_schedule_form

# Configuração da página
st.set_page_config(
    page_title="Calendário Estudantil",
    page_icon="📚",
    layout="wide"
)

# Interface principal
def main():
    st.title("📚 Calendário Estudantil")
    
    # Verificar autenticação
    check_authentication()
    
    # Obter informações do usuário atual
    user_data = get_current_user()
    
    # Menu lateral
    with st.sidebar:
        if user_data:
            st.success(f"Bem-vindo, {user_data.get('username', 'Usuário')}!")
            
        st.header("Menu")
        page = st.radio(
            "Navegação",
            options=["Tarefas", "Cronogramas"],
            index=0
        )
        
        if st.button("Sair"):
            logout()
    
    # Página de Tarefas
    if page == "Tarefas":
        st.header("Gerenciamento de Tarefas")
        
        # Botão para adicionar nova tarefa
        if st.button("➕ Nova Tarefa"):
            st.session_state["adding_task"] = True
        
        # Formulário para nova tarefa
        if st.session_state.get("adding_task", False):
            with st.form("new_task_form"):
                title = st.text_input("Título")
                description = st.text_area("Descrição")
                due_date = st.date_input("Data de entrega")
                priority = st.selectbox(
                    "Prioridade",
                    options=["Baixa", "Média", "Alta"]
                )
                
                if st.form_submit_button("Salvar"):
                    task_data = {
                        "title": title,
                        "description": description,
                        "due_date": due_date.isoformat(),
                        "priority": priority
                    }
                    create_task(task_data)
                    st.session_state["adding_task"] = False
                    st.experimental_rerun()
        
        # Formulário para editar tarefa existente
        if st.session_state.get("editing_task"):
            # Obter dados da tarefa atual
            current_task = None
            for task in get_tasks():
                if task['id'] == st.session_state["editing_task"]:
                    current_task = task
                    break
            
            if current_task:
                task_data = render_task_form(current_task)
                if task_data:
                    update_task(st.session_state["editing_task"], task_data)
                    st.session_state.pop("editing_task")
                    st.experimental_rerun()
            else:
                st.error("Tarefa não encontrada!")
                st.session_state.pop("editing_task")
                st.experimental_rerun()
        
        # Lista de tarefas
        tasks = get_tasks()
        for task in tasks:
            with st.expander(f"{task['title']} - {task['due_date']}"):
                st.write(f"**Descrição:** {task['description']}")
                st.write(f"**Prioridade:** {task['priority']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Editar", key=f"edit_{task['id']}"):
                        st.session_state["editing_task"] = task['id']
                with col2:
                    if st.button("🗑️ Excluir", key=f"delete_{task['id']}"):
                        delete_task(task['id'])
                        st.experimental_rerun()
    
    # Página de Cronogramas
    else:
        st.header("Gerenciamento de Cronogramas")
        
        # Botão para adicionar novo cronograma
        if st.button("➕ Novo Cronograma"):
            st.session_state["adding_schedule"] = True
        
        # Formulário para novo cronograma
        if st.session_state.get("adding_schedule", False):
            schedule_data = render_schedule_form()
            if schedule_data:
                create_schedule(schedule_data)
                st.session_state["adding_schedule"] = False
                st.experimental_rerun()
        
        # Formulário para editar cronograma existente
        if st.session_state.get("editing_schedule"):
            # Obter dados do cronograma atual
            current_schedule = None
            for schedule in get_schedules():
                if schedule['id'] == st.session_state["editing_schedule"]:
                    current_schedule = schedule
                    break
            
            if current_schedule:
                schedule_data = render_schedule_form(current_schedule)
                if schedule_data:
                    update_schedule(st.session_state["editing_schedule"], schedule_data)
                    st.session_state.pop("editing_schedule")
                    st.experimental_rerun()
            else:
                st.error("Cronograma não encontrado!")
                st.session_state.pop("editing_schedule")
                st.experimental_rerun()
        
        # Lista de cronogramas
        schedules = get_schedules()
        for schedule in schedules:
            with st.expander(f"{schedule['title']} - {', '.join(schedule['days'])}"):
                st.write(f"**Descrição:** {schedule['description']}")
                st.write(f"**Horário:** {schedule['start_time']} até {schedule['end_time']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Editar", key=f"edit_schedule_{schedule['id']}"):
                        st.session_state["editing_schedule"] = schedule['id']
                with col2:
                    if st.button("🗑️ Excluir", key=f"delete_schedule_{schedule['id']}"):
                        delete_schedule(schedule['id'])
                        st.experimental_rerun()

if __name__ == "__main__":
    main()