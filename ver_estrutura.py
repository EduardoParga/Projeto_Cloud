#!/usr/bin/env python3
# Script para ver a estrutura dos dados extraídos

import sys
import os
sys.path.append('.')

from extract_xml import parse_pricrpt

def main():
    xml_path = 'dados_b3/ARQUIVOSPREGAO_SPRE251007/BVBG.186.01_BV000471202510070001000061921366800.xml'
    
    print("🔍 ANALISANDO ESTRUTURA DOS DADOS")
    print("=" * 50)
    
    try:
        with open(xml_path, 'rb') as f:
            xml_data = f.read()
        
        data = parse_pricrpt(xml_data)
        print(f"✅ Total registros: {len(data)}")
        
        if data:
            print(f"\n📋 ESTRUTURA DO PRIMEIRO REGISTRO:")
            print("-" * 50)
            first_record = data[0]
            for key, value in first_record.items():
                print(f"{key}: {value}")
            
            print(f"\n📊 CAMPOS DISPONÍVEIS:")
            print("-" * 50)
            all_keys = set()
            for record in data[:10]:
                all_keys.update(record.keys())
            
            for key in sorted(all_keys):
                print(f"  - {key}")
                
            print(f"\n🔍 AMOSTRA DE DADOS (10 registros):")
            print("-" * 80)
            for i, record in enumerate(data[:10]):
                print(f"{i+1:2d}. {dict(list(record.items())[:3])}")
                
    except Exception as e:
        print(f"💥 Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()