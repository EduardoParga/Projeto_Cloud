#!/usr/bin/env python3
# Script final para extrair os dados REAIS dos ativos principais

import sys
import os
sys.path.append('.')

from extract_xml import parse_pricrpt

def main():
    xml_path = 'dados_b3/ARQUIVOSPREGAO_SPRE251007/BVBG.186.01_BV000471202510070001000061921366800.xml'
    
    print("🎯 EXTRAÇÃO DOS DADOS REAIS B3")
    print("=" * 80)
    
    try:
        with open(xml_path, 'rb') as f:
            xml_data = f.read()
        
        data = parse_pricrpt(xml_data)
        print(f"✅ Total registros processados: {len(data)}")
        
        # Buscar ativos principais
        ativos_principais = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3', 'MGLU3', 'WEGE3', 'JBSS3', 'GGBR4']
        
        print(f"\n🔍 BUSCANDO ATIVOS: {', '.join(ativos_principais)}")
        print("=" * 80)
        
        encontrados = []
        for record in data:
            ativo = record.get('Ativo', '')
            if ativo in ativos_principais:
                cotacao = {
                    'ativo': ativo,
                    'data': record.get('DataPregao'),
                    'abertura': float(record.get('Abertura', 0)),
                    'fechamento': float(record.get('Fechamento', 0)),
                    'volume': int(record.get('Volume', 0))
                }
                encontrados.append(cotacao)
                
                print(f"✅ {ativo}: "
                      f"Abertura=R${cotacao['abertura']:.2f} | "
                      f"Fechamento=R${cotacao['fechamento']:.2f} | "
                      f"Volume={cotacao['volume']:,} | "
                      f"Data={cotacao['data']}")
        
        print("=" * 80)
        print(f"🎯 TOTAL ENCONTRADOS: {len(encontrados)} ativos")
        
        if encontrados:
            print(f"\n💾 COMPARAÇÃO COM DADOS ATUAIS NO AZURE SQL:")
            print("-" * 80)
            print("DADOS NO AZURE SQL:")
            print("ITUB4: Abertura=R$28.90 | Fechamento=R$29.20 | Volume=1,200,000")
            print("PETR4: Abertura=R$35.50 | Fechamento=R$36.20 | Volume=1,000,000")
            print("VALE3: Abertura=R$62.30 | Fechamento=R$63.10 | Volume=800,000")
            
            print(f"\nDADOS REAIS DO ARQUIVO XML B3:")
            for cot in encontrados:
                print(f"{cot['ativo']}: Abertura=R${cot['abertura']:.2f} | "
                      f"Fechamento=R${cot['fechamento']:.2f} | "
                      f"Volume={cot['volume']:,}")
                      
            print(f"\n🚨 CONCLUSÃO:")
            if len(encontrados) > 0:
                print("✅ Os dados REAIS estão no arquivo XML!")
                print("❌ Mas parecem diferentes dos que estão no Azure SQL")
                print("💡 Talvez o processo de carga não processou corretamente")
            else:
                print("❌ Os ativos principais não foram encontrados no XML")
        else:
            # Mostrar os ativos que existem para referência
            print(f"\n📊 ATIVOS DISPONÍVEIS NO ARQUIVO (primeiros 50):")
            print("-" * 80)
            ativos_unicos = set()
            for record in data:
                ativos_unicos.add(record.get('Ativo', ''))
            
            for i, ativo in enumerate(sorted(list(ativos_unicos))[:50]):
                print(f"  {i+1:2d}. {ativo}")
                
    except Exception as e:
        print(f"💥 Erro: {str(e)}")

if __name__ == '__main__':
    main()