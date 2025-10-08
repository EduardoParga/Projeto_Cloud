import os
from typing import Optional
from azure.storage.blob import BlobServiceClient

CONN = os.environ.get("AZURE_STORAGE_CONNECTION_STRING") or os.environ.get("AZURE_BLOB_CONNECTION")
if not CONN:
    raise RuntimeError(
        "Defina AZURE_STORAGE_CONNECTION_STRING com a connection string do Azurite. Exemplo no PowerShell:\n"
        "$env:AZURE_STORAGE_CONNECTION_STRING='DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;'"
    )

_client = BlobServiceClient.from_connection_string(CONN)
CONTAINER = os.environ.get("AZURE_BLOB_CONTAINER", "b3")

def _ensure_container():
    c = _client.get_container_client(CONTAINER)
    try:
        c.create_container()
    except Exception:
        pass
    return c

def upload_to_azure(blob_name: str, local_path: str):
    c = _ensure_container()
    with open(local_path, "rb") as f:
        data = f.read()
    c.upload_blob(name=blob_name, data=data, overwrite=True, max_concurrency=1)
    return True

def get_file_from_blob(blob_name: str) -> Optional[bytes]:
    c = _ensure_container()
    blob = c.get_blob_client(blob_name)
    try:
        data = blob.download_blob().readall()
        return data
    except Exception:
        return None