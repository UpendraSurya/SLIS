"""Dashboard stats and model metrics endpoints."""
import json
from pathlib import Path
from fastapi import APIRouter
from backend.ml_service import ml_service
from backend.data_store import data_store

router = APIRouter(prefix="/api", tags=["dashboard"])
ML_DIR = Path(__file__).parent.parent.parent / "ml"


@router.get("/dashboard/stats")
def get_dashboard_stats():
    rows = []
    for sid, s in data_store.students.items():
        feat = data_store.build_feat_dict(sid)
        risk = ml_service.predict_risk(feat)
        rows.append({
            "student_id":     sid,
            "name":           s["name"],
            "avg_score":      round(feat["avg_weighted"], 1),
            "avg_attendance": round(feat["avg_attendance"], 1),
            "risk_level":     risk["risk_level"],
        })

    total     = len(rows)
    high_risk = sum(1 for r in rows if r["risk_level"] == "High")
    avg_perf  = round(sum(r["avg_score"] for r in rows) / total, 1) if total else 0
    avg_att   = round(sum(r["avg_attendance"] for r in rows) / total, 1) if total else 0

    risk_dist = {"Low": 0, "Medium": 0, "High": 0}
    for r in rows:
        risk_dist[r["risk_level"]] += 1

    subj_totals: dict = {}
    subj_counts: dict = {}
    for sc_list in data_store.scores.values():
        for sc in sc_list:
            subj = sc["subject"]
            subj_totals[subj] = subj_totals.get(subj, 0) + sc["weighted_score"]
            subj_counts[subj] = subj_counts.get(subj, 0) + 1
    subject_avgs = {s: round(subj_totals[s] / subj_counts[s], 1) for s in subj_totals}

    sorted_rows = sorted(rows, key=lambda x: x["avg_score"], reverse=True)
    return {
        "total_students":    total,
        "high_risk_count":   high_risk,
        "avg_performance":   avg_perf,
        "avg_attendance":    avg_att,
        "risk_distribution": risk_dist,
        "subject_averages":  subject_avgs,
        "top_5_students":    sorted_rows[:5],
        "bottom_5_students": sorted_rows[-5:][::-1],
    }


@router.get("/model-metrics")
def get_model_metrics():
    with open(ML_DIR / "model_metrics.json") as f:
        return json.load(f)
