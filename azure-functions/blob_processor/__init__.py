import azure.functions as func
import logging
import zipfile
import io
import psycopg2
import os
from datetime import datetime

def main(myblob: func.InputStream) -> None:
    logging.info(f"🔄 Processando blob: {myblob.name} ({myblob.length} bytes)")

    try:
        # Ler conteúdo do blob
        blob_content = myblob.read()
        
        # Processar ZIP
        with zipfile.ZipFile(io.BytesIO(blob_content), 'r') as zip_file:
            for file_name in zip_file.namelist():
                if file_name.upper().startswith('COTACAO') and file_name.endswith('.txt'):
                    logging.info(f"📄 Processando arquivo: {file_name}")
                    
                    with zip_file.open(file_name) as txt_file:
                        conteudo = txt_file.read().decode('latin-1')
                        cotacoes = processar_arquivo_b3(conteudo)
                        
                        if cotacoes:
                            inserir_cotacoes_bd(cotacoes)
                            logging.info(f"✅ {len(cotacoes)} registros inseridos")
                        else:
                            logging.warning("⚠️ Nenhuma cotação encontrada")
                        
                        return f"Processado: {len(cotacoes)} registros"
                        
    except Exception as e:
        logging.error(f"💥 Erro: {str(e)}")
        raise

def processar_arquivo_b3(conteudo_txt):
    """Processa arquivo TXT da B3"""
    linhas = conteudo_txt.strip().split('\n')
    cotacoes = []
    
    for linha in linhas:
        if linha.startswith('01') and len(linha) >= 245:  # Registro de cotação
            try:
                ativo = linha[12:24].strip()
                if not ativo:
                    continue
                    
                data_str = linha[2:10]
                data_pregao = datetime.strptime(data_str, '%Y%m%d').date()
                
                # Preços (centavos para reais)
                abertura = safe_int(linha[56:69]) / 100.0
                fechamento = safe_int(linha[108:121]) / 100.0
                preco_min = safe_int(linha[82:95]) / 100.0
                preco_max = safe_int(linha[69:82]) / 100.0
                volume = safe_int(linha[170:188])
                
                cotacoes.append({
                    'Ativo': ativo,
                    'DataPregao': data_pregao,
                    'Abertura': abertura if abertura > 0 else None,
                    'Fechamento': fechamento if fechamento > 0 else None,
                    'PrecoMin': preco_min if preco_min > 0 else None,
                    'PrecoMax': preco_max if preco_max > 0 else None,
                    'Volume': volume if volume > 0 else None
                })
                
            except Exception as e:
                logging.warning(f"⚠️ Erro linha: {e}")
                continue
    
    return cotacoes

def safe_int(value_str):
    """Converte string para int, retorna 0 se inválido"""
    try:
        return int(value_str.strip()) if value_str.strip() else 0
    except ValueError:
        return 0

def inserir_cotacoes_bd(cotacoes):
    """Insere no PostgreSQL"""
    connection_string = os.environ['DATABASE_CONNECTION_STRING']
    
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            upsert_sql = """
            INSERT INTO b3.cotacoes
            ("Ativo","DataPregao","Abertura","Fechamento","PrecoMin","PrecoMax","Volume")
            VALUES
            (%(Ativo)s,%(DataPregao)s,%(Abertura)s,%(Fechamento)s,%(PrecoMin)s,%(PrecoMax)s,%(Volume)s)
            ON CONFLICT ("Ativo","DataPregao") DO UPDATE SET
              "Abertura"   = EXCLUDED."Abertura",
              "Fechamento" = EXCLUDED."Fechamento",
              "PrecoMin"   = EXCLUDED."PrecoMin",
              "PrecoMax"   = EXCLUDED."PrecoMax",
              "Volume"     = EXCLUDED."Volume";
            """
            
            # Inserir em lotes
            for i in range(0, len(cotacoes), 1000):
                lote = cotacoes[i:i+1000]
                cur.executemany(upsert_sql, lote)
            
            conn.commit()
            logging.info(f"💾 {len(cotacoes)} registros salvos no BD")