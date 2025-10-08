from azure.storage.blob import BlobServiceClient
import os, sys

conn = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
if not conn:
    print("ERRO: AZURE_STORAGE_CONNECTION_STRING não definida nesta sessão.")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Uso: python delete_blob.py '<blob_name>'")
    sys.exit(1)

blob_name = sys.argv[1]
client = BlobServiceClient.from_connection_string(conn)
container = os.environ.get("AZURE_BLOB_CONTAINER", "b3")
c = client.get_container_client(container)
try:
    c.delete_blob(blob_name)
    print("Deletado:", blob_name)
except Exception as e:
    print("Erro ao deletar blob via SDK:", e)
    print("Se falhar, pare o Azurite e remova a entrada manualmente no JSON (veja instruções).")