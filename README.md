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
