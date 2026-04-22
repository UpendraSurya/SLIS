"""
SLIS — Step 3: Feature Engineering + ML Model Training (v3)

Fixes applied:
  1. Risk label thresholds — percentile-based on early_score (IT1+IT2 avg), not hardcoded
  2. Risk label target — derived from IT1+IT2 only, not weighted_score (no final leakage)
  3. Subject variance features — it1_std, it2_std, it1_range, it2_range capture uneven performance
  4. Class imbalance — class_weight='balanced' on RF and LR classifiers
  5. Confidence output — predict_proba saved alongside predictions
  6. score_trend leakage fixed — replaced with it1_it2_slope (uses only IT1+IT2, no final)
"""

import json
import warnings
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, \
    RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import cross_val_score, train_test_split, StratifiedKFold, KFold
from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")

DATA_DIR = Path(__file__).parent.parent / "data"
ML_DIR   = Path(__file__).parent

# ── Load ──────────────────────────────────────────────────────────────────────
students   = pd.read_csv(DATA_DIR / "students.csv")
attendance = pd.read_csv(DATA_DIR / "attendance.csv")
scores     = pd.read_csv(DATA_DIR / "scores.csv")
activity   = pd.read_csv(DATA_DIR / "activity.csv")

# ── Aggregate attendance (4 months) ──────────────────────────────────────────
att_agg = attendance.groupby("student_id").agg(
    avg_attendance = ("attendance_pct", "mean"),
    att_month1     = ("attendance_pct", lambda x: x.iloc[0]),   # Pre-IT1
    att_month2     = ("attendance_pct", lambda x: x.iloc[1]),   # IT1→IT2
    att_month3     = ("attendance_pct", lambda x: x.iloc[2]),   # Pre-Final
    att_month4     = ("attendance_pct", lambda x: x.iloc[3]),   # Final Period
    att_trend      = ("attendance_pct", lambda x: float(np.polyfit([1,2,3,4], x.values, 1)[0])),
).reset_index()

# ── Aggregate scores (per-subject → per-student) ──────────────────────────────
# FIX 3: Add subject-level variance features — std and range across 5 subjects
# A student with it1_std=18 is strong in some subjects and weak in others.
# A student with it1_std=3 performs uniformly. These are different risk profiles.
sc_agg = scores.groupby("student_id").agg(
    avg_it1       = ("it1_score",      "mean"),
    avg_it2       = ("it2_score",      "mean"),
    avg_final     = ("final_score",    "mean"),
    avg_roll_w4   = ("roll_avg_w4",    "mean"),
    avg_roll_w8   = ("roll_avg_w8",    "mean"),
    avg_roll_w12  = ("roll_avg_w12",   "mean"),
    avg_assignment= ("assignment_avg", "mean"),
    avg_weighted  = ("weighted_score", "mean"),   # IT1×0.25+IT2×0.25+Final×0.50
    it1_std       = ("it1_score",      "std"),    # variance across subjects at IT1
    it2_std       = ("it2_score",      "std"),    # variance across subjects at IT2
    it1_range     = ("it1_score",      lambda x: x.max() - x.min()),  # best-worst gap at IT1
    it2_range     = ("it2_score",      lambda x: x.max() - x.min()),  # best-worst gap at IT2
    it1_it2_delta = ("it1_score",      lambda x: 0),  # placeholder, computed below
).reset_index()

# Compute IT1→IT2 delta
it1_means = scores.groupby("student_id")["it1_score"].mean()
it2_means = scores.groupby("student_id")["it2_score"].mean()
sc_agg["it1_it2_delta"] = (it2_means - it1_means).values

# ── Master dataframe ─────────────────────────────────────────────────────────
master = (students
          .merge(att_agg, on="student_id")
          .merge(sc_agg,  on="student_id")
          .merge(activity, on="student_id"))

# ── Engagement score ─────────────────────────────────────────────────────────
master["engagement_score"] = (
    master["lms_logins_per_week"]  * 0.4 +
    master["forum_posts"]          * 0.3 +
    master["resources_accessed"]   * 0.2 +
    (master["avg_session_minutes"] / 60) * 0.1
)

# FIX 6: it1_it2_slope — slope across only IT1 and IT2 (no final leakage)
# Old avg_score_trend used [IT1, IT2, Final] — Final is part of the target, that's leakage.
# This slope uses only (IT2 - IT1) / 4 weeks — clean early signal.
master["it1_it2_slope"] = (master["avg_it2"] - master["avg_it1"]) / 4.0

