from datetime import datetime
from helpers import yymmdd
import requests
import os
import zipfile
import io
import gzip

PATH_TO_SAVE = "./dados_b3"

def build_url_download(date_to_download):
    return f"https://www.b3.com.br/pesquisapregao/download?filelist=PR{date_to_download}.zip"


def try_htpp_download(url):
    session = requests.Session()
    try:
        print(f"(INFO) Tentando {url}")
        resp = session.get(url, timeout=30)
        print(f"(DEBUG) Status code: {resp.status_code}")
        print(f"(DEBUG) Response headers: {resp.headers}")
        if (resp.ok) and resp.content and len(resp.content) > 200:
            if (resp.content[:2] == b"PK"):
                # Extract file name from URL or set a default
                zip_name = url.split("filelist=")[-1] if "filelist=" in url else "downloaded.zip"
                return resp.content, zip_name
        print("(DEBUG) Response content length:", len(resp.content))
        return None, None
    except requests.RequestException as e:
        print(f"[ERROR] Falha ao acessar a {url}: {e}")
        return None, None

def run():
    dt_raw = datetime.now()
    dt = yymmdd(dt_raw)
    # If yymmdd returns a tuple, join it as a string
    if isinstance(dt, tuple):
        dt = "".join(dt)
    url_to_download = build_url_download(dt)

    # 1) download do Zip

    zip_bytes, zip_name = try_htpp_download(url_to_download)

    if not zip_bytes:
        raise RuntimeError("Não foi possível baixar o arquivo de cotações")
    
    print (f"[OK] Baixado arquivo de cotações: {zip_name}")

     # 2) Salvar o Zip
     #Cria o diretório que irá salvar o arquivo Zip do download
    os.makedirs(PATH_TO_SAVE, exist_ok=True)

    zip_path = f"{PATH_TO_SAVE}/pregao_{dt}.zip"
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    print(f"[OK] Zip salvo em {zip_path}")

    # 3) Extrair os arquivos Zip
    # Detect gzip encoding and decompress if needed
    zip_data = zip_bytes
    if zip_bytes[:2] != b'PK':
        try:
            zip_data = gzip.decompress(zip_bytes)
            print('[INFO] Arquivo estava compactado com gzip, descompactado para zip.')
        except Exception as e:
            print(f'[ERROR] Falha ao descompactar gzip: {e}')
            raise RuntimeError('Arquivo baixado não é um zip válido.')
    # Extrair o zip
    with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
        zf.extractall(PATH_TO_SAVE)
        print('[OK] Arquivos extraídos:')
        print(zf.namelist())
    print(f"[OK] Arquivos extraídos do zip com sucesso")

if __name__ == "__main__":
    run()