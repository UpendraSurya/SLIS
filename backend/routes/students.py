"""Student routes — list, detail."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from backend.ml_service import ml_service
from backend.data_store import data_store

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("")
def list_students(
    page:        int           = Query(1, ge=1),
    limit:       int           = Query(20, ge=1, le=100),
    risk_filter: Optional[str] = Query(None),
    search:      Optional[str] = Query(None),
):
    rows = []
    for sid, s in data_store.students.items():
        feat      = data_store.build_feat_dict(sid)
        risk_info = ml_service.predict_risk(feat)
        rows.append({
            "student_id":     sid,
            "name":           s["name"],
            "major":          s["major"],
            "age":            s["age"],
            "gpa_start":      s["gpa_start"],
            "avg_score":      round(feat["avg_weighted"], 1),
            "avg_attendance": round(feat["avg_attendance"], 1),
            "risk_level":     risk_info["risk_level"],
        })

    if risk_filter:
        rows = [r for r in rows if r["risk_level"] == risk_filter]
    if search:
        q = search.lower()
        rows = [r for r in rows if q in r["name"].lower() or q in r["student_id"].lower()]

    total  = len(rows)
    offset = (page - 1) * limit
    return {"total": total, "page": page, "limit": limit, "students": rows[offset: offset + limit]}


@router.get("/{student_id}")
def get_student(student_id: str):
    s = data_store.students.get(student_id)
    if not s:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    feat       = data_store.build_feat_dict(student_id)
    risk_info  = ml_service.predict_risk(feat)
    pred_score = ml_service.predict_performance(feat)

    att_list   = data_store.attendance.get(student_id, [])
    score_list = data_store.scores.get(student_id, [])
    act        = data_store.activity.get(student_id, {})

    return {
        **s,
        "avg_attendance":      round(feat["avg_attendance"], 1),
        "avg_score":           round(feat["avg_weighted"], 1),
        "engagement_score":    round(feat["engagement_score"], 2),
        "risk_level":          risk_info["risk_level"],
        "risk_probabilities":  risk_info["risk_probabilities"],
        "predicted_score":     round(pred_score, 1),
        "attendance_by_month": sorted(att_list, key=lambda x: x["month"]),
        "scores_by_subject":   score_list,
        "activity":            act,
    }
