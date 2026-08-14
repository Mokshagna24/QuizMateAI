import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Literal, Optional

import fitz
import jwt
import numpy as np
import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile 
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel, Field

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "quizmate.db"
TOPICS_DIR = ROOT / "data" / "topics"

JWT_SECRET = os.getenv("JWT_SECRET", "demo-secret")
JWT_ALG = "HS256"
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")

app = FastAPI(title="QuizMate AI API", version="1.0.0")

origins = [o.strip() for o in FRONTEND_ORIGIN.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            difficulty TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    con.commit()
    con.close()

init_db()

class AuthIn(BaseModel):
    name: Optional[str] = None
    email: str
    password: str

class TokenOut(BaseModel):
    token: str
    user: dict

class QuizRequest(BaseModel):
    source_text: Optional[str] = None
    source_name: Optional[str] = None
    topic: Optional[str] = None
    count: int = Field(default=10, ge=1, le=20)
    question_type: Literal["MCQ", "True / False", "Short Answer", "Mixed"]
    difficulty: Literal["Easy", "Medium", "Hard", "Mixed"]

class QuizQuestion(BaseModel):
    type: Literal["MCQ", "True / False", "Short Answer"]
    question: str
    options: List[str] = []
    answer: str = ""
    explanation: str = ""
    keywords: List[str] = []

class QuizOut(BaseModel):
    questions: List[QuizQuestion]

class SubmitRequest(BaseModel):
    source_name: str
    difficulty: str
    questions: List[QuizQuestion]
    answers: dict

class SummaryRequest(BaseModel):
    text: str = Field(min_length=20)
    mode: Literal["Quick Summary", "Detailed Summary", "Exam Revision Notes", "Explain Simply"]

def hash_password(password: str, salt: Optional[bytes] = None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return salt.hex() + ":" + digest.hex()

def verify_password(password: str, stored: str):
    salt_hex, digest_hex = stored.split(":")
    test = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 120_000)
    return hmac.compare_digest(test.hex(), digest_hex)

def make_token(user_id: int, email: str):
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def current_user(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Please log in.")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return {"id": int(payload["sub"]), "email": payload["email"]}
    except Exception:
        raise HTTPException(status_code=401, detail="Session expired. Please log in.")

def load_topics():
    TOPICS_DIR.mkdir(parents=True, exist_ok=True)
    return {
        p.stem.replace("_", " ").title(): p.read_text(encoding="utf-8")
        for p in TOPICS_DIR.glob("*.txt")
    }
def get_topic_source(topic: str):
    data = load_topics()

    # Exact match
    if topic in data:
        return topic, data[topic]

    # Case-insensitive match
    topic_lower = topic.strip().lower()

    for name, text in data.items():
        if name.lower() == topic_lower:
            return name, text

    raise HTTPException(
        status_code=404,
        detail=f"Topic '{topic}' was not found."
    )


# ---------------------------------------------------------------------------
# LOCAL OLLAMA + RAG
# ---------------------------------------------------------------------------

# Simple in-memory cache for the current backend process.
# This avoids recomputing embeddings when the same PDF is used repeatedly.
RAG_CACHE = {}


def ollama_post(endpoint: str, payload: dict, timeout: int = 180):
    """Call the local Ollama HTTP API."""
    url = f"{OLLAMA_BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Ollama is not running. Start Ollama with 'ollama serve' "
                "and make sure the required models are installed."
            ),
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Ollama took too long to respond. Please try again.",
        )
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = response.json().get("error", "")
        except Exception:
            pass
        raise HTTPException(
            status_code=502,
            detail=f"Ollama API error: {detail or str(e)}",
        )


