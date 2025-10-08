from azure.storage.blob import BlobServiceClient
import os,sys

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
        print(len(b.name), b.name)
    if not found:
        print("Nenhum blob encontrado.")
except Exception as e:
    print("Erro listando blobs:", e)
    print("Execute inspect_azurite_db.py para localizar nomes problemáticos no arquivo azurite_data__azurite_db_blob.json")