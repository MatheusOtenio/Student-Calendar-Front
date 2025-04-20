import sqlite3
import os
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import secrets
import string

# Configuração do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), 'student_calendar.db')

# Função para gerar um token aleatório
def generate_token(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Função para criar hash de senha
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Inicialização do banco de dados
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabela de tokens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Tabela de tarefas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date DATE NOT NULL,
        priority TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Tabela de cronogramas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Tabela de dias da semana para cronogramas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedule_days (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_id INTEGER NOT NULL,
        day TEXT NOT NULL,
        FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

# Funções de autenticação
def register_user(username: str, email: Optional[str], password: str) -> Optional[Dict]:
    """Registra um novo usuário no banco de dados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se o usuário já existe
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            st.error(f"Usuário {username} já existe!")
            conn.close()
            return None
        
        # Hash da senha
        password_hash = hash_password(password)
        
        # Inserir novo usuário
        if email:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
        else:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # Obter dados do usuário
        cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "created_at": user[3]
            }
        return None
    except sqlite3.Error as e:
        st.error(f"Erro ao registrar usuário: {str(e)}")
        return None

def login_user(username: str, password: str) -> Optional[str]:
    """Realiza o login do usuário e retorna um token."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar credenciais
        password_hash = hash_password(password)
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        
        if not user:
            st.error("Credenciais inválidas!")
            conn.close()
            return None
        
        user_id = user[0]
        
        # Gerar e armazenar token
        token = generate_token()
        cursor.execute(
            "INSERT INTO tokens (user_id, token) VALUES (?, ?)",
            (user_id, token)
        )
        conn.commit()
        conn.close()
        
        return token
    except sqlite3.Error as e:
        st.error(f"Erro ao realizar login: {str(e)}")
        return None

def get_user_by_token(token: str) -> Optional[Dict]:
    """Obtém informações do usuário pelo token."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT u.id, u.username, u.email, u.created_at 
               FROM users u 
               JOIN tokens t ON u.id = t.user_id 
               WHERE t.token = ?""",
            (token,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "created_at": user[3]
            }
        return None
    except sqlite3.Error as e:
        st.error(f"Erro ao obter informações do usuário: {str(e)}")
        return None

# Funções para tarefas
def get_user_tasks(token: str) -> List[Dict]:
    """Obtém todas as tarefas do usuário."""
    try:
        user = get_user_by_token(token)
        if not user:
            return []
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, title, description, due_date, priority, created_at FROM tasks WHERE user_id = ?",
            (user["id"],)
        )
        tasks = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": task[0],
                "title": task[1],
                "description": task[2],
                "due_date": task[3],
                "priority": task[4],
                "created_at": task[5]
            }
            for task in tasks
        ]
    except sqlite3.Error as e:
        st.error(f"Erro ao obter tarefas: {str(e)}")
        return []

def create_user_task(token: str, task_data: Dict) -> Optional[Dict]:
    """Cria uma nova tarefa para o usuário."""
    try:
        user = get_user_by_token(token)
        if not user:
            return None
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO tasks (user_id, title, description, due_date, priority) 
               VALUES (?, ?, ?, ?, ?)""",
            (user["id"], task_data["title"], task_data["description"], 
             task_data["due_date"], task_data["priority"])
        )
        task_id = cursor.lastrowid
        conn.commit()
        
        # Obter a tarefa criada
        cursor.execute(
            "SELECT id, title, description, due_date, priority, created_at FROM tasks WHERE id = ?",
            (task_id,)
        )
        task = cursor.fetchone()
        conn.close()
        
        if task:
            return {
                "id": task[0],
                "title": task[1],
                "description": task[2],
                "due_date": task[3],
                "priority": task[4],
                "created_at": task[5]
            }
        return None
    except sqlite3.Error as e:
        st.error(f"Erro ao criar tarefa: {str(e)}")
        return None

def update_user_task(token: str, task_id: int, task_data: Dict) -> Optional[Dict]:
    """Atualiza uma tarefa existente."""
    try:
        user = get_user_by_token(token)
        if not user:
            return None
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tarefa pertence ao usuário
        cursor.execute(
            "SELECT id FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user["id"])
        )
        if not cursor.fetchone():
            st.error("Tarefa não encontrada ou não pertence ao usuário!")
            conn.close()
            return None
        
        # Atualizar tarefa
        cursor.execute(
            """UPDATE tasks 
               SET title = ?, description = ?, due_date = ?, priority = ? 
               WHERE id = ?""",
            (task_data["title"], task_data["description"], 
             task_data["due_date"], task_data["priority"], task_id)
        )
        conn.commit()
        
        # Obter a tarefa atualizada
        cursor.execute(
            "SELECT id, title, description, due_date, priority, created_at FROM tasks WHERE id = ?",
            (task_id,)
        )
        task = cursor.fetchone()
        conn.close()
        
        if task:
            return {
                "id": task[0],
                "title": task[1],
                "description": task[2],
                "due_date": task[3],
                "priority": task[4],
                "created_at": task[5]
            }
        return None
    except sqlite3.Error as e:
        st.error(f"Erro ao atualizar tarefa: {str(e)}")
        return None

def delete_user_task(token: str, task_id: int) -> bool:
    """Remove uma tarefa do usuário."""
    try:
        user = get_user_by_token(token)
        if not user:
            return False
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tarefa pertence ao usuário
        cursor.execute(
            "SELECT id FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user["id"])
        )
        if not cursor.fetchone():
            st.error("Tarefa não encontrada ou não pertence ao usuário!")
            conn.close()
            return False
        
        # Excluir tarefa
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao excluir tarefa: {str(e)}")
        return False

# Funções para cronogramas
def get_user_schedules(token: str) -> List[Dict]:
    """Obtém todos os cronogramas do usuário."""
    try:
        user = get_user_by_token(token)
        if not user:
            return []
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT s.id, s.title, s.description, s.start_time, s.end_time, s.created_at 
               FROM schedules s 
               WHERE s.user_id = ?""",
            (user["id"],)
        )
        schedules = cursor.fetchall()
        
        result = []
        for schedule in schedules:
            schedule_id = schedule[0]
            
            # Obter os dias da semana para este cronograma
            cursor.execute(
                "SELECT day FROM schedule_days WHERE schedule_id = ?",
                (schedule_id,)
            )
            days = [row[0] for row in cursor.fetchall()]
            
            result.append({
                "id": schedule_id,
                "title": schedule[1],
                "description": schedule[2],
                "start_time": schedule[3],
                "end_time": schedule[4],
                "days": days,
                "created_at": schedule[5]
            })
        
        conn.close()
        return result
    except sqlite3.Error as e:
        st.error(f"Erro ao obter cronogramas: {str(e)}")
        return []

