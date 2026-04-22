"""
SLIS — Checkpoint Risk Prediction
==================================
Simulates a real early-warning system with two prediction windows:

  Checkpoint 1 — After IT1 (month 1 complete):
    Features available: GPA, month-1 attendance, IT1 score, weeks-1-4 rolling avg, LMS activity
    → Predict who is at risk BEFORE IT2

  Checkpoint 2 — After IT2 (month 2 complete):
    Features available: all of above + month-2 attendance, IT2 score, IT1→IT2 delta, weeks-5-8 rolling avg
    → Predict who is at risk BEFORE Final Exam

Saves:
  data/snapshot_after_it1.csv  — 500 student feature snapshots at checkpoint 1
  data/snapshot_after_it2.csv  — 500 student feature snapshots at checkpoint 2
  ml/risk_predictions_it1.csv  — predictions at checkpoint 1
  ml/risk_predictions_it2.csv  — predictions at checkpoint 2
  ml/risk_shift_comparison.csv — side-by-side showing students whose risk changed
"""

import json
import warnings
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report

warnings.filterwarnings("ignore")

DATA_DIR = Path(__file__).parent.parent / "data"
ML_DIR   = Path(__file__).parent

RISK_MAP   = {0: "Low", 1: "Medium", 2: "High"}
RISK_COLOR = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}

# ── Load raw data ─────────────────────────────────────────────────────────────
students   = pd.read_csv(DATA_DIR / "students.csv")
attendance = pd.read_csv(DATA_DIR / "attendance.csv")
scores     = pd.read_csv(DATA_DIR / "scores.csv")
activity   = pd.read_csv(DATA_DIR / "activity.csv")

# ── Build per-student aggregates ──────────────────────────────────────────────
# Attendance by month
att_pivot = attendance.pivot(index="student_id", columns="month", values="attendance_pct")
att_pivot.columns = [f"att_month{c}" for c in att_pivot.columns]
att_pivot["avg_attendance"] = att_pivot.mean(axis=1)
att_pivot["att_trend"] = att_pivot[["att_month1","att_month2","att_month3","att_month4"]].apply(
    lambda row: float(np.polyfit([1,2,3,4], row.values, 1)[0]), axis=1
)

# Scores aggregated per student
sc_agg = scores.groupby("student_id").agg(
    avg_it1       = ("it1_score",      "mean"),
    avg_it2       = ("it2_score",      "mean"),
    avg_final     = ("final_score",    "mean"),
    avg_roll_w4   = ("roll_avg_w4",    "mean"),
    avg_roll_w8   = ("roll_avg_w8",    "mean"),
    avg_weighted  = ("weighted_score", "mean"),
    avg_trend     = ("score_trend",    "mean"),
).reset_index()
sc_agg["it1_it2_delta"] = sc_agg["avg_it2"] - sc_agg["avg_it1"]

# True risk label (ground truth — based on final weighted score)
def risk_label(ws):
    if ws > 70:   return 0
    elif ws >= 50: return 1
    else:         return 2

sc_agg["true_risk"] = sc_agg["avg_weighted"].apply(risk_label)

# Engagement (LMS activity — available throughout semester)
activity["engagement_score"] = (
    activity["lms_logins_per_week"]  * 0.4 +
    activity["forum_posts"]          * 0.3 +
    activity["resources_accessed"]   * 0.2 +
    (activity["avg_session_minutes"] / 60) * 0.1
)

# ── Master merge ──────────────────────────────────────────────────────────────
master = (students[["student_id","name","major","gpa_start","archetype"]]
          .merge(att_pivot.reset_index(), on="student_id")
          .merge(sc_agg,   on="student_id")
          .merge(activity[["student_id","lms_logins_per_week","forum_posts",
                            "resources_accessed","avg_session_minutes","engagement_score"]],
                 on="student_id"))

