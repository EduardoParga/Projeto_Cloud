from datetime import datetime, timedelta
from helpers import yymmdd
import requests
import os
import zipfile
import shutil
import glob
import sys

from load_azure import upload_to_azure

PATH_TO_SAVE = "./dados_b3"
POINTER_NAME = "_LATEST_B3_XML.txt"
MAX_LOOKBACK_DAYS = 7  # quantos dias voltar se hoje não tiver arquivo

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
    return None, None

# FUNCAO PRINCIPAL: busca sempre o arquivo mais recente disponível
def achar_zip_pregao_mais_recente(max_days):
    """
    Busca o arquivo B3 MAIS RECENTE disponível, começando de hoje e voltando até max_days
    """
    for days_back in range(0, max_days):
        dt_obj = datetime.now() - timedelta(days=days_back)
        # Pular fins de semana
        if dt_obj.weekday() >= 5:  # sábado=5, domingo=6
            continue
            
        dt_str = yymmdd(dt_obj)
        url = build_url_download(dt_str)
        zip_bytes, zip_name = try_http_download(url)
        
        if zip_bytes:
            if days_back == 0:
                print(f"[OK] Arquivo MAIS RECENTE encontrado para HOJE: {dt_str}")
            else:
                print(f"[OK] Arquivo MAIS RECENTE encontrado para {dt_str} (há {days_back} dias)")
            return dt_str, zip_bytes, zip_name
            
    return None, None, None

def extract_nested_zip(zip_bytes, dt_str):
    """
    Extrai o ZIP duplo da B3 e retorna o diretório com os XMLs
    """
    # Primeira extração
    first_extract_dir = os.path.join(PATH_TO_SAVE, f"pregao_{dt_str}")
    os.makedirs(first_extract_dir, exist_ok=True)
    
    zip_path = os.path.join(first_extract_dir, f"download_{dt_str}.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)
    
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(first_extract_dir)

    # Segunda extração (ZIP interno)
    inner_zips = glob.glob(os.path.join(first_extract_dir, "*.zip"))
    if not inner_zips:
        # Tentar buscar por SPRE*.zip especificamente
        inner_zip = os.path.join(first_extract_dir, f"SPRE{dt_str}.zip")
        if not os.path.exists(inner_zip):
            raise RuntimeError("Zip interno não encontrado após primeira extração.")
        inner_zips = [inner_zip]
    
    inner_zip_path = inner_zips[0]
    second_extract_dir = os.path.join(PATH_TO_SAVE, f"ARQUIVOSPREGAO_SPRE{dt_str}")
    os.makedirs(second_extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(inner_zip_path, "r") as zf:
        zf.extractall(second_extract_dir)

    return second_extract_dir

def upload_xmls_and_update_pointer(xml_dir, dt_str):
    """
    Faz upload dos XMLs para Azure e atualiza o ponteiro do arquivo mais recente
    """
    xml_files = [f for f in os.listdir(xml_dir) if f.lower().endswith(".xml")]
    if not xml_files:
        raise RuntimeError("Nenhum arquivo XML encontrado na extração.")

    last_xml_name = None
    for xml_file in xml_files:
        local_xml_path = os.path.join(xml_dir, xml_file)
        # Usar o nome original do arquivo XML
        upload_to_azure(xml_file, local_xml_path)
        last_xml_name = xml_file
        print(f"[OK] XML enviado para Azure: {xml_file}")

    # Atualizar ponteiro do arquivo MAIS RECENTE
    if last_xml_name:
        pointer_local = os.path.join(PATH_TO_SAVE, POINTER_NAME)
        with open(pointer_local, "w", encoding="utf-8") as f:
            f.write(f"{last_xml_name}|{dt_str}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        upload_to_azure(POINTER_NAME, pointer_local)
        print(f"[OK] Ponteiro do arquivo MAIS RECENTE atualizado: {last_xml_name}")
        
    return last_xml_name

def run():
    """
    Executa o processo completo de busca e upload do arquivo B3 MAIS RECENTE
    """
    print(f"🔍 Buscando arquivo B3 MAIS RECENTE (últimos {MAX_LOOKBACK_DAYS} dias)...")
    
    # 1) Buscar o arquivo MAIS RECENTE disponível
    dt_str, zip_bytes, zip_name = achar_zip_pregao_mais_recente(MAX_LOOKBACK_DAYS)

    if not zip_bytes:
        raise RuntimeError(f"❌ ERRO: Não foi possível baixar arquivo B3 nos últimos {MAX_LOOKBACK_DAYS} dias úteis!")

    print(f"✅ SUCESSO: Baixado arquivo MAIS RECENTE: {zip_name} (data: {dt_str})")

    # 2) Criar diretório e extrair
    os.makedirs(PATH_TO_SAVE, exist_ok=True)
    xml_dir = extract_nested_zip(zip_bytes, dt_str)
    print(f"✅ Arquivos extraídos em: {xml_dir}")

    # 3) Upload para Azure e atualizar ponteiro
    latest_xml = upload_xmls_and_update_pointer(xml_dir, dt_str)
    
    # 4) Limpeza
    shutil.rmtree(PATH_TO_SAVE, ignore_errors=True)
    print(f"✅ CONCLUÍDO: Arquivo B3 MAIS RECENTE processado e enviado!")
    print(f"📅 Data do pregão: {dt_str}")
    print(f"📄 Arquivo XML: {latest_xml}")
    
    return dt_str, latest_xml

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"❌ ERRO: {e}", file=sys.stderr)
        sys.exit(1)
