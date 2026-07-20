# Mova estas duas linhas para o TOPO de tudo
from dotenv import load_dotenv
load_dotenv()

# Agora sim, os outros imports
import os
import zipfile
import pandas as pd
import gdown
from sqlalchemy import create_engine, text
import config 
print(f"Senha carregada: {'OK' if os.environ.get('MYSQL_PASSWORD') else 'VAZIA'}")


# Configuração do banco vinda do seu arquivo config.py
db = config.MYSQL_CONFIG
db_url = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}/{db['database']}"
engine = create_engine(db_url)

# Definições de arquivos
URL = 'https://drive.google.com/file/d/1R6re1574aCeqNfwJXQ_T7BwHCEsPfgvc/view?usp=drive_linkI'  # Mantenha o link caso precise no futuro
OUTPUT_ZIP = 'dados_2025.zip'
PASTA_EXTRACAO = 'data_raw'

def executar_fase_1():
    print("--- FASE 1: EXTRAÇÃO E CARGA RAW ---")
    try:
        # 1. DOWNLOAD (Respeita o requisito do projeto)
        if not os.path.exists(OUTPUT_ZIP):
            print("Arquivo não encontrado. Baixando do Drive...")
            gdown.download(URL, OUTPUT_ZIP, quiet=False)
        else:
            print("Arquivo .zip já encontrado localmente. Pulando download.")
        
        # 2. DESCOMPACTAR
        print("Descompactando arquivos...")
        with zipfile.ZipFile(OUTPUT_ZIP, 'r') as zip_ref:
            zip_ref.extractall(PASTA_EXTRACAO)
        
       # 3. CARGA NO BANCO (Idempotente + Resiliente)
        arquivos = {
            '2025_Viagem.csv': 'raw_viagem',
            '2025_Pagamento.csv': 'raw_pagamento',
            '2025_Passagem.csv': 'raw_passagem',
            '2025_Trecho.csv': 'raw_trecho'
        }# 3. CARGA NO BANCO (Idempotente + Resiliente)
        arquivos = {
            '2025_Viagem.csv': 'raw_viagem',
            '2025_Pagamento.csv': 'raw_pagamento',
            '2025_Passagem.csv': 'raw_passagem',
            '2025_Trecho.csv': 'raw_trecho'
        }
        # MAPEAMENTO DE COLUNAS: Garante que os nomes do CSV batam com o seu banco SQL
        colunas_sql = {
            'raw_viagem': [
                'id_viagem', 'num_proposta', 'situacao', 'viagem_urgente', 
                'justificativa', 'cod_orgao_superior', 'nome_orgao_superior', 
                'cod_orgao_solicitante', 'nome_orgao_solicitante', 'cpf_viajante', 
                'nome', 'cargo', 'funcao', 'descricao_funcao', 
                'data_inicio', 'data_fim', 'destinos', 'motivo', 
                'valor_diarias', 'valor_passagens', 'valor_devolucao', 'valor_outros_gastos'
            ],
            'raw_pagamento': [
               'id_viagem', 'num_proposta', 'cod_orgao_superior', 
                'nome_orgao_superior', 'cod_orgao_pagador', 'nome_orgao_pagador', 
                'cod_ug', 'nome_ug', 'tipo_pagamento', 'valor'
            ],
            'raw_passagem': [
                'id_viagem', 'num_proposta', 'meio_transporte', 
                'pais_origem_ida', 'uf_origem_ida', 'cidade_origem_ida', 
                'pais_destino_ida', 'uf_destino_ida', 'cidade_destino_ida', 
                'pais_origem_volta', 'uf_origem_volta', 'cidade_origem_volta', 
                'pais_destino_volta', 'uf_destino_volta', 'cidade_destino_volta', 
                'valor', 'taxa', 'data_emissao', 'hora_emissao'
            ],
            'raw_trecho': [
                'id_viagem', 'num_proposta', 'sequencia', 
                'origem_data', 'origem_pais', 'origem_uf', 'origem_cidade', 
                'destino_data', 'destino_pais', 'destino_uf', 'destino_cidade', 
                'meio_transporte', 'numero_diarias', 'missao'
            ]
        }

        for arquivo, tabela in arquivos.items():
            caminho_csv = os.path.join(PASTA_EXTRACAO, arquivo)
            
            if os.path.exists(caminho_csv):
                print(f"Processando {arquivo} para a tabela {tabela}...")
                
                # Idempotência: Limpa a tabela antes de carregar (agora usando text() por segurança)
                with engine.connect() as conn:
                    conn.execute(text(f"TRUNCATE TABLE {tabela}"))
                    conn.commit()
                
                # Resiliência: Leitura em blocos
                chunk_size = 10000
                
                # CORREÇÕES APLICADAS AQUI (latin-1, str, keep_default_na)
                for chunk in pd.read_csv(
                    caminho_csv, 
                    chunksize=chunk_size, 
                    sep=';', 
                    encoding='latin-1',
                    dtype=str,
                    keep_default_na=False
                ):
                    # Renomeia as colunas do CSV para os exatos nomes da sua tabela SQL
                    chunk.columns = colunas_sql[tabela]
                    
                    # Insere no banco
                    chunk.to_sql(tabela, con=engine, if_exists='append', index=False)
                
                print(f"Sucesso: {tabela} carregada.")
            else:
                print(f"Atenção: Arquivo {arquivo} não encontrado na pasta {PASTA_EXTRACAO}.")

    except Exception as e:
        print(f"ERRO CRÍTICO NA FASE 1: {e}")

if __name__ == "__main__":
    executar_fase_1()