# ─────────────────────────────────────────────────────────────────────────────
# CHECKPOINT 1 — After IT1
# Features available: GPA, month-1 attendance, IT1 score, roll_w4, LMS activity
# ─────────────────────────────────────────────────────────────────────────────
CP1_FEATURES = [
    "gpa_start",              # known at enrollment
    "att_month1",             # attendance pre-IT1
    "avg_it1",                # IT1 score (week 4)
    "avg_roll_w4",            # assignment avg weeks 1-4
    "engagement_score",       # LMS activity (cumulative so far)
    "lms_logins_per_week",
    "forum_posts",
]

# ─────────────────────────────────────────────────────────────────────────────
# CHECKPOINT 2 — After IT2
# Features available: all CP1 + month-2 attendance, IT2 score, delta, roll_w8
# ─────────────────────────────────────────────────────────────────────────────
CP2_FEATURES = [
    "gpa_start",
    "att_month1",
    "att_month2",             # attendance between IT1 and IT2
    "att_trend",              # attendance direction (months 1-2 slope)
    "avg_it1",
    "avg_it2",                # IT2 score (week 8)
    "it1_it2_delta",          # improvement or drop between tests
    "avg_roll_w4",
    "avg_roll_w8",            # assignment avg weeks 5-8
    "engagement_score",
    "lms_logins_per_week",
    "forum_posts",
    "resources_accessed",
]

X_all = master[CP1_FEATURES + [f for f in CP2_FEATURES if f not in CP1_FEATURES]].copy()
y_all = master["true_risk"].values
sids  = master["student_id"].values

print("=" * 65)
print("SLIS — Checkpoint Risk Predictions")
print("=" * 65)
print(f"\nStudents: {len(master)}")
print(f"True risk distribution:")
for k in [0,1,2]:
    n = (y_all == k).sum()
    print(f"  {RISK_MAP[k]:8s}: {n:4d}  ({n/len(y_all)*100:.1f}%)")

# ── Train checkpoint models ───────────────────────────────────────────────────
def train_model(X, y, name, features):
    pipe = Pipeline([
        ("sc",  StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, C=0.5, random_state=42)),
    ])
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv  = cross_val_score(pipe, X, y, cv=skf, scoring="f1_macro")
    print(f"\n  {name}")
    print(f"  Features ({len(features)}): {', '.join(features)}")
    print(f"  CV F1-macro: {cv.mean():.4f} ± {cv.std():.4f}")
    pipe.fit(X, y)
    return pipe

print("\n" + "─" * 65)
print("Training checkpoint models...")

model_cp1 = train_model(master[CP1_FEATURES].values, y_all, "Checkpoint 1 (after IT1)", CP1_FEATURES)
model_cp2 = train_model(master[CP2_FEATURES].values, y_all, "Checkpoint 2 (after IT2)", CP2_FEATURES)

# ── Predictions ───────────────────────────────────────────────────────────────
pred_cp1       = model_cp1.predict(master[CP1_FEATURES].values)
proba_cp1      = model_cp1.predict_proba(master[CP1_FEATURES].values)

pred_cp2       = model_cp2.predict(master[CP2_FEATURES].values)
proba_cp2      = model_cp2.predict_proba(master[CP2_FEATURES].values)

# ── Build snapshot CSVs ───────────────────────────────────────────────────────

# Snapshot after IT1
snap_it1 = master[["student_id","name","major","gpa_start","archetype"] + CP1_FEATURES].copy()
snap_it1["avg_it1"]         = master["avg_it1"].round(1)
snap_it1["predicted_risk"]  = [RISK_MAP[p] for p in pred_cp1]
snap_it1["prob_low"]        = proba_cp1[:, 0].round(3)
snap_it1["prob_medium"]     = proba_cp1[:, 1].round(3)
snap_it1["prob_high"]       = proba_cp1[:, 2].round(3)
snap_it1["true_risk"]       = [RISK_MAP[r] for r in y_all]
snap_it1["correct"]         = (pred_cp1 == y_all)
snap_it1 = snap_it1.sort_values("prob_high", ascending=False)
snap_it1.to_csv(DATA_DIR / "snapshot_after_it1.csv", index=False)
print(f"\n[✓] Saved data/snapshot_after_it1.csv — {len(snap_it1)} rows")

