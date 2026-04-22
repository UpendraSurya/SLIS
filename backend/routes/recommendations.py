"""AI Recommendations via HuggingFace Inference API (Qwen/Qwen3-32B)."""
import os
import re
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from huggingface_hub import InferenceClient

from backend.data_store import data_store
from backend.ml_service import ml_service

router = APIRouter(prefix="/api", tags=["recommendations"])


def _get_hf_token() -> str:
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        hf_file = Path.home() / ".hf_token"
        if hf_file.exists():
            token = hf_file.read_text().strip()
    return token


def _build_profile(sid: str) -> dict:
    s = data_store.students.get(sid)
    if not s:
        raise HTTPException(404, f"Student {sid} not found")

    feat = data_store.build_feat_dict(sid)
    risk = ml_service.predict_risk(feat)
    sc   = data_store.scores.get(sid, [])
    act  = data_store.activity.get(sid, {})

    subject_scores = {r["subject"]: r["weighted_score"] for r in sc}
    worst = min(subject_scores, key=subject_scores.get) if subject_scores else "Unknown"
    best  = max(subject_scores, key=subject_scores.get) if subject_scores else "Unknown"

    return {
        "name":                s["name"],
        "major":               s["major"],
        "age":                 s["age"],
        "gpa_start":           feat["gpa_start"],
        "avg_score":           round(feat["avg_weighted"], 1),
        "avg_attendance":      round(feat["avg_attendance"], 1),
        "risk_level":          risk["risk_level"],
        "lms_logins_per_week": feat["lms_logins_per_week"],
        "forum_posts":         feat["forum_posts"],
        "resources_accessed":  feat["resources_accessed"],
        "avg_session_minutes": feat["avg_session_minutes"],
        "worst_subject":       worst,
        "best_subject":        best,
        "subject_scores":      subject_scores,
    }


def _call_hf(profile: dict, token: str) -> list:
    client = InferenceClient(token=token)
    prompt = f"""You are an academic advisor AI. Analyze this student profile and provide 4 specific, actionable recommendations.

Student Profile:
- Name: {profile['name']} | Major: {profile['major']} | Age: {profile['age']}
- Starting GPA: {profile['gpa_start']} | Current Average Score: {profile['avg_score']}/100
- Attendance: {profile['avg_attendance']}% | Risk Level: {profile['risk_level']}
- LMS Logins/Week: {profile['lms_logins_per_week']} | Forum Posts: {profile['forum_posts']}
- Resources Accessed: {profile['resources_accessed']} | Avg Session: {profile['avg_session_minutes']} min
- Weakest Subject: {profile['worst_subject']} ({profile['subject_scores'].get(profile['worst_subject'], 'N/A')}/100)
- Strongest Subject: {profile['best_subject']} ({profile['subject_scores'].get(profile['best_subject'], 'N/A')}/100)

Return ONLY a JSON array with exactly 4 recommendations. Each item must have:
- "title": short action title (max 8 words)
- "description": specific 2-sentence actionable advice for THIS student
- "priority": one of "High", "Medium", or "Low"

Output only the JSON array, no other text."""

    response = client.chat_completion(
        model="Qwen/Qwen3-32B",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.3,
    )
    text  = response.choices[0].message.content
    match = re.search(r'\[[\s\S]*\]', text)
    recs  = json.loads(match.group() if match else text)
    return [{"title": r.get("title",""), "description": r.get("description",""),
              "priority": r.get("priority","Medium")} for r in recs[:4]]


def _fallback(profile: dict, student_id: str) -> dict:
    recs = []
    if profile["avg_attendance"] < 75:
        recs.append({"title": "Improve Attendance Immediately",
                     "description": f"Your attendance of {profile['avg_attendance']}% is critically low. Aim for at least 85% — each missed class reduces your final score by ~1.2 points.",
                     "priority": "High"})
    if profile["lms_logins_per_week"] < 5:
        recs.append({"title": "Increase LMS Engagement",
                     "description": f"You log in only {profile['lms_logins_per_week']:.1f} times/week. Set a goal of daily logins to stay current with materials and assignments.",
                     "priority": "High" if profile["risk_level"] == "High" else "Medium"})
    if profile["worst_subject"]:
        recs.append({"title": f"Focus on {profile['worst_subject']}",
                     "description": f"Your score of {profile['subject_scores'].get(profile['worst_subject'],0):.0f}/100 in {profile['worst_subject']} drags your average down. Dedicate 3 extra hours/week and attend office hours.",
                     "priority": "High"})
    recs.append({"title": "Schedule Regular Study Sessions",
                 "description": f"With {profile['avg_session_minutes']:.0f} min avg sessions, schedule two 90-minute blocks per day using the Pomodoro technique for sustained focus.",
                 "priority": "Low"})
    return {"student_id": student_id, "student_name": profile["name"], "recommendations": recs[:4]}


@router.get("/recommendations/{student_id}")
def get_recommendations(student_id: str):
    profile = _build_profile(student_id)
    token   = _get_hf_token()
    if not token:
        return _fallback(profile, student_id)
    try:
        recs = _call_hf(profile, token)
        return {"student_id": student_id, "student_name": profile["name"], "recommendations": recs}
    except Exception as e:
        print(f"[HF] Error: {e} — falling back to rule-based")
        return _fallback(profile, student_id)
