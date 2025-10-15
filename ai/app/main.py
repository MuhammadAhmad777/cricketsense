# app/main.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import faiss
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not set in environment")
client = Groq(api_key=api_key)

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(BASE_DIR, "data", "matches_faiss.index")
META_FILE = os.path.join(BASE_DIR, "data", "matches_metadata.csv")

# --- Load FAISS index and metadata ---
if not os.path.exists(INDEX_FILE) or not os.path.exists(META_FILE):
    raise FileNotFoundError(
        "FAISS index or metadata CSV not found. Please run build_faiss_index.py first."
    )

index = faiss.read_index(INDEX_FILE)
meta_df = pd.read_csv(META_FILE)

# --- Load embedding model ---
EMB_MODEL = "all-MiniLM-L6-v2"
model = SentenceTransformer(EMB_MODEL)

# --- FastAPI app ---
app = FastAPI(title="CricketMind Semantic ReAct API", version="2.0")

# --- ✅ CORS Configuration ---
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",  # alternate local URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Retrieve top-k matches using FAISS ---
def retrieve_matches(query: str, top_k: int = 5):
    query_vector = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vector)
    scores, indices = index.search(query_vector, top_k)
    results = meta_df.iloc[indices[0]]
    return results

# --- Generate answer using Groq LLM ---
def generate_answer(question: str, context: str):
    prompt = f"""
You are an expert cricket analyst. Use the provided match context to answer the user's question accurately.

You may reason using the following pattern:
Thought: <your reasoning>
Action: <look up info in context>
Observation: <what you find>
Repeat as needed, then conclude:
Final Answer: <answer to the question>

Question: {question}

Context (top relevant matches from database):
{context}

Answer:
"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
    except Exception as e:
        return f"❌ Error calling Groq API: {e}"

    msg = completion.choices[0].message
    return msg.content if hasattr(msg, "content") else str(msg)

# --- FastAPI endpoint ---
@app.get("/reason")
def reason(question: str = Query(..., description="Cricket question"), top_k: int = 5):
    """
    Ask a cricket question and get an answer using FAISS semantic retrieval + Groq ReAct reasoning.
    """
    if not question.strip():
        return {"error": "Question cannot be empty"}

    # Retrieve top-k matches
    top_matches = retrieve_matches(question, top_k)
    context_text = "\n\n".join(top_matches["text_repr"].astype(str).tolist())

    # Generate answer
    answer = generate_answer(question, context_text)

    return {
        "final_answer": answer,
        "retrieved_matches_count": len(top_matches),
    }
