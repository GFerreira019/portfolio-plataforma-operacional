# Plano de Implementação

> Lista operacional alinhada ao contexto definido em [Architecture.md](Architecture.md).
> Marque uma tarefa como concluída somente quando o código, os testes e a documentação
> necessários estiverem atualizados.

## Como usar esta lista

- Execute as fases na ordem indicada, salvo decisão documentada.
- Antes de alterar código existente, identifique se ele pertence ao legado Laravel,
  à aplicação Python atual ou à futura migração Django.
- Não implemente itens fora do escopo simplificado sem uma necessidade explícita.
- Para cada tarefa, registre decisões de schema, compatibilidade ou migração quando
  elas afetarem dados existentes.

## Fase 0: Direcionamento e baseline

- [x] Confirmar o módulo-alvo da tarefa: legado Laravel, `python_app` ou arquitetura Django.
- [x] Registrar no README ou na documentação qual parte já existe e qual parte ainda é arquitetura-alvo.
- [x] Definir o ambiente local reproduzível com Python 3.12+, Django, DRF e PostgreSQL.
- [x] Confirmar como os testes serão executados no ambiente local e no CI.
- [x] Criar ou atualizar o `.env.example` sem incluir credenciais reais.
- [x] Garantir que o Git ignore segredos, arquivos temporários, bancos locais e artefatos de build.
- [x] Criar e manter o `CHANGELOG.md` como histórico cronológico das implementações.

## Fase 1: Infraestrutura e aplicação base

- [x] Configurar o projeto Django e o Django REST Framework.
- [x] Configurar conexão com PostgreSQL por variáveis de ambiente.
- [x] Criar o `docker-compose.yml` para aplicação e banco, quando o ambiente exigir containers.
- [x] Configurar migrations e uma rotina inicial de verificação do schema.
- [x] Configurar execução de testes, lint e formatação no projeto.
- [x] Documentar comandos de instalação, execução, testes e migrações.

## Fase 2: Modelo relacional e catálogo

- [x] Modelar `Cliente`.
- [x] Modelar `Projeto` com `UniqueConstraint` (Cliente + Código) para evitar duplicidades.
- [x] Aplicar virtualização (ex: `@property` para herdar Nome do Cliente no Projeto) mantendo integridade.
- [x] Modelar `Equipamento` e a relação `ProjetoEquipamento`.
- [x] Modelar `Atividade` e a relação `ProjetoEquipamentoAtividade`.
- [x] Modelar `Orcamento` com horas, quantidades, custos e prazo previstos.
- [x] Modelar `Colaborador` e seu custo-hora vigente.
- [x] Modelar `Apontamento` com projeto, equipamento, atividade, colaborador, data, horas e quantidade.
- [x] Adicionar status do apontamento (`EM_ANÁLISE`, `APROVADO`, `REJEITADO`) no modelo.
- [x] Adicionar campos de auditoria necessários, como data de criação e usuário responsável.
- [x] Criar migrations versionadas e testar em banco vazio. (Pendente apenas o apply final do migrate no Docker)

## Fase 3: Autenticação e permissões

- [x] Configurar a autenticação nativa do Django (dispensando a arquitetura SSO legada).
- [x] Criar o papel **Técnico de Campo** (acesso estrito a lançamentos e edições próprias).
- [x] Criar o papel **Planejador/Analista** (visão global, gestão de catálogo).
- [x] Implementar Row Level Security (RLS) nas listagens: Técnico só enxerga seus apontamentos.
- [x] Implementar regra de Anti-Autoaprovação na visualização de pendências do Planejador.
- [x] Aplicar proteção IDOR (Insecure Direct Object Reference) nas Views/APIs.
- [x] Forçar que o colaborador do apontamento seja sempre o usuário autenticado, prevenindo bypass via API.
- [x] Criar testes garantindo acesso negado em edições alheias.

## Fase 4: API e apontamento de campo

- [x] Criar endpoints base do DRF para listagem e criação.
- [x] Validar no backend a combinação projeto, equipamento e atividade.
- [x] Configurar Paginação (ex: `PageNumberPagination`) em views de grande volume.
- [x] Aplicar Eager Loading (`select_related`, `prefetch_related`) para prevenir N+1 queries herdando boa prática do legado.
- [x] Criar testes de API para validação de serializers e sanitização.

## Fase 5: Custos, auditoria e regras de domínio

