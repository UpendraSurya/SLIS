"""
SLIS — Step 2: Exploratory Data Analysis (v3)
Updated for new data schema: IT1/IT2/Final, 4-month attendance,
archetype analysis, anomaly archetypes, model confidence.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path

DATA_DIR  = Path(__file__).parent.parent / "data"
ML_DIR    = Path(__file__).parent.parent / "ml"
PLOTS_DIR = Path(__file__).parent / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use("dark_background")
ACCENT   = "#06b6d4"
BG_COLOR = "#0f172a"
CARD_BG  = "#1e293b"
PALETTE  = ["#06b6d4", "#f59e0b", "#ef4444", "#22c55e", "#a855f7", "#f97316", "#e879f9"]
RISK_COL = {"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"}
ARCH_MAP  = {0:"Consistent", 1:"Late Bloomer", 2:"Early Bird",
             3:"Struggle",   4:"Comeback",     5:"Exam Ace",  6:"Final Burnout"}

# ── Load ──────────────────────────────────────────────────────────────────────
students   = pd.read_csv(DATA_DIR / "students.csv")
attendance = pd.read_csv(DATA_DIR / "attendance.csv")
scores     = pd.read_csv(DATA_DIR / "scores.csv")
activity   = pd.read_csv(DATA_DIR / "activity.csv")

# Load model predictions if available
preds_path = ML_DIR / "risk_predictions_full.csv"
has_preds  = preds_path.exists()
if has_preds:
    preds = pd.read_csv(preds_path)

# ── Aggregate ─────────────────────────────────────────────────────────────────
att_agg = attendance.groupby("student_id")["attendance_pct"].mean().reset_index()
att_agg.columns = ["student_id", "avg_attendance"]

sc_agg = scores.groupby("student_id").agg(
    avg_it1      = ("it1_score",      "mean"),
    avg_it2      = ("it2_score",      "mean"),
    avg_final    = ("final_score",    "mean"),
    avg_weighted = ("weighted_score", "mean"),
    it1_std      = ("it1_score",      "std"),
    it2_std      = ("it2_score",      "std"),
).reset_index()

subject_avgs = scores.groupby("subject")[["it1_score","it2_score","final_score"]].mean().round(1)

master = (students
          .merge(att_agg, on="student_id")
          .merge(sc_agg,  on="student_id")
          .merge(activity, on="student_id"))

master["arch_name"]      = master["archetype"].map(ARCH_MAP)
master["engagement"]     = (master["lms_logins_per_week"] * 0.4 +
                            master["forum_posts"]         * 0.3 +
                            master["resources_accessed"]  * 0.2 +
                            (master["avg_session_minutes"] / 60) * 0.1)
master["early_score"]    = (master["avg_it1"] + master["avg_it2"]) / 2.0
master["final_it_delta"] = master["avg_final"] - master["early_score"]

p33 = master["early_score"].quantile(0.33)
p66 = master["early_score"].quantile(0.66)
master["risk_level"] = master["early_score"].apply(
    lambda x: "Low" if x >= p66 else ("Medium" if x >= p33 else "High")
)

# ── Summary ───────────────────────────────────────────────────────────────────
print("=" * 65)
print("SLIS — EDA Summary (v3)")
print("=" * 65)
print(f"\nStudents: {len(master)}")
print(f"\nArchetype breakdown:")
for k, n in ARCH_MAP.items():
    cnt = (master["archetype"] == k).sum()
    print(f"  {n:15s}: {cnt:3d} ({cnt/len(master)*100:.1f}%)")
print(f"\nRisk distribution (from IT1+IT2):")
for r, cnt in master["risk_level"].value_counts().items():
    print(f"  {r:8s}: {cnt} ({cnt/len(master)*100:.1f}%)")
print(f"\nScore averages:")
print(f"  IT1 avg    : {master['avg_it1'].mean():.1f}")
print(f"  IT2 avg    : {master['avg_it2'].mean():.1f}")
print(f"  Final avg  : {master['avg_final'].mean():.1f}")
print(f"  Weighted   : {master['avg_weighted'].mean():.1f}")
print(f"\nAnomaly archetypes:")
ea  = master[master["archetype"] == 5]
fb  = master[master["archetype"] == 6]
print(f"  Exam Ace     — IT1: {ea['avg_it1'].mean():.1f}  IT2: {ea['avg_it2'].mean():.1f}  Final: {ea['avg_final'].mean():.1f}")
print(f"  Final Burnout— IT1: {fb['avg_it1'].mean():.1f}  IT2: {fb['avg_it2'].mean():.1f}  Final: {fb['avg_final'].mean():.1f}")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 1 — IT1 / IT2 / Final score distributions (three overlapping histograms)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG_COLOR)
ax.set_facecolor(CARD_BG)
bins = np.linspace(0, 100, 35)
ax.hist(master["avg_it1"],    bins=bins, alpha=0.6, color="#06b6d4", label=f"IT1  μ={master['avg_it1'].mean():.1f}")
ax.hist(master["avg_it2"],    bins=bins, alpha=0.6, color="#f59e0b", label=f"IT2  μ={master['avg_it2'].mean():.1f}")
ax.hist(master["avg_final"],  bins=bins, alpha=0.6, color="#ef4444", label=f"Final μ={master['avg_final'].mean():.1f}")
ax.set_xlabel("Score", color="white", fontsize=12)
ax.set_ylabel("Number of Students", color="white", fontsize=12)
ax.set_title("IT1 / IT2 / Final Score Distributions (all students)", color="white", fontsize=14, fontweight="bold")
ax.legend(facecolor=CARD_BG, edgecolor=ACCENT, labelcolor="white", fontsize=11)
ax.tick_params(colors="white")
for s in ax.spines.values(): s.set_edgecolor("#334155")
plt.tight_layout()
plt.savefig(PLOTS_DIR / "1_score_distributions.png", dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
plt.close()
print("\n[✓] Plot 1: Score distributions saved")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 2 — Score trajectory by archetype (IT1 → IT2 → Final)
# Each archetype is a line showing its average score at each test point
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG_COLOR)
ax.set_facecolor(CARD_BG)
arch_order = [0, 1, 2, 3, 4, 5, 6]
x = [1, 2, 3]
xlabels = ["IT1\n(Week 4)", "IT2\n(Week 8)", "Final\n(Week 12)"]

for idx, arch_id in enumerate(arch_order):
    grp = master[master["archetype"] == arch_id]
    if len(grp) == 0:
        continue
    means = [grp["avg_it1"].mean(), grp["avg_it2"].mean(), grp["avg_final"].mean()]
    lw = 3.0 if arch_id in (5, 6) else 1.8
    ls = "--" if arch_id in (5, 6) else "-"
    ax.plot(x, means, color=PALETTE[idx], linewidth=lw, linestyle=ls,
            marker="o", markersize=7, label=f"{ARCH_MAP[arch_id]} (n={len(grp)})")

ax.set_xticks(x)
ax.set_xticklabels(xlabels, color="white", fontsize=11)
ax.set_ylabel("Average Score", color="white", fontsize=12)
ax.set_title("Score Trajectory by Archetype  (dashed = anomaly archetypes)", color="white", fontsize=14, fontweight="bold")
ax.legend(facecolor=CARD_BG, edgecolor="#334155", labelcolor="white", fontsize=9, loc="upper left")
ax.tick_params(colors="white")
ax.grid(axis="y", alpha=0.15, color="white")
for s in ax.spines.values(): s.set_edgecolor("#334155")
plt.tight_layout()
plt.savefig(PLOTS_DIR / "2_score_trajectory_by_archetype.png", dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
plt.close()
print("[✓] Plot 2: Score trajectory by archetype saved")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 3 — Anomaly spotlight: Final − IT avg delta by archetype (box plot)
# Positive = final was better than internals; negative = worse
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6), facecolor=BG_COLOR)
ax.set_facecolor(CARD_BG)

arch_names = [ARCH_MAP[i] for i in arch_order if (master["archetype"] == i).sum() > 0]
data_by_arch = [master.loc[master["archetype"] == i, "final_it_delta"].values
                for i in arch_order if (master["archetype"] == i).sum() > 0]
colors_by_arch = [PALETTE[i] for i in arch_order if (master["archetype"] == i).sum() > 0]

bp = ax.boxplot(data_by_arch, patch_artist=True, widths=0.5,
                medianprops={"color": "white", "linewidth": 2},
                whiskerprops={"color": "#94a3b8"},
                capprops={"color": "#94a3b8"},
                flierprops={"marker": ".", "markersize": 4, "alpha": 0.5})

for patch, color in zip(bp["boxes"], colors_by_arch):
    patch.set_facecolor(color)
    patch.set_alpha(0.75)

ax.axhline(0, color="white", linewidth=1, linestyle="--", alpha=0.4)
ax.set_xticklabels(arch_names, rotation=15, ha="right", color="white", fontsize=10)
ax.set_ylabel("Final Score − Avg(IT1, IT2)", color="white", fontsize=12)
ax.set_title("Final Exam Surprise by Archetype\n(+ve = overperformed vs internals, −ve = underperformed)",
             color="white", fontsize=13, fontweight="bold")
ax.tick_params(colors="white")
ax.grid(axis="y", alpha=0.12, color="white")
for s in ax.spines.values(): s.set_edgecolor("#334155")
plt.tight_layout()
plt.savefig(PLOTS_DIR / "3_final_surprise_by_archetype.png", dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
plt.close()
print("[✓] Plot 3: Final surprise by archetype saved")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 4 — Attendance vs Weighted Score (color by risk, shaped by anomaly)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG_COLOR)
ax.set_facecolor(CARD_BG)

# Normal archetypes
normal = master[~master["archetype"].isin([5, 6])]
for risk_lv, color in RISK_COL.items():
    m = normal["risk_level"] == risk_lv
    ax.scatter(normal.loc[m, "avg_attendance"], normal.loc[m, "avg_weighted"],
               c=color, alpha=0.45, s=22, edgecolors="none", label=risk_lv)

# Anomaly archetypes on top
exam_ace  = master[master["archetype"] == 5]
burnout   = master[master["archetype"] == 6]
ax.scatter(exam_ace["avg_attendance"], exam_ace["avg_weighted"],
           c="#a855f7", alpha=0.85, s=60, marker="^", edgecolors="white", linewidths=0.4, label="Exam Ace ▲")
ax.scatter(burnout["avg_attendance"], burnout["avg_weighted"],
           c="#f97316", alpha=0.85, s=60, marker="v", edgecolors="white", linewidths=0.4, label="Final Burnout ▼")

# Trend line on normal students
z = np.polyfit(normal["avg_attendance"], normal["avg_weighted"], 1)
xl = np.linspace(master["avg_attendance"].min(), master["avg_attendance"].max(), 100)
ax.plot(xl, np.poly1d(z)(xl), color=ACCENT, linewidth=1.8, linestyle="--", alpha=0.7)

ax.set_xlabel("Average Attendance (%)", color="white", fontsize=12)
ax.set_ylabel("Weighted Score", color="white", fontsize=12)
ax.set_title("Attendance vs Weighted Score  (anomalies highlighted)", color="white", fontsize=14, fontweight="bold")
ax.legend(facecolor=CARD_BG, edgecolor="#334155", labelcolor="white", fontsize=9)
ax.tick_params(colors="white")
for s in ax.spines.values(): s.set_edgecolor("#334155")
plt.tight_layout()
plt.savefig(PLOTS_DIR / "4_attendance_vs_score.png", dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
plt.close()
print("[✓] Plot 4: Attendance vs Score saved")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 5 — Subject variance (IT1 std per student) distribution
# Shows how uneven student performance is across subjects
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor=BG_COLOR)
for ax in axes: ax.set_facecolor(CARD_BG)

axes[0].hist(master["it1_std"], bins=25, color="#06b6d4", alpha=0.85, edgecolor="#0f172a")
axes[0].axvline(master["it1_std"].mean(), color="#f59e0b", linewidth=2, linestyle="--",
                label=f"Mean: {master['it1_std'].mean():.1f}")
axes[0].set_xlabel("IT1 Score Std Dev across Subjects", color="white", fontsize=11)
axes[0].set_ylabel("Students", color="white", fontsize=11)
axes[0].set_title("Subject Variance at IT1\n(high std = uneven, some subjects weak)", color="white", fontsize=12, fontweight="bold")
axes[0].legend(facecolor=CARD_BG, edgecolor=ACCENT, labelcolor="white")
axes[0].tick_params(colors="white")
for s in axes[0].spines.values(): s.set_edgecolor("#334155")

subj_data = [scores.loc[scores["subject"] == s, "it1_score"].values for s in scores["subject"].unique()]
subj_names = scores["subject"].unique()
bp2 = axes[1].boxplot(subj_data, patch_artist=True,
                      medianprops={"color": "white", "linewidth": 2},
                      whiskerprops={"color": "#94a3b8"},
                      capprops={"color": "#94a3b8"},
                      flierprops={"marker": ".", "markersize": 3, "alpha": 0.4})
for patch, color in zip(bp2["boxes"], PALETTE):
    patch.set_facecolor(color); patch.set_alpha(0.75)
axes[1].set_xticklabels(subj_names, rotation=20, ha="right", color="white", fontsize=9)
axes[1].set_ylabel("IT1 Score", color="white", fontsize=11)
axes[1].set_title("IT1 Score Distribution per Subject", color="white", fontsize=12, fontweight="bold")
axes[1].tick_params(colors="white")
axes[1].grid(axis="y", alpha=0.12, color="white")
for s in axes[1].spines.values(): s.set_edgecolor("#334155")

plt.tight_layout()
plt.savefig(PLOTS_DIR / "5_subject_variance.png", dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
plt.close()
print("[✓] Plot 5: Subject variance saved")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 6 — Correlation heatmap (updated feature set)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 9), facecolor=BG_COLOR)
ax.set_facecolor(BG_COLOR)
corr_cols = ["avg_it1", "avg_it2", "avg_final", "avg_weighted",
             "avg_attendance", "gpa_start", "engagement",
             "it1_std", "lms_logins_per_week", "resources_accessed"]
corr_labels = ["IT1", "IT2", "Final", "Weighted",
               "Attendance", "GPA Start", "Engagement",
               "IT1 Std", "LMS Logins", "Resources"]
corr_matrix = master[corr_cols].corr()
corr_matrix.index   = corr_labels
corr_matrix.columns = corr_labels
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
cmap = sns.diverging_palette(220, 10, as_cmap=True)
sns.heatmap(corr_matrix, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
            annot=True, fmt=".2f", linewidths=0.5, ax=ax,
            cbar_kws={"shrink": 0.75},
            annot_kws={"size": 9, "color": "white"})
ax.set_title("Feature Correlation Heatmap (v3)", color="white", fontsize=14, fontweight="bold", pad=15)
ax.tick_params(colors="white", labelsize=9)
ax.figure.axes[-1].tick_params(colors="white")
plt.tight_layout()
plt.savefig(PLOTS_DIR / "6_correlation_heatmap.png", dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
plt.close()
print("[✓] Plot 6: Correlation heatmap saved")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 7 — Model prediction confidence distribution (if preds available)
# ─────────────────────────────────────────────────────────────────────────────
if has_preds:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor=BG_COLOR)
    for ax in axes: ax.set_facecolor(CARD_BG)

    conf = preds["max_confidence"]
    axes[0].hist(conf, bins=25, color=ACCENT, alpha=0.85, edgecolor="#0f172a")
    axes[0].axvline(0.60, color="#ef4444", linewidth=2, linestyle="--", label="60% threshold (borderline)")
    axes[0].axvline(0.85, color="#22c55e", linewidth=2, linestyle="--", label="85% threshold (act first)")
    axes[0].set_xlabel("Max Prediction Confidence", color="white", fontsize=11)
    axes[0].set_ylabel("Students", color="white", fontsize=11)
    axes[0].set_title(f"Prediction Confidence Distribution\n"
                      f"<60%: {(conf<0.60).sum()} students  |  >85%: {(conf>0.85).sum()} students",
                      color="white", fontsize=12, fontweight="bold")
    axes[0].legend(facecolor=CARD_BG, edgecolor="#334155", labelcolor="white", fontsize=9)
    axes[0].tick_params(colors="white")
    for s in axes[0].spines.values(): s.set_edgecolor("#334155")

    correct   = preds[preds["correct"] == True]["max_confidence"]
    incorrect = preds[preds["correct"] == False]["max_confidence"]
    axes[1].hist(correct,   bins=20, color="#22c55e", alpha=0.7, label=f"Correct   (n={len(correct)})")
    axes[1].hist(incorrect, bins=20, color="#ef4444", alpha=0.7, label=f"Incorrect (n={len(incorrect)})")
    axes[1].set_xlabel("Max Prediction Confidence", color="white", fontsize=11)
    axes[1].set_ylabel("Students", color="white", fontsize=11)
    axes[1].set_title("Confidence: Correct vs Incorrect Predictions\n(good model = errors cluster at low confidence)",
                      color="white", fontsize=12, fontweight="bold")
    axes[1].legend(facecolor=CARD_BG, edgecolor="#334155", labelcolor="white", fontsize=10)
    axes[1].tick_params(colors="white")
    for s in axes[1].spines.values(): s.set_edgecolor("#334155")

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "7_prediction_confidence.png", dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print("[✓] Plot 7: Prediction confidence saved")
else:
    print("[!] Plot 7 skipped — run ml/train.py first to generate risk_predictions_full.csv")

print(f"\n[✓] All plots saved to {PLOTS_DIR}")
print(f"    Open with: open {PLOTS_DIR}")
