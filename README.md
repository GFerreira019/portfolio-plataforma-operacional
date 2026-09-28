# Plataforma Operacional (Django)

Este diretório contém a implementação da arquitetura-alvo para a Plataforma Operacional.

## Contexto da Arquitetura

Conforme definido em `docs/Architecture.md`, o sistema legado foi originalmente construído em Laravel/PHP (presente na raiz do repositório). A arquitetura-alvo e os novos desenvolvimentos ocorrem nesta pasta (`python_app`) utilizando **Django, Django REST Framework (DRF) e PostgreSQL**.

**O que já existe:**
- Setup base do projeto Django.
- Containerização (Docker e Docker Compose) para ambiente local e banco de dados PostgreSQL.
- Configuração de variáveis de ambiente via `python-dotenv`.

**O que é arquitetura-alvo (ainda em andamento):**
- Migração dos modelos relacionais (Fase 2).
- Autenticação e APIs (Fases 3 e 4).
- Regras de negócio e motor de orçamentação (Fases 5 e 6).

## Dependências

- Python 3.12+
- Docker e Docker Compose (para banco de dados e execução em containers)

## Como rodar o projeto localmente

### 1. Utilizando Docker (Recomendado)
Execute o comando abaixo para subir o banco de dados PostgreSQL e a aplicação Django:
```bash
docker-compose up --build
```
A aplicação estará disponível em `http://localhost:8000`.

### 2. Rodando localmente sem Docker (Apenas Python)
Caso prefira rodar a aplicação via ambiente virtual, será necessário subir pelo menos o banco de dados via Docker:
```bash
# Subir apenas o banco de dados
docker-compose up db -d

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar as migrações (se houver)
python manage.py migrate

# Executar o servidor de desenvolvimento
python manage.py runserver
```

## Como rodar os testes e ferramentas de código (Lint/Formatação)

Os testes e as rotinas de verificação do projeto serão realizados nativamente via `manage.py test` ou `pytest` (a ser configurado na sequência), e formatação de código com `black` ou `flake8`.

```bash
# Rodar testes nativos
python manage.py test
```
