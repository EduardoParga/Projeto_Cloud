# Load Azure - Script de Upload B3

Este script é responsável por fazer o upload dos arquivos extraídos da B3 para o Azure Blob Storage usando o Azurite (emulador local).

## Funcionalidades

- ✅ Upload automático de todas as pastas de dados extraídas
- ✅ Criação automática do container no blob storage
- ✅ Suporte para múltiplas pastas (pregao_* e ARQUIVOSPREGAO_*)
- ✅ Preservação da estrutura de pastas no blob storage
- ✅ Logs detalhados do processo de upload
- ✅ Tratamento de erros e reconexão

## Pré-requisitos

1. **Azurite rodando no Docker**:
   ```cmd
   start_azurite.bat
   ```
   
   Ou manualmente:
   ```cmd
   docker run -d --name azurite-b3 -p 10000:10000 -p 10001:10001 -p 10002:10002 mcr.microsoft.com/azure-storage/azurite
   ```

2. **Dados extraídos da B3**:
   ```cmd
   python extract.py
   ```

3. **Dependências Python instaladas**:
   ```cmd
   pip install -r requirements.txt
   ```

## Como usar

### Upload simples
```cmd
python load_azure.py
```

### Verificar arquivos enviados
```cmd
python list_blobs.py
```

## Estrutura criada no Blob Storage

```
Container: b3-dados-brutos
├── pregao_250910/
│   └── PR250910.zip
└── ARQUIVOSPREGAO_PR250910/
    ├── BVBG.086.01_BV000328202509100328000001838361656.xml
    ├── BVBG.086.01_BV000328202509100328000001908580396.xml
    └── BVBG.086.01_BV000328202509100328000001924489848.xml
```

## Configurações

### Connection String do Azurite
```python
azurite_connection_string = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)
```

### Endpoints disponíveis
- **Blob Service**: http://127.0.0.1:10000/devstoreaccount1
- **Container**: b3-dados-brutos

## Logs de exemplo

```
=== Iniciando upload B3 -> Blob Storage ===
Pastas de dados encontradas: ['dados_b3\\pregao_250910', 'dados_b3\\ARQUIVOSPREGAO_PR250910']

--- Inicializando conexão com Blob Storage ---
Container 'b3-dados-brutos' já existe

--- Upload para Blob Storage ---
Fazendo upload da pasta dados_b3\pregao_250910...
Uploading PR250910.zip -> pregao_250910/PR250910.zip
✓ Upload concluído: pregao_250910/PR250910.zip
Upload da pasta concluído. 1 arquivos enviados.

Fazendo upload da pasta dados_b3\ARQUIVOSPREGAO_PR250910...
Uploading BVBG.086.01_BV000328202509100328000001838361656.xml -> ARQUIVOSPREGAO_PR250910/BVBG.086.01_BV000328202509100328000001838361656.xml
✓ Upload concluído: ARQUIVOSPREGAO_PR250910/BVBG.086.01_BV000328202509100328000001838361656.xml
[...]

----- Upload concluído -----
Total de arquivos enviados: 4
Container: b3-dados-brutos
Endpoint: http://127.0.0.1:10000/devstoreaccount1
```

## Troubleshooting

### Erro de conexão com Azurite
```
Erro ao conectar no Azurite: [Error details]
Certifique-se de que o Azurite está rodando no Docker:
docker run -p 10000:10000 -p 10001:10001 -p 10002:10002 mcr.microsoft.com/azure-storage/azurite
```

**Solução**: Verificar se o Docker está rodando e se o Azurite foi iniciado corretamente.

### Nenhuma pasta de dados encontrada
```
Nenhuma pasta de dados encontrada. Execute extract.py primeiro.
```

**Solução**: Executar `python extract.py` para baixar e extrair os dados da B3.

### Erro no upload de arquivo específico
```
✗ Erro no upload de arquivo.xml: [Error details]
```

**Solução**: Verificar permissões do arquivo e espaço disponível.

## Scripts relacionados

- `extract.py` - Extrai dados da B3
- `test_azurite.py` - Testa conexão com Azurite  
- `list_blobs.py` - Lista arquivos no blob storage
- `start_azurite.bat` - Inicia Azurite no Docker
