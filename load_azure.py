# ...existing code...
# shim para compatibilidade: redireciona para seu módulo azure_storage
try:
    from azure_storage import upload_file_to_blob, get_file_from_blob  # nome do seu módulo
except Exception:
    # fallback mínimo: define stubs para evitar ImportError se funções não existirem
    def upload_file_to_blob(container: str, local_path: str, blob_name: str):
        raise RuntimeError("upload_file_to_blob não disponível. Verifique azure_storage.py")

    def get_file_from_blob(blob_name: str, container: str = None) -> bytes:
        raise RuntimeError("get_file_from_blob não disponível. Verifique azure_storage.py")
# ...existing code...