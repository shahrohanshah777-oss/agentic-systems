import os
from typing import Any, Dict, List
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# Scraped Data
POLICY_RECORDS = [
    {
        "id": "shopkart_returns_1",
        "text": (
            "Unopened items may be returned within 7 calendar days of delivery. "
            "Opened or used items are not eligible unless defective."
        ),
        "metadata": {"category": "returns", "source": "returns_policy"},
    },
    {
        "id": "shopkart_shipping_1",
        "text": (
            "Standard delivery takes 3 to 5 business days after dispatch. "
            "Express delivery (paid) arrives in 1 to 2 business days in metro cities only."
        ),
        "metadata": {"category": "shipping", "source": "shipping_policy"},
    },
    {
        "id": "shopkart_warranty_1",
        "text": (
            "Electronics carry a 12-month manufacturer warranty from the date of delivery. "
            "Warranty does not cover physical damage or liquid exposure."
        ),
        "metadata": {"category": "warranty", "source": "warranty_policy"},
    },
    {
        "id": "shopkart_refunds_1",
        "text": (
            "Refunds are credited within 5 to 7 business days after the returned item "
            "passes warehouse verification. Cash-on-delivery orders are refunded to the "
            "original UPI or bank account only."
        ),
        "metadata": {"category": "refunds", "source": "refunds_policy"},
    },
]

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
GENERATION_MODEL_NAME = "llama-3.3-70b-versatile"

# RAG Implementation
def create_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)

# ChromaDB setup and indexing
def setup_chroma_collection():
    client = chromadb.PersistentClient(path="./chroma_store")
    collection = client.get_or_create_collection(
        name="shopkart_policy_kb",
        embedding_function=None,
    )
    return collection

# Index the policy records into ChromaDB with their embeddings and metadata
def index_policy_records(collection, model: SentenceTransformer) -> None:
    ids = [row["id"] for row in POLICY_RECORDS]
    documents = [row["text"] for row in POLICY_RECORDS]
    metadatas = [row["metadata"] for row in POLICY_RECORDS]
    embeddings = model.encode(documents, convert_to_numpy=True, normalize_embeddings=True).tolist()
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    print(f"Indexed {collection.count()} ShopKart policy records.")

# Retrieve relevant policy chunks based on user query embedding similarity
def retrieve_policy_chunks(
    collection,
    model: SentenceTransformer,
    user_query: str,
    top_k: int = 2,
) -> List[Dict[str, Any]]:
    query_embedding = model.encode([user_query], convert_to_numpy=True, normalize_embeddings=True).tolist()
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

# Create a Groq client using the API key from environment variables
def create_groq_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Create a .env file next to rag.py containing:\n"
            "    GROQ_API_KEY=your_key_here"
        )
    return Groq(api_key=api_key)

# Build a prompt for the language model that includes the user query and the retrieved policy excerpts
def build_grounded_prompt(user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    context_block = ""
    for index, chunk in enumerate(retrieved_chunks, start=1):
        metadata = chunk.get("metadata") or {}
        source_name = metadata.get("source", "unknown")
        text = chunk.get("text", "")
        context_block += f"\nExcerpt {index} (source: {source_name}):\n{text}\n"
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

# Generate a grounded answer using the Groq language model based on the user query and the retrieved policy chunks
def generate_grounded_answer(client: Groq, user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
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

# Utility function to print the retrieved policy chunks for debugging and transparency
def print_retrieved_chunks(user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> None:
    print("\n" + "=" * 72)
    print(f"Customer question: {user_query}")
    print("=" * 72)
    for rank, chunk in enumerate(retrieved_chunks, start=1):
        print(f"\nRank {rank}")
        print(f"  Source   : {chunk['metadata'].get('source')}")
        print(f"  Category : {chunk['metadata'].get('category')}")
        print(f"  Distance : {chunk['distance']:.4f}")
        print(f"  Text     : {chunk['text']}")

# Main RAG function that ties everything together: retrieves relevant policy chunks and generates a grounded answer
def answer_with_rag(
    client: Groq,
    collection,
    model: SentenceTransformer,
    user_query: str,
    top_k: int = 2,
) -> str:
    retrieved_chunks = retrieve_policy_chunks(
        collection=collection,
        model=model,
        user_query=user_query,
        top_k=top_k,
    )
    print_retrieved_chunks(user_query, retrieved_chunks)
    grounded_answer = generate_grounded_answer(
        client=client,
        user_query=user_query,
        retrieved_chunks=retrieved_chunks,
    )
    return grounded_answer

# Demonstration of the entire RAG pipeline with sample queries
def main() -> None:
    model = create_embedding_model()
    collection = setup_chroma_collection()
    index_policy_records(collection, model)
    client = create_groq_client()
    sample_query = "How many days do I have to return an item?"
    sample_answer = answer_with_rag(
        client=client,
        collection=collection,
        model=model,
        user_query=sample_query,
        top_k=2,
    )
    print(f"\nGrounded answer:\n{sample_answer}")
    demo_queries = [
        "I received my phone case yesterday unopened. How many days do I have to return it?",
        "Will express shipping reach my address in a metro city by tomorrow?",
        "My wireless earphones stopped working after 10 months. Is repair covered?",
        "I returned a defective kettle on COD last week. When will the refund reach my UPI?",
    ]
    for user_query in demo_queries:
        print("\n\n" + "#" * 72)
        print("QUESTION:", user_query)
        print("\n--- RAG (retrieve + generate) ---")
        rag_answer = answer_with_rag(
            client=client,
            collection=collection,
            model=model,
            user_query=user_query,
            top_k=2,
        )
        print("\nFinal grounded answer:")
        print(rag_answer)

# Run the main function to demonstrate the RAG pipeline
if __name__ == "__main__":
    main()