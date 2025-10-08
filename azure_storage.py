from azure.storage.blob import BlobServiceClient
import os

CONN = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")

def _client():
    if not CONN:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING não definido")
    return BlobServiceClient.from_connection_string(CONN)

def upload_file_to_blob(container: str, local_path: str, blob_name: str):
    client = _client()
    c = client.get_container_client(container)
    try:
        c.create_container()
    except Exception:
        pass
    with open(local_path, "rb") as f:
        c.upload_blob(blob_name, f, overwrite=True)
    return True

def get_file_from_blob(blob_name: str, container: str = None) -> bytes:
    client = _client()
    container = container or os.environ.get("AZURE_BLOB_CONTAINER", "b3")
    c = client.get_container_client(container)
    downloader = c.download_blob(blob_name)
    return downloader.readall()