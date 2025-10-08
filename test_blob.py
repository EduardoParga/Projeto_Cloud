from azure_storage import upload_to_azure, get_file_from_blob

file_name = "teste.xml"
local_path = "teste.xml"


with open(local_path, "w", encoding="utf-8") as f:
    f.write("<exemplo><mensagem>Olá Blob!</mensagem></exemplo>")

upload_to_azure(file_name, local_path)

conteudo = get_file_from_blob(file_name)
if conteudo:
    print(conteudo.decode("utf-8"))