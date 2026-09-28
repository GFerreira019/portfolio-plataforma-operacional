# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [Unreleased] - 2026-09-26

### Adicionado
- Setup inicial da arquitetura Django + DRF + PostgreSQL para a `python_app`.
- Adicionado `.env.example` com configuração do banco de dados.
- Adicionado `requirements.txt` com as dependências do projeto.
- Removido código prévio utilizando FastAPI.
- Reestruturados `Architecture.md` e `TaskList.md` para orientar a IDE sobre o contexto do sistema, a arquitetura-alvo, o escopo simplificado e a ordem de implementação.
- Definido que toda implementação futura deve atualizar este arquivo com resumo, áreas afetadas e validações executadas.

### Validações
- Confirmada a execução das validações documentadas em cada fase.

### Pendências

- Registrar aqui cada nova implementação, correção ou decisão técnica antes de considerar a entrega concluída.

### 2026-09-28 (Fase 3)
- **O que foi feito:** Autenticação e Permissões (Fase 3) concluída.
- **Áreas afetadas:**
  - `core/settings.py`: DRF configurado com `TokenAuthentication` e `SessionAuthentication`.
  - `catalog/models.py`: Adicionado relacionamento OneToOne `usuario` no model `Colaborador`.
  - `catalog/migrations/0003_create_roles.py`: Data migration criando os Grupos "Técnico de Campo" e "Planejador/Analista".
  - `core/permissions.py` e `core/mixins.py`: Criadas classes `IsPlanejadorOrOwner` (IDOR) e `RLSMixin` (RLS).
  - `operations/serializers.py`: Implementado Serializer base do `Apontamento` com validação de *Anti-Autoaprovação* e injeção automática do colaborador autenticado.
- **Validações executadas:** Testes de unidade em `operations/tests.py` executados com sucesso (garantindo as regras RLS e a bloqueio de aprovação própria).

### 2026-09-26 (Fase 2)
- **O que foi feito:** Modelagem Relacional e Catálogo (Fase 2) concluída.
- **Áreas afetadas:** Criados os apps `catalog` e `operations` (adicionados ao `core/settings.py`).
- **Impacto técnico:** 
  - `catalog/models.py` abriga as entidades do catálogo estático e suas relações (com validações de unicidade): `Cliente`, `Projeto`, `Equipamento`, `Atividade`, `Colaborador`, `Orcamento`.
  - `operations/models.py` possui o transacional `Apontamento`, já contemplando o snapshot de custo e metadados.
- **Validações executadas:** Arquivos de migração (`0001_initial.py`) criados com sucesso (`python manage.py makemigrations`).
