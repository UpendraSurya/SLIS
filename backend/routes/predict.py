"""Prediction endpoint."""
from fastapi import APIRouter
from backend.models.schemas import PredictRequest, PredictResponse
from backend.ml_service import ml_service

router = APIRouter(prefix="/api", tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # Estimate missing score features from GPA (scaled to match training data range 0–100)
    est_score = req.gpa_start * 10.0  # gpa 1–10 → score 10–100
    feat_dict = {
        "avg_attendance":      req.avg_attendance,
        "att_month1":          req.avg_attendance,
        "att_month2":          req.avg_attendance,
        "att_trend":           0.0,
        "engagement_score":    req.engagement_score,
        "gpa_start":           req.gpa_start,
        "avg_it1":             est_score,
        "avg_it2":             est_score,
        "it1_it2_delta":       0.0,
        "it1_it2_slope":       0.0,
        "avg_roll_w4":         est_score,
        "avg_roll_w8":         est_score,
        "it1_std":             0.0,
        "it2_std":             0.0,
        "it1_range":           0.0,
        "it2_range":           0.0,
        "lms_logins_per_week": req.lms_logins_per_week,
        "forum_posts":         req.forum_posts,
        "resources_accessed":  req.lms_logins_per_week * 3,
        "avg_session_minutes": 45.0,
    }

    risk_info  = ml_service.predict_risk(feat_dict)
    pred_score = ml_service.predict_performance(feat_dict)

    return PredictResponse(
        risk_level=risk_info["risk_level"],
        risk_probabilities=risk_info["risk_probabilities"],
        predicted_score=round(pred_score, 1),
    )
