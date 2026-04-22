"""ML Service — loads models once on startup, provides inference functions."""
import json
import joblib
import numpy as np
from pathlib import Path

ML_DIR = Path(__file__).parent.parent / "ml"
RISK_LABELS = {0: "Low", 1: "Medium", 2: "High"}


class MLService:
    def __init__(self):
        self.classifier   = None
        self.regressor    = None
        self.clf_features = []
        self.reg_features = []
        self.metrics      = {}

    def load(self):
        self.classifier   = joblib.load(ML_DIR / "risk_classifier.joblib")
        self.regressor    = joblib.load(ML_DIR / "performance_predictor.joblib")
        with open(ML_DIR / "feature_columns.json") as f:
            cols = json.load(f)
        self.clf_features = cols["risk_classifier"]
        self.reg_features = cols["performance_predictor"]
        with open(ML_DIR / "model_metrics.json") as f:
            self.metrics = json.load(f)
        print("[ML] Models loaded successfully")

    def _build_features(self, feat_list: list, feat_dict: dict) -> np.ndarray:
        return np.array([[feat_dict.get(f, 0.0) for f in feat_list]])

    def predict_risk(self, feat_dict: dict) -> dict:
        x         = self._build_features(self.clf_features, feat_dict)
        label_int = int(self.classifier.predict(x)[0])
        proba     = self.classifier.predict_proba(x)[0]
        return {
            "risk_label": label_int,
            "risk_level": RISK_LABELS[label_int],
            "risk_probabilities": {RISK_LABELS[i]: round(float(p), 4) for i, p in enumerate(proba)},
        }

    def predict_performance(self, feat_dict: dict) -> float:
        x = self._build_features(self.reg_features, feat_dict)
        return float(np.clip(self.regressor.predict(x)[0], 0, 100))


ml_service = MLService()
