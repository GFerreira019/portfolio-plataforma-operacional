-- Views SQL Otimizadas para Power BI (Analytics & BI)
-- Essas consultas foram planejadas para fornecer os indicadores de Horas, Quantidades, Custos, Produtividade e Previsão.
-- Execute este script no banco de dados do PostgreSQL.

CREATE OR REPLACE VIEW bi_vw_projetos_kpi AS
SELECT 
    p.id AS projeto_id,
    p.codigo AS projeto_codigo,
    p.ativo AS projeto_ativo,
    c.nome AS cliente_nome,
    
    -- Orcamento (Previsto)
    COALESCE(o.horas_previstas, 0) AS horas_previstas,
    COALESCE(o.quantidade_prevista, 0) AS quantidade_prevista,
    COALESCE(o.custo_previsto, 0) AS custo_previsto,
    o.prazo_previsto,
    
    -- Apontamentos (Realizado - Apenas status APROVADO se desejarmos apenas o consolidado, mas aqui usamos tudo não REJEITADO)
    COALESCE(SUM(a.horas) FILTER (WHERE a.status IN ('APROVADO', 'EM_ANALISE')), 0) AS horas_realizadas,
    COALESCE(SUM(a.quantidade) FILTER (WHERE a.status IN ('APROVADO', 'EM_ANALISE')), 0) AS quantidade_executada,
    COALESCE(SUM(a.horas * a.custo_hora) FILTER (WHERE a.status IN ('APROVADO', 'EM_ANALISE')), 0) AS custo_realizado,
    
    -- KPI: Avanço Físico %
    CASE 
        WHEN COALESCE(o.quantidade_prevista, 0) > 0 THEN 
            ROUND((COALESCE(SUM(a.quantidade) FILTER (WHERE a.status IN ('APROVADO', 'EM_ANALISE')), 0) / o.quantidade_prevista) * 100, 2)
        ELSE 0 
    END AS avanco_fisico_pct,
    
    -- KPI: Desvio de Custo (Positivo = Acima do orçado, Negativo = Economia)
    COALESCE(SUM(a.horas * a.custo_hora) FILTER (WHERE a.status IN ('APROVADO', 'EM_ANALISE')), 0) - COALESCE(o.custo_previsto, 0) AS desvio_custo,
    
    -- KPI: Ritmo / Produtividade (Unidades executadas por hora de trabalho)
    CASE 
        WHEN COALESCE(SUM(a.horas) FILTER (WHERE a.status IN ('APROVADO', 'EM_ANALISE')), 0) > 0 THEN 
            ROUND(COALESCE(SUM(a.quantidade) FILTER (WHERE a.status IN ('APROVADO', 'EM_ANALISE')), 0) / COALESCE(SUM(a.horas) FILTER (WHERE a.status IN ('APROVADO', 'EM_ANALISE')), 0), 4)
        ELSE 0 
    END AS ritmo_execucao_unid_por_hora

FROM catalog_projeto p
LEFT JOIN catalog_cliente c ON p.cliente_id = c.id
LEFT JOIN catalog_orcamento o ON p.id = o.projeto_id
LEFT JOIN operations_apontamento a ON p.id = a.projeto_id
GROUP BY p.id, p.codigo, p.ativo, c.nome, o.horas_previstas, o.quantidade_prevista, o.custo_previsto, o.prazo_previsto;


CREATE OR REPLACE VIEW bi_vw_apontamentos_detalhados AS
SELECT 
    a.id AS apontamento_id,
    a.data AS data_apontamento,
    a.horas,
    a.quantidade,
    a.custo_hora,
    (a.horas * a.custo_hora) AS custo_total,
    a.status,
    
    -- Relacionamentos
    p.codigo AS projeto_codigo,
    c.nome AS colaborador_nome,
    e.nome AS equipamento_nome,
    atv.nome AS atividade_nome
    
FROM operations_apontamento a
INNER JOIN catalog_projeto p ON a.projeto_id = p.id
INNER JOIN catalog_colaborador c ON a.colaborador_id = c.id
INNER JOIN catalog_equipamento e ON a.equipamento_id = e.id
INNER JOIN catalog_atividade atv ON a.atividade_id = atv.id;
