from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import re

ENDPOINT = "Seu endpoint aqui!"
KEY = "Sua chave aqui!"
DOCUMENT_URL = "URL blob do documento aqui!"

MODELOS = {
    "1": ("Documento geral", "prebuilt-document"),
    "2": ("Nota fiscal", "prebuilt-invoice"),
    "3": ("Recibo", "prebuilt-receipt"),
    "4": ("Documento de identidade", "prebuilt-idDocument"),
    "5": ("Cartão de visita", "prebuilt-businessCard")
}

def escolher_modelo():
    print("\nEscolha o tipo de documento para análise:\n")
    for k, v in MODELOS.items():
        print(f"{k} - {v[0]}")

    escolha = input("\nDigite o número da opção: ")

    if escolha not in MODELOS:
        print("Opção inválida")
        exit()

    return MODELOS[escolha]

def validar_campos(campos_esperados, campos_extraidos):
    print("\n Validação de informações:\n")

    for campo in campos_esperados:
        if campo in campos_extraidos and campos_extraidos[campo]:
            print(f"{campo}: encontrado")
        else:
            print(f"{campo}: ausente ou inválido")

def validar_formato_data(valor):
    return bool(re.match(r"\d{2}/\d{2}/\d{4}", valor))

def analisar_documento():
    nome_modelo, model_id = escolher_modelo()

    client = DocumentAnalysisClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(KEY)
    )

    print(f"\n Analisando como: {nome_modelo}\n")

    poller = client.begin_analyze_document_from_url(
        model_id=model_id,
        document_url=DOCUMENT_URL
    )

    result = poller.result()

    if not result.documents:
        print("Nenhuma informação encontrada")
        return

    doc = result.documents[0]
    campos = {k: v.content if v else None for k, v in doc.fields.items()}

    if model_id == "prebuilt-invoice":
        validar_campos(
            ["InvoiceId", "InvoiceDate", "VendorName", "Total"],
            campos
        )

        if "InvoiceDate" in campos and campos["InvoiceDate"]:
            if validar_formato_data(campos["InvoiceDate"]):
                print("Data em formato válido")
            else:
                print("Data com formato suspeito")

    elif model_id == "prebuilt-receipt":
        validar_campos(
            ["MerchantName", "TransactionDate", "Total"],
            campos
        )

    elif model_id == "prebuilt-idDocument":
        validar_campos(
            ["FirstName", "LastName", "DocumentNumber", "DateOfBirth"],
            campos
        )

    elif model_id == "prebuilt-businessCard":
        validar_campos(
            ["ContactNames", "Emails", "Phones"],
            campos
        )

    else:
        print("Texto extraído do documento:\n")
        for page in result.pages:
            for line in page.lines:
                print(line.content)

if __name__ == "__main__":
    analisar_documento()
