from azure.storage.blob import BlobServiceClient
import os, sys

conn = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
if not conn:
    print("ERRO: AZURE_STORAGE_CONNECTION_STRING não definida nesta sessão.")
    sys.exit(1)

client = BlobServiceClient.from_connection_string(conn)
container = os.environ.get("AZURE_BLOB_CONTAINER", "b3")
try:
    c = client.get_container_client(container)
    print("Blobs in container:", container)
    found = False
    for b in c.list_blobs():
        found = True
        print(f"{b.name}  size={b.size}")
    if not found:
        print("Nenhum blob encontrado.")
except Exception as e:
    print("Erro listando blobs:", e)