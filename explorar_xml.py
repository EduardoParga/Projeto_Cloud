#!/usr/bin/env python3
# Script para explorar o arquivo XML B3 e ver que símbolos existem

import sys
import os
from lxml import etree
from io import BytesIO
from collections import Counter

def explorar_xml_b3():
    """Explora o arquivo XML B3 para ver os símbolos disponíveis"""
    
    xml_path = "dados_b3/ARQUIVOSPREGAO_SPRE251007/BVBG.186.01_BV000471202510070001000061921366800.xml"
    
    print("🔍 EXPLORANDO ARQUIVO XML B3")
    print(f"📁 Arquivo: {xml_path}")
    print("=" * 80)
    
    try:
        with open(xml_path, 'rb') as f:
            # Ler chunk maior para ter mais dados
            chunk_size = 100 * 1024 * 1024  # 100MB
            xml_chunk = f.read(chunk_size)
        
        print(f"📊 Lido: {len(xml_chunk):,} bytes")
        
        # Parse do XML
        tree = etree.parse(BytesIO(xml_chunk), etree.XMLParser(recover=True, huge_tree=True))
        
        # Buscar TODOS os símbolos para ver o que tem
        symbols = []
        pricrpts = tree.xpath('//*[local-name()="PricRpt"]')[:200]  # Primeiro 200
        
        print(f"📋 Analisando {len(pricrpts)} registros...")
        
        for pricrpt in pricrpts:
            try:
                # Diferentes formas de encontrar o símbolo
                symbol_paths = [
                    './/*[local-name()="FinInstrmId"]/*[local-name()="Othr"]/*[local-name()="Id"]',
                    './/*[local-name()="FinInstrmId"]/*[local-name()="Id"]',
                    './/*[local-name()="Symb"]',
                    './/*[local-name()="Nm"]'
                ]
                
                symbol = None
                for path in symbol_paths:
                    elem = pricrpt.xpath(path)
                    if elem and elem[0].text:
                        symbol = elem[0].text.strip()
                        if len(symbol) >= 4:  # Símbolos válidos
                            break
                
                if symbol:
                    symbols.append(symbol)
                    
                    # Se encontrou um símbolo interessante, mostrar detalhes
                    if any(s in symbol.upper() for s in ['ITUB', 'PETR', 'VALE', 'BBDC']):
                        print(f"🎯 ENCONTRADO: {symbol}")
                        mostrar_detalhes_registro(pricrpt)
                        
            except Exception as e:
                continue
        
        # Mostrar estatísticas
        symbol_counter = Counter(symbols)
        print(f"\n📊 SÍMBOLOS ENCONTRADOS (Top 20):")
        print("-" * 60)
        for symbol, count in symbol_counter.most_common(20):
            print(f"{symbol}: {count} registros")
            
        # Procurar por padrões conhecidos
        print(f"\n🔍 PROCURANDO PADRÕES CONHECIDOS:")
        print("-" * 60)
        padroes = ['ITUB', 'PETR', 'VALE', 'BBDC', 'ABEV', 'MGLU']
        for padrao in padroes:
            matches = [s for s in symbols if padrao in s.upper()]
            if matches:
                print(f"{padrao}: {matches}")
            else:
                print(f"{padrao}: ❌ não encontrado")
                
    except Exception as e:
        print(f"💥 Erro: {str(e)}")

def mostrar_detalhes_registro(pricrpt):
    """Mostra detalhes de um registro específico"""
    try:
        # Buscar todos os elementos filhos
        for child in pricrpt:
            if hasattr(child, 'tag') and hasattr(child, 'text'):
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if child.text and child.text.strip():
                    print(f"    {tag_name}: {child.text.strip()}")
        print("    " + "-" * 40)
    except Exception as e:
        print(f"    Erro ao mostrar detalhes: {e}")

if __name__ == '__main__':
    explorar_xml_b3()