# scripts/answer_match.py

import os
import pandas as pd
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq

# --- Load environment variables ---
load_dotenv()

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(BASE_DIR, "data", "matches_faiss.index")
META_FILE = os.path.join(BASE_DIR, "data", "matches_metadata.csv")

# --- Load FAISS index and metadata ---
print("📦 Loading FAISS index and metadata...")
index = faiss.read_index(INDEX_FILE)
meta_df = pd.read_csv(META_FILE)

# --- Load embedding model ---
print("🧠 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Initialize Groq client ---
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(
        "❌ GROQ_API_KEY not found. Please ensure it's set in your .env or environment variables."
    )

client = Groq(api_key=api_key)

# --- Core functions ---

def retrieve_matches(query, top_k=5):
    """Retrieve top-k similar matches for the given question."""
    query_vector = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vector)
    scores, indices = index.search(query_vector, top_k)
    results = meta_df.iloc[indices[0]]
    return results


def generate_answer(question, context):
    """Use Groq's Llama-3.3 model to generate a natural cricket answer."""
    prompt = f"""
You are an expert cricket analyst. Use the provided context to answer the user's question accurately.

Question: {question}

Context:
{context}

If the information is not clearly available, reply exactly with:
"Not enough data to determine."

Answer:
"""
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    # Access the message content safely
    msg = completion.choices[0].message
    return msg.content if hasattr(msg, "content") else str(msg)


# --- Interactive loop ---

if __name__ == "__main__":
    while True:
        question = input("\n🏏 Enter your cricket question (or 'exit'): ").strip()
        if question.lower() == "exit":
            print("👋 Exiting Cricket Answer Agent.")
            break

        print(f"\n🔍 Searching for: {question}")
        top_results = retrieve_matches(question)

        # Combine top matches as context text
        context_text = "\n\n".join(top_results["text_repr"].astype(str).tolist())

        print("\n🤖 Generating answer...\n")
        answer = generate_answer(question, context_text)

        print(f"🏆 Answer: {answer}\n")
