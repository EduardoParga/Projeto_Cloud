# init_db.py
from sqlalchemy import text
from db_write import get_engine

SCHEMA_SQL = "create schema if not exists b3;"

TABLE_SQL = """
create table if not exists b3.cotacoes(
   id bigserial primary key,
   "Ativo"       varchar(20) not null,
   "DataPregao"  date        not null,
   "Abertura"    numeric(10,2),
   "Fechamento"  numeric(10,2),
   "PrecoMin"    numeric(10,2),
   "PrecoMax"    numeric(10,2),
   "Volume"      numeric(18,2)
);
"""

# Basta um índice único para permitir ON CONFLICT ("Ativo","DataPregao")
UNIQUE_IDX_SQL = """
create unique index if not exists uq_cotacoes_ativo_data
  on b3.cotacoes("Ativo","DataPregao");
"""

INDEX_SQL = """
create index if not exists idx_cotacoes_datapregao
  on b3.cotacoes("DataPregao");
"""

def main():
    eng = get_engine()
    with eng.begin() as con:
        # evita travar para sempre se algo bloquear
        con.execute(text("set local statement_timeout = '15s'"))
        con.execute(text("set search_path to b3,public"))

        con.execute(text(SCHEMA_SQL))
        con.execute(text(TABLE_SQL))
        con.execute(text(UNIQUE_IDX_SQL))
        con.execute(text(INDEX_SQL))

    print("[OK] Schema/tabela/índices garantidos.")

if __name__ == "__main__":
    main()