# Snapshot after IT2
snap_it2 = master[["student_id","name","major","gpa_start","archetype"] + CP2_FEATURES].copy()
snap_it2["avg_it1"]         = master["avg_it1"].round(1)
snap_it2["avg_it2"]         = master["avg_it2"].round(1)
snap_it2["it1_it2_delta"]   = master["it1_it2_delta"].round(1)
snap_it2["predicted_risk"]  = [RISK_MAP[p] for p in pred_cp2]
snap_it2["prob_low"]        = proba_cp2[:, 0].round(3)
snap_it2["prob_medium"]     = proba_cp2[:, 1].round(3)
snap_it2["prob_high"]       = proba_cp2[:, 2].round(3)
snap_it2["true_risk"]       = [RISK_MAP[r] for r in y_all]
snap_it2["correct"]         = (pred_cp2 == y_all)
snap_it2 = snap_it2.sort_values("prob_high", ascending=False)
snap_it2.to_csv(DATA_DIR / "snapshot_after_it2.csv", index=False)
print(f"[✓] Saved data/snapshot_after_it2.csv — {len(snap_it2)} rows")

# ── Risk predictions CSVs (clean output) ─────────────────────────────────────
def make_pred_csv(sids, names, majors, preds, probas, true_risk, checkpoint_label):
    rows = []
    for sid, name, major, pred, proba, true in zip(sids, names, majors, preds, probas, true_risk):
        rows.append({
            "student_id":     sid,
            "name":           name,
            "major":          major,
            "checkpoint":     checkpoint_label,
            "predicted_risk": RISK_MAP[pred],
            "true_risk":      RISK_MAP[true],
            "correct":        pred == true,
            "prob_low":       round(proba[0], 3),
            "prob_medium":    round(proba[1], 3),
            "prob_high":      round(proba[2], 3),
            "confidence":     round(max(proba), 3),
        })
    return pd.DataFrame(rows)

df_pred_it1 = make_pred_csv(
    master["student_id"], master["name"], master["major"],
    pred_cp1, proba_cp1, y_all, "After IT1"
)
df_pred_it2 = make_pred_csv(
    master["student_id"], master["name"], master["major"],
    pred_cp2, proba_cp2, y_all, "After IT2"
)

df_pred_it1.to_csv(ML_DIR / "risk_predictions_it1.csv", index=False)
df_pred_it2.to_csv(ML_DIR / "risk_predictions_it2.csv", index=False)
print(f"[✓] Saved ml/risk_predictions_it1.csv")
print(f"[✓] Saved ml/risk_predictions_it2.csv")

# ── Risk shift comparison ─────────────────────────────────────────────────────
# Show students whose predicted risk CHANGED between checkpoints
compare = pd.DataFrame({
    "student_id":    master["student_id"].values,
    "name":          master["name"].values,
    "major":         master["major"].values,
    "archetype":     master["archetype"].values,
    "avg_it1":       master["avg_it1"].round(1).values,
    "avg_it2":       master["avg_it2"].round(1).values,
    "it1_it2_delta": master["it1_it2_delta"].round(1).values,
    "att_month1":    master["att_month1"].round(1).values,
    "att_month2":    master["att_month2"].round(1).values,
    "risk_after_it1": [RISK_MAP[p] for p in pred_cp1],
    "risk_after_it2": [RISK_MAP[p] for p in pred_cp2],
    "true_risk":       [RISK_MAP[r] for r in y_all],
    "prob_high_it1":   proba_cp1[:, 2].round(3),
    "prob_high_it2":   proba_cp2[:, 2].round(3),
})

arch_map = {0:"Consistent", 1:"Late Bloomer", 2:"Early Bird", 3:"Struggle", 4:"Comeback"}
compare["archetype"] = compare["archetype"].map(arch_map)

