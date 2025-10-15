import os
import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(BASE_DIR, "data", "matches_faiss.index")
METADATA_FILE = os.path.join(BASE_DIR, "data", "matches_metadata.csv")
EMB_MODEL = "all-MiniLM-L6-v2"

# --- Load model and index ---
print("🧠 Loading embedding model...")
model = SentenceTransformer(EMB_MODEL)

print("📦 Loading FAISS index and metadata...")
index = faiss.read_index(INDEX_FILE)
metadata = pd.read_csv(METADATA_FILE)

# --- Query Function ---
def search_matches(query, top_k=5):
    print(f"\n🔍 Searching for: {query}")
    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    
    # FAISS search
    D, I = index.search(q_emb, top_k)
    
    print("\n🎯 Top results:")
    results = []
    for rank, idx in enumerate(I[0]):
        match = metadata.iloc[idx]
        results.append((match["match_id"], match["text_repr"]))
        print(f"{rank+1}. {match['text_repr'][:200]}...")  # partial text
    
    return results

# --- Example query ---
if __name__ == "__main__":
    query = input("\nEnter your cricket question: ")
    top_results = search_matches(query)
