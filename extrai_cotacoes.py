from azure_storage import get_file_from_blob
from lxml import etree
import io

DATA_FILE = "250923"
FILE_NAME = f"BVBG186_{DATA_FILE}.xml"

def transform():
    xml_storage_file = get_file_from_blob(FILE_NAME)
    xml_bytes = io.BytesIO(xml_storage_file.encode('utf-8'))

    ns = "{urn:bvmf.217.01.xsd}"

    # Itera sobre cada relatório de preço (Pregão à vista)
    for _, pricrpt in etree.iterparse(xml_bytes, tag=f"{ns}PricRpt", huge_tree=True):
        # Nome da ação
        nome_acao = pricrpt.find(f".//{ns}TckrSymb")
        # Data da negociação
        data_negociacao = pricrpt.find(f".//{ns}Dt")
        # Detalhes das negociações (quantidade de negócios)
        detalhes = pricrpt.find(f".//{ns}RglrTxsQty")
        # Preço abertura
        preco_abertura = pricrpt.find(f".//{ns}FrstPric")
        # Preço mínimo
        preco_minimo = pricrpt.find(f".//{ns}MinPric")
        # Preço máximo
        preco_maximo = pricrpt.find(f".//{ns}MaxPric")
        # Preço fechamento
        preco_fechamento = pricrpt.find(f".//{ns}LastPric")

        print({
            "nome_acao": nome_acao.text if nome_acao is not None else None,
            "data_negociacao": data_negociacao.text if data_negociacao is not None else None,
            "detalhes": detalhes.text if detalhes is not None else None,
            "preco_abertura": preco_abertura.text if preco_abertura is not None else None,
            "preco_minimo": preco_minimo.text if preco_minimo is not None else None,
            "preco_maximo": preco_maximo.text if preco_maximo is not None else None,
            "preco_fechamento": preco_fechamento.text if preco_fechamento is not None else None
        })

transform()