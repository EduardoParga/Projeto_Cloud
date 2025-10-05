#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import List, Dict, Optional

from lxml import etree
from db_write import persist_quotes
from load_azure import get_file_from_blob

# TODO XML hardcoded (trocarei depois)
FILE_NAME = "BVBG.186.01_BV000471202510030001000062018462640.xml"

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
    """Extrai 1 linha por <PricRpt> (namespace-agnóstico)."""
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
        dt    = first_text(pr, './/*[local-name()="TradDt"]/*[local-name()="Dt"][1]/text()') \
                or first_text(pr, './/*[local-name()="TradDt"][1]/text()')
        if not (ativo and dt):
            continue

        abertura   = to_decimal(first_text(pr, './/*[local-name()="FrstPric"][1]/text()'))
        fechamento = to_decimal(first_text(pr, './/*[local-name()="LastPric"][1]/text()'))
        precomin   = to_decimal(first_text(pr, './/*[local-name()="MinPric"][1]/text()'))
        precomax   = to_decimal(first_text(pr, './/*[local-name()="MaxPric"][1]/text()'))
        volume     = to_decimal(first_text(pr, './/*[local-name()="NtlFinVol"][1]/text()')) # TODO confirmar tag de volume

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

def main():
    content = get_file_from_blob(FILE_NAME)
    xml_bytes = content if isinstance(content, (bytes, bytearray)) else content.encode("utf-8", errors="ignore")
    rows = parse_pricrpt(xml_bytes)
    if not rows:
        print(f"[WARN] 0 linha(s) extraída(s) de {FILE_NAME}")
        return
    persist_quotes(rows)
    print(f"[OK] Gravadas {len(rows)} linha(s) de {FILE_NAME}")

if __name__ == "__main__":
    main()
