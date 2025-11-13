from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import List, Dict, Optional
import os
import sys
import csv
import glob

from lxml import etree

POINTER_BLOB = "_LATEST_B3_XML.txt" 
LOCAL_POINTER = os.path.join("dados_b3", POINTER_BLOB)


try:
    from azure_storage import get_file_from_blob
except Exception:
    get_file_from_blob = None

try:
    from db_write import persist_quotes
except Exception:
    persist_quotes = None


def to_decimal(x) -> Optional[Decimal]:
    if x is None:
        return None
    s = str(x).strip().replace(",", ".")
    if not s:
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def to_date(s: str) -> date:
    if "T" in s:
        s = s.split("T", 1)[0]
    return datetime.strptime(s, "%Y-%m-%d").date()


def parse_pricrpt(xml_bytes: bytes) -> List[Dict]:

    
    tree = etree.parse(BytesIO(xml_bytes), etree.XMLParser(recover=True, huge_tree=True))
    pricrpts = tree.xpath('//*[local-name()="PricRpt"]')

    def first_text(node, xp: str) -> str:
        v = node.xpath(xp)
        if isinstance(v, list):
            v = v[0] if v else ""
        return (v or "").strip()

    rows: List[Dict] = []
    for pr in pricrpts:
        ativo = first_text(pr, './/*[local-name()="TckrSymb"][1]/text()')
        dt = first_text(pr, './/*[local-name()="TradDt"]/*[local-name()="Dt"][1]/text()') \
             or first_text(pr, './/*[local-name()="TradDt"][1]/text()')
        if not (ativo and dt):
            continue

       
        frst = first_text(pr, './/*[local-name()="FrstPric"][1]/text()')
        last = first_text(pr, './/*[local-name()="LastPric"][1]/text()')
        minp = first_text(pr, './/*[local-name()="MinPric"][1]/text()')
        maxp = first_text(pr, './/*[local-name()="MaxPric"][1]/text()')
        tradavg = first_text(pr, './/*[local-name()="TradAvrgPric"][1]/text()')

        ntlfinvol = first_text(pr, './/*[local-name()="NtlFinVol"][1]/text()')
        rglrtxsqty = first_text(pr, './/*[local-name()="RglrTxsQty"][1]/text()')
        opn_intrst = first_text(pr, './/*[local-name()="OpnIntrst"][1]/text()')

        # decidir se é mercado à vista:
        has_price = any(bool(x) for x in (frst, last, minp, maxp, tradavg))
        has_trade_volume = bool(ntlfinvol or rglrtxsqty)
     
        if not (has_price or has_trade_volume):
        
            continue
        if (not has_price) and opn_intrst and not has_trade_volume:
          
            continue

        abertura = to_decimal(frst)
        fechamento = to_decimal(last)
        precomin = to_decimal(minp)
        precomax = to_decimal(maxp)
        volume = to_decimal(ntlfinvol or rglrtxsqty)

        rows.append({
            "Ativo": ativo,
            "DataPregao": to_date(dt),
            "Abertura": abertura,
            "Fechamento": fechamento,
            "PrecoMin": precomin,
            "PrecoMax": precomax,
            "Volume": volume
        })
    return rows


def _read_pointer() -> Optional[str]:
    
    if get_file_from_blob:
        try:
            ptr = get_file_from_blob(POINTER_BLOB)
            if isinstance(ptr, (bytes, bytearray)):
                ptr = ptr.decode("utf-8", errors="ignore")
            name = str(ptr).strip()
            if name:
                print(f"[INFO] Ponteiro lido do blob: {name}")
                return name
        except Exception as e:
            print(f"[INFO] Não foi possível ler ponteiro do blob: {e}", file=sys.stderr)

    try:
        if os.path.exists(LOCAL_POINTER):
            with open(LOCAL_POINTER, "r", encoding="utf-8") as f:
                name = f.read().strip()
                if name:
                    print(f"[INFO] Ponteiro lido local: {name}")
                    return name
    except Exception as e:
        print(f"[INFO] Falha lendo ponteiro local: {e}", file=sys.stderr)

    return None


def _get_xml_bytes(name: str) -> Optional[bytes]:
    # tenta baixar do blob se disponível
    if get_file_from_blob:
        try:
            content = get_file_from_blob(name)
            if isinstance(content, str):
                content = content.encode("utf-8", errors="ignore")
            print(f"[OK] Blob {name} obtido do storage.")
            return content
        except Exception as e:
            print(f"[INFO] Falha ao obter blob {name}: {e}", file=sys.stderr)

    # fallback local direto
    local_path = os.path.join("dados_b3", name)
    if os.path.exists(local_path):
        try:
            with open(local_path, "rb") as f:
                print(f"[OK] Arquivo {local_path} lido localmente.")
                return f.read()
        except Exception as e:
            print(f"[INFO] Falha lendo local {local_path}: {e}", file=sys.stderr)

    # busca recursiva dentro de dados_b3 (procura por mesmo nome ou por basename)
    try:
        pattern_exact = os.path.join("dados_b3", "**", name)
        matches = glob.glob(pattern_exact, recursive=True)
        if matches:
            path = matches[0]
            with open(path, "rb") as f:
                print(f"[OK] Arquivo encontrado recursivamente: {path}")
                return f.read()

        basename = os.path.basename(name)
        if basename != name:
            pattern_basename = os.path.join("dados_b3", "**", basename)
            matches2 = glob.glob(pattern_basename, recursive=True)
            if matches2:
                path = matches2[0]
                with open(path, "rb") as f:
                    print(f"[OK] Arquivo encontrado por basename: {path}")
                    return f.read()
    except Exception as e:
        print(f"[INFO] Erro ao procurar recursivamente por {name}: {e}", file=sys.stderr)

    return None


def _save_csv_fallback(rows: List[Dict], blob_name: str):
    os.makedirs("out", exist_ok=True)
    base = os.path.splitext(os.path.basename(blob_name or "local"))[0]
    out_path = os.path.join("out", f"quotes_{base}.csv")
    fieldnames = ["Ativo", "DataPregao", "Abertura", "Fechamento", "PrecoMin", "PrecoMax", "Volume"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            rr = r.copy()
            rr["DataPregao"] = rr["DataPregao"].isoformat() if isinstance(rr["DataPregao"], date) else rr["DataPregao"]
            for k in ("Abertura", "Fechamento", "PrecoMin", "PrecoMax", "Volume"):
                v = rr.get(k)
                rr[k] = str(v) if v is not None else ""
            w.writerow(rr)
    print(f"[FALLBACK] CSV salvo em: {out_path}")


def main():
    pointer = _read_pointer()
    if not pointer:
        raise RuntimeError("Ponteiro vazio: _LATEST_B3_XML.txt não encontrado/no storage.")

    xml_bytes = _get_xml_bytes(pointer)
    if not xml_bytes:
        raise RuntimeError(f"Blob {pointer} não encontrado/pode não existir no storage ou localmente.")

    rows = parse_pricrpt(xml_bytes)
    if not rows:
        print(f"[WARN] 0 linha(s) extraída(s) de {pointer}")
        return

   
    if persist_quotes:
        try:
            persist_quotes(rows)
            print(f"[OK] Gravadas {len(rows)} linha(s) de {pointer}")
            return
        except Exception as e:
            print(f"[ERROR] persist_quotes falhou: {e}", file=sys.stderr)

    _save_csv_fallback(rows, pointer)


if __name__ == "__main__":
    main()