def call_ai(prompt: str):
    """Generate text locally with Llama 3.2 through Ollama."""
    print("\n========== OLLAMA DEBUG ==========")
    print("OLLAMA URL:", OLLAMA_BASE_URL)
    print("LLM MODEL:", OLLAMA_MODEL)
    print("EMBED MODEL:", OLLAMA_EMBED_MODEL)
    print("PROMPT LENGTH:", len(prompt))

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are QuizMate AI. Follow the user's instructions exactly. "
                    "Use only the supplied retrieved study context when generating "
                    "educational content."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2,
        },
    }

    data = ollama_post("/api/chat", payload, timeout=300)
    result = data.get("message", {}).get("content", "")

    print("OLLAMA SUCCESS:", bool(result))
    print("RESPONSE LENGTH:", len(result))
    print("RESPONSE PREVIEW:", result[:500])
    print("==================================\n")
    return result


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    """
    Split document text into overlapping chunks.

    Character-based chunking is deliberately simple and dependency-light for
    the hackathon. Each chunk keeps enough surrounding context for retrieval.
    """
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks = []
    start = 0
    length = len(cleaned)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = cleaned[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= length:
            break

        start = max(end - overlap, start + 1)

    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Create local embeddings with nomic-embed-text through Ollama."""
    if not texts:
        return []

    # Ollama supports a list of inputs on /api/embed.
    data = ollama_post(
        "/api/embed",
        {
            "model": OLLAMA_EMBED_MODEL,
            "input": texts,
            "truncate": True,
        },
        timeout=300,
    )

    embeddings = data.get("embeddings")
    if not embeddings or len(embeddings) != len(texts):
        raise HTTPException(
            status_code=502,
            detail="Ollama did not return valid embeddings. Check nomic-embed-text.",
        )

    return embeddings


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two embedding vectors."""
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def build_rag_index(source_text: str, source_name: str):
    """
    Chunk and embed a document.

    The index is cached by content hash so repeated quiz attempts on the same
    PDF do not recompute all embeddings during the current server session.
    """
    content_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

    if content_hash in RAG_CACHE:
        return RAG_CACHE[content_hash]

    chunks = chunk_text(source_text)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No usable text was found in the document.",
        )

    print(f"RAG: creating {len(chunks)} chunks for {source_name}")
    embeddings = embed_texts(chunks)

    index = {
        "source_name": source_name,
        "chunks": chunks,
        "embeddings": np.asarray(embeddings, dtype=np.float32),
    }

    RAG_CACHE[content_hash] = index

    # Prevent unlimited memory growth during a long demo.
    if len(RAG_CACHE) > 5:
        oldest_key = next(iter(RAG_CACHE))
        if oldest_key != content_hash:
            del RAG_CACHE[oldest_key]

    return index


def retrieve_context(index, queries: List[str], top_k: int = 10):
    """
    Retrieve the most relevant document chunks for the quiz-generation task.

    We use multiple retrieval queries so the quiz can cover definitions,
    concepts, processes, examples, and relationships instead of focusing on
    one small part of the document.
    """
    chunks = index["chunks"]
    matrix = index["embeddings"]

    query_embeddings = embed_texts(queries)

    scores = np.zeros(len(chunks), dtype=np.float32)

    for query_vector in query_embeddings:
        q = np.asarray(query_vector, dtype=np.float32)
        query_scores = np.array(
            [cosine_similarity(q, row) for row in matrix],
            dtype=np.float32,
        )
        scores = np.maximum(scores, query_scores)

    top_k = min(top_k, len(chunks))
    ranked_indices = np.argsort(scores)[::-1][:top_k]

    retrieved = []
    for idx in ranked_indices:
        retrieved.append(
            {
                "chunk_id": int(idx),
                "score": float(scores[idx]),
                "text": chunks[idx],
            }
        )

    return retrieved


def build_retrieval_queries(req: QuizRequest):
    """Create semantic retrieval queries from the user's quiz settings."""
    type_query = {
        "MCQ": "important concepts, definitions, comparisons, examples and distinctions",
        "True / False": "facts, definitions, properties, relationships and statements that can be judged true or false",
        "Short Answer": "important definitions, explanations, processes and key concepts",
        "Mixed": "important definitions, concepts, examples, processes, comparisons and relationships",
    }[req.question_type]

    difficulty_query = {
        "Easy": "basic concepts and direct explanations",
        "Medium": "conceptual understanding, comparisons and applications",
        "Hard": "deeper relationships, reasoning, edge cases and detailed explanations",
        "Mixed": "a mixture of basic, conceptual and deeper material",
    }[req.difficulty]

    return [
        f"Study material about {type_query}.",
        f"Study material suitable for {difficulty_query} quiz questions.",
        f"Most important examinable concepts and definitions in this study material.",
        f"Processes, examples, relationships, comparisons, formulas, and key facts in this study material.",
    ]


def format_retrieved_context(retrieved):
    """Format retrieved chunks for the LLM while keeping source boundaries clear."""
    parts = []

    for item in retrieved:
        parts.append(
            f"[SOURCE CHUNK {item['chunk_id']} | relevance={item['score']:.3f}]\n"
            f"{item['text']}"
        )

    return "\n\n".join(parts)

def clean_json(raw: str):
    raw = raw.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return raw

