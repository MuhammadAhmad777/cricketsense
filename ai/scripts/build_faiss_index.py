import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss

# --- Define paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, "data", "matches_summary.csv")
INDEX_FILE = os.path.join(BASE_DIR, "data", "matches_faiss.index")
EMB_MODEL = "all-MiniLM-L6-v2"

# --- Load CSV ---
print("📄 Loading match summaries...")
df = pd.read_csv(CSV_FILE)

# --- Prepare text representations ---
def create_text_repr(row):
    return (
        f"Match between {row['team1']} and {row['team2']} at {row['venue']}, "
        f"on {row['date']}. Winner: {row['winner']}. "
        f"Player of match: {row['player_of_match']}. "
        f"Type: {row['match_type']}, Gender: {row['gender']}, "
        f"Season: {row['season']}, City: {row['city']}."
    )

df["text_repr"] = df.apply(create_text_repr, axis=1)

# --- Load embedding model ---
print(f"🧠 Loading model: {EMB_MODEL} ...")
model = SentenceTransformer(EMB_MODEL)

# --- Encode all matches ---
print("🔢 Generating embeddings...")
embeddings = model.encode(
    df["text_repr"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True,
    batch_size=64
)

# --- Normalize vectors ---
embeddings = embeddings.astype("float32")
faiss.normalize_L2(embeddings)

# --- Build FAISS index ---
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)

# --- Save index and metadata ---
print("💾 Saving FAISS index and metadata...")
faiss.write_index(index, INDEX_FILE)
df[["match_id", "text_repr"]].to_csv(os.path.join(BASE_DIR, "data", "matches_metadata.csv"), index=False)

print(f"✅ Index built successfully for {len(df)} matches!")
