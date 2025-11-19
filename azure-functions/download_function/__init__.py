import azure.functions as func
import logging
import requests
import zipfile
import io
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta

# Função para extrair cotações do mercado à vista (TpMerc = 010) de um XML B3
from lxml import etree
from decimal import Decimal, InvalidOperation

import re
# Regex para ticker padrão B3 (ex: PETR4, VALE3)
_TICKER_B3 = re.compile(r"^[A-Z]{4}[0-9]{1,2}$")

def extrair_cotacoes_mercado_vista(xml_bytes):
    """
    Lê o XML da B3 e retorna lista de dicionários com cotações do mercado à vista (TpMerc = 010).
    """
    parser = etree.XMLParser(recover=True, huge_tree=True)
    arvore = etree.parse(io.BytesIO(xml_bytes), parser)
    precos = []
    total = 0
    vista = 0
    formato_ok = 0
    for pr in arvore.xpath('//*[local-name()="PricRpt"]'):
        total += 1
        # Busca tipo de mercado em diferentes tags possíveis
        tipo = pr.xpath('.//*[local-name()="TpMerc"]/text()')
        if not tipo:
            tipo = pr.xpath('.//*[local-name()="MktTp"]/text()')
        if not tipo:
            tipo = pr.xpath('.//*[local-name()="MktTpCd"]/text()')
        tipo = tipo[0].strip() if tipo else ''
        if tipo not in ('010', '10', ''):
            continue
        vista += 1
        # Extrai ticker
        ticker = pr.xpath('.//*[local-name()="TckrSymb"]/text()')
        ticker = ticker[0].strip().upper() if ticker else ''
        if not _TICKER_B3.match(ticker):
            continue
        formato_ok += 1
        # Extrai data
        data = pr.xpath('.//*[local-name()="TradDt"]/*[local-name()="Dt"]/text()')
        if not data:
            data = pr.xpath('.//*[local-name()="TradDt"]/text()')
        data = data[0].split('T')[0] if data else ''
        # Função para converter para decimal
        def dec(x):
            try:
                return Decimal(str(x).replace(',', '.'))
            except Exception:
                return None
        cotacao = {
            'Ativo': ticker,
            'DataPregao': data,
            'Abertura': dec(pr.xpath('.//*[local-name()="FrstPric"]/text()')[0]) if pr.xpath('.//*[local-name()="FrstPric"]/text()') else None,
            'Fechamento': dec(pr.xpath('.//*[local-name()="LastPric"]/text()')[0]) if pr.xpath('.//*[local-name()="LastPric"]/text()') else None,
            'PrecoMin': dec(pr.xpath('.//*[local-name()="MinPric"]/text()')[0]) if pr.xpath('.//*[local-name()="MinPric"]/text()') else None,
            'PrecoMax': dec(pr.xpath('.//*[local-name()="MaxPric"]/text()')[0]) if pr.xpath('.//*[local-name()="MaxPric"]/text()') else None,
            'Volume': dec(pr.xpath('.//*[local-name()="NtlFinVol"]/text()')[0]) if pr.xpath('.//*[local-name()="NtlFinVol"]/text()') else None
        }
        precos.append(cotacao)
    logging.info(f"[EXTRATOR] Total PricRpt: {total} | Mercado à vista: {vista} | Ticker ok: {formato_ok} | Resultados: {len(precos)}")
    return precos

