from azure_storage import get_file_from_blob

blob_name = "BVBG186_251007.xml"
conteudo = get_file_from_blob(blob_name)
if conteudo:
    print("[OK] Blob encontrado:")
    print(conteudo.decode("utf-8")[:500])  
else:
    print("[ERRO] Blob não encontrado")