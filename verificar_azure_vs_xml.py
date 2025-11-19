#!/usr/bin/env python3
# Verificação: Azure Function vs XML B3 Real

import sys
import os
sys.path.append('.')
import requests
import json
from extract_xml import parse_pricrpt

def verificar_azure_vs_xml():
    """Compara dados da Azure Function com XML real da B3"""
    
    print("🔍 VERIFICAÇÃO: AZURE FUNCTION vs XML B3 REAL")
    print("=" * 80)
    
    # 1. Buscar dados da Azure Function
    print("📡 1. BUSCANDO DADOS DA AZURE FUNCTION...")
    try:
        response = requests.get("https://func-b3-test.azurewebsites.net/api/dados")
        azure_data = response.json()
        print(f"✅ Azure API: {len(azure_data['dados'])} registros")
        print(f"   Fonte: {azure_data['fonte']}")
    except Exception as e:
        print(f"❌ Erro na API Azure: {e}")
        return
    
    # 2. Extrair dados do XML real
    print("\n📄 2. EXTRAINDO DADOS DO XML B3 REAL...")
    xml_path = 'dados_b3/ARQUIVOSPREGAO_SPRE251007/BVBG.186.01_BV000471202510070001000061921366800.xml'
    
    try:
        with open(xml_path, 'rb') as f:
            xml_data = f.read()
        
        xml_cotacoes = parse_pricrpt(xml_data)
        print(f"✅ XML B3: {len(xml_cotacoes)} registros")
        
    except Exception as e:
        print(f"❌ Erro no XML: {e}")
        return
    
    # 3. Filtrar ativos principais para comparação
    ativos_principais = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3', 'MGLU3', 'WEGE3', 'GGBR4']
    
    print(f"\n🎯 3. COMPARAÇÃO DOS ATIVOS PRINCIPAIS:")
    print("=" * 80)
    print(f"{'ATIVO':<8} | {'AZURE ABERTURA':<15} | {'XML ABERTURA':<15} | {'AZURE VOLUME':<15} | {'XML VOLUME':<15} | {'STATUS':<10}")
    print("-" * 80)
    
    # Organizar dados do Azure por símbolo
    azure_dict = {}
    for item in azure_data['dados']:
        azure_dict[item['simbolo']] = item
    
    # Organizar dados do XML por ativo
    xml_dict = {}
    for item in xml_cotacoes:
        ativo = item.get('Ativo', '')
        if ativo in ativos_principais:
            xml_dict[ativo] = item
    
    # Comparar ativo por ativo
    total_ativos = 0
    ativos_corretos = 0
    ativos_diferentes = 0
    ativos_faltando_azure = 0
    ativos_faltando_xml = 0
    
    for ativo in ativos_principais:
        total_ativos += 1
        
        azure_item = azure_dict.get(ativo)
        xml_item = xml_dict.get(ativo)
        
        if azure_item and xml_item:
            # Ambos existem - comparar valores
            azure_abertura = azure_item['abertura']
            xml_abertura = float(xml_item.get('Abertura', 0))
            azure_volume = azure_item['volume']
            xml_volume = int(xml_item.get('Volume', 0))
            
            # Verificar se são similares (tolerância de ±1% para preços)
            abertura_similar = abs(azure_abertura - xml_abertura) <= (xml_abertura * 0.01)
            volume_igual = azure_volume == xml_volume
            
            if abertura_similar and volume_igual:
                status = "✅ OK"
                ativos_corretos += 1
            else:
                status = "❌ DIFF"
                ativos_diferentes += 1
            
            print(f"{ativo:<8} | R$ {azure_abertura:<12.2f} | R$ {xml_abertura:<12.2f} | {azure_volume:<13,} | {xml_volume:<13,} | {status}")
            
        elif azure_item and not xml_item:
            ativos_faltando_xml += 1
            print(f"{ativo:<8} | R$ {azure_item['abertura']:<12.2f} | {'FALTA NO XML':<15} | {azure_item['volume']:<13,} | {'FALTA NO XML':<15} | ❌ XML")
            
        elif xml_item and not azure_item:
            ativos_faltando_azure += 1
            print(f"{ativo:<8} | {'FALTA AZURE':<15} | R$ {float(xml_item.get('Abertura', 0)):<12.2f} | {'FALTA AZURE':<15} | {int(xml_item.get('Volume', 0)):<13,} | ❌ AZURE")
            
        else:
            print(f"{ativo:<8} | {'NÃO ENCONTRADO':<15} | {'NÃO ENCONTRADO':<15} | {'N/A':<15} | {'N/A':<15} | ❌ AMBOS")
    
    # 4. Estatísticas da comparação
    print("\n" + "=" * 80)
    print("📊 4. ESTATÍSTICAS DA VERIFICAÇÃO:")
    print("-" * 40)
    print(f"Total de ativos verificados: {total_ativos}")
    print(f"✅ Dados corretos/similares: {ativos_corretos}")
    print(f"❌ Dados diferentes: {ativos_diferentes}")
    print(f"❌ Faltando no XML: {ativos_faltando_xml}")
    print(f"❌ Faltando na Azure: {ativos_faltando_azure}")
    
    # 5. Conclusão
    print(f"\n🎯 5. CONCLUSÃO:")
    print("-" * 40)
    
    if ativos_corretos == total_ativos:
        print("✅ PERFEITO! Todos os dados da Azure batem com o XML B3!")
    elif ativos_corretos > 0:
        print(f"⚠️ PARCIAL: {ativos_corretos}/{total_ativos} ativos corretos")
        if ativos_diferentes > 0:
            print("💡 Alguns valores estão diferentes - pode ser problema no processamento")
        if ativos_faltando_azure > 0:
            print("💡 Alguns ativos não chegaram na Azure - verificar blob processor")
        if ativos_faltando_xml > 0:
            print("💡 Azure tem dados que não estão no XML - pode ser dados antigos")
    else:
        print("❌ PROBLEMA! Nenhum dado bate - verificar todo o pipeline")
    
    # 6. Detalhes adicionais do XML para debug
    print(f"\n🔍 6. AMOSTRA DO XML B3 (primeiros 5 ativos encontrados):")
    print("-" * 60)
    count = 0
    for item in xml_cotacoes:
        if count >= 5:
            break
        ativo = item.get('Ativo', 'N/A')
        abertura = item.get('Abertura', 'N/A')
        volume = item.get('Volume', 'N/A')
        data = item.get('DataPregao', 'N/A')
        print(f"  {ativo}: Abertura=R${abertura} | Volume={volume:,} | Data={data}")
        count += 1

if __name__ == '__main__':
    verificar_azure_vs_xml()