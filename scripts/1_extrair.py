import os
import zipfile
import pandas as pd
import gdown
from sqlalchemy import create_engine
import config

# Configuração do banco vinda do seu arquivo config.py
db = config.MYSQL_CONFIG
db_url = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}/{db['database']}"
engine = create_engine(db_url)

# Definições de arquivos
URL = 'SEU_LINK_DO_DRIVE_AQUI'  # Mantenha o link caso precise no futuro
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
            'viagem.csv': 'raw_viagem',
            'pagamento.csv': 'raw_pagamento',
            'passagem.csv': 'raw_passagem',
            'trecho.csv': 'raw_trecho'
        }

        for arquivo, tabela in arquivos.items():
            caminho_csv = os.path.join(PASTA_EXTRACAO, arquivo)
            
            if os.path.exists(caminho_csv):
                print(f"Processando {arquivo} para a tabela {tabela}...")
                
                # Idempotência: Limpa a tabela antes de carregar
                with engine.connect() as conn:
                    conn.execute(f"TRUNCATE TABLE {tabela}")
                    conn.commit()
                
                # Resiliência: Leitura em blocos
                chunk_size = 10000
                for chunk in pd.read_csv(caminho_csv, chunksize=chunk_size, sep=';', encoding='utf-8'):
                    chunk.to_sql(tabela, con=engine, if_exists='append', index=False)
                
                print(f"Sucesso: {tabela} carregada.")
            else:
                print(f"Atenção: Arquivo {arquivo} não encontrado na pasta {PASTA_EXTRACAO}.")

    except Exception as e:
        print(f"ERRO CRÍTICO NA FASE 1: {e}")

if __name__ == "__main__":
    executar_fase_1()