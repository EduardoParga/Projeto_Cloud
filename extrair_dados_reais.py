#!/usr/bin/env python3
# Script para extrair valores reais do XML B3

import sys
import os
sys.path.append('.')

from extract_xml import parse_pricrpt

def main():
    xml_path = 'dados_b3/ARQUIVOSPREGAO_SPRE251007/BVBG.186.01_BV000471202510070001000061921366800.xml'
    
    print("=== EXTRAINDO DADOS REAIS DO ARQUIVO B3 ===")
    print(f"Arquivo: {xml_path}")
    
    try:
        with open(xml_path, 'rb') as f:
            data = parse_pricrpt(f.read())
        
        print(f"\nTotal de registros: {len(data)}")
        print("\n=== PRINCIPAIS ATIVOS ===")
        
        ativos_principais = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3', 'MGLU3', 'WEGE3', 'JBSS3']
        
        for ativo in ativos_principais:
            for record in data:
                if record['symbol'] == ativo:
                    print(f"{ativo}: Volume={record['volume']:,} | Fecha=R${record['last_price']} | Abertura=R${record['first_price']}")
                    break
            else:
                print(f"{ativo}: NÃO ENCONTRADO")
                
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == '__main__':
    main()