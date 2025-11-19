#!/usr/bin/env python3
# Script simples para extrair dados do XML local

import sys
import os
sys.path.append('.')

from extract_xml import parse_pricrpt

def main():
    xml_path = 'dados_b3/ARQUIVOSPREGAO_SPRE251007/BVBG.186.01_BV000471202510070001000061921366800.xml'
    
    print("🔍 EXTRAINDO DADOS REAIS DO ARQUIVO XML B3")
    print(f"📁 Arquivo: {xml_path}")
    print("=" * 80)
    
    try:
        print("📖 Lendo arquivo XML... (pode demorar)")
        
        with open(xml_path, 'rb') as f:
            xml_data = f.read()
            
        print(f"📊 Tamanho: {len(xml_data):,} bytes")
        print("⚙️ Processando XML...")
        
        # Usar a função existente
        data = parse_pricrpt(xml_data)
        
        print(f"✅ Total de registros processados: {len(data)}")
        
        # Mostrar primeiros registros
        print(f"\n📋 PRIMEIROS 10 REGISTROS:")
        print("-" * 80)
        for i, record in enumerate(data[:10]):
            if 'symbol' in record:
                print(f"{i+1:2d}. {record['symbol']}: "
                      f"First=R${record.get('first_price', 0):.2f} | "
                      f"Last=R${record.get('last_price', 0):.2f} | "
                      f"Volume={record.get('volume', 0):,}")
        
        # Buscar ativos específicos
        print(f"\n🎯 BUSCANDO ATIVOS ESPECÍFICOS:")
        print("-" * 80)
        ativos_busca = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3']
        
        encontrados = 0
        for record in data:
            if 'symbol' in record and record['symbol'] in ativos_busca:
                print(f"✅ {record['symbol']}: "
                      f"Abertura=R${record.get('first_price', 0):.2f} | "
                      f"Fechamento=R${record.get('last_price', 0):.2f} | "
                      f"Volume={record.get('volume', 0):,}")
                encontrados += 1
        
        if encontrados == 0:
            print("❌ Nenhum ativo específico encontrado")
            print("\n📊 Mostrando todos os símbolos únicos encontrados:")
            symbols = set()
            for record in data:
                if 'symbol' in record:
                    symbols.add(record['symbol'])
            
            for symbol in sorted(list(symbols))[:20]:
                print(f"  - {symbol}")
                
    except Exception as e:
        print(f"💥 Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()