def main(mytimer: func.TimerRequest) -> None:
    """
    ⏰ TIME TRIGGER DIÁRIO - ESPECIFICAÇÃO DO PROFESSOR
    
    Executa DIARIAMENTE às 20h para baixar arquivo B3 mais recente
    Conforme arquitetura: Time Trigger → Blob Trigger → WebApp → Frontend
    """
    logging.info('🕒 TIME TRIGGER INICIADO - Download diário arquivo B3')
    
    try:
        # Configuração Azure Storage
        
        import os
        connection_string = os.getenv("AZURE_CONNECTION_STRING")
        container_name = "b3-dados-brutos"
        
        # Calcular data do arquivo (dia atual ou último dia útil)
        data_hoje = datetime.now()
        
        # Se for fim de semana, buscar sexta-feira anterior
        if data_hoje.weekday() == 5:  # Sábado
            data_busca = data_hoje - timedelta(days=1)
        elif data_hoje.weekday() == 6:  # Domingo  
            data_busca = data_hoje - timedelta(days=2)
        else:
            data_busca = data_hoje
            
        data_str = data_busca.strftime('%y%m%d')
        
        logging.info(f'📅 TIME TRIGGER - Buscando arquivo B3: SPRE{data_str} ({data_busca.strftime("%d/%m/%Y")})')
        
        # URL oficial da B3
        url_b3 = f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{data_str}.zip"
        
        logging.info(f'🌐 URL B3: {url_b3}')
        
        # Headers para simular browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/zip, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Referer': 'https://www.b3.com.br/'
        }
        
        # Download do arquivo
        response = requests.get(url_b3, headers=headers, timeout=120)
        
        if response.status_code == 200 and len(response.content) > 1000:
            # Nome do arquivo para storage
            timestamp = datetime.now().strftime("%H%M%S")
            nome_arquivo = f'B3_DIARIO_SPRE{data_str}_{timestamp}.zip'
            
            # Upload para Azure Storage (vai disparar BLOB TRIGGER)
            blob_service = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service.get_blob_client(container=container_name, blob=nome_arquivo)
            
            blob_client.upload_blob(response.content, overwrite=True)
            
            logging.info(f'✅ TIME TRIGGER SUCESSO!')
            logging.info(f'📦 Arquivo salvo: {nome_arquivo}')
            logging.info(f'📊 Tamanho: {len(response.content):,} bytes')
            logging.info(f'🔄 BLOB TRIGGER será executado automaticamente para processar')
            
            # Marcar como último arquivo baixado
            marcador_nome = f'_ULTIMO_DOWNLOAD_B3.txt'
            blob_marcador = blob_service.get_blob_client(container=container_name, blob=marcador_nome)
            info_marcador = f"""ÚLTIMO DOWNLOAD B3
Arquivo: {nome_arquivo}
Data Pregão: {data_busca.strftime("%d/%m/%Y")}
Download: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
Tamanho: {len(response.content):,} bytes
Status: DOWNLOAD_CONCLUIDO_AGUARDANDO_PROCESSAMENTO
"""
            blob_marcador.upload_blob(info_marcador.encode(), overwrite=True)
            
        else:
            logging.warning(f'⚠️ Arquivo não disponível - Status: {response.status_code}, Tamanho: {len(response.content)}')
            
            # Tentar datas anteriores (máximo 5 dias úteis)
            for dias_atras in range(1, 6):
                data_anterior = data_busca - timedelta(days=dias_atras)
                
                # Pular fins de semana
                if data_anterior.weekday() >= 5:
                    continue
                    
                data_str_ant = data_anterior.strftime('%y%m%d')
                url_anterior = f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{data_str_ant}.zip"
                
                logging.info(f'🔄 Tentando data anterior: SPRE{data_str_ant} ({data_anterior.strftime("%d/%m/%Y")})')
                
                resp_ant = requests.get(url_anterior, headers=headers, timeout=120)
                
                if resp_ant.status_code == 200 and len(resp_ant.content) > 1000:
                    nome_arquivo_ant = f'B3_DIARIO_SPRE{data_str_ant}_{datetime.now().strftime("%H%M%S")}.zip'
                    
                    blob_service = BlobServiceClient.from_connection_string(connection_string)
                    blob_client = blob_service.get_blob_client(container=container_name, blob=nome_arquivo_ant)
                    blob_client.upload_blob(resp_ant.content, overwrite=True)
                    
                    logging.info(f'✅ TIME TRIGGER SUCESSO (data anterior)!')
                    logging.info(f'📦 Arquivo: {nome_arquivo_ant}')
                    break
            else:
                logging.error(f'❌ TIME TRIGGER FALHOU - Nenhum arquivo B3 disponível nos últimos 5 dias úteis')
        
    except Exception as e:
        logging.error(f'❌ ERRO TIME TRIGGER: {str(e)}')
        raise e