def generate_questions(req: QuizRequest):

    # ---------------------------------------------------------
    # Determine the source: uploaded document OR predefined topic
    # ---------------------------------------------------------

    if req.topic:
        source_name, source_text = get_topic_source(req.topic)

    elif req.source_text:
        source_text = req.source_text.strip()
        source_name = req.source_name or "Uploaded Document"

    else:
        raise HTTPException(
            status_code=400,
            detail="Please upload a document or select/enter a topic."
        )

    if len(source_text) < 100:
        raise HTTPException(
            status_code=400,
            detail="The selected topic/document does not contain enough study material."
        )

    # ---------------------------------------------------------
    # Existing RAG pipeline continues from here
    # ---------------------------------------------------------

    index = build_rag_index(source_text, source_name)

    retrieval_queries = build_retrieval_queries(req)

    top_k = min(
        max(8, req.count // 2 + 5),
        15,
        len(index["chunks"])
    )

    retrieved = retrieve_context(
        index,
        retrieval_queries,
        top_k=top_k
    )

    # Build/reuse local vector index.
    index = build_rag_index(source_text, req.source_name)

    # Retrieve only the most relevant parts of the uploaded document.
    retrieval_queries = build_retrieval_queries(req)

    # A little extra context helps the model produce the requested count.
    top_k = min(max(8, req.count // 2 + 5), 15, len(index["chunks"]))
    retrieved = retrieve_context(index, retrieval_queries, top_k=top_k)

    if not retrieved:
        raise HTTPException(
            status_code=502,
            detail="RAG could not retrieve relevant content from the document.",
        )

    context = format_retrieved_context(retrieved)

    question_type_instruction = {
        "MCQ": "Generate only Multiple Choice Questions.",
        "True / False": "Generate only True / False questions.",
        "Short Answer": "Generate only Short Answer questions.",
        "Mixed": "Generate a balanced mixture of MCQ, True / False, and Short Answer questions.",
    }[req.question_type]

    difficulty_instruction = {
        "Easy": "Test basic understanding and definitions.",
        "Medium": "Test understanding, comparison, application, and concepts.",
        "Hard": "Require deeper reasoning and careful understanding of the retrieved material.",
        "Mixed": "Use a mixture of easy, medium, and hard questions.",
    }[req.difficulty]

    prompt = f"""
You are QuizMate AI, an educational quiz generator using Retrieval-Augmented
Generation (RAG).

Create EXACTLY {req.count} NEW quiz questions.

The study material was chunked and searched using the local embedding model
nomic-embed-text:latest. The text below contains the retrieved evidence from
the user's selected study source.

STRICT GROUNDING RULES:
1. Use ONLY information explicitly supported by the RETRIEVED STUDY CONTEXT.
2. Do NOT use your general knowledge to fill gaps.
3. Do NOT invent facts, examples, definitions, dates, formulas, or relationships.
4. Do NOT create generic questions unrelated to the retrieved context.
5. Every answer and explanation must be supported by the retrieved context.
6. Create NEW questions; do not use hard-coded/demo questions.
7. Make questions meaningfully different from one another.
8. If the retrieved context does not support a requested question, do not invent one.

QUESTION TYPE:
{question_type_instruction}

DIFFICULTY:
{difficulty_instruction}

OUTPUT:
Return ONLY a valid JSON object with this exact structure:
{{
  "questions": [
    ...
  ]
}}

MCQ object:
{{
  "type": "MCQ",
  "question": "Question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": "Exactly one option",
  "explanation": "Brief explanation based only on retrieved study context",
  "keywords": []
}}

True / False object:
{{
  "type": "True / False",
  "question": "Statement based only on retrieved study context",
  "options": [],
  "answer": "True",
  "explanation": "Brief explanation based only on retrieved study context",
  "keywords": []
}}

Short Answer object:
{{
  "type": "Short Answer",
  "question": "Question based only on retrieved study context",
  "options": [],
  "answer": "Expected answer supported by retrieved study context",
  "explanation": "Brief explanation based only on retrieved study context",
  "keywords": ["important", "answer"]
}}

QUALITY RULES:
- MCQ must have exactly four unique options.
- The answer must exactly match one option.
- True/False answer must be exactly True or False.
- Do not reveal the answer inside the question.
- Do not duplicate questions.
- Keep explanations concise.
- Do not output markdown.

RETRIEVED STUDY CONTEXT:
<RETRIEVED_CONTEXT>
{context}
</RETRIEVED_CONTEXT>
"""

    raw = call_ai(prompt)

    if not raw:
        raise HTTPException(
            status_code=503,
            detail="Local Llama generation failed. Check that Ollama is running and llama3.2:latest is installed.",
        )

    try:
        import json

        parsed = json.loads(clean_json(raw))

        # Support both the desired object format and a raw array in case a
        # local model ignores the exact JSON wrapper.
        if isinstance(parsed, dict):
            items = parsed.get("questions", [])
        else:
            items = parsed

        if not isinstance(items, list) or not items:
            raise ValueError("Llama did not return a question list.")

        validated = []
        seen = set()

        for item in items:
            q = QuizQuestion(**item)

            question_key = " ".join(q.question.lower().split())
            if not question_key or question_key in seen:
                continue

            if q.type == "MCQ":
                if len(q.options) != 4:
                    continue

                normalized_options = [
                    str(option).strip().lower() for option in q.options
                ]

                if len(set(normalized_options)) != 4:
                    continue

                if q.answer.strip().lower() not in normalized_options:
                    continue

            elif q.type == "True / False":
                if q.answer.strip().lower() not in {"true", "false"}:
                    continue

            elif q.type == "Short Answer":
                if not q.answer.strip():
                    continue

            seen.add(question_key)
            validated.append(q)

            if len(validated) == req.count:
                break

        if len(validated) < req.count:
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Llama generated only {len(validated)} valid questions out of "
                    f"{req.count}. Try again or upload a document with more detailed content."
                ),
            )

        print(
            f"RAG SUCCESS: {len(validated)} questions generated from "
            f"{len(retrieved)} retrieved chunks using {OLLAMA_EMBED_MODEL}"
        )

        return validated

    except HTTPException:
        raise
    except Exception as e:
        print("RAG QUIZ PARSE ERROR:", repr(e))
        print("RAW LLAMA RESPONSE:", raw[:3000])

        raise HTTPException(
            status_code=502,
            detail="Llama returned an invalid quiz format. Please generate the quiz again.",
        )

def score_questions(questions, answers):
    score = 0
    for i, q in enumerate(questions):
        user = str(answers.get(str(i), "")).strip().lower()
        correct = str(q.answer).strip().lower()
        if q.type == "Short Answer":
            kws = [str(k).lower() for k in q.keywords]
            if kws and any(k in user for k in kws):
                score += 1
        elif user == correct:
            score += 1
    return score

@app.get("/")
def health():
    return {"name": "QuizMate AI", "status": "ok"}

@app.get("/api/topics")
def topics():
    return [{"name": name, "description": "Practice important concepts with AI."} for name in load_topics()]

@app.get("/api/topics/{topic_name}")
def topic_content(topic_name: str):
    data = load_topics()
    if topic_name not in data:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"name": topic_name, "text": data[topic_name]}

