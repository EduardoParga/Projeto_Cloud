import pymssql
import os

def conectar_azure_sql():
    """Conecta ao Azure SQL Database"""
    try:
        conn = pymssql.connect(
            server='sqlb3server123.database.windows.net',
            user='b3admin',
            password='SenhaSegura123!',
            database='b3database',
            port=1433,
            charset='utf8'
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def verificar_dados_reais():
    """Verifica os dados reais salvos no Azure SQL"""
    conn = conectar_azure_sql()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Verificar quantos registros temos
        cursor.execute("SELECT COUNT(*) FROM Cotacoes")
        total = cursor.fetchone()[0]
        print(f"=== AZURE SQL DATABASE ===")
        print(f"Total de registros: {total}")
        
        # Buscar dados dos principais ativos
        ativos = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3', 'MGLU3', 'WEGE3', 'JBSS3']
        
        print(f"\n=== DADOS REAIS DOS ATIVOS ===")
        for ativo in ativos:
            cursor.execute("""
                SELECT Ativo, DataPregao, Abertura, Fechamento, Volume
                FROM Cotacoes 
                WHERE Ativo = %s
                ORDER BY DataPregao DESC
            """, (ativo,))
            
            result = cursor.fetchone()
            if result:
                print(f"{result[0]}: Data={result[1]} | Abertura=R${result[2]} | Fechamento=R${result[3]} | Volume={result[4]:,}")
            else:
                print(f"{ativo}: NÃO ENCONTRADO")
                
    except Exception as e:
        print(f"Erro na consulta: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    verificar_dados_reais()