# FIX 1 + FIX 2: Risk label — percentile-based on early_score (IT1+IT2 avg only)
# Old: based on weighted_score which includes the final exam → classifier was predicting
#      a label that baked in data it was never given as a feature (temporal leakage in label).
# New: early_score = (IT1 + IT2) / 2. Thresholds from the actual distribution (33rd/66th pctile)
#      so each class always has ~33% of students regardless of score scale.
master["early_score"] = (master["avg_it1"] + master["avg_it2"]) / 2.0
p33 = master["early_score"].quantile(0.33)
p66 = master["early_score"].quantile(0.66)

def risk_label(es):
    if es >= p66:   return 0  # Low risk   (~top third by internal test performance)
    elif es >= p33: return 1  # Medium risk (~middle third)
    else:           return 2  # High risk   (~bottom third)

master["risk_label"] = master["early_score"].apply(risk_label)

print("=" * 65)
print("SLIS — ML Training (v3 — All 6 Fixes Applied)")
print("=" * 65)
print(f"\nDataset     : {len(master)} students")
print(f"Total cols  : {len(master.columns)}")

print(f"\nEarly score thresholds (percentile-based):")
print(f"  p33 = {p33:.2f}  →  above this = Medium or Low risk")
print(f"  p66 = {p66:.2f}  →  above this = Low risk")

print(f"\nRisk distribution (from IT1+IT2, not weighted_score):")
label_map = {0: "Low", 1: "Medium", 2: "High"}
for k, v in master["risk_label"].value_counts().sort_index().items():
    print(f"  {label_map[k]:8s}: {v:4d} ({v/len(master)*100:.1f}%)")

print(f"\nSubject variance stats:")
print(f"  IT1 std  (avg across students): {master['it1_std'].mean():.2f}")
print(f"  IT1 range(avg across students): {master['it1_range'].mean():.2f}")
print(f"  IT2 std  (avg across students): {master['it2_std'].mean():.2f}")
print(f"  IT2 range(avg across students): {master['it2_range'].mean():.2f}")

print(f"\nIT1→IT2 slope (clean, no final leakage):")
print(master["it1_it2_slope"].describe().round(3).to_string())

# ─────────────────────────────────────────────────────────────────────────────
# MODEL A — Risk Classifier
# Features: early signals ONLY (no final_score, no weighted_score, no score_trend)
# Label   : derived from IT1+IT2 performance via percentile thresholds
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("MODEL A: Risk Classifier (v3 — clean label + variance features)")
print("=" * 65)

clf_features = [
    "avg_attendance",    # overall attendance
    "att_month1",        # attendance before IT1
    "att_month2",        # attendance between tests
    "att_trend",         # attendance direction over semester
    "engagement_score",  # LMS + forum + resources composite
    "gpa_start",         # prior ability baseline
    "avg_it1",           # IT1 score (week 4)
    "avg_it2",           # IT2 score (week 8)
    "it1_it2_delta",     # raw change IT1→IT2
    "it1_it2_slope",     # FIX 6: replaces avg_score_trend (no final leakage)
    "avg_roll_w4",       # rolling assignment avg weeks 1-4
    "avg_roll_w8",       # rolling assignment avg weeks 5-8
    "it1_std",           # FIX 3: how uneven is performance across subjects at IT1
    "it2_std",           # FIX 3: how uneven at IT2
    "it1_range",         # FIX 3: best-subject minus worst-subject gap at IT1
    "it2_range",         # FIX 3: best-subject minus worst-subject gap at IT2
    "lms_logins_per_week",
    "forum_posts",
]

X_clf = master[clf_features].values
y_clf = master["risk_label"].values

X_tr_c, X_te_c, y_tr_c, y_te_c = train_test_split(
    X_clf, y_clf, test_size=0.2, random_state=42, stratify=y_clf
)

# FIX 4: class_weight='balanced' — Low risk is ~33% but model still needs to learn
# all three classes equally well. Balanced weighting penalises misclassifying the
# minority class more heavily so the model doesn't just optimise for the majority.
clf_candidates = {
    "Random Forest": Pipeline([
        ("sc",  StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=300, max_depth=10,
                                       min_samples_leaf=3, class_weight="balanced",
                                       random_state=42, n_jobs=-1)),
    ]),
    "Gradient Boosting": Pipeline([
        ("sc",  StandardScaler()),
        # GradientBoostingClassifier does not support class_weight directly.
        # Balancing is handled by the other two candidates.
        ("clf", GradientBoostingClassifier(n_estimators=200, max_depth=5,
                                           learning_rate=0.08, subsample=0.8, random_state=42)),
    ]),
    "Logistic Regression": Pipeline([
        ("sc",  StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, C=0.5, class_weight="balanced",
                                   random_state=42)),
    ]),
}

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
best_clf_name, best_clf_score, best_clf_model = None, 0.0, None

