# Import necessary libraries and load environment variables

import os
import re
from typing import Any, Dict, List
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

# Configuration constants

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
GENERATION_MODEL_NAME = "llama-3.1-8b-instant"
POLICY_FOLDER = "./policy_documents"
CHROMA_PATH = "./chroma_store"
COLLECTION_NAME = "shopkart_policy_kb_v2"
DEFAULT_CHUNK_SIZE = 100
DEFAULT_CHUNK_OVERLAP = 20

#Loading and preprocessing policy documents

def infer_policy_category(filename: str) -> str:
    name = filename.lower()
    if "return" in name:
        return "returns"
    if "shipping" in name:
        return "shipping"
    if "warranty" in name:
        return "warranty"
    if "refund" in name:
        return "refunds"
    if "delivery" in name:
        return "delivery"
    return "general"


def clean_text(raw_text: str) -> str:
    text = raw_text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_txt_file(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r", encoding="utf-8") as handle:
        raw_text = handle.read()

    cleaned = clean_text(raw_text)
    filename = os.path.basename(file_path)

    return [
        {
            "text": cleaned,
            "metadata": {
                "source": filename,
                "category": infer_policy_category(filename),
                "file_type": "txt",
            },
        }
    ]


def load_pdf_file(file_path: str) -> List[Dict[str, Any]]:
    documents: List[Dict[str, Any]] = []
    filename = os.path.basename(file_path)
    category = infer_policy_category(filename)
    reader = PdfReader(file_path)

    for page_number, page in enumerate(reader.pages, start=1):
        cleaned = clean_text(page.extract_text() or "")
        if not cleaned:
            continue
        documents.append(
            {
                "text": cleaned,
                "metadata": {
                    "source": filename,
                    "category": category,
                    "file_type": "pdf",
                    "page": page_number,
                },
            }
        )

    return documents


def load_all_policy_documents(folder_path: str) -> List[Dict[str, Any]]:
    all_documents: List[Dict[str, Any]] = []

    for filename in sorted(os.listdir(folder_path)):
        full_path = os.path.join(folder_path, filename)

        if filename.endswith(".txt"):
            docs = load_txt_file(full_path)
        elif filename.endswith(".pdf"):
            docs = load_pdf_file(full_path)
        else:
            continue

        all_documents.extend(docs)
        print(f"Loaded {len(docs)} document(s) from {filename}")

    print(f"Total loaded documents: {len(all_documents)}")
    return all_documents

# Chunking policy documents for embedding and retrieval

def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start += chunk_size - overlap

    return chunks


def create_chunks_from_documents(
    documents: List[Dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    all_chunks: List[Dict[str, Any]] = []

    for doc_index, document in enumerate(documents):
        for chunk_index, chunk_body in enumerate(
            chunk_text(document["text"], chunk_size, overlap)
        ):
            category = document["metadata"].get("category", "general")
            chunk_metadata = dict(document["metadata"])
            chunk_metadata["chunk_index"] = chunk_index

            all_chunks.append(
                {
                    "id": f"{category}_{doc_index}_{chunk_index}",
                    "text": chunk_body,
                    "metadata": chunk_metadata,
                }
            )

    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks

# Setting up embedding model and vector database

def create_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def setup_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=None,
    )


def index_policy_chunks(
    collection,
    model: SentenceTransformer,
    chunks: List[Dict[str, Any]],
) -> None:
    if not chunks:
        print("No chunks to index.")
        return

    ids = [row["id"] for row in chunks]
    documents = [row["text"] for row in chunks]
    metadatas = [row["metadata"] for row in chunks]

    embeddings = model.encode(
        documents,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Indexed {collection.count()} chunks into {COLLECTION_NAME}.")


def build_knowledge_base(model, collection, folder_path: str = POLICY_FOLDER) -> None:
    documents = load_all_policy_documents(folder_path)
    chunks = create_chunks_from_documents(documents)
    index_policy_chunks(collection, model, chunks)
    print("Knowledge base build complete.")

# Retrieval stage

def retrieve_policy_chunks(
    collection,
    model: SentenceTransformer,
    user_query: str,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    query_embedding = model.encode(
        [user_query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append(
            {
                "text": doc,
                "metadata": meta,
                "distance": dist,
            }
        )

    return retrieved

# Generation stage using Groq API

def create_groq_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Create a .env file next to rag_pipeline.py containing:\n"
            "    GROQ_API_KEY=your_key_here"
        )

    return Groq(api_key=api_key)


def build_grounded_prompt(user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    context_block = ""
    for index, chunk in enumerate(retrieved_chunks, start=1):
        metadata = chunk.get("metadata") or {}
        source_name = metadata.get("source", "unknown")
        category = metadata.get("category", "unknown")
        text = chunk.get("text", "")
        context_block += f"\nExcerpt {index} (source: {source_name}, category: {category}):\n{text}\n"

    if not context_block:
        context_block = "\n(No policy excerpts were retrieved for this question.)\n"

    prompt = f"""You are ShopKart customer support.
Answer the customer's question using ONLY the policy excerpts below.
Rules:
1. Do not invent numbers, timelines, or eligibility rules not present in the excerpts.
2. If the excerpts do not contain enough information, say:
"I do not have enough information in the provided policy excerpts."
3. Keep the answer short, polite, and clear.
4. Mention important conditions (opened vs unopened, metro-only express, COD refund path) when they appear in the excerpts.

Policy excerpts:
{context_block}

Customer question:
{user_query}

Final answer:"""

    return prompt

# Generation Stage: Generating grounded answer

def generate_grounded_answer(
    client: Groq,
    user_query: str,
    retrieved_chunks: List[Dict[str, Any]],
) -> str:
    prompt = build_grounded_prompt(user_query, retrieved_chunks)

    response = client.chat.completions.create(
        model=GENERATION_MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a precise ShopKart support assistant. Follow the policy excerpts exactly.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def print_retrieved_chunks(user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> None:
    print("\n" + "=" * 72)
    print(f"Customer question: {user_query}")
    print("=" * 72)

    for rank, chunk in enumerate(retrieved_chunks, start=1):
        print(f"\nRank {rank}")
        print(f"  Category : {chunk['metadata'].get('category')}")
        print(f"  Source   : {chunk['metadata'].get('source')}")
        print(f"  Distance : {chunk['distance']:.4f}")
        print(f"  Text     : {chunk['text']}")


def answer_with_rag(
    client: Groq,
    collection,
    model: SentenceTransformer,
    user_query: str,
    top_k: int = 3,
) -> str:
    retrieved_chunks = retrieve_policy_chunks(
        collection=collection,
        model=model,
        user_query=user_query,
        top_k=top_k,
    )

    print_retrieved_chunks(user_query, retrieved_chunks)

    return generate_grounded_answer(
        client=client,
        user_query=user_query,
        retrieved_chunks=retrieved_chunks,
    )

# Main execution flow

def main() -> None:
    model = create_embedding_model()

    collection = setup_chroma_collection()

    build_knowledge_base(model, collection)

    client = create_groq_client()

    demo_queries = [
        "I received my phone case yesterday unopened. How many days do I have to return it?",
        "Will express shipping reach my address in a metro city by tomorrow?",
        "My wireless earphones stopped working after 10 months. Is repair covered?",
        "I returned a defective kettle on COD last week. When will the refund reach my UPI?",
        "I missed the second delivery attempt for my order. Will it be delivered again?",
    ]

    for user_query in demo_queries:
        print("\n\n" + "#" * 72)
        print("QUESTION:", user_query)

        answer = answer_with_rag(
            client=client,
            collection=collection,
            model=model,
            user_query=user_query,
            top_k=3,
        )

        print("\nFinal grounded answer:")
        print(answer)

# Declare main execution

if __name__ == "__main__":
    main()
