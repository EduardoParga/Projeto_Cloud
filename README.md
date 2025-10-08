☁️ Projeto Cloud

Repositório da disciplina de Projeto Cloud — Quarta-feira de manhã
Professor: Rafael
Alunos:

Eduardo Parga

Enzo Rafael

🚀 Projeto: Pipeline Cloud para Processamento de Cotações da B3

Este projeto demonstra como construir uma arquitetura completa em nuvem para coleta, transformação, armazenamento e análise de dados da B3 (Bolsa de Valores do Brasil), utilizando serviços do Microsoft Azure.

O objetivo é simular um ambiente de Big Data, aplicando práticas de ETL, computação serverless, banco de dados em nuvem e containers Docker, de forma automatizada, escalável e eficiente.

🎯 Objetivos

Compreender, na prática, a criação de pipelines de dados em ambiente cloud.

Aplicar integração entre diferentes serviços e processos automatizados.

Converter dados brutos em informações úteis para relatórios e análises.

📊 Contexto

A B3 divulga diariamente arquivos contendo informações de mercado (ativos, datas, preços de abertura e fechamento, volume negociado, entre outros).
Nosso desafio é automatizar a coleta, o tratamento e o armazenamento desses dados, preparando-os para análises e dashboards em ferramentas como o Power BI.

🏗️ Arquitetura da Solução

Azure Storage Account: armazenamento dos arquivos originais e processados.

Azure Data Factory: responsável pelo fluxo ETL (extração, transformação e carga).

Azure Function: faz a inserção incremental dos dados no banco de dados.

Azure SQL Database: guarda as informações já tratadas e normalizadas.

Logic Apps: automatiza alertas e integrações entre os serviços.

Docker + Azure Container Instance: simula o envio de arquivos para o ambiente cloud.

🔄 Fluxo do Pipeline

Ingestão: container Docker envia os arquivos para o Azure Blob Storage.

Transformação: o Data Factory executa o processo de limpeza e formatação.

Carga: Azure Function insere os dados no banco de forma incremental.

Automação: Logic Apps envia notificações e aciona fluxos automáticos.

Visualização: dados disponíveis para dashboards e relatórios.

📦 Conteúdo do Repositório

Documento com o desenho da arquitetura e o fluxo completo do projeto.

Pipeline configurado no Azure Data Factory.

Função Python para carga e atualização de dados.

Container Docker para ingestão simulada dos arquivos da B3.

Exemplo de Logic App para automação e notificações.

🔗 Referências Úteis (B3)

Cotações Históricas – Mercado à Vista

Boletim Diário do Mercado

Layout dos Arquivos da B3

⚙️ Como Executar

1. Clonar o repositório:

git clone <URL_DO_REPOSITORIO>


2. Instalar dependências:

pip install -r requirements.txt


3. Executar o pipeline:

python extract.py