@app.post("/api/auth/register", response_model=TokenOut)
def register(req: AuthIn):
    if not req.name or len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Name and password (6+ characters) are required.")
    con = get_db()
    try:
        cur = con.execute(
            "INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
            (req.name.strip(), req.email.lower(), hash_password(req.password))
        )
        con.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        con.close()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    con.close()
    return {"token": make_token(user_id, req.email.lower()), "user": {"id": user_id, "name": req.name, "email": req.email.lower()}}

@app.post("/api/auth/login", response_model=TokenOut)
def login(req: AuthIn):
    con = get_db()
    row = con.execute("SELECT * FROM users WHERE email=?", (req.email.lower(),)).fetchone()
    con.close()
    if not row or not verify_password(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"token": make_token(row["id"], row["email"]), "user": {"id": row["id"], "name": row["name"], "email": row["email"]}}

@app.post("/api/quiz/generate", response_model=QuizOut)
def quiz_generate(req: QuizRequest, user=Depends(current_user)):
    return {"questions": generate_questions(req)}

@app.post("/api/quiz/submit")
def quiz_submit(req: SubmitRequest, user=Depends(current_user)):
    score = score_questions(req.questions, req.answers)
    total = len(req.questions)
    con = get_db()
    con.execute(
        "INSERT INTO results(user_id,topic,score,total,difficulty,created_at) VALUES(?,?,?,?,?,?)",
        (user["id"], req.source_name, score, total, req.difficulty, datetime.now().isoformat())
    )
    
    con.commit()
    con.close()
    pct = round(score / total * 100) if total else 0
    return {"score": score, "total": total, "percentage": pct}

@app.get("/api/results")
def results(user=Depends(current_user)):
    con = get_db()
    rows = [dict(r) for r in con.execute(
        "SELECT topic, score, total, difficulty, created_at FROM results WHERE user_id=? ORDER BY id DESC",
        (user["id"],)
    ).fetchall()]
    con.close()
    return rows

@app.post("/api/pdf/extract")
async def extract_pdf(file: UploadFile = File(...), user=Depends(current_user)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Please upload a PDF.")
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="PDF is too large. Please keep it under 10 MB.")
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        text = "\n".join(page.get_text("text") for page in doc)
        doc.close()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="We couldn't read this PDF. Please try another PDF."
        )

    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    if len(text) < 100:
        raise HTTPException(
            status_code=400,
            detail="This PDF has little or no selectable text. Please upload a text-based PDF."
        )

    return {"filename": file.filename, "text": text}

@app.post("/api/summary")
def summary(req: SummaryRequest, user=Depends(current_user)):
    prompt = f"""
You are QuizMate AI.
Summarize ONLY the document below.
Style: {req.mode}
Use clear headings and bullet points.
Do not invent facts.

Document:
{req.text[:40000]}
"""
    result = call_ai(prompt)
    if result:
        return {"summary": result}
    raise HTTPException(status_code=503, detail="Local Llama summary generation failed. Check Ollama.")
