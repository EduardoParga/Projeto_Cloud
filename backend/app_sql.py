from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc
import os
from datetime import datetime, timedelta
import logging
import urllib.parse

app = Flask(__name__)
CORS(app)

# Configuração do banco Azure SQL Server
DATABASE_URL = os.environ.get('DATABASE_URL', 
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=sqlb3server123.database.windows.net;DATABASE=b3database;UID=b3admin;PWD=SenhaSegura123!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')

def get_db_connection():
    try:
        return pyodbc.connect(DATABASE_URL)
    except Exception as e:
        logging.error(f"Erro conexão BD: {e}")
        raise

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'API B3 com Azure SQL funcionando!', 'status': 'OK'})

@app.route('/dados', methods=['GET'])
def get_dados():
    """Lista dados B3 processados"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT TOP 50 TpReg, Cod_Isin, Symb, Dt_Pregao, 
                   Prc_Aber, Prc_Min, Prc_Max, Prc_Ult, Qtd_Neg, Vol_Neg
            FROM B3_Dados 
            ORDER BY Dt_Pregao DESC, Symb
        ''')
        
        results = cursor.fetchall()
        dados = []
        for row in results:
            dados.append({
                'tipo_registro': row[0],
                'codigo_isin': row[1], 
                'simbolo': row[2],
                'data_pregao': row[3].strftime('%Y-%m-%d') if row[3] else None,
                'preco_abertura': float(row[4]) if row[4] else None,
                'preco_minimo': float(row[5]) if row[5] else None,
                'preco_maximo': float(row[6]) if row[6] else None,
                'preco_ultimo': float(row[7]) if row[7] else None,
                'quantidade_negociacoes': int(row[8]) if row[8] else None,
                'volume_negociacoes': float(row[9]) if row[9] else None
            })
        
        cursor.close()
        conn.close()
        return jsonify({'dados': dados, 'total': len(dados)})
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar dados: {str(e)}'}), 500

@app.route('/ativos', methods=['GET'])
def get_ativos():
    """Lista ativos únicos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT Symb 
            FROM B3_Dados 
            WHERE Symb IS NOT NULL 
            ORDER BY Symb
        ''')
        
        ativos = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({'ativos': ativos, 'total': len(ativos)})
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar ativos: {str(e)}'}), 500

@app.route('/ativo/<simbolo>', methods=['GET'])
def get_ativo_detalhes(simbolo):
    """Detalhes de um ativo específico"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT TOP 30 Dt_Pregao, Prc_Aber, Prc_Min, Prc_Max, Prc_Ult, Qtd_Neg, Vol_Neg
            FROM B3_Dados 
            WHERE Symb = ?
            ORDER BY Dt_Pregao DESC
        ''', simbolo)
        
        results = cursor.fetchall()
        cotacoes = []
        for row in results:
            cotacoes.append({
                'data': row[0].strftime('%Y-%m-%d') if row[0] else None,
                'abertura': float(row[1]) if row[1] else None,
                'minimo': float(row[2]) if row[2] else None,
                'maximo': float(row[3]) if row[3] else None,
                'fechamento': float(row[4]) if row[4] else None,
                'negocios': int(row[5]) if row[5] else None,
                'volume': float(row[6]) if row[6] else None
            })
        
        cursor.close()
        conn.close()
        return jsonify({'simbolo': simbolo, 'cotacoes': cotacoes, 'total': len(cotacoes)})
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar ativo: {str(e)}'}), 500

@app.route('/stats', methods=['GET'])
def get_estatisticas():
    """Estatísticas gerais dos dados"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_registros,
                COUNT(DISTINCT Symb) as total_ativos,
                MIN(Dt_Pregao) as data_inicial,
                MAX(Dt_Pregao) as data_final,
                SUM(Vol_Neg) as volume_total
            FROM B3_Dados
        ''')
        
        result = cursor.fetchone()
        stats = {
            'total_registros': result[0] if result[0] else 0,
            'total_ativos': result[1] if result[1] else 0,
            'data_inicial': result[2].strftime('%Y-%m-%d') if result[2] else None,
            'data_final': result[3].strftime('%Y-%m-%d') if result[3] else None,
            'volume_total': float(result[4]) if result[4] else 0
        }
        
        cursor.close()
        conn.close()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar estatísticas: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)