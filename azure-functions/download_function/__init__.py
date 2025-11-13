import azure.functions as func
import logging
import requests
import os
from datetime import datetime, timezone, timedelta
from azure.storage.blob import BlobServiceClient

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('⚠️ Timer atrasado!')

    logging.info(f'🚀 Function Download iniciada em: {utc_timestamp}')
    
    try:
        # Data atual no formato da B3
        dt_str = datetime.now().strftime('%y%m%d')
        url = f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{dt_str}.zip"
        
        logging.info(f'📥 Tentando download: {url}')
        
        # Download
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        resp = session.get(url, timeout=60)
        
        if resp.ok and resp.content and len(resp.content) > 200:
            if resp.content[:2] == b"PK":  # Verifica ZIP válido
                
                # Upload para Blob Storage
                connection_string = os.environ['AzureWebJobsStorage']
                blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                
                # Nome do blob
                blob_name = f"SPRE{dt_str}.zip"
                
                # Upload
                blob_client = blob_service_client.get_blob_client(
                    container="b3-dados-brutos", 
                    blob=blob_name
                )
                
                blob_client.upload_blob(resp.content, overwrite=True)
                
                logging.info(f'✅ Sucesso! Arquivo {blob_name} enviado para Blob Storage')
                logging.info(f'📊 Tamanho: {len(resp.content)} bytes')
                
                return f"Download OK - {blob_name}"
                
            else:
                logging.error('❌ Arquivo não é ZIP válido')
                return "Erro: Arquivo inválido"
        else:
            logging.warning(f'⚠️ Download falhou - Status: {resp.status_code}')
            
            # Tentar dias anteriores
            for days_back in range(1, 8):
                dt_obj = datetime.now() - timedelta(days=days_back)
                dt_str_back = dt_obj.strftime('%y%m%d')
                url_back = f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{dt_str_back}.zip"
                
                logging.info(f'📥 Tentando {days_back} dias atrás: {url_back}')
                
                resp_back = session.get(url_back, timeout=60)
                if resp_back.ok and resp_back.content and len(resp_back.content) > 200:
                    if resp_back.content[:2] == b"PK":
                        
                        blob_name_back = f"SPRE{dt_str_back}.zip"
                        connection_string = os.environ['AzureWebJobsStorage']
                        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                        
                        blob_client = blob_service_client.get_blob_client(
                            container="b3-dados-brutos", 
                            blob=blob_name_back
                        )
                        
                        blob_client.upload_blob(resp_back.content, overwrite=True)
                        
                        logging.info(f'✅ Sucesso com arquivo de {days_back} dias atrás: {blob_name_back}')
                        return f"Download OK (backup) - {blob_name_back}"
            
            return "Erro: Nenhum arquivo encontrado"
            
    except Exception as e:
        logging.error(f'💥 Erro na função: {str(e)}')
        raise