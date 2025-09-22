# pegar o arquivo, ler do blob storage, extrair os dados e salvar no cosmos db
# carregar somente os dados do mercardo a vista (BOVESPA), ignorando os outros mercados, seguindo documentacao de escopo do projeto
from datetime import datetime, timedelta
from helpers import yymmdd
import requests
import os
import zipfile
import shutil
import azure.storage.blob as BlobServiceClient
from azure.cosmos import CosmosClient, PartitionKey

AZURE_BLOB_CONNECTION = 'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;'
BLOB_CONTAINER_NAME = "b3-dados-brutos"
COSMOS_ENDPOINT = "https://localhost:8081/"
COSMOS_KEY = "chave_primaria_do_cosmos_db"
COSMOS_DATABASE_NAME = "B3Database"
COSMOS_CONTAINER_NAME = "Cotações"
PATH_TO_SAVE = "./dados_b3"