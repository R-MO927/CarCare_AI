import re
import requests
import chromadb
from pathlib import Path


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3.2:3b"


# ============================================================
# ChromaDB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = chroma_client.get_collection(
    name="carcare_maintenance"
)


# ============================================================
# Vehicle Part Names
# ============================================================

PART_NAME_MAP = {
    "back_bumper": "rear bumper",
    "back_door": "rear door",
    "back_glass": "rear window glass",
    "back_left_door": "rear left door",
    "back_left_light": "rear left light",
    "back_light": "rear light",
    "back_right_door": "rear right door",
    "back_right_light": "rear right light",
    "front_bumper": "front bumper",
    "front_door": "front door",
    "front_glass": "windshield/front glass",
    "front_left_door": "front left door",
    "front_left_light": "front left light",
    "front_light": "front light",
    "front_right_door": "front right door",
    "front_right_light": "front right light",
    "hood": "hood",
    "left_mirror": "left side mirror",
    "right_mirror": "right side mirror",
    "tailgate": "tailgate",
    "trunk": "trunk",
    "wheel": "wheel"
}


# ============================================================
# Hybrid Retrieval
# ============================================================

def hybrid_retrieve(query, top_k=5, semantic_k=10):

    results = collection.query(
        query_texts=[query],
        n_results=semantic_k
    )

    query_words = set(
        re.findall(r"\b[a-zA-Z]{3,}\b", query.lower())
    )

    scored_results = []

    for i in range(len(results["documents"][0])):

        text = results["documents"][0][i]

        page = results["metadatas"][0][i]["page"]

        source = results["metadatas"][0][i]["source"]

        distance = results["distances"][0][i]

        text_words = set(
            re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        )

        keyword_matches = query_words.intersection(
            text_words
        )

        keyword_score = (
            len(keyword_matches) /
            max(len(query_words), 1)
        )

        semantic_score = 1 / (1 + distance)

        final_score = (
            0.75 * semantic_score +
            0.25 * keyword_score
        )

        scored_results.append({
            "text": text,
            "page": page,
            "source": source,
            "distance": distance,
            "semantic_score": semantic_score,
            "keyword_score": keyword_score,
            "final_score": final_score,
            "keyword_matches": sorted(keyword_matches)
        })

    scored_results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return scored_results[:top_k]


# ============================================================
# Direct Evidence Check
# ============================================================

def has_direct_part_evidence(
    friendly_part,
    retrieved_results
):

    part_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            friendly_part.lower()
        )
    )

    for result in retrieved_results:

        text_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                result["text"].lower()
            )
        )

        if part_words.intersection(text_words):
            return True

    return False


# ============================================================
# Ollama Generation
# ============================================================

def generate_with_ollama(
    query,
    retrieved_results,
    model_name=OLLAMA_MODEL
):

    context_parts = []

    for i, result in enumerate(
        retrieved_results,
        start=1
    ):

        context_parts.append(
            f"[Source {i} | PDF Page {result['page']}]\n"
            f"{result['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are CarCare AI, a document-grounded automotive maintenance assistant.

Your task is to answer the user's question using ONLY the information contained in the Maintenance Context below.

IMPORTANT RULES:
1. You MUST use the provided Maintenance Context to answer.
2. Do NOT answer from general knowledge.
3. Do NOT say that you cannot provide vehicle maintenance information.
4. Do NOT refuse the question unless the Maintenance Context is actually insufficient.
5. If the context contains relevant information, explain it clearly and practically.
6. If the context is insufficient, say:
   "The available maintenance document does not provide enough information to answer this question reliably."
7. Do not invent procedures, measurements, specifications, causes, or safety instructions.
8. Keep the answer focused on the user's question.
9. Do NOT include PDF page numbers, source numbers, or source labels in your answer.
10. The application will provide the supporting PDF sources separately.
11. Never write words such as "Source 1", "Source 2", "Source 3", "PDF Page", or any page number in your answer.
12. Return only the maintenance guidance itself, with no citations or source references.

Maintenance Context:
{context}

User Question:
{query}

Answer based strictly on the Maintenance Context:
"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model_name,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"].strip()