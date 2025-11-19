import pymssql
import random
from datetime import datetime, timedelta
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def simular_arquivos_b3_multiplas_datas():
    """
    Simula inserção de dados B3 de múltiplas datas para testar o sistema de "arquivo mais recente"
    """
    
    # Configuração do banco
    server = 'sqlb3server123.database.windows.net'
    database = 'b3database'
    username = 'sqladmin'
    password = 'MinhaSenh@123'
    
    print(f"🔗 Conectando ao Azure SQL: {server}")
    
    conn = pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
        timeout=30
    )
    
    cursor = conn.cursor()
    
    # Ativos para simular
    ativos = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3', 'MGLU3', 'WEGE3', 'GGBR4']
    
    # Simular dados dos últimos 5 dias úteis
    hoje = datetime.now()
    datas_processamento = []
    
    for i in range(5):
        data_proc = hoje - timedelta(days=i)
        # Pular fins de semana
        if data_proc.weekday() < 5:
            datas_processamento.append(data_proc)
    
    print(f"📅 Simulando dados para {len(datas_processamento)} datas:")
    for data in datas_processamento:
        print(f"   - {data.strftime('%d/%m/%Y %H:%M')}")
    
    # Para cada data de processamento
    for idx, data_processamento in enumerate(datas_processamento):
        
        print(f"\n📊 Processando data: {data_processamento.strftime('%d/%m/%Y %H:%M')}")
        
        # Data do pregão (sempre 07/10/2025 para manter compatibilidade)
        data_pregao = datetime(2025, 10, 7)
        
        for ativo in ativos:
            # Gerar preços aleatórios mas realistas
            preco_base = {
                'ITUB4': 37.0,
                'PETR4': 30.5,
                'VALE3': 59.0,
                'BBDC4': 16.5,
                'ABEV3': 11.5,
                'MGLU3': 8.5,
                'WEGE3': 35.5,
                'GGBR4': 17.0
            }.get(ativo, 30.0)
            
            # Variação de ±5% para simular diferentes "arquivos"
            variacao = 1 + (random.random() - 0.5) * 0.1  # ±5%
            
            abertura = round(preco_base * variacao, 2)
            fechamento = round(abertura * (1 + (random.random() - 0.5) * 0.06), 2)  # ±3%
            minimo = round(min(abertura, fechamento) * 0.995, 5)
            maximo = round(max(abertura, fechamento) * 1.005, 5)
            
            # Volume com variação
            volume_base = {
                'ITUB4': 37598,
                'PETR4': 29375,
                'VALE3': 30159,
                'BBDC4': 28687,
                'ABEV3': 17008,
                'MGLU3': 18831,
                'WEGE3': 14116,
                'GGBR4': 17188
            }.get(ativo, 20000)
            
            volume = int(volume_base * (0.8 + random.random() * 0.4))  # Variação de 80% a 120%
            negocios = int(volume / 20)  # Aproximação
            
            # Inserir no banco
            query = """
            INSERT INTO Cotacoes (
                Ativo, Data, Abertura, Minimo, Maximo, Fechamento, 
                Volume, Negocios, DataProcessamento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            try:
                cursor.execute(query, (
                    ativo, data_pregao, abertura, minimo, maximo, fechamento,
                    volume, negocios, data_processamento
                ))
                
                print(f"   ✅ {ativo}: R${fechamento} (Vol: {volume:,})")
                
            except Exception as e:
                print(f"   ❌ Erro ao inserir {ativo}: {e}")
    
    # Commit das transações
    conn.commit()
    
    # Verificar quantos registros foram inseridos
    cursor.execute("SELECT COUNT(*) FROM Cotacoes")
    total_registros = cursor.fetchone()[0]
    
    # Verificar quantas datas de processamento temos
    cursor.execute("SELECT COUNT(DISTINCT DataProcessamento) FROM Cotacoes")
    total_datas = cursor.fetchone()[0]
    
    # Mostrar arquivo mais recente
    cursor.execute("SELECT MAX(DataProcessamento) FROM Cotacoes")
    arquivo_mais_recente = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print(f"\n✅ SIMULAÇÃO CONCLUÍDA!")
    print(f"📊 Total de registros: {total_registros}")
    print(f"📅 Total de datas processamento: {total_datas}")
    print(f"🎯 Arquivo MAIS RECENTE: {arquivo_mais_recente.strftime('%d/%m/%Y %H:%M:%S')}")
    
    print(f"\n🌐 TESTE AGORA:")
    print(f"   API Dados: https://func-b3-test.azurewebsites.net/api/dados")
    print(f"   Frontend: https://stb3projeto123.z5.web.core.windows.net")

if __name__ == "__main__":
    print("🚀 Simulando múltiplas datas de arquivos B3...")
    simular_arquivos_b3_multiplas_datas()