from azure_storage import get_file_from_blob
from lxml import etree
import io

DATA_FILE = "250923"
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
    local_path = f"./{FILE_NAME}"
    get_file_from_blob(FILE_NAME, local_path)

    with open(local_path, "rb") as f:
        xml_bytes = f.read()

    tree = etree.parse(io.BytesIO(xml_bytes), etree.XMLParser(recover=True, huge_tree=True))
    pricrpts = tree.xpath('//*[local-name()="PricRpt"]')

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
        ent = find_by_localname(pr, "Ent")  

        print(
            f"Ação: {nome_acao}, "
            f"Data: {data_negociacao}, "
            f"Abertura: {preco_abertura}, "
            f"Fechamento: {preco_fechamento}, "
            f"Min: {preco_min}, "
            f"Max: {preco_max}, "
            f"Volume: {volume}, "
            f"Ent: {ent}"
        )

transform()