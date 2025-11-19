import azure.functions as func
import logging
import zipfile
import io
import xml.etree.ElementTree as ET
import pymssql
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient

def main(myblob: func.InputStream) -> None:
    """
    🎯 BLOB TRIGGER - ESPECIFICAÇÃO DO PROFESSOR
    
    Executa AUTOMATICAMENTE quando arquivo é enviado pelo TIME TRIGGER
    Processa arquivo ZIP/XML da B3 e carrega no Azure SQL Database
    """
    logging.info(f'🎯 BLOB TRIGGER ATIVADO!')
    logging.info(f'📁 Arquivo: {myblob.name}')
    logging.info(f'📏 Tamanho: {myblob.length} bytes')
    
    try:
        # Só processar arquivos B3
        if not ('SPRE' in myblob.name or 'B3_DIARIO' in myblob.name):
            logging.info(f'⏭️ Arquivo ignorado: {myblob.name} (não é arquivo B3)')
            return
            
        logging.info('🔄 BLOB TRIGGER - Processando arquivo B3...')
        
        # Ler conteúdo do blob
        blob_content = myblob.read()

        # Processar até dois níveis de ZIP aninhado
        def find_xml_in_zip(zip_bytes, nivel=1):
            with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as z:
                xml_files = [f for f in z.namelist() if f.endswith('.xml')]
                if xml_files:
                    xml_file = xml_files[0]
                    logging.info(f'📄 Processando XML (nível {nivel}): {xml_file}')
                    with z.open(xml_file) as xml_content:
                        tree = ET.parse(xml_content)
                        root = tree.getroot()
                        cotacoes = extrair_cotacoes_b3(root, xml_file)
                        if cotacoes:
                            salvar_no_banco(cotacoes)
                            logging.info(f'✅ BLOB TRIGGER CONCLUÍDO!')
                            logging.info(f'📊 {len(cotacoes)} cotações processadas')
                            logging.info(f'💾 Dados salvos no Azure SQL Database')
                        else:
                            logging.warning('⚠️ Nenhuma cotação extraída do XML')
                    return True
                # Procurar ZIP aninhado
                zip_files = [f for f in z.namelist() if f.endswith('.zip')]
                if zip_files and nivel < 3:
                    inner_zip_name = zip_files[0]
                    logging.info(f'📦 ZIP aninhado (nível {nivel}) encontrado: {inner_zip_name}')
                    with z.open(inner_zip_name) as inner_zip_content:
                        inner_zip_bytes = inner_zip_content.read()
                    return find_xml_in_zip(inner_zip_bytes, nivel=nivel+1)
                return False

        if not find_xml_in_zip(blob_content, nivel=1):
            logging.warning('⚠️ Nenhum arquivo XML encontrado em até dois níveis de ZIP aninhado')
        
    except Exception as e:
        logging.error(f'❌ ERRO BLOB TRIGGER: {str(e)}')
        raise e

def extrair_cotacoes_b3(root, nome_arquivo):
    """
    Extrai cotações do XML da B3 de forma robusta, igual ao parse_pricrpt local.
    """
    from lxml import etree
    from decimal import Decimal, InvalidOperation
    import re
    logging.info('📊 Extraindo cotações do XML (robusto)...')

    def to_decimal(x):
        if x is None:
            return None
        s = str(x).strip().replace(",", ".")
        if not s:
            return None
        try:
            return Decimal(s)
        except (InvalidOperation, ValueError):
            return None

    def to_date(s):
        if not s:
            return None
        if "T" in s:
            s = s.split("T", 1)[0]
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return datetime.now().date()

    # Converter root para lxml se necessário
    if not hasattr(root, 'xpath'):
        xml_str = ET.tostring(root, encoding='utf-8')
        root = etree.fromstring(xml_str)

    pricrpts = root.xpath('//*[local-name()="PricRpt"]')
    def first_text(node, xp: str) -> str:
        v = node.xpath(xp)
        if isinstance(v, list):
            v = v[0] if v else ""
        return (v or "").strip()

    cotacoes = []
    for pr in pricrpts:
        ativo = first_text(pr, './/*[local-name()="TckrSymb"][1]/text()')
        dt = first_text(pr, './/*[local-name()="TradDt"]/*[local-name()="Dt"][1]/text()') \
             or first_text(pr, './/*[local-name()="TradDt"][1]/text()')
        if not (ativo and dt):
            continue

        frst = first_text(pr, './/*[local-name()="FrstPric"][1]/text()')
        last = first_text(pr, './/*[local-name()="LastPric"][1]/text()')
        minp = first_text(pr, './/*[local-name()="MinPric"][1]/text()')
        maxp = first_text(pr, './/*[local-name()="MaxPric"][1]/text()')
        tradavg = first_text(pr, './/*[local-name()="TradAvrgPric"][1]/text()')

        ntlfinvol = first_text(pr, './/*[local-name()="NtlFinVol"][1]/text()')
        rglrtxsqty = first_text(pr, './/*[local-name()="RglrTxsQty"][1]/text()')
        opn_intrst = first_text(pr, './/*[local-name()="OpnIntrst"][1]/text()')

        has_price = any(bool(x) for x in (frst, last, minp, maxp, tradavg))
        has_trade_volume = bool(ntlfinvol or rglrtxsqty)
        if not (has_price or has_trade_volume):
            continue
        if (not has_price) and opn_intrst and not has_trade_volume:
            continue

        abertura = to_decimal(frst)
        fechamento = to_decimal(last)
        precomin = to_decimal(minp)
        precomax = to_decimal(maxp)
        volume = to_decimal(ntlfinvol or rglrtxsqty)

        cotacoes.append({
            "Ativo": ativo,
            "DataPregao": to_date(dt),
            "Abertura": abertura,
            "Fechamento": fechamento,
            "PrecoMin": precomin,
            "PrecoMax": precomax,
            "Volume": volume
        })

    logging.info(f'📈 {len(cotacoes)} ativos únicos extraídos')
    return cotacoes

def salvar_no_banco(cotacoes):
    """
    Salva cotações no Azure SQL Database
    """
    logging.info('💾 Salvando no Azure SQL Database...')
    
    try:
        # Conectar ao banco
        conn = pymssql.connect(
            server='sqlb3server123.database.windows.net',
            user='b3admin',
            password='SenhaSegura123!',
            database='b3database',
            timeout=30
        )
        
        cursor = conn.cursor()
        
        # Limpar dados antigos
        cursor.execute("DELETE FROM Cotacoes")
        logging.info('🗑️ Dados antigos removidos')
        
        # Inserir novos dados
        for cotacao in cotacoes:
            cursor.execute("""
                INSERT INTO Cotacoes (Ativo, DataPregao, Abertura, Fechamento, Volume)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                cotacao['Ativo'],
                cotacao['DataPregao'],
                cotacao['Abertura'],
                cotacao['Fechamento'],
                cotacao['Volume']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info(f'✅ {len(cotacoes)} cotações inseridas no banco!')
        
    except Exception as e:
        logging.error(f'❌ Erro ao salvar no banco: {e}')
        raise e