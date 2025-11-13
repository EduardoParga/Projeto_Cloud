from datetime import datetime, timedelta
from helpers import yymmdd
import requests
import os
import zipfile
<<<<<<< HEAD
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

    # Subir o(s) XML(s) para o Azure Blob Storage
    arquivos = [f for f in os.listdir(f"{PATH_TO_SAVE}/ARQUIVOSPREGAO_SPRE{dt}") if f.endswith(".xml")]
    last_xml_name = None
    for arquivo in arquivos:
        upload_to_azure(arquivo, f"{PATH_TO_SAVE}/ARQUIVOSPREGAO_SPRE{dt}/{arquivo}")
        last_xml_name = arquivo
    print(f"[OK] Arquivo(s) XML enviado(s) para o Azure Blob Storage com sucesso")

    # >>> NOVO: grava um ponteiro com o nome do último XML enviado
    if last_xml_name:
        POINTER_LOCAL = os.path.join(PATH_TO_SAVE, "_LATEST_B3_XML.txt")
        with open(POINTER_LOCAL, "w", encoding="utf-8") as f:
            f.write(last_xml_name.strip())
        upload_to_azure("_LATEST_B3_XML.txt", POINTER_LOCAL)

    # Apagar as pastas locais
    shutil.rmtree(f"{PATH_TO_SAVE}", ignore_errors=True)
    print(f"[OK] Pastas locais apagadas com sucesso")

        


if __name__ == "__main__":
    run()
=======
import glob
import sys

from azure_storage import upload_to_azure  # importa funções para o Blob

PATH_TO_SAVE = "./dados_b3"
POINTER_NAME = "_LATEST_B3_XML.txt"
MAX_LOOKBACK_DAYS = 7  # quantos dias voltar se hoje não tiver arquivo

def download_zip_for_date(dt_str: str):
    url = f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{dt_str}.zip"
    print(f"[INFO] Tentando download: {url}")
    try:
        r = requests.get(url, timeout=30)
        if r.ok and r.content and len(r.content) > 200 and r.content[:2] == b"PK":
            return r.content, os.path.basename(url)
    except requests.RequestException as e:
        print(f"[WARN] Erro HTTP: {e}")
    return None, None

def find_recent_zip(max_days: int): # busca sempre o arquivo mais recente
    for delta in range(max_days):
        dt = datetime.now() - timedelta(days=delta)
        dt_str = yymmdd(dt)
        zip_bytes, zip_name = download_zip_for_date(dt_str)
        if zip_bytes:
            if delta > 0:
                print(f"[INFO] Encontrado zip para {dt_str} (há {delta} dias).")
            return dt_str, zip_bytes, zip_name
    return None, None, None

def extract_nested_zip(zip_bytes: bytes, dt_str: str) -> str:
    base_dir = os.path.join(PATH_TO_SAVE, f"pregao_{dt_str}")
    os.makedirs(base_dir, exist_ok=True)
    outer_zip_path = os.path.join(base_dir, f"download_{dt_str}.zip")
    with open(outer_zip_path, "wb") as f:
        f.write(zip_bytes)
    with zipfile.ZipFile(outer_zip_path, "r") as zf:
        zf.extractall(base_dir)

    inner_zip = glob.glob(os.path.join(base_dir, "*.zip"))
    if not inner_zip:
        raise RuntimeError("Zip interno não encontrado após primeira extração.")
    inner_zip_path = inner_zip[0]

    second_extract_dir = os.path.join(PATH_TO_SAVE, f"ARQUIVOSPREGAO_SPRE{dt_str}")
    os.makedirs(second_extract_dir, exist_ok=True)
    with zipfile.ZipFile(inner_zip_path, "r") as zf:
        zf.extractall(second_extract_dir)

    return second_extract_dir

def publish_xmls_and_pointer(xml_dir: str, dt_str: str):
    xml_files = [f for f in os.listdir(xml_dir) if f.lower().endswith(".xml")]
    if not xml_files:
        raise RuntimeError("Nenhum arquivo XML encontrado na extração.")

    last_xml = None
    for xml in xml_files:
        local_path = os.path.join(xml_dir, xml)
        blob_name = f"BVBG186_{dt_str}.xml"
        upload_to_azure(blob_name, local_path)
        last_xml = xml
        print(f"[OK] Processado e enviado: {xml}")

    # envia ponteiro do último XML
    pointer_local = os.path.join(PATH_TO_SAVE, POINTER_NAME)
    with open(pointer_local, "w", encoding="utf-8") as f:
        f.write(last_xml or "")
    upload_to_azure(POINTER_NAME, pointer_local)
    print(f"[OK] Ponteiro salvo e enviado: {last_xml}")

def run():
    os.makedirs(PATH_TO_SAVE, exist_ok=True)
    dt_str, zip_bytes, zip_name = find_recent_zip(MAX_LOOKBACK_DAYS)
    if not zip_bytes:
        raise RuntimeError(f"Não foi possível baixar zip nos últimos {MAX_LOOKBACK_DAYS} dias.")

    print(f"[OK] Zip baixado: {zip_name}")
    xml_dir = extract_nested_zip(zip_bytes, dt_str)
    print(f"[OK] Extração concluída em: {xml_dir}")

    publish_xmls_and_pointer(xml_dir, dt_str)
    print("[OK] Processo finalizado.")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"[ERRO] {e}", file=sys.stderr)
    sys.exit(1)
>>>>>>> c5b4dfd60e268e8c5bb06c8bdafaf9d1eb16fd14
