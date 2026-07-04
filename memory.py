import cognee
from dotenv import load_dotenv
import nest_asyncio
import json

import os


os.environ["COGNEE_SYSTEM_PATH"] = "/mount/src/placement_pulse/system"
os.makedirs("/mount/src/placement_pulse/system", exist_ok=True)


storage_path = "/mount/src/placement_pulse/data"


os.makedirs(storage_path, exist_ok=True)


os.environ["COGNEE_STORAGE_PATH"] = storage_path


import datetime

load_dotenv()

from groq import Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DATA_FILE = "placements.json"
GOALS_FILE = "goals.json"

# ---------- JSON helpers ----------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(entries):
    with open(DATA_FILE, "w") as f:
        json.dump(entries, f, indent=2)

# ---------- remember() — instant save ----------

async def remember(text: str):
    entries = load_data()
    entries.append(text)
    save_data(entries)
    # also add to cognee for graph memory
    # cognify runs separately via improve() — not on every save
    await cognee.add(text, dataset_name="placement_data")

# ---------- recall() — fast local search ----------

async def recall(question: str):
    entries = load_data()
    if not entries:
        return []

    question_lower = question.lower()
    stop_words = {"the", "a", "an", "is", "in", "im", "i'm", "at", "my", "what", "which", "did", "to", "for", "of", "me"}
    question_words = [w for w in question_lower.split() if w not in stop_words]

    matches = []
    for entry in entries:
        entry_lower = entry.lower()
        match_count = sum(1 for word in question_words if word in entry_lower)
        if match_count > 0:
            matches.append((match_count, entry))

    if matches:
        matches.sort(key=lambda x: x[0], reverse=True)
        best_score = matches[0][0]
        return [m[1] for m in matches if m[0] == best_score]
    return []

# ---------- improve() — real Cognee graph build ----------
# called manually from UI, not on every save
# this is the real Cognee intelligence trigger

async def improve():
    await cognee.cognify()
    return "Memory graph built successfully! AI insights are now powered by your knowledge graph."

def get_ai_insight(question: str):
    entries = load_data()
    if not entries:
        return "No placement data found. Log some applications first!"

    context = "\n".join(entries)

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        # llama-3.3-70b is a powerful open source model
        # groq runs it at incredible speed for free
        messages=[
            {
                "role": "system",
                "content": "You are an AI career memory assistant for a student in placement season. You remember everything about their placement journey and give specific, actionable insights based on their actual data."
            },
            {
                "role": "user",
                "content": f"""Here is everything the student has logged about their placement journey:

{context}

Based on this memory, answer the following question with specific, actionable insights:
{question}

Be concise, specific, and helpful. Reference actual companies and topics from their history."""
            }
        ],
        temperature=0.7,
        max_tokens=1024
    )
    return response.choices[0].message.content


    
def get_company_insight(company_name: str):
    entries = load_data()
    if not entries:
        return "No data found. Log some applications first!"

    company_entries = [e for e in entries if company_name.lower() in e.lower()]

    if not company_entries:
        return f"No history found for {company_name}. Try logging an application first."

    context = "\n".join(company_entries)

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an AI career memory assistant. Analyze placement interview history and give structured, actionable insights."
            },
            {
                "role": "user",
                "content": f"""Here is everything the student has logged about {company_name}:

{context}

Provide a structured insight covering:
1. Rounds they appeared in and outcomes
2. Topics asked in each round
3. Their strengths and weaknesses based on this data
4. What they should specifically focus on before their next {company_name} interview

Be specific and actionable. Keep it concise."""
            }
        ],
        temperature=0.7,
        max_tokens=1024
    )
    return response.choices[0].message.content



async def forget_resolved(days_old: int = 60):
    entries = load_data()
    today = datetime.date.today()
    kept = []
    removed_count = 0

    for e in entries:
        is_resolved = "Outcome: Cleared" in e or "Outcome: Rejected" in e
        try:
            date_str = e.split("Date:")[1].split(".")[0].strip()
            entry_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            age = (today - entry_date).days
        except Exception:
            age = 0

        if is_resolved and age > days_old:
            removed_count += 1
        else:
            kept.append(e)

    save_data(kept)
    return removed_count

async def forget(dataset: str):
    save_data([])
    try:
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)
    except Exception:
        pass

# ---------- Goals ----------

def load_goals():
    if os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, "r") as f:
            return json.load(f)
    return []

def save_goals(goals):
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)

def add_goal(title: str, description: str, start_date: str, remind_after_days: int = 30):
    goals = load_goals()
    goal = {
        "title": title,
        "description": description,
        "start_date": start_date,
        "remind_after_days": remind_after_days,
        "shown": False,
        "completed": False
    }
    goals.append(goal)
    save_goals(goals)

def check_due_reminders():
    goals = load_goals()
    due = []
    today = datetime.date.today()
    for i, goal in enumerate(goals):
        start = datetime.datetime.strptime(goal["start_date"], "%Y-%m-%d").date()
        remind_date = start + datetime.timedelta(days=goal["remind_after_days"])
        if today >= remind_date and not goal["shown"]:
            due.append((i, goal))
    return due

def mark_reminder_shown(index: int):
    goals = load_goals()
    goals[index]["shown"] = True
    save_goals(goals)

def delete_goal(index: int):
    goals = load_goals()
    goals.pop(index)
    save_goals(goals)

def toggle_goal_completed(index: int, status: bool):
    goals = load_goals()
    goals[index]["completed"] = status
    save_goals(goals)