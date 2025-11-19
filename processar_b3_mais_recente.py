import pymssql
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os

def processar_xml_b3_mais_recente():
    """
    Processa o arquivo XML B3 MAIS RECENTE e insere na Azure SQL
    """
    
    print("🔍 Buscando arquivo XML B3 MAIS RECENTE...")
    
    # Buscar arquivo XML mais recente
    base_dir = "dados_b3"
    xml_file = None
    
    # Verificar últimos 3 dias
    for dias in range(3):
        data = datetime.now() - timedelta(days=dias)
        data_str = data.strftime("%y%m%d")
        
        pasta = f"ARQUIVOSPREGAO_SPRE{data_str}"
        pasta_path = os.path.join(base_dir, pasta)
        
        if os.path.exists(pasta_path):
            for arquivo in os.listdir(pasta_path):
                if arquivo.endswith('.xml'):
                    xml_file = os.path.join(pasta_path, arquivo)
                    print(f"✅ Arquivo MAIS RECENTE encontrado: {arquivo} (data: {data.strftime('%d/%m/%Y')})")
                    break
            if xml_file:
                break
    
    if not xml_file:
        print("❌ Nenhum arquivo XML recente encontrado!")
        return
    
    print(f"📄 Processando: {xml_file}")
    
    # Configuração Azure SQL
    server = 'sqlb3server123.database.windows.net'
    database = 'b3database'
    username = 'b3admin'
    password = 'SenhaSegura123!'
    
    try:
        conn = pymssql.connect(
            server=server,
            user=username,
            password=password,
            database=database,
            timeout=30
        )
        cursor = conn.cursor()
        
        print("🔗 Conectado ao Azure SQL Database")
        
        # Limpar dados antigos
        cursor.execute("DELETE FROM Cotacoes")
        print("🗑️ Dados antigos removidos")
        
        # Processar XML
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Extrair data do pregão do nome do arquivo
        nome_arquivo = os.path.basename(xml_file)
        data_str = nome_arquivo.split('_')[2][:8]  # Extrair YYYYMMDD
        data_pregao = datetime.strptime(data_str, '%Y%m%d').date()
        data_processamento = datetime.now()
        
        print(f"📅 Data do pregão: {data_pregao}")
        print(f"📅 Data de processamento: {data_processamento}")
        
        # Dicionário para agrupar dados por ativo
        ativos_dados = {}
        
        # Processar todas as transações
        print("📊 Extraindo dados do XML...")
        
        for item in root.findall('.//BizGrp/Document/FinInstrmRptgTxRpt/TxRpts/TxRpt'):
            try:
                fin_instrm = item.find('FinInstrm')
                if fin_instrm is not None:
                    isin_elem = fin_instrm.find('Id/ISIN')
                    if isin_elem is not None and isin_elem.text:
                        isin = isin_elem.text
                        
                        # Extrair símbolo do ativo (padrão B3)
                        if len(isin) >= 12:
                            simbolo = isin[4:9]  # Posição padrão do código no ISIN
                        else:
                            continue
                        
                        # Extrair preço
                        price_elem = item.find('Tx/Pric')
                        if price_elem is not None and price_elem.text:
                            preco = float(price_elem.text) / 100  # B3 usa centavos
                            
                            # Extrair volume
                            qty_elem = item.find('Tx/Qty')
                            volume = 0
                            if qty_elem is not None and qty_elem.text:
                                volume = int(float(qty_elem.text))
                            
                            # Agrupar por ativo
                            if simbolo not in ativos_dados:
                                ativos_dados[simbolo] = {
                                    'precos': [],
                                    'volumes': [],
                                    'negocios': 0
                                }
                            
                            ativos_dados[simbolo]['precos'].append(preco)
                            ativos_dados[simbolo]['volumes'].append(volume)
                            ativos_dados[simbolo]['negocios'] += 1
                            
            except Exception:
                continue
        
        print(f"✅ Encontrados {len(ativos_dados)} ativos únicos")
        
        # Inserir dados consolidados por ativo
        registros_inseridos = 0
        for simbolo, dados in ativos_dados.items():
            if len(dados['precos']) > 0:
                # Calcular estatísticas
                precos = sorted(dados['precos'])
                volumes = dados['volumes']
                
                abertura = precos[0]
                fechamento = precos[-1]
                minimo = min(precos)
                maximo = max(precos)
                volume_total = sum(volumes)
                negocios_total = dados['negocios']
                
                # Inserir na base
                query = """
                INSERT INTO Cotacoes (
                    Ativo, Data, Abertura, Minimo, Maximo, Fechamento, 
                    Volume, Negocios, DataProcessamento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(query, (
                    simbolo, data_pregao, abertura, minimo, maximo, fechamento,
                    volume_total, negocios_total, data_processamento
                ))
                
                registros_inseridos += 1
                
                # Log dos principais ativos
                if simbolo in ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3']:
                    print(f"  📈 {simbolo}: R$ {fechamento:.2f} | Vol: {volume_total:,}")
        
        # Commit
        conn.commit()
        
        print(f"✅ SUCESSO! {registros_inseridos} ativos inseridos na Azure SQL")
        print(f"📅 Data do arquivo: {data_pregao}")
        print(f"🎯 Dados B3 MAIS RECENTES disponíveis na Azure!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    processar_xml_b3_mais_recente()