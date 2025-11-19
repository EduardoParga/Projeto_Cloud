import json
import logging
import azure.functions as func
import pymssql

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    API para retornar lista de ativos REAIS da B3 do arquivo mais recente
    """
    logging.info('🔍 API ativos REAIS chamada')
    
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
        logging.info('📊 Buscando ativos REAIS do Azure SQL Database')
        
        # Conectar ao Azure SQL Database
        conn = pymssql.connect(
            server='sqlb3server123.database.windows.net',
            user='b3admin',
            password='SenhaSegura123!',
            database='b3database',
            timeout=30
        )
        
        cursor = conn.cursor()
        
        # Buscar ativos APENAS do arquivo MAIS RECENTE
        query = """
        SELECT DISTINCT Ativo
        FROM Cotacoes 
        WHERE DataPregao = (
            SELECT MAX(DataPregao) FROM Cotacoes
        )
        ORDER BY Ativo
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            # Fallback para qualquer arquivo disponível
            cursor.execute("SELECT DISTINCT Ativo FROM Cotacoes ORDER BY Ativo")
            rows = cursor.fetchall()
        
        # Buscar informações do arquivo
        cursor.execute("""
            SELECT 
                MAX(DataPregao) as ArquivoMaisRecente,
                COUNT(DISTINCT Ativo) as TotalAtivos,
                COUNT(*) as TotalRegistros
            FROM Cotacoes
        """)
        
        info_arquivo = cursor.fetchone()
        data_arquivo = info_arquivo[0] if info_arquivo[0] else None
        
        cursor.close()
        conn.close()
        
        # Converter para lista
        ativos = [row[0] for row in rows]
        
        response = {
            'ativos': ativos,
            'total': len(ativos),
            'status': 'success',
            'fonte': f'Azure SQL Database - Ativos REAIS B3',
            'arquivo_info': {
                'data_processamento': data_arquivo.strftime('%Y-%m-%d %H:%M:%S') if data_arquivo else 'N/A',
                'data_processamento_formatada': data_arquivo.strftime('%d/%m/%Y %H:%M') if data_arquivo else 'N/A',
                'total_ativos_arquivo': info_arquivo[1] if info_arquivo else 0,
                'total_registros': info_arquivo[2] if info_arquivo else 0,
                'eh_dados_reais': True
            }
        }
        
        logging.info(f'✅ Retornando {len(ativos)} ativos REAIS do arquivo {data_arquivo}')
        
        return func.HttpResponse(
            json.dumps(response, ensure_ascii=False),
            status_code=200,
            headers=headers
        )
        
    except Exception as e:
        logging.error(f'❌ Erro ao buscar ativos reais: {str(e)}')
        
        # Fallback apenas em caso de erro crítico
        ativos_fallback = ['ABEV3', 'BBDC4', 'GGBR4', 'ITUB4', 'MGLU3', 'PETR4', 'VALE3', 'WEGE3']
        
        return func.HttpResponse(
            json.dumps({
                'ativos': ativos_fallback,
                'total': len(ativos_fallback),
                'status': 'fallback',
                'error': str(e),
                'fonte': 'Fallback - Erro na conexão com Azure SQL',
                'arquivo_info': {
                    'eh_dados_reais': False,
                    'erro': 'Não foi possível acessar dados reais'
                }
            }),
            status_code=200,
            headers=headers
        )