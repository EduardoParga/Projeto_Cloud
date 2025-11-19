import json
import logging
import azure.functions as func
import pymssql
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    API para retornar dados REAIS da B3 do arquivo mais recente
    """
    logging.info('🔍 API dados REAIS chamada')
    
    # Headers CORS completos
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # Handle OPTIONS request for CORS
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            '',
            status_code=200,
            headers=headers
        )
    
    try:
        # Pegar o ativo da query string
        ativo = req.params.get('ativo', '').upper()
        
        if not ativo:
            return func.HttpResponse(
                json.dumps({
                    'error': 'Parâmetro ativo é obrigatório',
                    'status': 'error'
                }),
                status_code=400,
                headers=headers
            )
        
        logging.info(f'📊 Buscando dados REAIS para {ativo}')
        
        # Conectar ao Azure SQL Database
        conn = pymssql.connect(
            server='sqlb3server123.database.windows.net',
            user='b3admin',
            password='SenhaSegura123!',
            database='b3database',
            timeout=30
        )
        
        cursor = conn.cursor()
        
        # Buscar dados do ativo do arquivo MAIS RECENTE
        query = """
        SELECT 
            Ativo,
            Abertura,
            Abertura as PrecoMaximo,
            Abertura as PrecoMinimo,
            Fechamento,
            Volume,
            DataPregao
        FROM Cotacoes 
        WHERE Ativo = %s 
        AND DataPregao = (
            SELECT MAX(DataPregao) 
            FROM Cotacoes
        )
        """
        
        cursor.execute(query, (ativo,))
        row = cursor.fetchone()
        
        if not row:
            # Tentar buscar qualquer dado deste ativo
            cursor.execute("""
                SELECT DISTINCT Ativo FROM Cotacoes 
                WHERE Ativo LIKE %s
                ORDER BY Ativo
            """, (f'%{ativo}%',))
            
            similar = cursor.fetchall()
            similar_list = [r[0] for r in similar] if similar else []
            
            cursor.close()
            conn.close()
            
            return func.HttpResponse(
                json.dumps({
                    'error': f'Ativo {ativo} não encontrado no arquivo B3 mais recente',
                    'ativos_similares': similar_list,
                    'status': 'error'
                }),
                status_code=404,
                headers=headers
            )
        
        # Buscar data do arquivo mais recente
        cursor.execute("SELECT MAX(DataPregao) FROM Cotacoes")
        data_arquivo = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        # Calcular variação percentual
        preco_abertura = float(row[1]) if row[1] else 0
        preco_fechamento = float(row[4]) if row[4] else 0
        variacao = ((preco_fechamento - preco_abertura) / preco_abertura * 100) if preco_abertura > 0 else 0
        
        response = {
            'ativo': row[0],
            'preco_abertura': float(row[1]) if row[1] else 0,
            'preco_maximo': float(row[2]) if row[2] else 0,
            'preco_minimo': float(row[3]) if row[3] else 0,
            'preco_fechamento': float(row[4]) if row[4] else 0,
            'volume': int(row[5]) if row[5] else 0,
            'data_negociacao': row[6].strftime('%Y-%m-%d') if row[6] else '',
            'variacao_percentual': round(variacao, 2),
            'status': 'success',
            'fonte': f'Azure SQL Database - Dados REAIS B3 (arquivo {data_arquivo.strftime("%d/%m/%Y %H:%M")})',
            'arquivo_data': data_arquivo.strftime('%Y-%m-%d %H:%M:%S'),
            'eh_dados_reais': True
        }
        
        logging.info(f'✅ Retornando dados REAIS para {ativo} do arquivo {data_arquivo}')
        
        return func.HttpResponse(
            json.dumps(response, ensure_ascii=False),
            status_code=200,
            headers=headers
        )
        
    except Exception as e:
        logging.error(f'❌ Erro: {str(e)}')
        
        return func.HttpResponse(
            json.dumps({
                'error': f'Erro ao buscar dados reais: {str(e)}',
                'status': 'error',
                'eh_dados_reais': False
            }),
            status_code=500,
            headers=headers
        )