# risk shift: -1 = improved (risk went down), 0 = same, +1 = worsened
risk_order = {"Low": 0, "Medium": 1, "High": 2}
compare["risk_it1_int"] = compare["risk_after_it1"].map(risk_order)
compare["risk_it2_int"] = compare["risk_after_it2"].map(risk_order)
compare["risk_shift"]   = compare["risk_it2_int"] - compare["risk_it1_int"]
compare["shift_label"]  = compare["risk_shift"].map(
    {-2:"⬇⬇ Big Drop", -1:"⬇ Improved", 0:"= Unchanged", 1:"⬆ Worsened", 2:"⬆⬆ Big Jump"}
)

# Save full comparison
compare.drop(columns=["risk_it1_int","risk_it2_int","risk_shift"]).to_csv(
    ML_DIR / "risk_shift_comparison.csv", index=False
)
print(f"[✓] Saved ml/risk_shift_comparison.csv")

# ── Final summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("ACCURACY COMPARISON")
print("=" * 65)
acc1 = (pred_cp1 == y_all).mean()
acc2 = (pred_cp2 == y_all).mean()
print(f"\n  Checkpoint 1 (after IT1) accuracy : {acc1:.4f}  ({acc1*100:.1f}%)")
print(f"  Checkpoint 2 (after IT2) accuracy : {acc2:.4f}  ({acc2*100:.1f}%)")
print(f"  Accuracy gain from IT2 data       : +{(acc2-acc1)*100:.1f} pp")

print("\n  Classification Report — After IT1:")
print(classification_report(y_all, pred_cp1, target_names=["Low","Medium","High"]))

print("  Classification Report — After IT2:")
print(classification_report(y_all, pred_cp2, target_names=["Low","Medium","High"]))

# Risk shift stats
print("=" * 65)
print("RISK SHIFT BETWEEN CHECKPOINTS")
print("=" * 65)
shift_counts = compare["shift_label"].value_counts()
for label, count in shift_counts.sort_index().items():
    print(f"  {label:20s}: {count:4d} students  ({count/len(compare)*100:.1f}%)")

print("\n  Shifts by archetype:")
shift_arch = compare.groupby("archetype")["risk_shift"].mean().round(3).sort_values()
for arch, val in shift_arch.items():
    direction = "↑ risk" if val > 0 else "↓ risk" if val < 0 else "stable"
    print(f"    {arch:15s}: avg shift = {val:+.3f}  ({direction})")

# Students who improved (risk went down after IT2)
improved = compare[compare["risk_shift"] < 0].sort_values("risk_shift")
worsened = compare[compare["risk_shift"] > 0].sort_values("risk_shift", ascending=False)

print(f"\n  Students who IMPROVED risk level   : {len(improved)}")
print(f"  Students who WORSENED risk level   : {len(worsened)}")
print(f"  Students with unchanged prediction : {(compare['risk_shift']==0).sum()}")

if len(improved) > 0:
    print(f"\n  Top 5 improvers (risk dropped after IT2):")
    for _, r in improved.head(5).iterrows():
        delta = f"{r['it1_it2_delta']:+.1f}"
        print(f"    {r['student_id']}  {r['name']:<22s}  "
              f"{r['risk_after_it1']:8s} → {r['risk_after_it2']:8s}  "
              f"IT1→IT2 delta: {delta:>6s}  [{r['archetype']}]")

if len(worsened) > 0:
    print(f"\n  Top 5 who worsened (risk increased after IT2):")
    for _, r in worsened.head(5).iterrows():
        delta = f"{r['it1_it2_delta']:+.1f}"
        print(f"    {r['student_id']}  {r['name']:<22s}  "
              f"{r['risk_after_it1']:8s} → {r['risk_after_it2']:8s}  "
              f"IT1→IT2 delta: {delta:>6s}  [{r['archetype']}]")

print(f"\n[✓] Done. 4 files saved:")
print(f"  data/snapshot_after_it1.csv     — student data + features at checkpoint 1")
print(f"  data/snapshot_after_it2.csv     — student data + features at checkpoint 2")
print(f"  ml/risk_predictions_it1.csv     — risk predictions after IT1")
print(f"  ml/risk_predictions_it2.csv     — risk predictions after IT2")
print(f"  ml/risk_shift_comparison.csv    — who changed risk between checkpoints")
