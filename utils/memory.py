"""
Persistent JSON memory, same pattern as AstraMind Travel Agent: stores a
lightweight history of past analyses (filename, target role, timestamp,
top priorities, scores) so returning users can see progress over time.
Scores are stored specifically so the dashboard KPI cards can show a
real trend delta against the previous run, not a fabricated arrow.
"""
import json
import os
from datetime import datetime

HISTORY_PATH = os.path.join("data", "history.json")


def _ensure_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w") as f:
            json.dump([], f)


def load_history() -> list[dict]:
    _ensure_file()
    with open(HISTORY_PATH, "r") as f:
        return json.load(f)


def get_previous_scores() -> dict | None:
    """Returns the scores dict from the most recent prior analysis, or
    None if this is the first run ever. Used for KPI trend deltas."""
    history = load_history()
    if not history:
        return None
    return history[-1].get("scores")


def save_analysis(filename: str, target_role: str, results: dict):
    _ensure_file()
    history = load_history()
    overall = results.get("overall_recommendations", {})
    skills = results.get("skill_gap_analysis", {})
    current = skills.get("current_skills", [])
    missing = skills.get("missing_skills", [])
    total = len(current) + len(missing)
    skill_match = round((len(current) / total) * 100) if total else 0

    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "filename": filename,
        "target_role": target_role,
        "top_3_priorities": overall.get("top_3_priorities", []),
        "scores": {
            "resume_score": overall.get("resume_score", 0),
            "ats_score": overall.get("ats_score", 0),
            "skill_match": skill_match,
            "career_readiness": overall.get("career_readiness", 0),
        },
    }
    history.append(entry)
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)