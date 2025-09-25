import azure.storage.blob as BlobServiceClient

AZURE_BLOB_CONNECTION = 'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;'
BLOB_CONTAINER_NAME = "b3-dados-brutos"

def upload_to_azure(file_name, local_pathe_file):
    service = BlobServiceClient.BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
    container = service.get_container_client(BLOB_CONTAINER_NAME)
    try:
        container.create_container() # Tenta criar o container
    except Exception:
        pass  # Container(Pasta) já existe

    with open(local_pathe_file, "rb") as data:
        container.upload_blob(name=file_name, data=data, overwrite=True) # Faz upload do arquivo
        print(f"LOAD_AZURE: [OK] Arquivo {file_name} enviado para o Azure Blob Storage no container {BLOB_CONTAINER_NAME}")

def get_file_from_blob(file_name):
    service = BlobServiceClient.BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
    container = service.get_container_client(BLOB_CONTAINER_NAME)
    try:
        container.create_container() # Tenta criar o container
    except Exception:
        pass  # Container(Pasta) já existe

    blob_client = container.get_blob_client(file_name)

    try:
        download_stream = blob_client.download_blob()
        blob_content = download_stream.readall().decode('utf-8')
        return blob_content
    except Exception as e:
        print(f'Error reading blob {e}')