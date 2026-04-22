"""
SLIS — Step 1: Data Generation (v2)
Generates 500 students with realistic correlated data across 4 CSV files.

scores.csv now includes:
  - Internal Test 1 (week 4), Internal Test 2 (week 8), Final Exam (week 12)
  - Weekly assignment scores (weeks 1-12) per subject
  - 4-week rolling averages: roll_avg_w4, roll_avg_w8, roll_avg_w12
  - score_trend: slope across the 3 test points (positive = improving)
  - weighted_score: IT1×0.25 + IT2×0.25 + Final×0.50
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)
N = 500
DATA_DIR = Path(__file__).parent

MAJORS   = ["Computer Science", "Data Science", "Electronics", "Mechanical", "Civil", "Mathematics"]
GENDERS  = ["Male", "Female", "Non-binary"]
SUBJECTS = ["Mathematics", "Physics", "Programming", "Data Structures", "Statistics"]

FIRST_NAMES = [
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Ayaan","Krishna","Ishaan",
    "Priya","Ananya","Divya","Shreya","Pooja","Meera","Kavya","Lakshmi","Nandini","Riya",
    "Rohan","Kiran","Neha","Aryan","Tanvi","Rahul","Sneha","Vijay","Anjali","Suresh",
    "Omar","Liam","Noah","Emma","Olivia","Ava","Sophia","Isabella","Mia","Charlotte",
    "Amara","Zara","Fatima","Hassan","Yusuf","Leila","Tariq","Noor","Amir","Yasmin",
]
LAST_NAMES = [
    "Sharma","Patel","Singh","Kumar","Gupta","Joshi","Verma","Reddy","Nair","Rao",
    "Khan","Ali","Ahmed","Hassan","Shah","Malik","Chaudhary","Ansari","Siddiqui","Mirza",
    "Smith","Johnson","Williams","Brown","Jones","Davis","Miller","Wilson","Moore","Taylor",
]

def gen_name():
    return f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}"

# ── Latent variables per student ──────────────────────────────────────────────
# These are INDEPENDENT — high attendance does NOT automatically mean high marks
latent_ability  = np.random.beta(2, 1.5, N)       # raw academic ability (0–1)
latent_effort   = np.random.beta(1.8, 1.8, N)     # sustained work ethic  (0–1)
latent_momentum = np.random.normal(0, 0.18, N)    # score trajectory over semester
latent_anxiety  = np.random.beta(1.5, 3, N)       # exam anxiety (hurts test vs assignment)
latent_social   = np.random.beta(1.5, 2, N)       # social/forum engagement tendency

# NOTE: Attendance driven by SEPARATE factors — not ability directly
# Some brilliant students skip class; some poor students attend everything
# Attendance correlates ~0.35 with marks — significant but not deterministic
latent_discipline = 0.5 * latent_effort + 0.2 * np.random.rand(N) + 0.3 * np.random.rand(N)

# Student archetype (determines how they progress across tests)
# 0=Consistent, 1=Late Bloomer (low IT1 high Final), 2=Early Bird (high IT1 drops)
# 3=Struggle-throughout, 4=Comeback
# 5=Exam Ace (bad internals, dominates final — real world anomaly)
# 6=Final Burnout (great internals, collapses at final)
ARCHETYPES = np.random.choice(
    [0, 1, 2, 3, 4, 5, 6],
    N,
    p=[0.33, 0.13, 0.19, 0.13, 0.08, 0.08, 0.06]
)

# ── 1. students.csv ───────────────────────────────────────────────────────────
student_ids = [f"STU{str(i+1).zfill(4)}" for i in range(N)]
names       = [gen_name() for _ in range(N)]
ages        = np.random.randint(15, 23, N)
genders     = np.random.choice(GENDERS, N, p=[0.48, 0.48, 0.04])
majors      = np.random.choice(MAJORS, N)
enroll_year = np.random.choice([2020,2021,2022,2023,2024], N, p=[0.1,0.15,0.25,0.3,0.2])
gpa_start   = np.clip(latent_ability * 7 + np.random.normal(1.5, 0.8, N), 1.0, 10.0).round(1)

students = pd.DataFrame({
    "student_id":      student_ids,
    "name":            names,
    "age":             ages,
    "gender":          genders,
    "major":           majors,
    "enrollment_year": enroll_year,
    "gpa_start":       gpa_start,
    "archetype":       ARCHETYPES,  # keep for correlation validation
})
students.to_csv(DATA_DIR / "students.csv", index=False)
print(f"[✓] students.csv — {len(students)} rows")
print(f"    Archetypes: {dict(zip(*np.unique(ARCHETYPES, return_counts=True)))}")
print(f"    ⚠ Anomaly archetypes: Exam Ace (5) and Final Burnout (6) included")


# ── 2. attendance.csv ─────────────────────────────────────────────────────────
# 4 months aligned with assessment calendar:
#   Month 1 → before IT1 (week 4)
#   Month 2 → IT1 to IT2 (weeks 5-8)
#   Month 3 → IT2 to Final prep (weeks 9-10)
#   Month 4 → Final exam period (weeks 11-12)
MONTH_LABELS = {1: "Pre-IT1", 2: "IT1-to-IT2", 3: "Pre-Final", 4: "Final Period"}

attendance_rows = []
# week_attendance[i, w] stores weekly % for score correlation — 12 internal weeks
week_attendance = np.zeros((N, 12))

for i, sid in enumerate(student_ids):
    # Attendance driven by discipline + random life events — NOT ability
    base_att = latent_discipline[i] * 55 + 30  # range ~30–85

    # Some highly able students are lazy attenders (realistic)
    if latent_ability[i] > 0.75 and latent_discipline[i] < 0.4:
        base_att -= np.random.uniform(10, 20)   # smart but skips class

    # Some hard workers with lower ability attend everything
    if latent_effort[i] > 0.7 and latent_ability[i] < 0.4:
        base_att += np.random.uniform(5, 15)

    # Month-level attendance (4 months)
    for month in range(1, 5):
        # Random personal events (illness, family) — any student any month
        life_event = np.random.uniform(-15, 0) if np.random.rand() < 0.12 else 0

        # Post-IT1 motivation crash (month 2) — affects low-discipline students
        dip = 0
        if month == 2 and latent_discipline[i] < 0.35:
            dip = np.random.uniform(10, 25)

        # Pre-final cramming boost (month 4) for effort students
        boost = 0
        if month == 4 and latent_effort[i] > 0.65:
            boost = np.random.uniform(4, 14)

        # Large individual noise — real attendance data is messy
        noise = np.random.normal(0, 9)
        pct   = np.clip(base_att - dip + boost + life_event + noise, 0, 100)

        attendance_rows.append({
            "student_id":     sid,
            "month":          month,
            "month_label":    MONTH_LABELS[month],
            "attendance_pct": round(float(pct), 1),
        })

        # Map month → 3 internal weeks for score generation
        week_start = (month - 1) * 3
        for w in range(3):
            week_attendance[i, week_start + w] = np.clip(
                pct + np.random.normal(0, 4), 0, 100
            )

attendance = pd.DataFrame(attendance_rows)
attendance.to_csv(DATA_DIR / "attendance.csv", index=False)
print(f"[✓] attendance.csv — {len(attendance)} rows  (4 months × 500 students)")
print(f"    Months: Pre-IT1 | IT1-to-IT2 | Pre-Final | Final Period")


# ── 3. scores.csv ─────────────────────────────────────────────────────────────
# For each student × subject:
#   - 12 weekly assignment scores (week 1–12)
#   - IT1 at week 4, IT2 at week 8, Final at week 12
#   - Rolling averages: roll_w4 (weeks 1-4), roll_w8 (weeks 5-8), roll_w12 (weeks 9-12)
#   - score_trend = linear slope across [IT1, IT2, Final]
#   - weighted_score = IT1×0.25 + IT2×0.25 + Final×0.50

DIFFICULTY = {
    "Mathematics":     -10,
    "Physics":          -6,
    "Programming":       2,
    "Data Structures":  -4,
    "Statistics":       -2,
}

score_rows = []

for i, sid in enumerate(student_ids):
    arch  = ARCHETYPES[i]
    ab    = latent_ability[i]
    eff   = latent_effort[i]
    mom   = latent_momentum[i]
    att_w = week_attendance[i]   # shape (12,)

    for subj in SUBJECTS:
        diff = DIFFICULTY[subj]

        # Subject affinity: each student has random strength/weakness per subject
        # This breaks the "all subjects follow same pattern" assumption
        subj_affinity = np.random.normal(0, 8)   # could be +15 or -15 — real variation
        subj_consistency = np.random.uniform(0.5, 1.5)  # some students vary wildly by subject

        # Base ability for this subject — driven by ability+effort, NOT attendance
        # Scale: average student (ab=0.55, eff=0.5) should land ~55-65 range
        base = (ab * 50 + eff * 22 + 28 + diff + subj_affinity)  # ~28–100 range

        # Generate 12 weekly assignment scores with temporal evolution
        weekly = []
        for w in range(12):
            # Attendance has WEAK effect on assignments (~0.15 weight, not primary driver)
            # Real insight: students who study at home can score well despite low attendance
            att_effect = (att_w[w] - 65) * 0.12  # weak partial correlation

            # Archetype trajectory modifier (drives actual score arc)
            if arch == 0:   # Consistent — small variance around base
                traj = mom * w * 0.25 + np.random.normal(0, 2)
            elif arch == 1: # Late Bloomer — low start, genuine improvement
                traj = -8 + w * 1.4 + np.random.normal(0, 3)
            elif arch == 2: # Early Bird — peak early, mental burnout mid-sem
                traj = 6 - w * 0.9 + max(0, (w - 9) * 1.2) + np.random.normal(0, 3)
            elif arch == 3: # Struggle — lower base, week-by-week variance high
                traj = -10 - w * 0.3 + np.random.normal(0, 5)
            elif arch == 4: # Comeback — personal crisis mid-semester then recovery
                if w < 3:   traj = np.random.normal(0, 3)
                elif w < 8: traj = np.random.uniform(-18, -8)
                else:       traj = np.random.uniform(5, 14)
            elif arch == 5: # Exam Ace — mediocre weekly work, but intense final prep
                # Assignments are average or slightly below; they don't engage week-to-week
                traj = -4 + np.random.normal(0, 5)
            else:           # Final Burnout — strong start, exhausted by exam time
                # Consistent high work through internals, then collapses
                traj = 8 - w * 0.3 + np.random.normal(0, 3)

            score_w = np.clip(
                (base + traj + att_effect) * subj_consistency + np.random.normal(0, 8),
                0, 100
            )
            weekly.append(float(score_w))

        # Test scores — exam anxiety makes tests noisier than assignments
        # High-anxiety students underperform in formal tests relative to assignments
        anxiety_penalty = latent_anxiety[i] * 10   # 0–10 point penalty
        it1   = np.clip(weekly[3]  + np.random.normal(-3 - anxiety_penalty, 6), 0, 100)
        it2   = np.clip(weekly[7]  + np.random.normal(-3 - anxiety_penalty, 6), 0, 100)
        final = np.clip(weekly[11] + np.random.normal(-5 - anxiety_penalty, 7), 0, 100)

        # ── Anomaly archetypes: override test scores explicitly ──────────────
        # Arch 5 — Exam Ace: tanks internal tests, then goes all-out for final
        # Real pattern: some students only study when it truly counts (end-semester)
        if arch == 5:
            ace_internal_penalty = np.random.uniform(14, 24)  # bad at IT1/IT2
            ace_final_boost      = np.random.uniform(16, 28)  # dominates final
            it1   = np.clip(it1   - ace_internal_penalty,          0, 100)
            it2   = np.clip(it2   - ace_internal_penalty * 0.85,   0, 100)
            final = np.clip(final + ace_final_boost,               0, 100)

        # Arch 6 — Final Burnout: performs well in internals, crashes at final
        # Real pattern: academic exhaustion, anxiety spike, or personal crisis at exam time
        elif arch == 6:
            burnout_boost = np.random.uniform(8, 16)    # inflated IT1/IT2
            burnout_crash = np.random.uniform(22, 38)   # hard fall at final
            it1   = np.clip(it1   + burnout_boost,          0, 100)
            it2   = np.clip(it2   + burnout_boost * 0.75,   0, 100)
            final = np.clip(final - burnout_crash,           0, 100)

        # Rolling 4-week averages of assignments
        roll_w4  = float(np.mean(weekly[0:4]))    # weeks 1-4
        roll_w8  = float(np.mean(weekly[4:8]))    # weeks 5-8
        roll_w12 = float(np.mean(weekly[8:12]))   # weeks 9-12

        # Overall assignment average
        assignment_avg = float(np.mean(weekly))

        # Score trend: linear slope across the 3 test points
        # Positive = improving; Negative = declining
        x = np.array([4, 8, 12])
        y = np.array([it1, it2, final])
        slope = float(np.polyfit(x, y, 1)[0])

        # Weighted final score
        weighted = it1 * 0.25 + it2 * 0.25 + final * 0.50

        score_rows.append({
            "student_id":      sid,
            "subject":         subj,
            "it1_score":       round(it1, 1),          # Internal Test 1 (week 4)
            "it2_score":       round(it2, 1),          # Internal Test 2 (week 8)
            "final_score":     round(final, 1),        # Final Exam (week 12)
            "roll_avg_w4":     round(roll_w4, 1),      # Rolling avg weeks 1-4
            "roll_avg_w8":     round(roll_w8, 1),      # Rolling avg weeks 5-8
            "roll_avg_w12":    round(roll_w12, 1),     # Rolling avg weeks 9-12
            "assignment_avg":  round(assignment_avg, 1),
            "score_trend":     round(slope, 3),        # +ve = improving
            "weighted_score":  round(weighted, 1),     # IT1×0.25 + IT2×0.25 + Final×0.50
        })

scores = pd.DataFrame(score_rows)
scores.to_csv(DATA_DIR / "scores.csv", index=False)
print(f"[✓] scores.csv — {len(scores)} rows  (5 subjects × 500 students)")
print(f"    New columns: it1_score, it2_score, final_score, roll_avg_w4, "
      f"roll_avg_w8, roll_avg_w12, score_trend, weighted_score")


# ── 4. activity.csv ───────────────────────────────────────────────────────────
# LMS logins driven mostly by effort+discipline, NOT ability directly
# Forum posts driven by social tendency (some brilliant introverts never post)
# Resources accessed driven by effort + curiosity (partially independent)
# Session minutes = effort-driven but with high individual noise

lms_logins   = np.clip(
    latent_discipline * 8 + latent_effort * 5 + np.random.normal(0, 2.5, N), 0, 20
).round(1)

forum_posts  = np.clip(
    latent_social * 30 + latent_effort * 8 + np.random.normal(0, 5, N), 0, 60
).astype(int)

resources    = np.clip(
    latent_effort * 55 + latent_ability * 20 + np.random.normal(0, 14, N), 0, 120
).astype(int)

session_mins = np.clip(
    latent_effort * 60 + np.random.normal(30, 18, N), 5, 180
).round(1)

activity = pd.DataFrame({
    "student_id":          student_ids,
    "lms_logins_per_week": lms_logins,
    "forum_posts":         forum_posts,
    "resources_accessed":  resources,
    "avg_session_minutes": session_mins,
})
activity.to_csv(DATA_DIR / "activity.csv", index=False)
print(f"[✓] activity.csv — {len(activity)} rows")

print("\n[✓] All datasets generated in:", DATA_DIR)
print("\nArchetype breakdown:")
arch_map = {0:"Consistent", 1:"Late Bloomer", 2:"Early Bird", 3:"Struggle", 4:"Comeback",
            5:"Exam Ace", 6:"Final Burnout"}
for k, v in arch_map.items():
    count = int((ARCHETYPES == k).sum())
    print(f"  {v:15s}: {count} students ({count/N*100:.1f}%)")
