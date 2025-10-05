from sqlalchemy import create_engine, text

def get_engine():
    # ajuste a porta se mapeou diferente no Docker (ex.: 5433)
    return create_engine(
        "postgresql+psycopg://b3:b3pwd_local_mude@localhost:5432/b3db",
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
