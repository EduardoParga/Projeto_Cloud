
from load_azure import get_file_from_blob
from lxml import etree
import io

# AZURE_BLOB_CONNECTION = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
# BLOB_CONTAINER_BRUTOS = "b3-dados-brutos"

# def run():
#     service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
#     container = service.get_container_client(BLOB_CONTAINER_BRUTOS)

#     blobs = list(container.list_blobs())
#     if not blobs:
#         print("[ERRO] Nenhum arquivo encontrado no container!")
#         return

#     ultimo_blob = blobs[-1]
#     print(f"[INFO] Lendo arquivo: {ultimo_blob.name}")

#     blob_data = container.download_blob(ultimo_blob.name).readall()

#     # Parse manual usando ElementTree para pegar campos aninhados
#     ns = {
#         "bvmf": "urn:bvmf.217.01.xsd"
#     }
#     root = ET.fromstring(blob_data.decode("latin1"))
#     pricrpts = root.findall(".//bvmf:PricRpt", ns)

#     data = []
#     for pr in pricrpts:
#         trad_dt = pr.findtext("bvmf:TradDt/bvmf:Dt", default="", namespaces=ns)
#         tckr = pr.findtext("bvmf:SctyId/bvmf:TckrSymb", default="", namespaces=ns)
#         opn_intrst = pr.findtext("bvmf:FinInstrmAttrbts/bvmf:OpnIntrst", default="", namespaces=ns)
#         data.append({
#             "TradDt": trad_dt,
#             "TckrSymb": tckr,
#             "OpnIntrst": opn_intrst
#         })

#     df = pd.DataFrame(data)
#     print(df.head())
#     print("\nColunas disponíveis no DataFrame:")
#     print(df.columns)

# if __name__ == "__main__":
#     run()


file_name = "BVBG.186.01_BV000471202509240001000061923366930.xml"

def transform():
    xml_storage_file = get_file_from_blob(file_name)
    xml_bytes = io.BytesIO(xml_storage_file.encode('utf-8'))

#Buscar TckrSymb (nome das ações)
#Buscar TradDtls (detalhes das negociações)
#volume financeiro, preco min, preco max, preco abertura, preco fechamento, data negociacoes

    for _, elemxml in etree.iterparse(xml_bytes, tag='{urn:bvmf.217.01.xsd}TckrSymb', huge_tree=True):
        # Process each 'TckrSymb' element
        print(f'Ação: {elemxml.text}')


transform()