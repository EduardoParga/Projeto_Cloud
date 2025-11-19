#!/usr/bin/env python3
# Script para limpar Azure SQL e inserir dados REAIS do XML

import sys
import os
sys.path.append('.')
import pymssql
from extract_xml import parse_pricrpt

def limpar_e_inserir_dados_reais():
    """Limpa Azure SQL e insere dados REAIS do XML B3"""
    
    print("🔄 LIMPEZA E INSERÇÃO DE DADOS REAIS")
    print("=" * 50)
    
    # 1. Extrair dados REAIS do XML
    xml_path = 'dados_b3/ARQUIVOSPREGAO_SPRE251007/BVBG.186.01_BV000471202510070001000061921366800.xml'
    
    print("📄 Extraindo dados do XML...")
    try:
        with open(xml_path, 'rb') as f:
            xml_data = f.read()
        
        xml_cotacoes = parse_pricrpt(xml_data)
        print(f"✅ {len(xml_cotacoes)} registros extraídos")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # 2. Filtrar apenas ativos principais
    ativos_principais = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3', 'MGLU3', 'WEGE3', 'GGBR4']
    cotacoes_filtradas = []
    
    for item in xml_cotacoes:
        ativo = item.get('Ativo', '')
        if ativo in ativos_principais:
            cotacoes_filtradas.append({
                'Ativo': ativo,
                'DataPregao': item.get('DataPregao'),
                'Abertura': float(item.get('Abertura', 0)),
                'Fechamento': float(item.get('Fechamento', 0)),
                'Volume': int(item.get('Volume', 0))
            })
    
    print(f"🎯 {len(cotacoes_filtradas)} ativos principais encontrados")
    
    # 3. Conectar ao Azure SQL e limpar tabela
    print("\n💾 Conectando ao Azure SQL...")
    try:
        conn = pymssql.connect(
            server='sqlb3server123.database.windows.net',
            user='b3admin',
            password='SenhaSegura123!',
            database='b3database'
        )
        
        with conn.cursor() as cursor:
            # Limpar tabela
            print("🗑️ Limpando dados antigos...")
            cursor.execute("DELETE FROM Cotacoes")
            
            # Inserir dados REAIS
            print("📊 Inserindo dados REAIS...")
            for cotacao in cotacoes_filtradas:
                cursor.execute('''
                    INSERT INTO Cotacoes (Ativo, DataPregao, Abertura, Fechamento, Volume)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    cotacao['Ativo'],
                    cotacao['DataPregao'],
                    cotacao['Abertura'],
                    cotacao['Fechamento'],
                    cotacao['Volume']
                ))
                
                print(f"  ✅ {cotacao['Ativo']}: R${cotacao['Abertura']:.2f} | Vol={cotacao['Volume']:,}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 SUCESSO! {len(cotacoes_filtradas)} registros REAIS inseridos!")
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        
if __name__ == '__main__':
    limpar_e_inserir_dados_reais()