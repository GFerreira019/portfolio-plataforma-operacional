# Arquitetura e Contexto do Sistema

## 1. Objetivo do Projeto
Este arquivo é a fonte oficial de contexto para a IDE de vibe coding e para qualquer desenvolvedor envolvido no projeto.
O sistema é uma **plataforma operacional interna** para gestão de obras, apontamentos de campo, orçamentação e análise de desempenho.
O objetivo principal é demonstrar, em formato de portfólio técnico, a capacidade de transformar dados operacionais em inteligência de negócio.

O fluxo central consiste em:
1. Técnico de campo registra apontamentos (horas e quantidades).
2. O sistema amarra esse apontamento ao contexto exato (Projeto, Equipamento, Atividade).
3. O backend congela os custos (snapshot) no momento do registro.
4. O Planejador compara o planejado com o executado.
5. O sistema provê dados consolidados para dashboards e cálculos dinâmicos de desvios.

## 2. Arquitetura-alvo
O repositório originalmente continha código legado em PHP/Laravel. A arquitetura definitiva (*target*) agora reside em `python_app` e obedece à seguinte stack:

| Camada | Tecnologia | Diretriz |
| --- | --- | --- |
| Linguagem principal | Python 3.12+ | Backend web, regras de negócio e análises compartilham o mesmo ecossistema. |
| Backend e API | Django + DRF | O Django ORM cuida do domínio; o Django REST Framework fornece os contratos HTTP. |
| Banco de dados | PostgreSQL | Modelagem relacional estrita (chaves estrangeiras, `UniqueConstraints`, restrições lógicas). |
| Frontend | React | SPA que consome a API do Django, operando de forma isolada. |
| Analytics e BI | Pandas / Power BI | O backend pode usar Pandas para consolidações complexas; o BI consome views do banco. |
| Infraestrutura | Docker | Execução conteinerizada via `docker-compose.yml`. |

## 3. Escopo Funcional
### 3.1 Cadastros Base e Catálogo
- Projetos e Clientes (com relação simplificada).
- Equipamentos vinculados a projetos.
- Atividades permitidas por equipamento.
- Orçamentos (previsto: horas, quantidade, prazo e custo).
- Colaboradores (incluindo o seu custo-hora financeiro atual).

### 3.2 Apontamento de Campo
O apontamento diário é a *Fonte da Verdade*. Ele armazena o que ocorreu em campo:
- **Relacionamentos Restritos:** Todo apontamento exige vínculo com Projeto, Equipamento, Atividade e Colaborador.
- **Valores:** Quantidade executada e horas gastas.
- **Auditoria:** O backend salva metadados de criação e quem foi o autor.

### 3.3 Orçamentação e Análise
Visão voltada à gestão: comparar previsto *vs* realizado. Visualizar o custo acumulado, o desvio de produtividade, calcular o avanço físico e projetar a data de término.

## 4. Modelo de Dados Conceitual
O banco de dados separa entidades estáticas (Catálogo) de entidades dinâmicas (Operação).
* **Catálogo:** `Cliente`, `Projeto`, `Equipamento`, `Atividade`, `ProjetoEquipamentoAtividade` (onde ficam as premissas previstas), `Colaborador`.
* **Operação (Transacional):** `Apontamento`. 
* **Regra de Integridade:** Evita-se a duplicação no banco por meio de `UniqueConstraint` (ex: `Cliente + Codigo do Projeto`).

## 5. Regras de Negócio Essenciais
### 5.1 Congelamento do Custo-Hora (Snapshot)
É terminantemente proibido recalcular apontamentos históricos com base em aumentos salariais futuros. 
Ao criar um `Apontamento`, o backend DEVE copiar o `custo_hora` atual do `Colaborador` e fixá-lo na linha do apontamento. Essa regra é o coração da estabilidade financeira do sistema e deve ser protegida transacionalmente (ex: sobrescrita do método `save()` ou via `Signals`).

### 5.2 Validação de Relações
Um apontamento não pode receber IDs arbitrários. O backend validará se a `Atividade` enviada pertence àquele `Equipamento`, e se o `Equipamento` pertence àquele `Projeto`. Se o Payload for inconsistente, a API retornará falha, mesmo que a UI tente enviar os dados.

### 5.3 Cálculo de Avanço e Prazo
O motor calculará dinamicamente a relação de performance cruzando o avanço físico (quantidade realizada / quantidade prevista) contra o prazo consumido, gerando projeções de término.

## 6. Usuários, Papéis e Permissões
A aplicação descarta modelos legados de SSO e adota a Autenticação Nativa Django com 2 papéis claros (Role-Based Access Control):
1. **Técnico de Campo:** Acesso restrito (RLS). Lança apontamentos apenas no seu próprio nome. Pode editar os próprios lançamentos enquanto permitidos.
2. **Planejador / Analista:** Visão global de gestão. Edita catálogos e orçamentos. Aprova/Reprova apontamentos (obedecendo à regra de *Anti-Autoaprovação*: não pode aprovar um apontamento em que ele mesmo é o executante).

A segurança é back-end first. Ocultar botões no React não exime a API de validar a autorização da ação via DRF Permissions/Policies.

## 7. Limites do Escopo (O que NÃO implementar)
Para garantir foco total no portfólio sem introduzir ruídos legados, **não faça**:
- Isolamento multi-tenant (`tenant_id`).
- Integrações de provisionamento (JIT) ou SSO com ERP.
- Mapeamentos complexos de Razão Social/CNPJ e filiais (basta usar Código).
- Regras trabalhistas noturnas (plantão, 17h às 07:30h, regras CLT específicas).
- Rateio fracionado de apontamentos múltiplos.

## 8. Diretrizes de Implementação para a IDE
Ao criar ou alterar código, você deve:
1. **Atuar na camada correta:** Regras de negócio moram no backend (Models/Services), não apenas no React ou nas Views do banco.
2. **Performance e Integridade:** Prevenir *N+1 queries* através de `select_related` e `prefetch_related`. Implementar paginação por padrão.
3. **Testabilidade:** Garantir que o congelamento de custo e as restrições de catálogo estejam cobertos por testes unitários e de integração (`pytest-django` / `manage.py test`).
4. **Respeitar os Contratos:** Devolver mensagens de erro estruturadas e previsíveis do DRF.

## 9. Uso Obrigatório do CHANGELOG.md
Toda alteração de arquitetura, conclusão de uma feature ou refatoração estrutural DEVE ser registrada no arquivo `CHANGELOG.md`. 
O registro deve ser inserido de forma decrescente (mais recente no topo) e conter:
- Resumo objetivo.
- Arquivos ou áreas afetadas.
- Testes / validações executadas.

## 10. Prioridade de Desenvolvimento (Fases)
Salvo instrução do usuário, siga esta cadência:
1. Modelo Relacional e Catálogo (Fase 2).
2. Autenticação, Papéis e Permissões (Fase 3).
3. API Rest e Lógica de Apontamentos com Snapshot (Fases 4 e 5).
4. Orçamentação, BI e Visões Analíticas (Fases 6 e 8).
5. Frontend React (Fase 7).
6. Qualidade, Testes e Deploy (Fases 9 e 10).

## 11. Critério de Pronto
Uma tarefa da lista operacional só é considerada entregue se:
- O banco barra inconsistências;
- Os cálculos são determinísticos e auditáveis;
- A API restringe visualização cruzada quando aplicável;
- Está acompanhada de testes;
- A alteração foi declarada no CHANGELOG.