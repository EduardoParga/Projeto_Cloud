import psycopg2, sys
try:
    conn = psycopg2.connect(host='127.0.0.1', port=5432, dbname='postgres', user='postgres', password='postgres')
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('public.quotes');")
    print("table:", cur.fetchone())
    cur.execute("SELECT count(*) FROM quotes;")
    print("rows in quotes:", cur.fetchone())
    cur.execute("SELECT ticker, trade_date, open, close, volume FROM quotes ORDER BY trade_date DESC LIMIT 5;")
    for r in cur.fetchall():
        print(r)
    cur.close()
    conn.close()
except Exception as e:
    print("Erro conexão/consulta Postgres:", e)
    sys.exit(1)