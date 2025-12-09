# utils/ocr.py
import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

FORMREC_ENDPOINT = os.getenv("AZURE_FORMREC_ENDPOINT")
FORMREC_KEY = os.getenv("AZURE_FORMREC_KEY")

client = DocumentAnalysisClient(FORMREC_ENDPOINT, AzureKeyCredential(FORMREC_KEY))

def run_ocr_streamlit(file) -> str:
    poller = client.begin_analyze_document("prebuilt-read", file)
    result = poller.result()
    lines = []
    for page in result.pages:
        for line in page.lines:
            lines.append(line.content)
    return "\n".join(lines)
