# Calendário Estudantil - Frontend

Interface gráfica para organização de atividades estudantis desenvolvida com Streamlit.

## Funcionalidades

- Gerenciamento de tarefas (criar, editar, excluir)
- Cronogramas de estudo
- Interface responsiva e intuitiva
- Integração com API RESTful

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Student-Calendar-V2.git
cd Student-Calendar-V2/python-front
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

Para iniciar a aplicação, execute:
```bash
streamlit run main.py
```

A aplicação estará disponível em `http://localhost:8501`

## Estrutura do Projeto

- `main.py`: Arquivo principal da aplicação
- `auth.py`: Módulo de autenticação
- `tasks.py`: Gerenciamento de tarefas
- `schedules.py`: Gerenciamento de cronogramas
- `requirements.txt`: Dependências do projeto