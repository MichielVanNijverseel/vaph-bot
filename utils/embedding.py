import os
import pandas as pd
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
EMB_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") 

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")

llm_client = AzureOpenAI(
    api_key=OPENAI_KEY,
    azure_endpoint=OPENAI_ENDPOINT,
    api_version="2024-12-01-preview",
)

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_KEY),
)

def get_embedding(text):
    resp = llm_client.embeddings.create(
        model=EMB_DEPLOYMENT,
        input=text,
    )
    return resp.data[0].embedding

def build_index():
    df = pd.read_csv("stoorniscodes.csv", delimiter=";", encoding="utf-8")

    docs = []
    for _, row in df.iterrows():
        code = str(row["stoorniscode"])
        name = str(row["stoornisnaam"])
        ctx = str(row["stoorniscontext"]) if "stoorniscontext" in row else ""

        text_repr = f"{code} - {name}. {ctx}"

        emb = get_embedding(text_repr)

        docs.append({
            "id": code,
            "code": code,
            "name": name,
            "context": ctx,
            "content": text_repr,
            "vector": emb,
        })

    result = search_client.upload_documents(docs)
    print(f"Geüpload: {len(result)} vector documenten")

if __name__ == "__main__":
    build_index()
