import azure.functions as func
import logging
import zipfile
import io
import pymssql
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
    """Insere no Azure SQL Database"""
    try:
        conn = pymssql.connect(
            server='sqlb3server123.database.windows.net',
            user='b3admin',
            password='SenhaSegura123!',
            database='b3database'
        )
        
        with conn.cursor() as cur:
            # SQL Server syntax
            for cotacao in cotacoes:
                cur.execute('''
                    MERGE Cotacoes AS target
                    USING (SELECT %s as Ativo, %s as DataPregao, %s as Abertura, %s as Fechamento, %s as Volume) AS source
                    ON target.Ativo = source.Ativo AND target.DataPregao = source.DataPregao
                    WHEN MATCHED THEN
                        UPDATE SET Abertura = source.Abertura, Fechamento = source.Fechamento, Volume = source.Volume
                    WHEN NOT MATCHED THEN
                        INSERT (Ativo, DataPregao, Abertura, Fechamento, Volume)
                        VALUES (source.Ativo, source.DataPregao, source.Abertura, source.Fechamento, source.Volume);
                ''', (cotacao['Ativo'], cotacao['DataPregao'], cotacao['Abertura'], cotacao['Fechamento'], cotacao['Volume']))
            
            conn.commit()
            logging.info(f"💾 {len(cotacoes)} registros salvos no Azure SQL")
            
    except Exception as e:
        logging.error(f"💥 Erro BD: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()