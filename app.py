from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
CORS(app)

# Configuração do banco - MUDAR DEPOIS PARA O AZURE
DATABASE_URL = os.environ.get('DATABASE_URL', 
    'postgresql://b3:b3pwd_local_mude@localhost:5433/b3db')

def get_db_connection():
    try:
        # No Azure, usar SSL
        if 'postgres.database.azure.com' in DATABASE_URL:
            return psycopg2.connect(DATABASE_URL, sslmode='require')
        else:
            return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logging.error(f"Erro conexão BD: {e}")
        raise

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'API B3 funcionando!', 'status': 'OK'})

@app.route('/api/ativos', methods=['GET'])
def get_ativos():
    """Lista todos os ativos únicos"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT "Ativo" FROM b3.cotacoes ORDER BY "Ativo" LIMIT 100')
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
            SELECT "DataPregao", "Abertura", "Fechamento", "PrecoMin", "PrecoMax", "Volume"
            FROM b3.cotacoes 
            WHERE "Ativo" = %s AND "DataPregao" >= %s
            ORDER BY "DataPregao" DESC
            LIMIT 100
        ''', (ativo, start_date.date()))
        
        results = cur.fetchall()
        cotacoes = []
        for row in results:
            cotacoes.append({
                'data': row[0].isoformat(),
                'abertura': float(row[1]) if row[1] else None,
                'fechamento': float(row[2]) if row[2] else None,
                'minimo': float(row[3]) if row[3] else None,
                'maximo': float(row[4]) if row[4] else None,
                'volume': float(row[5]) if row[5] else None
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
                AVG("Fechamento") as preco_medio,
                MIN("PrecoMin") as menor_preco,
                MAX("PrecoMax") as maior_preco,
                SUM("Volume") as volume_total,
                MAX("DataPregao") as ultima_data
            FROM b3.cotacoes 
            WHERE "Ativo" = %s
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)