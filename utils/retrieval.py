# retrieval.py
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import tiktoken

load_dotenv()

OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
EMB_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")


# -----------------------------------------------------------
# 🔹 Initialize Azure OpenAI + Azure Cognitive Search
# -----------------------------------------------------------
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


# -----------------------------------------------------------
# 🔹 CHUNKING FUNCTION (prevents token overflow)
# -----------------------------------------------------------
def chunk_text(text: str, max_tokens: int = 500):
    """
    Split long text into chunks of max_tokens.
    Ensures embedding model never receives too many tokens.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)

    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)

    return chunks


# -----------------------------------------------------------
# 🔹 Embedding wrapper
# -----------------------------------------------------------
def embed(text: str) -> list[float]:
    resp = llm_client.embeddings.create(
        model=EMB_DEPLOYMENT,
        input=text,
    )
    return resp.data[0].embedding


# -----------------------------------------------------------
# 🔹 MAIN RETRIEVAL FUNCTION (vector search + merging)
# -----------------------------------------------------------
def retrieve_candidate_stoornissen(ocr_text: str, top_k: int = 15):
    """
    1. Splits OCR text into small chunks (500 tokens each)
    2. Embeds each chunk separately
    3. Runs Azure Cognitive Search vector lookup
    4. Merges & deduplicates results
    5. Returns top K stoornissen
    """
    # Step 1: chunking
    chunks = chunk_text(ocr_text, max_tokens=500)

    all_hits = []

    # Step 2: loop over chunks
    for chunk in chunks:
        vector = embed(chunk)

        results = search_client.search(
            search_text="",
            vectors=[{
                "value": vector,
                "fields": "vector",
                "k": top_k,
            }],
            select=["code", "name", "context"]
        )

        # Step 3: collect results per chunk
        for r in results:
            all_hits.append({
                "code": r["code"],
                "name": r.get("name", ""),
                "context": r.get("context", ""),
                "score": r["@search.score"],
            })

    # Step 4: Deduplicate — keep highest scoring hit per code
    best_by_code = {}
    for hit in all_hits:
        code = hit["code"]
        if code not in best_by_code or hit["score"] > best_by_code[code]["score"]:
            best_by_code[code] = hit

    # Step 5: sort by score
    sorted_results = sorted(
        best_by_code.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    # Step 6: return top-K final list
    return sorted_results[:top_k]