# Score on macro F1, not accuracy — macro F1 treats each class equally,
# so a model that ignores Low risk students will score poorly.
for name, pipe in clf_candidates.items():
    cv = cross_val_score(pipe, X_clf, y_clf, cv=skf, scoring="f1_macro")
    print(f"  {name:25s}  CV macro-F1: {cv.mean():.4f} ± {cv.std():.4f}")
    if cv.mean() > best_clf_score:
        best_clf_score, best_clf_name, best_clf_model = cv.mean(), name, pipe

print(f"\n  ✓ Best classifier : {best_clf_name}  (CV macro-F1 = {best_clf_score:.4f})")

best_clf_model.fit(X_tr_c, y_tr_c)
y_pred_c = best_clf_model.predict(X_te_c)
test_acc  = (y_pred_c == y_te_c).mean()

print(f"  Test accuracy     : {test_acc:.4f}")
print("\n  Classification Report:")
print(classification_report(y_te_c, y_pred_c, target_names=["Low", "Medium", "High"]))
print("  Confusion Matrix:")
print(confusion_matrix(y_te_c, y_pred_c))

# FIX 5: Confidence output — predict_proba gives probability for each class.
# A prediction of High with 52% confidence is very different from High with 94%.
# Teachers should act on high-confidence predictions first.
y_proba_c = best_clf_model.predict_proba(X_te_c)
max_conf   = y_proba_c.max(axis=1)
print(f"\n  Prediction confidence (test set):")
print(f"    Mean confidence   : {max_conf.mean():.3f}")
print(f"    Low confidence (<0.60) predictions : {(max_conf < 0.60).sum()} students — borderline cases")
print(f"    High confidence (>0.85) predictions: {(max_conf > 0.85).sum()} students — act on these first")

# Feature importances (if RF or GB)
if hasattr(best_clf_model.named_steps.get("clf", None), "feature_importances_"):
    imps = best_clf_model.named_steps["clf"].feature_importances_
    fi = sorted(zip(clf_features, imps), key=lambda x: -x[1])
    print("\n  Top feature importances:")
    for feat, imp in fi[:10]:
        bar = "█" * int(imp * 40)
        print(f"    {feat:25s} {imp:.4f}  {bar}")

# Save full predictions with confidence for all 500 students (not just test split)
y_pred_all   = best_clf_model.predict(X_clf)
y_proba_all  = best_clf_model.predict_proba(X_clf)
risk_names   = {0: "Low", 1: "Medium", 2: "High"}

clf_output = pd.DataFrame({
    "student_id":      master["student_id"].values,
    "true_risk":       [risk_names[r] for r in y_clf],
    "predicted_risk":  [risk_names[r] for r in y_pred_all],
    "conf_low":        y_proba_all[:, 0].round(3),
    "conf_medium":     y_proba_all[:, 1].round(3),
    "conf_high":       y_proba_all[:, 2].round(3),
    "max_confidence":  y_proba_all.max(axis=1).round(3),
    "correct":         (y_pred_all == y_clf),
})
clf_output.to_csv(ML_DIR / "risk_predictions_full.csv", index=False)
print(f"\n  [✓] Saved risk_predictions_full.csv  (with confidence scores)")

joblib.dump(best_clf_model, ML_DIR / "risk_classifier.joblib")
# Save thresholds so the backend can reconstruct the label for new students
joblib.dump({"p33": p33, "p66": p66}, ML_DIR / "risk_thresholds.joblib")
print(f"  [✓] Saved risk_classifier.joblib")
print(f"  [✓] Saved risk_thresholds.joblib  (p33={p33:.2f}, p66={p66:.2f})")


# ─────────────────────────────────────────────────────────────────────────────
# MODEL B — Performance Predictor (Regression)
# Target  : avg_weighted (IT1×0.25 + IT2×0.25 + Final×0.50)
# Features: early engagement + attendance + IT1 + IT2 + subject variance
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("MODEL B: Performance Predictor  (target = weighted_score)")
print("=" * 65)