- [x] Implementar Snapshot Histórico: Salvar o custo-hora e nível do colaborador no momento do apontamento (via Model `save()` ou Signals).
- [x] Calcular o custo realizado a partir deste snapshot imutável.
- [x] Isolar as regras de mudança de Status (`EM_ANÁLISE`, `APROVADO`, `REJEITADO`).
- [x] Bloquear edição de apontamentos se o Status for `APROVADO`.
- [x] Criar testes de auditoria e imutabilidade de custos históricos frente a promoções de colaboradores.

## Fase 6: Orçamento, avanço e previsão

- [x] Criar a comparação entre horas previstas e horas apontadas.
- [x] Criar a comparação entre quantidade prevista e quantidade realizada.
- [x] Calcular custo previsto, custo realizado e desvio de custo.
- [x] Calcular avanço físico com base na quantidade planejada e executada.
- [x] Definir e documentar a fórmula do ritmo de execução observado.
- [x] Calcular o desvio de prazo e a data prevista de término.
- [x] Isolar os cálculos em serviços Python determinísticos e independentes da interface.
- [x] Criar testes unitários para casos normais, ausência de dados, divisão por zero, excesso de execução e atraso.
- [x] Validar os resultados com um conjunto pequeno de dados de referência.

## Fase 7: Frontend operacional

- [ ] Definir a aplicação React e a integração com a API Django.
- [ ] Implementar formulário principal (Seleção em cascata + Apontamento).
- [ ] Aplicar bloqueio no frontend de edições indesejadas forçando envio seguro.
- [ ] Criar painel do Planejador implementando a regra de fila de Anti-Autoaprovação na UI.
- [ ] Implementar paginação transparente na leitura de apontamentos e orçamentos.
- [ ] Testar fluxo mobile, carregamento vazio e sucesso.

## Fase 8: CPQ, indicadores e BI

- [ ] Definir o menor fluxo de orçamentação que entregue valor ao projeto.
- [ ] Permitir ao planejador selecionar equipamentos e atividades válidos para um projeto.
- [ ] Consolidar horas, quantidades, custos e prazo do orçamento.
- [ ] Criar views ou consultas estáveis para indicadores operacionais e analíticos.
- [ ] Conectar o PostgreSQL ao Power BI usando as views documentadas.
- [ ] Criar dashboard de horas previstas versus realizadas.
- [ ] Criar dashboard de quantidade prevista versus executada.
- [ ] Criar indicadores de custo, produtividade, desvio e previsão de término.
- [ ] Confirmar que o Power BI consome dados derivados sem se tornar a fonte oficial de operação.

## Fase 9: Qualidade, segurança e performance

- [ ] Executar a suíte de testes após cada alteração de schema ou regra de domínio.
- [ ] Verificar autorização nos endpoints e proteção contra IDOR.
- [ ] Verificar validação de payloads, mensagens de erro e limites numéricos.
- [ ] Medir consultas críticas e corrigir N+1 queries sem aplicar eager loading indiscriminadamente.
- [ ] Adicionar dados de teste representativos para projeto, catálogo, apontamentos e orçamento.
- [ ] Verificar logs, tratamento de exceções e ausência de segredos nos registros.
- [ ] Revisar migrations, índices, constraints e estratégia de backup antes do deploy.
- [ ] Atualizar o `CHANGELOG.md` com o que foi implementado, arquivos afetados e validações executadas.

## Fase 10: Deploy e documentação

- [ ] Finalizar imagens Docker reproduzíveis para os serviços necessários.
- [ ] Definir variáveis de ambiente e configuração de produção.
- [ ] Executar migrations de forma controlada no ambiente de deploy.
- [ ] Publicar a aplicação em AWS, GCP ou Azure, conforme a infraestrutura escolhida.
- [ ] Configurar observabilidade mínima: logs, health check e alertas básicos.
- [ ] Documentar arquitetura, modelo de dados, APIs, cálculos e limitações conhecidas.
- [ ] Atualizar o README com instruções de execução local e demonstração do fluxo principal.
- [ ] Organizar o repositório para apresentação pública sem expor credenciais ou dados reais.
- [ ] Confirmar que a entrega final possui uma entrada no `CHANGELOG.md` em ordem cronológica reversa.

## Critério final de conclusão

- [ ] Um técnico consegue registrar um apontamento válido pela interface.
- [ ] O backend rejeita projeto, equipamento e atividade incompatíveis.
- [ ] O custo-hora fica congelado no apontamento e permanece auditável.
- [ ] Um planejador consegue comparar previsto versus realizado.
- [ ] O sistema calcula avanço, desvios e previsão de término com testes automatizados.
- [ ] Os indicadores podem ser consumidos pelo Power BI.
- [ ] A documentação permite executar o projeto e entender suas limitações.
