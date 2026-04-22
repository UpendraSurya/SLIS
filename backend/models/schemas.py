"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List


class PredictRequest(BaseModel):
    avg_attendance:       float = Field(..., ge=0, le=100)
    engagement_score:     float = Field(..., ge=0)
    gpa_start:            float = Field(..., ge=0.0, le=10.0)
    lms_logins_per_week:  float = Field(..., ge=0)
    forum_posts:          float = Field(..., ge=0)


class PredictResponse(BaseModel):
    risk_level:        str
    risk_probabilities: dict
    predicted_score:   float


class Recommendation(BaseModel):
    title:       str
    description: str
    priority:    str  # High / Medium / Low


class RecommendationsResponse(BaseModel):
    student_id:      str
    student_name:    str
    recommendations: List[Recommendation]
