from azure.storage.blob import BlobServiceClient, PublicAccess

# Troque pela sua string de conexão real do Azure, se não for usar Azurite
AZURE_BLOB_CONNECTION = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1;"
CONTAINER = "dados-pregao"

def save_file_to_blob(file_name, local_path_file):
    service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
    container = service.get_container_client(CONTAINER)
    try:
        container.create_container()
    except Exception:
        pass

    with open(local_path_file, "rb") as data:
        container.upload_blob(name=file_name, data=data, overwrite=True)

def get_file_from_blob(file_name, download_path):
    service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
    container = service.get_container_client(CONTAINER)
    try:
        container.create_container(public_access=PublicAccess.Container)
    except Exception:
        pass

    blob_client = container.get_blob_client(file_name)
    with open(download_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())