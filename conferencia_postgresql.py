# Arquivo para conferir se os dados foram realmente inseridos no PostgreSQL

from sqlalchemy import text
from db_write import get_engine

SQL = """
select "Ativo","DataPregao","Abertura","Fechamento","PrecoMin","PrecoMax","Volume"
from b3.cotacoes
order by "DataPregao" desc, "Ativo" asc
limit 15;
"""

def main():
    eng = get_engine()
    with eng.connect() as c:
        rows = c.execute(text(SQL)).fetchall()
        # printa bonitinho
        print(f"{'Ativo':<12} {'DataPregao':<12} {'Abert':>8} {'Fech':>8} {'Min':>8} {'Max':>8} {'Vol':>14}")
        print("-"*72)
        for r in rows:
            print(f"{r.Ativo:<12} {r.DataPregao:%Y-%m-%d} "
                  f"{(r.Abertura or 0):>8} {(r.Fechamento or 0):>8} "
                  f"{(r.PrecoMin or 0):>8} {(r.PrecoMax or 0):>8} "
                  f"{(r.Volume or 0):>14}")

if __name__ == "__main__":
    main()
