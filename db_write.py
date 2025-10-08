import os
import sys
from typing import List, Dict
import psycopg2
from psycopg2.extras import execute_values

PG_HOST = os.environ.get("POSTGRES_HOST", "localhost")
PG_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
PG_DB = os.environ.get("POSTGRES_DB", "postgres")
PG_USER = os.environ.get("POSTGRES_USER", "postgres")
PG_PASS = os.environ.get("POSTGRES_PASSWORD", "postgres")

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS quotes (
  id SERIAL PRIMARY KEY,
  ticker TEXT NOT NULL,
  trade_date DATE NOT NULL,
  open NUMERIC,
  close NUMERIC,
  low NUMERIC,
  high NUMERIC,
  volume NUMERIC
);
"""

INSERT_SQL = """
INSERT INTO quotes (ticker, trade_date, open, close, low, high, volume)
VALUES %s
ON CONFLICT DO NOTHING;
"""

def _connect():
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
    )

def persist_quotes(rows: List[Dict]):
    if not rows:
        return
    vals = []
    for r in rows:
        vals.append((
            r.get("Ativo"),
            r.get("DataPregao"),
            r.get("Abertura"),
            r.get("Fechamento"),
            r.get("PrecoMin"),
            r.get("PrecoMax"),
            r.get("Volume"),
        ))
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(CREATE_SQL)
        execute_values(cur, INSERT_SQL, vals, template=None, page_size=100)
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] persist_quotes: {e}", file=sys.stderr)
        raise
    finally:
        conn.close()