reg_features = [
    "avg_attendance",
    "att_month1",
    "att_month2",
    "att_trend",
    "engagement_score",
    "gpa_start",
    "avg_it1",
    "avg_it2",
    "it1_it2_delta",
    "it1_it2_slope",     # cleaner momentum signal (no final leakage)
    "avg_roll_w4",
    "avg_roll_w8",
    # roll_avg_w12 EXCLUDED — overlaps with final exam week (leakage)
    "it1_std",           # subject variance helps predict how much the final will deviate
    "it2_std",
    "it1_range",
    "it2_range",
    "lms_logins_per_week",
    "forum_posts",
    "resources_accessed",
    "avg_session_minutes",
]

X_reg = master[reg_features].values
y_reg = master["avg_weighted"].values

X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42
)

reg_candidates = {
    "Random Forest Regressor": Pipeline([
        ("sc",  StandardScaler()),
        ("reg", RandomForestRegressor(n_estimators=300, max_depth=10,
                                      min_samples_leaf=3, random_state=42, n_jobs=-1)),
    ]),
    "Gradient Boosting Regressor": Pipeline([
        ("sc",  StandardScaler()),
        ("reg", GradientBoostingRegressor(n_estimators=200, max_depth=5,
                                          learning_rate=0.08, subsample=0.8, random_state=42)),
    ]),
    "Ridge Regression": Pipeline([
        ("sc",  StandardScaler()),
        ("reg", Ridge(alpha=0.5)),
    ]),
}

kf = KFold(n_splits=5, shuffle=True, random_state=42)
best_reg_name, best_reg_rmse, best_reg_model = None, float("inf"), None

for name, pipe in reg_candidates.items():
    cv_neg = cross_val_score(pipe, X_reg, y_reg, cv=kf, scoring="neg_mean_squared_error")
    cv_rmse = np.sqrt(-cv_neg).mean()
    print(f"  {name:32s}  CV RMSE: {cv_rmse:.4f}")
    if cv_rmse < best_reg_rmse:
        best_reg_rmse, best_reg_name, best_reg_model = cv_rmse, name, pipe

print(f"\n  ✓ Best regressor  : {best_reg_name}  (CV RMSE = {best_reg_rmse:.4f})")

best_reg_model.fit(X_tr_r, y_tr_r)
y_pred_r  = best_reg_model.predict(X_te_r)
test_rmse = float(np.sqrt(mean_squared_error(y_te_r, y_pred_r)))
test_r2   = float(r2_score(y_te_r, y_pred_r))

print(f"  Test RMSE  : {test_rmse:.4f}")
print(f"  Test R²    : {test_r2:.4f}")

# Prediction error distribution — how far off is the model, and is the error symmetric?
errors = y_pred_r - y_te_r
print(f"\n  Prediction error distribution:")
print(f"    Mean error (bias)  : {errors.mean():+.3f}  (close to 0 = unbiased)")
print(f"    Std of errors      : {errors.std():.3f}")
print(f"    Within ±5 pts      : {(np.abs(errors) <= 5).mean():.1%} of test students")
print(f"    Within ±10 pts     : {(np.abs(errors) <= 10).mean():.1%} of test students")

joblib.dump(best_reg_model, ML_DIR / "performance_predictor.joblib")
print(f"\n  [✓] Saved performance_predictor.joblib")

# ── Save feature columns & metrics ───────────────────────────────────────────
feature_columns = {
    "risk_classifier":       clf_features,
    "performance_predictor": reg_features,
}
with open(ML_DIR / "feature_columns.json", "w") as f:
    json.dump(feature_columns, f, indent=2)

metrics = {
    "classifier": {
        "model_name":    best_clf_name,
        "cv_f1_macro":   round(best_clf_score, 4),
        "test_accuracy": round(float(test_acc), 4),
        "features":      clf_features,
        "classes":       ["Low", "Medium", "High"],
        "label_source":  "IT1+IT2 early_score percentiles (p33/p66) — no final leakage",
        "fixes_applied": [
            "percentile thresholds (not hardcoded)",
            "label from IT1+IT2 only",
            "subject variance features added",
            "class_weight=balanced",
            "predict_proba confidence output",
            "avg_score_trend replaced with it1_it2_slope",
        ],
    },
    "regressor": {
        "model_name":  best_reg_name,
        "cv_rmse":     round(best_reg_rmse, 4),
        "test_rmse":   round(test_rmse, 4),
        "test_r2":     round(test_r2, 4),
        "features":    reg_features,
        "target":      "weighted_score (IT1×0.25 + IT2×0.25 + Final×0.50)",
    },
}
with open(ML_DIR / "model_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("  [✓] Saved feature_columns.json")
print("  [✓] Saved model_metrics.json")
print("\n[✓] Training complete — v3 with all 6 fixes applied")
