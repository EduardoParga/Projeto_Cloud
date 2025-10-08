import os
from typing import Optional
from azure.storage.blob import BlobServiceClient

CONN = os.environ.get("AZURE_STORAGE_CONNECTION_STRING") or os.environ.get("AZURE_BLOB_CONNECTION")
if not CONN:
    raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING não definido.")

_client = BlobServiceClient.from_connection_string(CONN)
CONTAINER = os.environ.get("AZURE_BLOB_CONTAINER", "b3")

def _ensure_container():
    c = _client.get_container_client(CONTAINER)
    try:
        c.create_container()
    except Exception:
        pass
    return c

def upload_to_azure(local_path: str, blob_name: Optional[str] = None):
    if blob_name is None:
        blob_name = os.path.basename(local_path)
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