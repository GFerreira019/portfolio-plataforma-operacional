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

### 2026-10-04 (Setup de Equipamentos e Autoajuste)
- **O que foi feito:** Funcionalidade completa de Setup de Equipamentos por Projeto com recálculo automático de Produtividade (Tempo Médio Autoajustável).
- **Áreas afetadas:**
  - `catalog/models.py`: Adicionados campos `tempo_medio_estimado`, `tempo_medio_real`, `desvio_tempo_pct` e `total_amostras` à tabela `ProjetoEquipamentoAtividade`.
  - `catalog/migrations/0005_projetoequipamentoatividade_desvio_tempo_pct_and_more.py`: Migration criada e aplicada com sucesso.
  - `catalog/views.py`: Adicionada ação `setup_equipamentos` em `ProjetoViewSet` para salvar o Setup em Lote disparado pelo frontend.
  - `operations/services.py`: Criado serviço `EquipamentoProdutividadeService` contendo a regra de negócios pura de agrupamento e recálculo do tempo médio e desvio percentual.
  - `operations/views.py`: O serviço de recálculo foi injetado dentro da ação `aprovar` de `ApontamentoViewSet`, garantindo que todo apontamento aprovado atualize o KPI na mesma transação/request.
  - `operations/tests.py`: Criado o `EquipamentoProdutividadeServiceTestCase` validando todo o fluxo de cálculos, apontamentos e ignorando aprovações pendentes ou rejeitadas.
  - `frontend_app/src/components/SetupEquipamentos.jsx`: Componente UI criado e renderizado no `PainelPlanejador` para a gestão interativa dos tempos médios previstos.

### 2026-10-04 (Fase 8)
- **O que foi feito:** Configuração do CPQ, Indicadores e Business Intelligence (Fase 8) concluída.
- **Áreas afetadas:**
  - `catalog/serializers.py` & `catalog/views.py`: Exposição de APIs e serializadores para o fluxo de Orçamentação (`OrcamentoViewSet`, `ProjetoEquipamentoViewSet`).
  - `core/urls.py`: Adicionadas as rotas de API para suprir o fluxo mínimo viável de orçamentação.
  - `catalog/migrations/0004_create_bi_views.py`: Migration que constrói de forma robusta e persistente duas Views em SQL Otimizado (`bi_vw_projetos_kpi` e `bi_vw_apontamentos_detalhados`).
  - `docs/powerbi_views.sql`: Export do código nativo SQL para rápida consulta de negócio.
  - `docs/powerbi_guide.md`: Criação de guia tático e passo-a-passo explicando a arquitetura (Decoupling) entre a fonte de operação transacional e o consumo no PowerBI utilizando Read-Only Views.

### 2026-09-28 (Fase 7)
- **O que foi feito:** Frontend Operacional (Fase 7) concluída.
- **Áreas afetadas:**
  - `frontend_app/`: Criado e configurado usando Vite, React, React Router e Axios.
  - `frontend_app/src/index.css`: Criado sistema de design "Glassmorphism" do zero (Dark Mode premium com paleta vibrante).
  - `App.jsx` & `api.js`: Desenvolvido "Seletor de Usuário" para facilitar testes rápidos (Técnico vs Planejador).
  - `ApontamentoForm.jsx`: Formulário com seleção de campos em cascata consumindo os dados da API com paginação inteligente.
  - `PainelPlanejador.jsx`: Tabela para fila de aprovação de apontamentos e Dashboard em Tempo Real consumindo dados da arquitetura de KPIs (Avanço Físico, Desvio, Ritmo e Previsão) desenvolvida na Fase 6.
  - `python_app/core/settings.py`: Resolvido CORS injetando globalmente o `django-cors-headers`.

### 2026-09-28 (Fase 6)
- **O que foi feito:** Orçamento, avanço e previsão (Fase 6) concluída.
- **Áreas afetadas:**
  - `operations/services.py`: Camada de domínio puramente determinística para cálculo dos KPIs. Lida com divisão por zero.
  - `catalog/views.py`: Exposição dos KPIs via API REST através de uma `@action` de detalhe (`/api/projetos/<id>/kpis/`).
- **Métricas calculadas:** Avanço físico (%), Desvio de Custo (R$ e %), Ritmo de Execução (unidades/hora) e Previsão de horas finais com extrapolação.
- **Validações executadas:** Criados testes exaustivos (`AnalyticsServiceTestCase`) cobrindo ausência de apontamentos, projetos rodando no ritmo perfeito e projetos com estouro de custo e atraso. Suíte com 9 testes passando sem erros.

### 2026-09-28 (Fase 5)
- **O que foi feito:** Custos, auditoria e regras de domínio (Fase 5) concluída.
- **Áreas afetadas:**
  - `operations/models.py`: Implementado snapshot no método `save()` do model `Apontamento` para capturar e congelar o `custo_hora` do Colaborador. Adicionado o atributo de propriedade `@property` `custo_realizado`.
  - `operations/models.py` e `operations/serializers.py`: Adicionada validação rigorosa que bloqueia a edição de campos (`horas`, `data`, `projeto`, etc.) em Apontamentos cujo status já seja `APROVADO`.
- **Validações executadas:** Adicionados e passados os testes `test_snapshot_historico_imutabilidade` e `test_bloquear_edicao_apontamento_aprovado` em `operations/tests.py`. A suíte conta agora com 6 testes passando em 100%.

### 2026-09-28 (Fase 4)
- **O que foi feito:** API e Apontamento de Campo (Fase 4) concluída.
- **Áreas afetadas:**
  - `core/settings.py`: Configurada a paginação global com `PageNumberPagination` (tamanho 20).
  - `catalog/serializers.py` e `catalog/views.py`: Criados ViewSets do DRF para listar todo o catálogo usando *Eager Loading* (`select_related`) e permissão de leitura para os técnicos.
  - `operations/serializers.py` e `operations/views.py`: API de Apontamento criada. Injetada regra de negócio no `validate()` exigindo que a combinação `(Projeto, Equipamento, Atividade)` exista na tabela de vínculos. Eager loading aplicado com `select_related`.
  - `core/urls.py`: Adicionada as rotas usando o `DefaultRouter` do DRF para `clientes`, `projetos`, `equipamentos`, `atividades`, `colaboradores` e `apontamentos`.
- **Validações executadas:** Adicionado `test_combinacao_invalida_rejeitada` na suíte, validando que equipamentos não vinculados aos projetos são rejeitados de imediato. Todos os 4 testes da aplicação estão passando.

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
