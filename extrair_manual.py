#!/usr/bin/env python3
# Script para extrair dados manualmente do arquivo B3

import sys
import os
import zipfile
from datetime import datetime

def extrair_arquivo_b3():
    """Extrai dados do arquivo B3 manualmente"""
    
    # Caminho para o arquivo ZIP
    zip_path = "dados_b3/ARQUIVOSPREGAO_SPRE251007/SPRE251007.zip"
    
    if not os.path.exists(zip_path):
        print(f"❌ Arquivo não encontrado: {zip_path}")
        return
    
    print("🔍 EXTRAÇÃO MANUAL DO ARQUIVO B3")
    print(f"📁 Arquivo: {zip_path}")
    print("=" * 50)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            print(f"📋 Arquivos no ZIP:")
            for file_name in zip_file.namelist():
                print(f"   - {file_name}")
            
            print("\n" + "=" * 50)
            
            # Procurar arquivo de cotação
            for file_name in zip_file.namelist():
                if file_name.upper().startswith('COTACAO') and file_name.endswith('.txt'):
                    print(f"📄 Processando: {file_name}")
                    
                    with zip_file.open(file_name) as txt_file:
                        conteudo = txt_file.read().decode('latin-1')
                        processar_cotacoes(conteudo)
                    break
            else:
                print("⚠️ Nenhum arquivo COTACAO*.txt encontrado")
                
    except Exception as e:
        print(f"💥 Erro: {str(e)}")

def processar_cotacoes(conteudo):
    """Processa o conteúdo do arquivo de cotações"""
    
    linhas = conteudo.strip().split('\n')
    print(f"\n📊 Total de linhas: {len(linhas)}")
    
    cotacoes = []
    ativos_principais = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3']
    
    print(f"\n🔍 Buscando ativos: {', '.join(ativos_principais)}")
    print("=" * 80)
    
    for i, linha in enumerate(linhas):
        if linha.startswith('01') and len(linha) >= 245:  # Registro de cotação
            try:
                # Extrair campos conforme layout B3
                ativo = linha[12:24].strip()
                data_str = linha[2:10]
                abertura = float(linha[56:69]) / 100  # Posição 57-69 (13 posições)
                fechamento = float(linha[108:121]) / 100  # Posição 109-121 (13 posições)
                volume = int(linha[170:188])  # Posição 171-188 (18 posições)
                
                if ativo in ativos_principais:
                    cotacao = {
                        'linha': i+1,
                        'ativo': ativo,
                        'data': f"{data_str[:4]}-{data_str[4:6]}-{data_str[6:8]}",
                        'abertura': abertura,
                        'fechamento': fechamento,
                        'volume': volume
                    }
                    cotacoes.append(cotacao)
                    
                    print(f"✅ {ativo}: Abertura=R${abertura:.2f} | Fechamento=R${fechamento:.2f} | Volume={volume:,}")
                    
            except (ValueError, IndexError) as e:
                continue
    
    print("=" * 80)
    print(f"🎯 Total encontrado: {len(cotacoes)} ativos")
    
    if cotacoes:
        print(f"\n📋 RESUMO DOS DADOS EXTRAÍDOS:")
        print("-" * 80)
        for cot in cotacoes:
            print(f"{cot['ativo']}: Data={cot['data']} | Abertura=R${cot['abertura']:.2f} | "
                  f"Fechamento=R${cot['fechamento']:.2f} | Volume={cot['volume']:,}")
    else:
        print("❌ Nenhum ativo principal encontrado!")

if __name__ == '__main__':
    extrair_arquivo_b3()