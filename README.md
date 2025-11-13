<<<<<<< HEAD
# Projeto Cloud
## Repositorio para a materia de Projeto Cloud, quarta manha -> Prof. Rafael
#### Alunos: 
    - João Gabriel Tasca
    - Ewerton
    - Miguel Veiga


🚀 Projeto: Pipeline Cloud para Análise de Cotações da B3

Este projeto mostra como montar uma arquitetura em nuvem para coletar, transformar, armazenar e analisar dados da B3 (Bolsa de Valores do Brasil) usando serviços da Microsoft Azure.

A ideia é simular um cenário real de Big Data, trabalhando com ETL, Serverless, Banco de Dados Cloud e Containers Docker, de forma automatizada e escalável.

🎯 Objetivo

Ensinar, na prática, como criar pipelines de dados na nuvem.

Trabalhar com conceitos de integração de serviços, automação e análise em larga escala.

Transformar dados brutos em informações úteis para relatórios e dashboards.

📊 Contexto

A B3 disponibiliza diariamente arquivos com as cotações do pregão (ativo, data, abertura, fechamento, volume, etc).
O desafio aqui é pegar esses dados, processá-los automaticamente e deixá-los prontos para análise em dashboards.

🏗️ Arquitetura Utilizada

Azure Storage Account → guarda os arquivos originais e processados.

Azure Data Factory → faz o ETL (extração, transformação e carga).

Azure Function → insere os dados de forma incremental no banco.

Azure SQL Database → armazena as informações já tratadas.

Logic Apps → envia notificações e integrações automáticas.

Docker + Azure Container Instance → simula a ingestão dos arquivos da B3.

🔄 Fluxo do Projeto

Ingestão de dados → Docker envia arquivos para o Azure Blob Storage.

Transformação → Data Factory processa os dados.

Carga → Azure Function insere no banco.

Automação → Logic Apps dispara alertas e integrações.

Visualização → dados prontos para dashboards no Power BI ou Synapse Analytics.

📦 O que você encontra aqui

Documento com a arquitetura e o fluxo do projeto.

Pipeline pronto no Data Factory.

Função em Python para carga dos dados.

Container Docker de exemplo para ingestão.

Exemplo de Logic App para notificações.

🔗 Links Úteis da B3

- [Cotações históricas – Mercado à vista](https://www.b3.com.br/pt_br/market-data-eindices/servicos-de-dados/market-data/historico/mercado-a-vista/cotacoes-historicas/)
- [Pesquisa por pregão – Boletim Diário do Mercado](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/marketdata/historico/boletins-diarios/pesquisa-por-pregao/pesquisa-por-pregao/)
- [Layout dos arquivos – Pesquisa por pregão](https://www.b3.com.br/pt_br/market-datae-indices/servicos-de-dados/market-data/historico/boletins-diarios/pesquisa-porpregao/layout-dos-arquivos/)

## Como executar

1. Clonar o repositório:
   - git clone <URL_DO_REPOSITORIO>

2. Instalar dependências:
   - pip install -r requirements.txt

3. Executar:
   - python extract.py
=======
# ☁️ Projeto Cloud  
**Repositório da disciplina de Projeto Cloud — Quarta-feira de Noite**  
**Professor:** Rafael  

## 👥 Alunos  
- **Eduardo Parga**  
- **Enzo Rafael**  

---

## 🚀 Projeto: Pipeline Cloud para Processamento de Cotações da B3  

Este projeto demonstra como construir uma arquitetura completa em nuvem para **coleta, transformação, armazenamento e análise** de dados da **B3 (Bolsa de Valores do Brasil)**, utilizando **serviços do Microsoft Azure**.  

O objetivo é simular um ambiente de **Big Data**, aplicando práticas de **ETL**, **computação serverless**, **banco de dados em nuvem** e **containers Docker**, de forma automatizada, escalável e eficiente.  

---

## 🎯 Objetivos  

- Criar pipelines de dados em ambiente cloud.  
- Integrar diferentes serviços de forma automatizada.  
- Transformar dados brutos em informações úteis para análise.  

---

## 📊 Contexto  

A **B3** disponibiliza diariamente arquivos com informações de mercado — ativos, datas, preços de abertura e fechamento, volume negociado, etc.  

O desafio do projeto é **automatizar a coleta, o tratamento e o armazenamento** desses arquivos, tornando-os prontos para **análises e dashboards** em ferramentas como **Power BI** ou **Azure Synapse Analytics**.  

---

## 🏗️ Arquitetura da Solução  

| Serviço | Função |
|----------|--------|
| **Azure Storage Account** | Armazena os arquivos originais e processados |
| **Azure Data Factory** | Responsável pelo processo ETL (Extração, Transformação e Carga) |
| **Azure Function** | Insere os dados de forma incremental no banco |
| **Azure SQL Database** | Guarda os dados tratados e prontos para análise |
| **Logic Apps** | Gera notificações e integrações automáticas |
| **Docker + Azure Container Instance** | Simula a ingestão dos arquivos da B3 |

---

## 🔄 Fluxo do Pipeline  

1. **Ingestão:** o container Docker envia os arquivos para o Azure Blob Storage.  
2. **Transformação:** o Data Factory processa e estrutura os dados.  
3. **Carga:** a Azure Function grava as informações no banco SQL.  
4. **Automação:** o Logic Apps dispara alertas e fluxos automáticos.  
5. **Visualização:** os dados tratados são usados em dashboards e relatórios.  

---

## 🧩 Tecnologias Utilizadas  

- **Python** 🐍  
- **Microsoft Azure** ☁️  
- **Azure Data Factory**  
- **Azure Functions**  
- **Azure SQL Database**  
- **Logic Apps**  
- **Docker** 🐳  
- **Power BI** 📊  

---

## 📦 Conteúdo do Repositório  

- 📁 Documento com a **arquitetura e fluxo do projeto**  
- ⚙️ Pipeline configurado no **Azure Data Factory**  
- 🧠 Função **Python** para carga e atualização dos dados  
- 🐳 **Container Docker** para simulação de ingestão  
- 🔔 Exemplo de **Logic App** para automação e alertas  

---

## 🔗 Referências Úteis  

- [Cotações Históricas – Mercado à Vista](https://www.b3.com.br/pt_br/market-data-e-indices/mercado-a-vista/arquivos-historicos/)  
- [Boletim Diário do Mercado](https://www.b3.com.br/pt_br/market-data-e-indices/servicos/boletim-diario-do-mercado/)  
- [Layout dos Arquivos da B3](https://www.b3.com.br/pt_br/market-data-e-indices/servicos/layout-dos-arquivos/)  

---

## ⚙️ Como Executar  

### 1️⃣ Clonar o repositório  
```bash
git clone <URL_DO_REPOSITORIO>
>>>>>>> c5b4dfd60e268e8c5bb06c8bdafaf9d1eb16fd14
