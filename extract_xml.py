from azure_storage import get_file_from_blob
from lxml import etree
import io
import csv
from datetime import datetime
from helpers import yymmdd

DATA_FILE = yymmdd(datetime.now())
FILE_NAME = f"BVBG186_{DATA_FILE}.xml"

def to_decimal(x):
    if x is None:
        return None
    s = str(x).strip().replace(",", ".")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None

def find_by_localname(element, name):
    for child in element.iterdescendants():
        if etree.QName(child).localname == name:
            return child.text
    return None

def transform():
    xml_bytes = get_file_from_blob(FILE_NAME)
    if not xml_bytes:
        print("Arquivo não encontrado ou vazio no Blob Storage.")
        return

    tree = etree.parse(io.BytesIO(xml_bytes), etree.XMLParser(recover=True, huge_tree=True))
    pricrpts = tree.xpath('//*[local-name()="PricRpt"]')

    with open("resultados.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Ação", "Data", "Abertura", "Fechamento", "Min", "Max", "Volume"])
        for pr in pricrpts:
            nome_acao = find_by_localname(pr, "TckrSymb")
            data_negociacao = find_by_localname(pr, "Dt")
            preco_abertura = find_by_localname(pr, "FrstPric")
            preco_fechamento = find_by_localname(pr, "LastPric")
            preco_min = find_by_localname(pr, "MinPric")
            preco_max = find_by_localname(pr, "MaxPric")
            volume = find_by_localname(pr, "NtlFinVol")
            if volume is None:
                volume = find_by_localname(pr, "TradQty")
            if volume is None:
                volume = find_by_localname(pr, "FinQty")
            if volume is None:
                volume = find_by_localname(pr, "TotTradQty")

            if nome_acao and data_negociacao:
                writer.writerow([
                    nome_acao,
                    data_negociacao,
                    preco_abertura,
                    preco_fechamento,
                    preco_min,
                    preco_max,
                    volume
                ])

transform()