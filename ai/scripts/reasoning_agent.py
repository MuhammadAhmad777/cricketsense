import os
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY is not set in environment variables.")

# --- Initialize Groq client ---
client = Groq(api_key=api_key)

# --- Paths ---
# Now that we're inside ai/scripts/, go one level up to ai/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

INDEX_FILE = os.path.join(DATA_DIR, "matches_faiss.index")
META_FILE = os.path.join(DATA_DIR, "matches_metadata.csv")

# --- Load FAISS index and metadata ---
print("📦 Loading FAISS index and metadata...")
index = faiss.read_index(INDEX_FILE)
meta_df = pd.read_csv(META_FILE)

# --- Load embedding model ---
EMB_MODEL = "all-MiniLM-L6-v2"
print(f"🧠 Loading embedding model: {EMB_MODEL} ...")
model = SentenceTransformer(EMB_MODEL)


# --- Retrieve top-k similar matches for a query ---
def retrieve_matches(query, top_k=5):
    query_vector = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vector)
    scores, indices = index.search(query_vector, top_k)
    results = meta_df.iloc[indices[0]]
    return results


# --- Generate answer using Groq ReAct reasoning ---
def generate_answer(question, context):
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
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return completion.choices[0].message.content


# --- Main interactive loop ---
if __name__ == "__main__":
    print("\n🏏 Cricket QA Assistant Ready! Type 'exit' to quit.\n")
    while True:
        question = input("❓ Enter your cricket question: ").strip()
        if question.lower() == "exit":
            print("👋 Exiting. Goodbye!")
            break

        print(f"\n🔍 Searching for relevant matches...")
        top_matches = retrieve_matches(question)

        context_text = "\n\n".join(top_matches["text_repr"].tolist())

        print("\n🤖 Generating answer...\n")
        answer = generate_answer(question, context_text)
        print(f"🏆 Answer: {answer}\n")
