import pymssql
from datetime import datetime
import logging

def persist_quotes(quotes_data, connection_params=None):
    """
    Persiste dados de cotações no Azure SQL Database
    """
    logging.basicConfig(level=logging.INFO)
    
    if connection_params is None:
        connection_params = {
            'server': 'sqlb3server123.database.windows.net',
            'database': 'b3database',
            'user': 'b3admin',
            'password': 'SenhaSegura123!'
        }
    
    try:
        # Conectar ao banco
        conn = pymssql.connect(
            server=connection_params['server'],
            user=connection_params['user'],
            password=connection_params['password'],
            database=connection_params['database'],
            timeout=30
        )
        
        cursor = conn.cursor()
        
        # Limpar dados antigos
        cursor.execute("DELETE FROM Cotacoes")
        logging.info("🗑️ Dados antigos removidos")
        
        # Inserir novos dados
        insert_count = 0
        for quote in quotes_data:
            cursor.execute("""
                INSERT INTO Cotacoes (Ativo, DataPregao, Abertura, Fechamento, Volume)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                quote['Ativo'],
                quote['DataPregao'], 
                quote['Abertura'],
                quote['Fechamento'],
                quote['Volume']
            ))
            insert_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info(f"✅ {insert_count} cotações inseridas com sucesso")
        return insert_count
        
    except Exception as e:
        logging.error(f"❌ Erro ao persistir dados: {e}")
        raise e
