"""In-memory data store — loads all CSVs at startup."""
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


class DataStore:
    def __init__(self):
        self.students:   dict = {}
        self.attendance: dict = {}
        self.scores:     dict = {}
        self.activity:   dict = {}

    def load(self):
        students_df   = pd.read_csv(DATA_DIR / "students.csv")
        attendance_df = pd.read_csv(DATA_DIR / "attendance.csv")
        scores_df     = pd.read_csv(DATA_DIR / "scores.csv")
        activity_df   = pd.read_csv(DATA_DIR / "activity.csv")

        for _, row in students_df.iterrows():
            self.students[row["student_id"]] = row.to_dict()

        for sid, grp in attendance_df.groupby("student_id"):
            self.attendance[sid] = grp.sort_values("month")[["month", "attendance_pct"]].to_dict("records")

        for sid, grp in scores_df.groupby("student_id"):
            self.scores[sid] = grp[["subject", "it1_score", "it2_score", "final_score",
                                     "weighted_score", "assignment_avg",
                                     "roll_avg_w4", "roll_avg_w8"]].to_dict("records")

        for _, row in activity_df.iterrows():
            self.activity[row["student_id"]] = row.to_dict()

        print(f"[DataStore] Loaded {len(self.students)} students from CSVs")

    def build_feat_dict(self, sid: str) -> dict:
        """Build the full 18/20-feature dict the ML models expect."""
        s   = self.students.get(sid, {})
        att = self.attendance.get(sid, [])
        sc  = self.scores.get(sid, [])
        act = self.activity.get(sid, {})

        att_vals = [r["attendance_pct"] for r in sorted(att, key=lambda x: x["month"])]
        while len(att_vals) < 4:
            att_vals.append(0.0)

        avg_attendance = float(np.mean(att_vals))
        att_month1, att_month2, att_month3, att_month4 = att_vals[:4]
        att_trend = float(np.polyfit([1, 2, 3, 4], att_vals[:4], 1)[0]) if len(att_vals) >= 4 else 0.0

        avg_it1  = float(np.mean([r["it1_score"]      for r in sc])) if sc else 0.0
        avg_it2  = float(np.mean([r["it2_score"]      for r in sc])) if sc else 0.0
        avg_roll_w4 = float(np.mean([r["roll_avg_w4"] for r in sc])) if sc else 0.0
        avg_roll_w8 = float(np.mean([r["roll_avg_w8"] for r in sc])) if sc else 0.0
        it1_std  = float(np.std([r["it1_score"]  for r in sc])) if len(sc) > 1 else 0.0
        it2_std  = float(np.std([r["it2_score"]  for r in sc])) if len(sc) > 1 else 0.0
        it1_range = float(max(r["it1_score"] for r in sc) - min(r["it1_score"] for r in sc)) if sc else 0.0
        it2_range = float(max(r["it2_score"] for r in sc) - min(r["it2_score"] for r in sc)) if sc else 0.0

        lms_logins  = float(act.get("lms_logins_per_week", 0))
        forum_posts = float(act.get("forum_posts", 0))
        resources   = float(act.get("resources_accessed", 0))
        session_min = float(act.get("avg_session_minutes", 0))

        engagement_score = lms_logins * 0.4 + forum_posts * 0.3 + resources * 0.2 + (session_min / 60) * 0.1

        return {
            "avg_attendance":      avg_attendance,
            "att_month1":          att_month1,
            "att_month2":          att_month2,
            "att_month3":          att_month3,
            "att_month4":          att_month4,
            "att_trend":           att_trend,
            "engagement_score":    engagement_score,
            "gpa_start":           float(s.get("gpa_start", 5.0)),
            "avg_it1":             avg_it1,
            "avg_it2":             avg_it2,
            "it1_it2_delta":       avg_it2 - avg_it1,
            "it1_it2_slope":       (avg_it2 - avg_it1) / 4.0,
            "avg_roll_w4":         avg_roll_w4,
            "avg_roll_w8":         avg_roll_w8,
            "it1_std":             it1_std,
            "it2_std":             it2_std,
            "it1_range":           it1_range,
            "it2_range":           it2_range,
            "lms_logins_per_week": lms_logins,
            "forum_posts":         forum_posts,
            "resources_accessed":  resources,
            "avg_session_minutes": session_min,
            "avg_weighted":        float(np.mean([r["weighted_score"] for r in sc])) if sc else 0.0,
        }


data_store = DataStore()
