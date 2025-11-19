#!/usr/bin/env python3
# Script para extrair dados manualmente do arquivo XML B3

import sys
import os
import zipfile
from lxml import etree
from io import BytesIO
from decimal import Decimal

def extrair_xml_b3():
    """Extrai dados do arquivo XML B3 manualmente"""
    
    # Caminho para o arquivo XML
    xml_path = "dados_b3/ARQUIVOSPREGAO_SPRE251007/BVBG.186.01_BV000471202510070001000061921366800.xml"
    
    if not os.path.exists(xml_path):
        print(f"❌ Arquivo não encontrado: {xml_path}")
        return
    
    print("🔍 EXTRAÇÃO MANUAL DO ARQUIVO XML B3")
    print(f"📁 Arquivo: {xml_path}")
    print("=" * 80)
    
    try:
        # Ler arquivo em chunks para evitar problemas de memória
        print("📖 Lendo arquivo XML... (arquivo grande, aguarde)")
        
        with open(xml_path, 'rb') as f:
            # Ler primeiros 50MB para teste
            chunk_size = 50 * 1024 * 1024  # 50MB
            xml_chunk = f.read(chunk_size)
        
        print(f"📊 Lido: {len(xml_chunk):,} bytes")
        
        # Procurar por elementos PricRpt (cotações)
        processar_xml_chunk(xml_chunk)
        
    except Exception as e:
        print(f"💥 Erro: {str(e)}")

def processar_xml_chunk(xml_bytes):
    """Processa chunk do XML para extrair cotações"""
    
    try:
        # Parse do XML
        tree = etree.parse(BytesIO(xml_bytes), etree.XMLParser(recover=True, huge_tree=True))
        
        # Buscar elementos PricRpt
        pricrpts = tree.xpath('//*[local-name()="PricRpt"]')
        print(f"📋 Encontrados {len(pricrpts)} registros PricRpt")
        
        ativos_principais = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3', 'MGLU3', 'WEGE3', 'JBSS3']
        cotacoes_encontradas = []
        
        print(f"\n🔍 Buscando ativos: {', '.join(ativos_principais)}")
        print("=" * 80)
        
        for i, pricrpt in enumerate(pricrpts[:100]):  # Processar só os primeiros 100
            try:
                # Extrair símbolo
                symbol_elem = pricrpt.xpath('.//*[local-name()="FinInstrmId"]/*[local-name()="Othr"]/*[local-name()="Id"]')
                if not symbol_elem:
                    continue
                    
                symbol = symbol_elem[0].text.strip()
                
                if symbol not in ativos_principais:
                    continue
                
                # Extrair preços
                first_price_elem = pricrpt.xpath('.//*[local-name()="FrstPric"]/*[local-name()="Amt"]')
                last_price_elem = pricrpt.xpath('.//*[local-name()="LastPric"]/*[local-name()="Amt"]')
                
                # Extrair volume
                ttl_vol_elem = pricrpt.xpath('.//*[local-name()="TtlVol"]')
                
                if first_price_elem and last_price_elem and ttl_vol_elem:
                    first_price = float(first_price_elem[0].text)
                    last_price = float(last_price_elem[0].text)
                    volume = int(float(ttl_vol_elem[0].text))
                    
                    cotacao = {
                        'symbol': symbol,
                        'first_price': first_price,
                        'last_price': last_price,
                        'volume': volume
                    }
                    
                    cotacoes_encontradas.append(cotacao)
                    print(f"✅ {symbol}: Abertura=R${first_price:.2f} | Fechamento=R${last_price:.2f} | Volume={volume:,}")
                    
            except Exception as e:
                continue
        
        print("=" * 80)
        print(f"🎯 Total encontrado: {len(cotacoes_encontradas)} ativos")
        
        if cotacoes_encontradas:
            print(f"\n📋 RESUMO DOS DADOS EXTRAÍDOS:")
            print("-" * 80)
            for cot in cotacoes_encontradas:
                print(f"{cot['symbol']}: Abertura=R${cot['first_price']:.2f} | "
                      f"Fechamento=R${cot['last_price']:.2f} | Volume={cot['volume']:,}")
                      
            print(f"\n💾 COMPARAÇÃO COM AZURE SQL:")
            print("-" * 80)
            print("Azure SQL atual:")
            print("ITUB4: Abertura=R$28.90 | Fechamento=R$29.20 | Volume=1,200,000")
            print("PETR4: Abertura=R$35.50 | Fechamento=R$36.20 | Volume=1,000,000") 
            print("VALE3: Abertura=R$62.30 | Fechamento=R$63.10 | Volume=800,000")
        else:
            print("❌ Nenhum ativo principal encontrado!")
            
    except Exception as e:
        print(f"💥 Erro no processamento XML: {str(e)}")

if __name__ == '__main__':
    extrair_xml_b3()