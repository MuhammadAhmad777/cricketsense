# scripts/react_agent.py

import os
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Initialize Groq client ---
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Load match data ---
DATA_PATH = os.path.join("data", "matches_summary.csv")
df = pd.read_csv(DATA_PATH)

# --- Action (tool) functions ---

def search_venue(venue):
    """Return matches played at a given venue."""
    matches = df[df["venue"].str.contains(venue, case=False, na=False)]
    if matches.empty:
        return f"No matches found at venue '{venue}'."
    return matches[["teams", "winner", "venue"]].to_string(index=False)

def search_match(venue, team1, team2):
    """Return details for a specific match based on venue and two teams."""
    mask = (
        df["venue"].str.contains(venue, case=False, na=False)
        & df["teams"].str.contains(team1, case=False, na=False)
        & df["teams"].str.contains(team2, case=False, na=False)
    )
    match = df[mask]
    if match.empty:
        return f"No match found at {venue} between {team1} and {team2}."
    row = match.iloc[0]
    return f"At {row['venue']}, {row['teams']} played. Winner: {row['winner']}."

def search_winner(venue):
    """Quickly return who won at a given venue (first match found)."""
    matches = df[df["venue"].str.contains(venue, case=False, na=False)]
    if matches.empty:
        return f"No matches found at venue '{venue}'."
    winners = matches["winner"].dropna().unique().tolist()
    if len(winners) == 1:
        return f"{winners[0]} won the match at {venue}."
    else:
        return f"Matches at {venue} have multiple winners: {', '.join(winners)}."

# --- Tool registry ---
TOOLS = {
    "SearchVenue": search_venue,
    "SearchMatch": search_match,
    "SearchWinner": search_winner,
}

# --- Main ReAct loop ---
def react_loop(user_query):
    prompt = f"""
You are a cricket data assistant using ReAct reasoning.
You can use these actions:
{', '.join(TOOLS.keys())}

Use the pattern:
Thought: <your reasoning>
Action: <ToolName>(parameters)
Observation: <tool output>
Repeat as needed, then conclude with:
Final Answer: <final answer>

Question: {user_query}
"""
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    print("--- Model Output ---")
    print(completion.choices[0].message.content)

# --- Script entry point ---
if __name__ == "__main__":
    query = input("Ask a cricket question: ")
    react_loop(query)
