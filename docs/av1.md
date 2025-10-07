# AV1 — Entrega: Ingestão B3 → Azurite (Blob) → Cosmos DB

Este documento descreve o escopo e os passos necessários para a entrega da AV1 do projeto. O objetivo é coletar o arquivo de cotações da B3 (já implementado no script `extract.py`), gravar esse arquivo no Storage Account simulado pelo Azurite (Docker) e carregar os registros no Cosmos DB (emulador ou serviço real).

Use este guia como checklist de execução e como documentação a ser entregue junto com artefatos (scripts e prints/saídas).

## Checklist de requisitos (o que será entregue)

- Documento com instruções de execução (`docs/av1.md`) — este arquivo.
- Script de extração e extração dos arquivos (já presente: `extract.py`).
- Script de upload e carga para Azure/Cosmos (`load_azure.py`).
- Arquivos de dados baixados em `dados_b3/` (pasta criada pelo `extract.py`).
- Load na base de dados no CosmoDB
- Rodando tudo no Docker

## Objetivo

1. Baixar o arquivo de pregão da B3 (dia atual ou dia mais próximo) — responsabilidade do `extract.py`.
2. Armazenar o arquivo de cotações extraído no Azure Blob Storage (simulado localmente pelo Azurite).
3. Ler o arquivo do Blob Storage, fazer parsing das linhas e inserir os registros no Cosmos DB.

## Arquitetura e mapeamento com o projeto "Pipeline Cloud"

- Fonte: arquivos de pregão da B3 (baixados via `extract.py`).
- Storage temporário: Azurite (emulação do Azure Blob Storage) — representa o Storage Account do projeto em nuvem.
- Persistência final: Cosmos DB (NoSQL) — onde os documentos serão armazenados para consultas posteriores.

O arquivo `load_azure.py` implementa a etapa de upload para Blob e a etapa de leitura/parsing + `upsert` no Cosmos DB.

## Pré-requisitos locais

- Docker instalado (Windows).
- Python 3.8+ (recomenda-se 3.11). Virtualenv recomendado.
- Dependências Python (ver `requirements.txt`). Exemplos:
	- azure-storage-blob
	- azure-cosmos

- (Opcional) Azure Storage Explorer ou similar para inspecionar blobs.
- (Opcional) Azure Cosmos DB Emulator (Windows) ou uma conta Cosmos DB real (se for usar o serviço remoto ajuste as chaves/endpoints em `load_azure.py`).

Claro, aqui está o tutorial atualizado com os novos passos.

## Instruções passo-a-passo

1)  Iniciar os Serviços (Docker)

Abra um terminal (cmd.exe) e suba os serviços necessários (Azurite, PostgreSQL, etc.) usando o Docker Compose. Este comando irá iniciá-los em background.

```cmd
docker compose up -d
```

2)  Preparar o ambiente Python

No terminal (cmd.exe):

```cmd
python -m venv.venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Se `requirements.txt` não existir ou faltar dependências, instale manualmente:

```cmd
pip install azure-storage-blob azure-cosmos
```

3)  Inicializar o Banco de Dados

Execute o script para criar as tabelas e a estrutura necessária no banco de dados PostgreSQL.

```cmd
python init_db.py
```

4)  Baixar e extrair o arquivo da B3

Execute o script principal de extração. Ele tentará baixar o ZIP mais recente e extrair os arquivos em `dados_b3/`:

```cmd
python extract.py
```

Resultados esperados:

  - Diretório `dados_b3/pregao_<yymmdd>/` contendo os arquivos extraídos.

<!-- end list -->

5)  Transformar e Carregar os Dados

Execute o script que processa os arquivos extraídos e os carrega para o banco de dados.

```cmd
python transform&load.py
```

6)  Conferir os Dados Carregados

Para visualizar a tabela criada e verificar se os dados foram carregados corretamente, execute o script de conferência.

```cmd
python conferencia_postgresql.py
```

## Verificação

- Verifique se o blob foi criado usando o Azure Storage Explorer apontando para `http://127.0.0.1:10000/devstoreaccount1` (se estiver usando Azurite).
- No Cosmos DB Emulator (ou na conta real), abra o Data Explorer e confirme a presença do database `B3Database` e do container `Cotacoes`. Verifique alguns documentos e campos (id, codneg, datpreg, preult).
- Logs do `load_azure.py` indicam quantos registros foram processados e quantos foram inseridos com sucesso.

## Estrutura de dados salvo no Cosmos DB

- Cada documento corresponde a uma linha de registro do tipo `01` (cotação) do arquivo de pregão.
- Campos principais (exemplo):
	- `id`: `<datpreg>-<codneg>` (string) — chave única.
	- `codneg`: código do papel (ticker).
	- `datpreg`: data do pregão (YYYYMMDD).
	- `preabe`, `premax`, `premin`, `preult`: preços (float).
	- `quatot`, `voltot`: quantidade e volume negociado.
	- `partitionKey`: campo usado como chave de partição (ano ou outro atributo de sua escolha).

## Dicas e observações técnicas

- Se o volume de dados for grande, não use upsert linha a linha no SDK: prefira soluções de bulk (Azure Data Factory, Azure Functions com Bulk Executor, ou pipelines dedicados).
- Para facilitar consultas no Athena ou no Analítico, mantenha os dados em formatos colunar (Parquet) quando possível — isso não se aplica diretamente ao Cosmos DB, mas é uma sugestão para a camada de data lake do projeto.
- Garanta o princípio do menor privilégio ao configurar chaves e roles em ambientes reais.

## Entrega da AV1 — o que anexar

- Este arquivo `docs/av1.md` (documentação passo a passo).
- Print do terminal mostrando:
	- Azurite iniciado (logs do docker ou `docker ps`).
	- Saída do `extract.py` confirmando download e extração.
	- Saída do `load_azure.py` mostrando upload e número de registros carregados.
- (Opcional) Captura do Azure Storage Explorer mostrando o blob criado.
- (Opcional) Captura do Data Explorer do Cosmos DB mostrando alguns documentos.

## Próximos passos e melhorias (para referência)

- Automatizar o fluxo completo em Docker Compose ou em um Makefile para reprodutibilidade.
- Adicionar testes unitários para o parser (`parse_line`) e um teste de integração de pequena amostra de dados.
- Parametrizar `load_azure.py` para obter conexão via variáveis de ambiente em vez de strings hard-coded.
- Implementar bulk import no Cosmos ou usar Azure Data Factory para cargas maiores.

---

Se quiser, eu atualizo o `docs/av1.md` com screenshots de exemplo ou adiciono um `docker-compose.yml` que já inicia o Azurite e o Cosmos DB Emulator (se aplicável ao seu ambiente).