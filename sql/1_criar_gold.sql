-- 1. Remove as estruturas antigas se existirem
DROP VIEW IF EXISTS vw_gold_resumo_viagens;
DROP TABLE IF EXISTS gold_resumo_viagens;

-- 2. Cria a Tabela Gold (Usando LEFT JOIN para não perder dados e somando da própria tabela viagem)
CREATE TABLE gold_resumo_viagens AS
SELECT 
    v.nome_orgao_superior,
    COUNT(DISTINCT v.id_viagem) AS quantidade_viagens,
    SUM(v.valor_total) AS custo_total
FROM silver_viagem v
LEFT JOIN silver_pagamento p 
    ON v.id_viagem = p.id_viagem
GROUP BY 
    v.nome_orgao_superior;

-- 3. Cria a View baseada na tabela
CREATE VIEW vw_gold_resumo_viagens AS
SELECT * FROM gold_resumo_viagens;