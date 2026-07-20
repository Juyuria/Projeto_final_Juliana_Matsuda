# Projeto Pipeline de Dados de Transparência Pública

🎓 Contexto Acadêmico 
Projeto desenvolvido para o curso de **Tecnologia em Análise de Dados** do **SENAI - SCTEC**. Este repositório documenta a aplicação prática de engenharia de dados, modelagem de banco de dados e análise de informações estruturadas.

# 🎯 Objetivo do Projeto
Estruturar um pipeline de dados (ETL) para consumir, tratar e analisar despesas de viagens a serviço do Governo Federal. A solução transforma dados públicos brutos do Portal da Transparência em inteligência de negócio, permitindo a auditoria e o monitoramento eficiente de gastos institucionais.

## 🛠 Arquitetura de Dados
A solução foi implementada seguindo a arquitetura **Medallion**, garantindo a qualidade e governança da informação em três níveis:

*   **Camada Raw (Bronze):** Ingestão fiel dos dados brutos, preservando a fonte original para auditoria e rastreabilidade.
*   **Camada Silver:** Processamento, limpeza, tratamento de inconsistências e normalização (cálculo de `valor_total` e `duracao_dias`).
*   **Camada Gold:** Consolidação focada em tabelas agregadas e views analíticas, prontas para consumo e suporte à decisão.

## ⚙️ Tecnologias e Ferramentas
*   **Linguagens:** Python e SQL.
*   **Banco de Dados:** MySQL.
*   **Manipulação de Dados:** Pandas e SQLAlchemy.
*   **Visualização:** Matplotlib e Seaborn.
*   **Versionamento:** Git e GitHub.

# 🚀 Guia de Implementação

Para replicar este ambiente, execute os passos abaixo:

Clonar o repositório:
git clone URL_DO_REPOSITORIO.

1. **Requisitos:** Python 3.x, MySQL Server e as dependências listadas em `requirements.txt`.
2. **Setup:** Configure as variáveis de ambiente em um arquivo `.env`:
   ```env
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=sua_senha
   MYSQL_DATABASE=transparencia

   Pipeline (ETL):

Execute o schema: sql/0_criar_banco.sql

Extração: python 1_extrair.py

Transformação: python 2_transformar.py

Análise: Execute o notebook notebooks/3_analise.ipynb para visualizar os insights e gráficos.

## 📊 Resumo dos Indicadores (Resultados)

As análises realizadas na camada Gold e Silver permitiram identificar os seguintes indicadores chave:

1. **Top Órgão (Qtd Viagens)** → Ministério da Justiça (75.742)  
2. **Top Órgão (Custo Total - Gold)** → Ministério da Justiça (R$ 7,5 Bilhões)  
3. **Destino com Maior Custo Médio** → Abu Dabi/Riad (R$ 245.852,80)  
4. **Valor Médio por Pagamento** → Diárias (R$ 2.078,28)  
5. **Meio de Transporte mais usado** → Veículo Oficial (386.424)  
6. **UF de Destino mais frequente** → São Paulo (82.722 trechos)  
7. **Órgão com maior custo (Silver)** → Ministério da Justiça (R$ 486,9 Mi)  


# 🚀 Próximos Passos
Para a evolução da solução:

Automação: Orquestração de cargas incrementais.

Data Quality: Implementação de testes de integridade automática entre as camadas.

BI: Integração com dashboards interativos.

Projeto desenvolvido por Juliana Matsuda – Curso de Análise de Dados – SENAI/SCTEC.
