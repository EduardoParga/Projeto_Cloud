from datetime import datetime, timedelta
from helpers import yymmdd
import requests
import os
import zipfile
import shutil

from load_azure import upload_to_azure

PATH_TO_SAVE = "./dados_b3"

def build_url_download(date_to_download):
    return f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{date_to_download}.zip"

def try_http_download(url):
    session = requests.Session()
    try:
        print(f"[INFO] Tentando {url}")
        resp = session.get(url, timeout=30)
        if (resp.ok) and resp.content and len(resp.content) > 200:
            if (resp.content[:2] == b"PK"):
                return resp.content, os.path.basename(url)
    except requests.RequestException:
        print(f"[ERROR] Falha ao acessar a {url}")
        pass
    # Garantir retorno consistente como tupla
    return None, None

# FUNCAO para caso de falha no download pegar dias anteriores
def achar_zip_pregao_recente(max_days):
    for days_back in range(0, max_days):
        dt_obj = datetime.now() - timedelta(days=days_back)
        dt_str = yymmdd(dt_obj)
        url = build_url_download(dt_str)
        zip_bytes, zip_name = try_http_download(url)
        if zip_bytes:
            if days_back > 0:
                print(f"[INFO] Arquivo encontrado para {dt_str} (há {days_back} dias)")
            return dt_str, zip_bytes, zip_name
    return None, None, None

def run():
    # 1) Procurar e baixar o zip a partir da data atual, recuando até MAX_DAYS
    MAX_DAYS = 7
    dt, zip_bytes, zip_name = achar_zip_pregao_recente(MAX_DAYS)

    if not zip_bytes:
        raise RuntimeError(f"Não foi possível baixar o arquivo de cotações nos últimos {MAX_DAYS} dias. Verifique conexão / site da B3.")

    print(f"[OK] Baixado arquivo de cotaçoes: {zip_name}")

    # 2) Salvar o Zip
    
    #Cria o diretorio que ira salvar o arquivo zip do download
    os.makedirs(PATH_TO_SAVE, exist_ok=True)
    zip_path = f"{PATH_TO_SAVE}/pregao_{dt}.zip"
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    print(f"[OK] Zip salvo em {zip_path}")

    # 3) Extrair os arquivos do zip

    #Extrair a primeira pasta
    first_extract_dir = os.path.join(PATH_TO_SAVE, f"pregao_{dt}")
    os.makedirs(first_extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(first_extract_dir)

    #Extrair a segunda parte
    second_zip = os.path.join(first_extract_dir, f"SPRE{dt}.zip")
    second_extract_dir = os.path.join(PATH_TO_SAVE, f"ARQUIVOSPREGAO_SPRE{dt}")
    os.makedirs(second_extract_dir, exist_ok=True)
    with zipfile.ZipFile(second_zip, "r") as zf:
        zf.extractall(second_extract_dir)

    print(f"[OK] Arquivos extraidos do zip com sucesso")

    # Subir o arquivo xml para o Azure Blob Storage
    arquivos = [f for f in os.listdir(f"{PATH_TO_SAVE}/ARQUIVOSPREGAO_SPRE{dt}") if f.endswith(".xml")]
    for arquivo in arquivos:
        upload_to_azure(arquivo, f"{PATH_TO_SAVE}/ARQUIVOSPREGAO_SPRE{dt}/{arquivo}")
    print(f"[OK] Arquivo(s) XML enviado(s) para o Azure Blob Storage com sucesso")

    # Apagar os pasta com arquivos salvos localmente
    shutil.rmtree(f"{PATH_TO_SAVE}", ignore_errors=True)
    print(f"[OK] Pastas locais apagadas com sucesso")
    


if __name__ == "__main__":
    run()