import pymssql
import json
import logging
import os
from datetime import datetime, timedelta
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function para buscar arquivos B3 mais recentes.
    Verifica sempre o arquivo mais atual disponível.
    """
    logging.info('🔍 Iniciando busca por arquivo B3 mais recente...')
    
    try:
        # Configuração do banco
        server = os.environ.get('SQL_SERVER', 'sqlb3server123.database.windows.net')
        database = os.environ.get('SQL_DATABASE', 'b3database')
        username = os.environ.get('SQL_USERNAME', 'sqladmin')
        password = os.environ.get('SQL_PASSWORD', 'MinhaSenh@123')
        
        logging.info(f'📊 Conectando ao banco: {server}')
        
        # Conectar ao banco
        conn = pymssql.connect(
            server=server,
            user=username,
            password=password,
            database=database,
            timeout=30
        )
        
        cursor = conn.cursor()
        
        # Buscar arquivo mais recente baseado na data de processamento
        query = """
        SELECT TOP 1 
            MAX(DataProcessamento) as UltimaData,
            COUNT(*) as TotalRegistros,
            MIN(Data) as DataInicial,
            MAX(Data) as DataFinal
        FROM Cotacoes
        ORDER BY DataProcessamento DESC
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result and result[0]:
            ultima_data = result[0]
            total_registros = result[1]
            data_inicial = result[2]
            data_final = result[3]
            
            logging.info(f'✅ Arquivo mais recente encontrado: {ultima_data}')
            
            # Buscar dados da data mais recente
            query_dados = """
            SELECT 
                Ativo as simbolo,
                Data as data,
                Abertura as abertura,
                Minimo as minimo,
                Maximo as maximo,
                Fechamento as fechamento,
                Volume as volume,
                Negocios as negocios
            FROM Cotacoes 
            WHERE DataProcessamento = ?
            ORDER BY Ativo
            """
            
            cursor.execute(query_dados, (ultima_data,))
            dados = cursor.fetchall()
            
            # Converter para formato JSON
            cotacoes = []
            for row in dados:
                cotacoes.append({
                    'simbolo': row[0],
                    'data': row[1].strftime('%Y-%m-%d') if row[1] else None,
                    'abertura': float(row[2]) if row[2] else 0,
                    'minimo': float(row[3]) if row[3] else 0,
                    'maximo': float(row[4]) if row[4] else 0,
                    'fechamento': float(row[5]) if row[5] else 0,
                    'volume': int(row[6]) if row[6] else 0,
                    'negocios': int(row[7]) if row[7] else 0
                })
            
            response_data = {
                'dados': cotacoes,
                'total': len(cotacoes),
                'status': 'success',
                'arquivo_mais_recente': {
                    'data_processamento': ultima_data.strftime('%Y-%m-%d %H:%M:%S'),
                    'data_pregao_inicial': data_inicial.strftime('%Y-%m-%d') if data_inicial else None,
                    'data_pregao_final': data_final.strftime('%Y-%m-%d') if data_final else None,
                    'total_registros': total_registros
                },
                'fonte': f'Azure SQL Database - Arquivo B3 mais recente ({ultima_data.strftime("%d/%m/%Y %H:%M")})'
            }
            
            logging.info(f'✅ Retornando {len(cotacoes)} cotações do arquivo mais recente')
            
        else:
            logging.warning('⚠️ Nenhum arquivo B3 encontrado no banco')
            response_data = {
                'error': 'Nenhum arquivo B3 encontrado',
                'status': 'error',
                'total': 0
            }
        
        cursor.close()
        conn.close()
        
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            status_code=200,
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
        
    except Exception as e:
        logging.error(f'❌ Erro na function: {str(e)}')
        
        error_response = {
            'error': str(e),
            'status': 'error',
            'total': 0,
            'fonte': 'Azure SQL Database - ERRO'
        }
        
        return func.HttpResponse(
            json.dumps(error_response, ensure_ascii=False),
            status_code=500,
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*'
            }
        )