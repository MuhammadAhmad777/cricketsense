import os
import json
import pandas as pd
from tqdm import tqdm

# --- Define paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "all_json_extracted")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "matches_summary.csv")

records = []

# --- Get list of JSON files ---
file_list = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".json")])
total_files = len(file_list)
print(f"📂 Found {total_files} JSON files to process...\n")

# --- Process files with progress bar ---
for i, filename in enumerate(tqdm(file_list, desc="Processing matches", unit="file"), start=1):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"⚠️ Skipping {filename}: {e}")
        continue

    info = data.get("info", {})
    match_id = info.get("match_id") or filename.replace(".json", "")
    venue = info.get("venue") or "Unknown"
    match_type = info.get("match_type") or "Unknown"
    gender = info.get("gender") or "Unknown"
    city = info.get("city") or "Unknown"
    season = info.get("season") or "Unknown"
    event_name = info.get("event", {}).get("name") or "Unknown"
    date = info.get("dates", [None])[0]

    teams = info.get("teams", [])
    team1 = teams[0] if len(teams) > 0 else "Unknown"
    team2 = teams[1] if len(teams) > 1 else "Unknown"

    toss = info.get("toss", {})
    toss_winner = toss.get("winner") or "Unknown"
    toss_decision = toss.get("decision") or "Unknown"

    outcome = info.get("outcome", {})
    winner = outcome.get("winner") or "Unknown"
    overs = info.get("overs") or 0

    # --- Handle player_of_match properly ---
    player_list = info.get("player_of_match", [])
    if player_list and isinstance(player_list, list) and len(player_list) > 0:
        player_of_match = ", ".join(player_list)
    else:
        player_of_match = "Unknown"

    # --- Calculate first innings runs ---
    first_innings_runs = None
    innings = data.get("innings", [])
    if innings:
        try:
            first_innings = innings[0]
            deliveries = []
            for over in first_innings.get("overs", []):
                deliveries.extend(over.get("deliveries", []))
            first_innings_runs = sum(d.get("runs", {}).get("total", 0) for d in deliveries)
        except Exception:
            first_innings_runs = None

    # --- Build record ---
    records.append({
        "match_id": match_id,
        "filename": filename,
        "date": date,
        "city": city,
        "venue": venue,
        "season": season,
        "event_name": event_name,
        "match_type": match_type,
        "gender": gender,
        "team1": team1,
        "team2": team2,
        "toss_winner": toss_winner,
        "toss_decision": toss_decision,
        "winner": winner,
        "overs": overs,
        "player_of_match": player_of_match,
        "first_innings_runs": first_innings_runs,
    })

    # --- Auto-save every 2000 files ---
    if i % 2000 == 0:
        df_temp = pd.DataFrame(records)
        df_temp.to_csv(OUTPUT_FILE, index=False)
        print(f"\n💾 Auto-saved {i} records to {OUTPUT_FILE}")

# --- Final DataFrame creation ---
df = pd.DataFrame(records)

# --- Clean the dataset ---
print("\n🧹 Cleaning data...")

# Drop rows missing only *critical* information
df = df.dropna(subset=["venue", "winner", "team1", "team2"])

# Fill optional fields
df["player_of_match"] = df["player_of_match"].fillna("Unknown").replace("", "Unknown")
df["city"] = df["city"].fillna("Unknown").replace("", "Unknown")
df["overs"] = df["overs"].fillna(0)

print(f"✅ After cleaning: {len(df)} matches remain.")

# --- Save CSV ---
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)
print(f"\n✅ Completed! Saved {len(df)} matches to {OUTPUT_FILE}")
print(df.head().to_string(index=False))
