import hashlib
from typing import List

import numpy as np
from fastapi import HTTPException
from google import genai

from ..schemas.models import QuizRequest
from ..core.config import GEMINI_API_KEY, GEMINI_EMBED_MODEL


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# RAG CACHE
# ============================================================

RAG_CACHE = {}


# ============================================================
# TEXT CHUNKING
# ============================================================

def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
):
    cleaned = " ".join(
        text.split()
    )

    if not cleaned:
        return []

    chunks = []

    start = 0
    length = len(cleaned)

    while start < length:

        end = min(
            start + chunk_size,
            length,
        )

        chunk = cleaned[
            start:end
        ].strip()

        if chunk:
            chunks.append(chunk)

        if end >= length:
            break

        start = max(
            end - overlap,
            start + 1,
        )

    return chunks


# ============================================================
# EMBEDDINGS
# ============================================================

def embed_texts(
    texts: List[str],
):
    """
    Generate embeddings using Gemini.

    """

    if not texts:
        return []

    try:

        response = client.models.embed_content(
            model=GEMINI_EMBED_MODEL,
            contents=texts,
        )

        embeddings = [
            embedding.values
            for embedding in response.embeddings
        ]

    except Exception as exc:

        print(
            f"Gemini embedding error: {exc!r}"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Gemini did not return valid embeddings. "
                "Check the Gemini API key and embedding model."
            ),
        )

    if (
        not embeddings
        or len(embeddings) != len(texts)
    ):
        raise HTTPException(
            status_code=502,
            detail=(
                "Gemini did not return valid embeddings."
            ),
        )

    return embeddings


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    a: np.ndarray,
    b: np.ndarray,
):
    denom = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denom == 0:
        return 0.0

    return float(
        np.dot(a, b) / denom
    )


# ============================================================
# BUILD RAG INDEX
# ============================================================

def build_rag_index(
    source_text: str,
    source_name: str,
):
    content_hash = hashlib.sha256(
        source_text.encode("utf-8")
    ).hexdigest()

    if content_hash in RAG_CACHE:
        return RAG_CACHE[
            content_hash
        ]

    chunks = chunk_text(
        source_text
    )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail=(
                "No usable text was found "
                "in the document."
            ),
        )

    print(
        f"RAG: creating {len(chunks)} "
        f"chunks for {source_name}"
    )

    embeddings = embed_texts(
        chunks
    )

    index = {
        "source_name": source_name,
        "chunks": chunks,
        "embeddings": np.asarray(
            embeddings,
            dtype=np.float32,
        ),
    }

    RAG_CACHE[
        content_hash
    ] = index

    if len(RAG_CACHE) > 5:

        oldest_key = next(
            iter(RAG_CACHE)
        )

        if oldest_key != content_hash:
            del RAG_CACHE[
                oldest_key
            ]

    return index


# ============================================================
# RETRIEVE RELEVANT CONTEXT
# ============================================================

def retrieve_context(
    index,
    queries: List[str],
    top_k: int = 10,
):
    chunks = index["chunks"]

    matrix = index["embeddings"]

    query_embeddings = embed_texts(
        queries
    )

    scores = np.zeros(
        len(chunks),
        dtype=np.float32,
    )

    for query_vector in query_embeddings:

        q = np.asarray(
            query_vector,
            dtype=np.float32,
        )

        query_scores = np.array(
            [
                cosine_similarity(
                    q,
                    row,
                )
                for row in matrix
            ],
            dtype=np.float32,
        )

        scores = np.maximum(
            scores,
            query_scores,
        )

    top_k = min(
        top_k,
        len(chunks),
    )

    ranked_indices = np.argsort(
        scores
    )[::-1][:top_k]

    retrieved = []

    for idx in ranked_indices:

        retrieved.append(
            {
                "chunk_id": int(idx),
                "score": float(
                    scores[idx]
                ),
                "text": chunks[idx],
            }
        )

    return retrieved


# ============================================================
# BUILD RETRIEVAL QUERIES
# ============================================================

def build_retrieval_queries(
    req: QuizRequest,
):
    type_query = {
        "MCQ":
            "important concepts, definitions, comparisons, examples and distinctions",

        "True / False":
            "facts, definitions, properties, relationships and statements that can be judged true or false",

        "Short Answer":
            "important definitions, explanations, processes and key concepts",

        "Mixed":
            "important definitions, concepts, examples, processes, comparisons and relationships",
    }[
        req.question_type
    ]

    difficulty_query = {
        "Easy":
            "basic concepts and direct explanations",

        "Medium":
            "conceptual understanding, comparisons and applications",

        "Hard":
            "deeper relationships, reasoning, edge cases and detailed explanations",

        "Mixed":
            "a mixture of basic, conceptual and deeper material",
    }[
        req.difficulty
    ]

    return [
        f"Study material about {type_query}.",

        f"Study material suitable for {difficulty_query} quiz questions.",

        "Most important examinable concepts and definitions.",

        "Processes, examples, relationships, comparisons, formulas, and key facts.",
    ]


# ============================================================
# FORMAT RETRIEVED CONTEXT
# ============================================================

def format_retrieved_context(
    retrieved,
):
    parts = []

    for item in retrieved:

        parts.append(
            f"[SOURCE CHUNK {item['chunk_id']} "
            f"| relevance={item['score']:.3f}]\n"
            f"{item['text']}"
        )

    return "\n\n".join(parts)