from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc
import os
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
CORS(app)

# Configuração do Azure SQL Database - DRIVER CORRETO
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

@app.route('/api/ativos', methods=['GET'])
def get_ativos():
    """Lista todos os ativos únicos"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT Ativo FROM Cotacoes ORDER BY Ativo')
        ativos = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'ativos': ativos, 'total': len(ativos)})
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar ativos: {str(e)}'}), 500

@app.route('/api/cotacoes/<ativo>', methods=['GET'])
def get_cotacoes_ativo(ativo):
    """Busca cotações de um ativo específico"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT DataPregao, Abertura, Fechamento, Volume
            FROM Cotacoes 
            WHERE Ativo = ? AND DataPregao >= ?
            ORDER BY DataPregao DESC
        ''', (ativo, start_date.date()))
        
        cotacoes = []
        for row in cur.fetchall():
            cotacoes.append({
                'data': row[0].isoformat() if row[0] else None,
                'abertura': float(row[1]) if row[1] else None,
                'fechamento': float(row[2]) if row[2] else None,
                'volume': float(row[3]) if row[3] else None
            })
        
        cur.close()
        conn.close()
        return jsonify({'ativo': ativo, 'cotacoes': cotacoes, 'total': len(cotacoes)})
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar cotações: {str(e)}'}), 500

@app.route('/api/resumo/<ativo>', methods=['GET'])
def get_resumo_ativo(ativo):
    """Resumo estatístico de um ativo"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT 
                COUNT(*) as total_registros,
                AVG(Fechamento) as preco_medio,
                MIN(Abertura) as menor_preco,
                MAX(Fechamento) as maior_preco,
                SUM(Volume) as volume_total,
                MAX(DataPregao) as ultima_data
            FROM Cotacoes 
            WHERE Ativo = ?
        ''', (ativo,))
        
        result = cur.fetchone()
        resumo = {
            'ativo': ativo,
            'total_registros': result[0],
            'preco_medio': float(result[1]) if result[1] else None,
            'menor_preco': float(result[2]) if result[2] else None,
            'maior_preco': float(result[3]) if result[3] else None,
            'volume_total': float(result[4]) if result[4] else None,
            'ultima_data': result[5].isoformat() if result[5] else None
        }
        
        cur.close()
        conn.close()
        return jsonify(resumo)
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar resumo: {str(e)}'}), 500

@app.route('/api/debug/drivers', methods=['GET'])
def debug_drivers():
    """Lista drivers ODBC disponíveis"""
    try:
        drivers = pyodbc.drivers()
        return jsonify({'drivers': drivers})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)