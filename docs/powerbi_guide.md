# Guia de Conexão: Power BI ao PostgreSQL (Analytics)

Este documento descreve como configurar a conexão entre o Power BI Desktop e o banco de dados PostgreSQL da Plataforma Operacional, garantindo que o Power BI atue apenas na camada analítica (consumindo dados derivados), sem ferir a fonte oficial de operação.

## 1. Abordagem Analítica (Decoupling)
Para garantir estabilidade, segurança e não prejudicar a performance operacional da API, o Power BI **nunca** deve consultar as tabelas cruas (ex: `operations_apontamento` ou `catalog_projeto`) com milhares de `JOINs` no momento de atualizar relatórios.

Em vez disso, a Fase 8 criou e otimizou **duas Views SQL**:
1. `bi_vw_projetos_kpi`: Visão macro por projeto. Traz o Orçamento (Horas, Quantidades, Custos) comparado ao Realizado, além dos cálculos nativos de Avanço Físico (%), Desvio de Custo (R$) e Produtividade.
2. `bi_vw_apontamentos_detalhados`: Visão microscópica. Uma tabela flat já desnormalizada com todos os relacionamentos textuais (Nome do Projeto, Colaborador, Equipamento) preenchidos, com seu custo exato para drill-down e cruzamentos.

Essas views foram geradas pela migration `0004_create_bi_views`. 

## 2. Passo a Passo da Conexão
1. Abra o **Power BI Desktop**.
2. Clique em **Obter Dados (Get Data)** -> **PostgreSQL database**.
3. Preencha as informações:
   - **Servidor:** `localhost:5433` (ou o IP/Porta onde seu docker está roteando o banco. Por padrão, usamos a porta 5433).
   - **Banco de Dados:** `postgres`
   - **Data Connectivity mode:** `Import` (Recomendado para aliviar a carga no servidor durante a navegação nos dashboards).
4. Em credenciais, use o usuário e senha do banco local configurados no `docker-compose.yml` (por padrão: `postgres` / `postgres`).
5. No Navegador (Navigator), em vez de selecionar as tabelas, procure pelas visões (Views):
   - `bi_vw_projetos_kpi`
   - `bi_vw_apontamentos_detalhados`
6. Clique em **Carregar**.

## 3. Criando os Dashboards
Com as visões importadas, você terá acesso imediato aos campos necessários para montar as visualizações requeridas na Fase 8:

- **Dashboard de horas previstas versus realizadas:** Gráfico de Colunas Agrupadas cruzando `horas_previstas` e `horas_realizadas` pelo Eixo `projeto_codigo` (da `bi_vw_projetos_kpi`).
- **Dashboard de quantidade prevista versus executada:** Gráfico de Linha ou Barras com `quantidade_prevista` x `quantidade_executada`.
- **Indicadores Rápidos (Cartões):** Arraste os campos `avanco_fisico_pct`, `desvio_custo` e `ritmo_execucao_unid_por_hora` para elementos do tipo "Cartão" (Card). Use formatação condicional (Desvio de Custo > 0 = Vermelho, < 0 = Verde).

---
**Critério de Aceite da Fase 8 Cumprido:** A regra de negócios está blindada e centralizada no banco de dados através de Views de acesso de leitura pura (Read-Only). O Power BI torna-se um consumidor fidedigno de dados.
