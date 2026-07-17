import banco

# Esvaziar tabelas Silver antes de carregar
LIMPAR_SILVER = [
    "DELETE FROM silver_trecho",
    "DELETE FROM silver_passagem",
    "DELETE FROM silver_pagamento",
    "DELETE FROM silver_viagem",
]

# 1. Transformação VIAGEM
SQL_VIAGEM = """
INSERT INTO silver_viagem (
    id_viagem, num_proposta, situacao, viagem_urgente, cod_orgao_superior, 
    nome_orgao_superior, nome_viajante, cargo, data_inicio, data_fim, 
    destinos, motivo, valor_diarias, valor_passagens, valor_devolucao, valor_outros_gastos
)
SELECT 
    id_viagem, num_proposta, situacao, viagem_urgente, 
    cod_orgao_superior, nome_orgao_superior, nome, cargo, 
    STR_TO_DATE(NULLIF(TRIM(data_inicio), ''), '%d/%m/%Y'),
    STR_TO_DATE(NULLIF(TRIM(data_fim), ''), '%d/%m/%Y'),
    destinos, motivo,
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_diarias), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_passagens), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_devolucao), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_outros_gastos), ''), '.', ''), ',', '.') AS DECIMAL(10,2))
FROM raw_viagem;
"""

# 2. Transformação PAGAMENTO
SQL_PAGAMENTO = """
INSERT INTO silver_pagamento (
    id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora, tipo_pagamento, valor
)
SELECT 
    identificadorProcessoViagem, numeroPropostaPcdp, nomeOrgaoPagador, 
    nomeUnidadeGestoraPagadora, tipoPagamento,
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor), ''), '.', ''), ',', '.') AS DECIMAL(10,2))
FROM raw_pagamento;
"""

# 3. Transformação PASSAGEM (Removida a data_emissao, pois não existe na silver)
SQL_PASSAGEM = """
INSERT INTO silver_passagem (
    id_viagem, meio_transporte, pais_origem_ida, uf_origem_ida, cidade_origem_ida, 
    pais_destino_ida, uf_destino_ida, cidade_destino_ida, valor_passagem, taxa_servico
)
SELECT 
    id_viagem, meio_transporte, pais_origem_ida, uf_origem_ida, 
    cidade_origem_ida, pais_destino_ida, uf_destino_ida, cidade_destino_ida,
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(taxa), ''), '.', ''), ',', '.') AS DECIMAL(10,2))
FROM raw_passagem;
"""

# 4. Transformação TRECHO
SQL_TRECHO = """
INSERT INTO silver_trecho (
    id_viagem, sequencia_trecho, origem_data, origem_uf, origem_cidade, 
    destino_data, destino_uf, destino_cidade, meio_transporte, numero_diarias
)
SELECT 
    id_viagem, 
    CAST(NULLIF(TRIM(sequencia), '') AS UNSIGNED),
    STR_TO_DATE(NULLIF(TRIM(origem_data), ''), '%d/%m/%Y'),
    origem_uf, origem_cidade,
    STR_TO_DATE(NULLIF(TRIM(destino_data), ''), '%d/%m/%Y'),
    destino_uf, destino_cidade, meio_transporte,
    CAST(REPLACE(REPLACE(NULLIF(TRIM(numero_diarias), ''), '.', ''), ',', '.') AS DECIMAL(10,2))
FROM raw_trecho;
"""

# 5. Cálculo Final
SQL_CALC_VIAGEM = """
UPDATE silver_viagem
SET 
    valor_total = COALESCE(valor_diarias, 0) + COALESCE(valor_passagens, 0) + COALESCE(valor_outros_gastos, 0) - COALESCE(valor_devolucao, 0),
    duracao_dias = DATEDIFF(data_fim, data_inicio);
"""

def main():
    print("=== FASE 2: TRANSFORMACAO + CAMADA SILVER ===")
    try:
        conexao = banco.conectar()
        
        print("[1/3] Esvaziando tabelas SILVER...")
        for comando in LIMPAR_SILVER:
            banco.executar(conexao, comando)
            
        print("[2/3] Copiando e convertendo RAW -> SILVER...")
        banco.executar(conexao, SQL_VIAGEM)
        banco.executar(conexao, SQL_PAGAMENTO)
        banco.executar(conexao, SQL_PASSAGEM)
        banco.executar(conexao, SQL_TRECHO)
        
        print("[3/3] Calculando valor_total e duracao_dias...")
        banco.executar(conexao, SQL_CALC_VIAGEM)
        
        conexao.commit()
        conexao.close()
        print("=== Camada SILVER concluída com sucesso! ===")
    except Exception as erro:
        print("[ERRO] Algo deu errado:", erro)

if __name__ == "__main__":
    main()