def create_user_schedule(token: str, schedule_data: Dict) -> Optional[Dict]:
    """Cria um novo cronograma para o usuário."""
    try:
        user = get_user_by_token(token)
        if not user:
            return None
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Inserir cronograma
        cursor.execute(
            """INSERT INTO schedules (user_id, title, description, start_time, end_time) 
               VALUES (?, ?, ?, ?, ?)""",
            (user["id"], schedule_data["title"], schedule_data["description"], 
             schedule_data["start_time"], schedule_data["end_time"])
        )
        schedule_id = cursor.lastrowid
        
        # Inserir dias da semana
        for day in schedule_data["days"]:
            cursor.execute(
                "INSERT INTO schedule_days (schedule_id, day) VALUES (?, ?)",
                (schedule_id, day)
            )
        
        conn.commit()
        
        # Obter o cronograma criado
        cursor.execute(
            """SELECT id, title, description, start_time, end_time, created_at 
               FROM schedules WHERE id = ?""",
            (schedule_id,)
        )
        schedule = cursor.fetchone()
        
        # Obter os dias da semana
        cursor.execute(
            "SELECT day FROM schedule_days WHERE schedule_id = ?",
            (schedule_id,)
        )
        days = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        if schedule:
            return {
                "id": schedule[0],
                "title": schedule[1],
                "description": schedule[2],
                "start_time": schedule[3],
                "end_time": schedule[4],
                "days": days,
                "created_at": schedule[5]
            }
        return None
    except sqlite3.Error as e:
        st.error(f"Erro ao criar cronograma: {str(e)}")
        return None

def update_user_schedule(token: str, schedule_id: int, schedule_data: Dict) -> Optional[Dict]:
    """Atualiza um cronograma existente."""
    try:
        user = get_user_by_token(token)
        if not user:
            return None
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se o cronograma pertence ao usuário
        cursor.execute(
            "SELECT id FROM schedules WHERE id = ? AND user_id = ?",
            (schedule_id, user["id"])
        )
        if not cursor.fetchone():
            st.error("Cronograma não encontrado ou não pertence ao usuário!")
            conn.close()
            return None
        
        # Atualizar cronograma
        cursor.execute(
            """UPDATE schedules 
               SET title = ?, description = ?, start_time = ?, end_time = ? 
               WHERE id = ?""",
            (schedule_data["title"], schedule_data["description"], 
             schedule_data["start_time"], schedule_data["end_time"], schedule_id)
        )
        
        # Atualizar dias da semana
        cursor.execute("DELETE FROM schedule_days WHERE schedule_id = ?", (schedule_id,))
        for day in schedule_data["days"]:
            cursor.execute(
                "INSERT INTO schedule_days (schedule_id, day) VALUES (?, ?)",
                (schedule_id, day)
            )
        
        conn.commit()
        
        # Obter o cronograma atualizado
        cursor.execute(
            """SELECT id, title, description, start_time, end_time, created_at 
               FROM schedules WHERE id = ?""",
            (schedule_id,)
        )
        schedule = cursor.fetchone()
        
        # Obter os dias da semana
        cursor.execute(
            "SELECT day FROM schedule_days WHERE schedule_id = ?",
            (schedule_id,)
        )
        days = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        if schedule:
            return {
                "id": schedule[0],
                "title": schedule[1],
                "description": schedule[2],
                "start_time": schedule[3],
                "end_time": schedule[4],
                "days": days,
                "created_at": schedule[5]
            }
        return None
    except sqlite3.Error as e:
        st.error(f"Erro ao atualizar cronograma: {str(e)}")
        return None

def delete_user_schedule(token: str, schedule_id: int) -> bool:
    """Remove um cronograma do usuário."""
    try:
        user = get_user_by_token(token)
        if not user:
            return False
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se o cronograma pertence ao usuário
        cursor.execute(
            "SELECT id FROM schedules WHERE id = ? AND user_id = ?",
            (schedule_id, user["id"])
        )
        if not cursor.fetchone():
            st.error("Cronograma não encontrado ou não pertence ao usuário!")
            conn.close()
            return False
        
        # Excluir cronograma (os dias serão excluídos automaticamente pela restrição ON DELETE CASCADE)
        cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
        conn.commit()
        conn.close()
        
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao excluir cronograma: {str(e)}")
        return False

# Inicializar o banco de dados quando o módulo for importado
init_db()