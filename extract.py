from datetime import datetime
from helpers import yymmdd
import requests
import os
import zipfile
##from azure_storage import save_file_to_blob
import shutil

DIRETORIO_DESTINO = "./dados_b3"

def montar_url(data):
    return f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{data}.zip"

def baixar_arquivo(url):
    sessao = requests.Session()
    try:
        print(f"[INFO] Baixando de {url}")
        resposta = sessao.get(url, timeout=30)
        if resposta.ok and resposta.content and len(resposta.content) > 200:
            if resposta.content.startswith(b"PK"):
                return resposta.content, os.path.basename(url)
    except requests.RequestException:
        print(f"[ERRO] Falha ao acessar {url}")
    return None, None

def principal():
    data_ref = "250923"  # Exemplo fixo, troque para yymmdd(datetime.now()) se quiser automatizar
    url = montar_url(data_ref)

    # 1) Download do arquivo ZIP
    conteudo_zip, nome_zip = baixar_arquivo(url)
    if not conteudo_zip:
        raise RuntimeError("Falha ao baixar o arquivo de cotações.")

    print(f"[SUCESSO] Arquivo baixado: {nome_zip}")

    # 2) Salvar ZIP localmente
    os.makedirs(DIRETORIO_DESTINO, exist_ok=True)
    caminho_zip = f"{DIRETORIO_DESTINO}/pregao_{data_ref}.zip"
    with open(caminho_zip, "wb") as arq:
        arq.write(conteudo_zip)

    print(f"[SUCESSO] ZIP salvo em {caminho_zip}")

    # 3) Extrair o primeiro ZIP
    pasta_temp = f"{DIRETORIO_DESTINO}/pregao_{data_ref}"
    with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
        zip_ref.extractall(pasta_temp)

    # 4) Extrair o ZIP interno
    zip_interno = f"{pasta_temp}/SPRE{data_ref}.zip"
    pasta_final = f"{DIRETORIO_DESTINO}/SPRE{data_ref}"
    with zipfile.ZipFile(zip_interno, "r") as zip_ref2:
        zip_ref2.extractall(pasta_final)

    # 5) Enviar arquivos para Blob Storage
    for arquivo in os.listdir(pasta_final):
        caminho_arquivo = os.path.join(pasta_final, arquivo)
        save_file_to_blob(f"BVBG186_{data_ref}.xml", caminho_arquivo)
        print(f"[SUCESSO] {arquivo} enviado para Blob Storage")

    # 6) Limpeza dos arquivos locais
    shutil.rmtree(DIRETORIO_DESTINO, ignore_errors=True)
    print(f"[SUCESSO] Limpeza dos arquivos locais concluída")

if __name__ == "__main__" :
    principal()