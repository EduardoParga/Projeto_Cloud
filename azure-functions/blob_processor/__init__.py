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
        
        # Processar ZIP
        with zipfile.ZipFile(io.BytesIO(blob_content), 'r') as zip_file:
            xml_files = [f for f in zip_file.namelist() if f.endswith('.xml')]
            
            if not xml_files:
                logging.warning('⚠️ Nenhum arquivo XML encontrado no ZIP')
                return
                
            xml_file = xml_files[0]
            logging.info(f'📄 Processando XML: {xml_file}')
            
            # Extrair e processar XML
            with zip_file.open(xml_file) as xml_content:
                tree = ET.parse(xml_content)
                root = tree.getroot()
                
                # Extrair dados de cotações
                cotacoes = extrair_cotacoes_b3(root, xml_file)
                
                if cotacoes:
                    # Salvar no Azure SQL Database
                    salvar_no_banco(cotacoes)
                    
                    logging.info(f'✅ BLOB TRIGGER CONCLUÍDO!')
                    logging.info(f'📊 {len(cotacoes)} cotações processadas')
                    logging.info(f'💾 Dados salvos no Azure SQL Database')
                else:
                    logging.warning('⚠️ Nenhuma cotação extraída do XML')
        
    except Exception as e:
        logging.error(f'❌ ERRO BLOB TRIGGER: {str(e)}')
        raise e

def extrair_cotacoes_b3(root, nome_arquivo):
    """
    Extrai cotações do XML da B3
    """
    logging.info('📊 Extraindo cotações do XML...')
    
    cotacoes = []
    
    # Extrair data do arquivo
    data_str = None
    if 'SPRE' in nome_arquivo:
        # Formato: SPRE251118
        data_part = nome_arquivo.split('SPRE')[1][:6]  # 251118
        data_str = f'20{data_part}'  # 20251118
    
    if data_str:
        try:
            data_pregao = datetime.strptime(data_str, '%Y%m%d').date()
        except:
            data_pregao = datetime.now().date()
    else:
        data_pregao = datetime.now().date()
    
    logging.info(f'📅 Data do pregão: {data_pregao}')
    
    # Processar namespace do XML B3
    namespace = {'ns': 'urn:bvmf.052.01.xsd'}
    
    # Buscar transações no XML
    for finInstrm in root.findall('.//ns:FinInstrm', namespace):
        try:
            # Extrair símbolo do ativo
            ativo_elem = finInstrm.find('.//ns:TckrSymb', namespace)
            if ativo_elem is None:
                continue
                
            ativo = ativo_elem.text.strip()
            
            # Filtrar apenas ações (termina com 3, 4, 11, etc.)
            if not any(ativo.endswith(x) for x in ['3', '4', '11']):
                continue
            
            # Buscar dados de preço
            preco_elems = finInstrm.findall('.//ns:TradDt', namespace)
            
            for trade_elem in preco_elems:
                try:
                    # Preços
                    abertura_elem = trade_elem.find('.//ns:FrstPric', namespace)
                    fechamento_elem = trade_elem.find('.//ns:LastPric', namespace)
                    volume_elem = trade_elem.find('.//ns:TtlVol', namespace)
                    
                    if abertura_elem is not None and fechamento_elem is not None:
                        abertura = float(abertura_elem.text)
                        fechamento = float(fechamento_elem.text)
                        volume = float(volume_elem.text) if volume_elem is not None else 0
                        
                        cotacao = {
                            'Ativo': ativo,
                            'DataPregao': data_pregao,
                            'Abertura': abertura,
                            'Fechamento': fechamento,
                            'Volume': int(volume)
                        }
                        
                        cotacoes.append(cotacao)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            continue
    
    # Agrupar por ativo (pegar apenas um registro por ativo)
    cotacoes_finais = {}
    for cot in cotacoes:
        ativo = cot['Ativo']
        if ativo not in cotacoes_finais:
            cotacoes_finais[ativo] = cot
            
    resultado = list(cotacoes_finais.values())
    logging.info(f'📈 {len(resultado)} ativos únicos extraídos')
    
    return resultado

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