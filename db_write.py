<<<<<<< HEAD
from sqlalchemy import create_engine, text

def get_engine():
    # mudando porta para 5433 para não conflitar com projeto de Big Data
    return create_engine(
        "postgresql+psycopg://b3:b3pwd_local_mude@localhost:5433/b3db",
        echo=True  # mostra os INSERT/UPDATE no terminal
    )

UPSERT_SQL = """
insert into b3.cotacoes
("Ativo","DataPregao","Abertura","Fechamento","PrecoMin","PrecoMax","Volume")
values
(:Ativo,:DataPregao,:Abertura,:Fechamento,:PrecoMin,:PrecoMax,:Volume)
on conflict ("Ativo","DataPregao") do update set
  "Abertura"   = excluded."Abertura",
  "Fechamento" = excluded."Fechamento",
  "PrecoMin"   = excluded."PrecoMin",
  "PrecoMax"   = excluded."PrecoMax",
  "Volume"     = excluded."Volume";
"""

def persist_quotes(rows, batch=2000):
    eng = get_engine()
    with eng.begin() as con:
        con.execute(text("set search_path to b3,public"))
        # grava em lotes para não mandar 30k+ linhas de uma vez
        for i in range(0, len(rows), batch):
            con.execute(text(UPSERT_SQL), rows[i:i+batch])
=======
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
>>>>>>> c5b4dfd60e268e8c5bb06c8bdafaf9d1eb16fd14
