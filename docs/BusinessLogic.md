# Lógica de Negócio e Fluxos Validados (Adaptação para Django)

Este documento consolida as regras de negócio extraídas da versão legada (Laravel) e as adapta para a **arquitetura-alvo em Django**. O objetivo é aproveitar a inteligência de fluxos já validados em produção (prevenção de duplicidades, rastreabilidade, controle de acesso) descartando lógicas que fogem do escopo do portfólio (como SSO e rotinas trabalhistas de plantão).

---

## 1. Controle de Acesso, Visibilidade e Segurança (RLS e IDOR)

Em vez do modelo complexo de 5 perfis e SSO do legado, o sistema foca em dois perfis principais, mas mantém o rigor na segurança e visibilidade de dados:

* **Técnico de Campo (Operacional):**
  * **Visibilidade (Row Level Security - RLS):** Enxerga estritamente os seus próprios apontamentos e os dados básicos para preenchimento.
  * **IDOR Protection (Prevenção de Edição Assimétrica):** A API restringe edições/exclusões apenas a registros pertencentes ao usuário autenticado (`request.user`). O backend injeta silenciosamente o ID do usuário autenticado no momento do apontamento, ignorando tentativas de enviar IDs de terceiros via payload.
* **Planejador / Analista (Gerencial):**
  * **Visibilidade:** Visão global dos projetos, orçamentos e apontamentos.
  * **Prevenção de Autoaprovação (Anti-Self-Approval):** Caso o Analista registre apontamentos para si mesmo, ele é impedido de aprovar suas próprias horas (estes registros não aparecem na sua fila de pendências de aprovação).

---

## 2. Catálogo e Integridade de Dados (Obras e Clientes)

Para alinhar com a proposta simplificada do portfólio, a modelagem de dados descarta a complexidade de Unidades, CNPJ e Razão Social, mantendo apenas a amarração essencial:

* **Unique Constraints (Banco e API):** O uso de Chaves Únicas Compostas é restrito ao núcleo da entidade (ex: Cliente + Código do Projeto). Se essa exata combinação tentar ser salva, o banco deve rejeitar para evitar duplicidades silenciosas.
* **Virtualização de Campos:** Propriedades redundantes (ex: o nome do projeto ser idêntico ao do cliente) podem ser virtualizadas via `@property` nos Models do Django, garantindo integridade sem duplicação no banco.

---

## 3. Fluxo de Apontamentos (Core)

O apontamento de horas é a Fonte da Verdade e adota regras rígidas de imutabilidade histórica.

* **Congelamento de Custo (Snapshot Histórico):** A regra mais valiosa do legado. Ao criar ou editar um apontamento, o sistema copia o custo-hora e o cargo vigente do colaborador naquele exato milissegundo e salva no registro. 
  * *Implementação no Django:* Pode ser feito sobrescrevendo o método `save()` do Model ou utilizando `Signals`. Se o colaborador receber aumento de salário amanhã, o custo da obra de hoje não será inflacionado.
* **Ciclo de Vida (Status de Aprovação):**
  * Um apontamento nasce com status `EM_ANALISE`.
  * Pode ser `APROVADO` (faturado) ou `REJEITADO` pelo Planejador.
  * Edições constantes do Técnico podem ser permitidas até o limite de bloqueio (se configurado), passando o apontamento para aprovação pendente.
* **Rateio e Plantão (Simplificados):** Conforme definido em `Architecture.md`, o rateio complexo (fracionamento de horas) e as lógicas de virada de madrugada/plantões são descartadas no Django para manter o foco analítico da ferramenta.

---

## 4. Performance e Prevenção de Gargalos (N+1 Queries)

Dado o volume gerado por timesheets, a performance de listagem é tratada preventivamente:

* **Eager Loading Intencional:** As listagens da API (DRF) devem obrigar o uso de `select_related()` (para Foreign Keys) e `prefetch_related()` (para Many-to-Many). 
* **Paginação Obrigatória:** As views legadas não usam `->get()`. No Django, configuramos a paginação padrão no DRF (`PageNumberPagination` ou `LimitOffsetPagination`) para evitar crashes de memória.
* **Índices de Banco:** O cruzamento de relatórios exige a configuração de índices compostos (via `class Meta: indexes = [...]`) nas tabelas, principalmente associando o colaborador e a data do apontamento.
