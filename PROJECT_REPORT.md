# SLIS — Student Learning Intelligence System
## Project Report

---

## 1. Problem Statement

Academic institutions struggle to identify at-risk students early enough to intervene effectively. By the time poor performance becomes visible through final exam results, it is too late to provide meaningful support. Educators lack a centralised, data-driven tool to:

- Monitor individual student performance trends across multiple subjects
- Detect risk early using early-semester signals (attendance, internal test scores, LMS engagement)
- Deliver personalised, actionable guidance at scale

The absence of such a system leads to preventable student failures, delayed interventions, and an inability to direct limited faculty support toward students who need it most.

---

## 2. Objective

To design and develop an end-to-end AI-powered academic analytics platform that:

1. **Predicts student risk level** (Low / Medium / High) using early-semester data — before final exams
2. **Forecasts final weighted score** to give students and teachers a concrete performance target
3. **Generates personalised AI recommendations** for each student based on their academic profile
4. **Provides a Teacher Portal** for cohort-level monitoring, student search, score upload, and inline mark editing
5. **Provides a Student Portal** for self-monitoring of risk, performance, attendance, and recommendations
6. **Enables live score ingestion** — teachers can upload CSV/Excel sheets after each exam and the system updates instantly

---

## 3. Approach / Methodology

### Phase 1 — Data Generation
Synthetic data was generated for 500 students across 7 behavioural archetypes that reflect real academic patterns:

| Archetype | Pattern |
|-----------|---------|
| Consistent | Stable performance throughout |
| Late Bloomer | Low early scores, strong final |
| Early Bird | High early scores, drops off |
| Struggle | Consistently low across all tests |
| Comeback | Crisis mid-semester, then recovery |
| Exam Ace | Poor internals, dominates final |
| Final Burnout | Strong internals, collapses at final |

Four CSV files were generated: `students.csv`, `scores.csv`, `attendance.csv`, `activity.csv`.

### Phase 2 — Feature Engineering
18 features were engineered for the risk classifier and 20 for the performance predictor:

- **Attendance features:** average, monthly (M1–M2), trend slope
- **Score features:** avg IT1, avg IT2, delta (IT2−IT1), slope, rolling averages (W4, W8), standard deviation, range per subject
- **Engagement features:** LMS logins/week, forum posts, resources accessed, session minutes (composite engagement score)
- **Student features:** GPA at start of semester

### Phase 3 — Risk Labelling (No Leakage)
Risk labels (Low / Medium / High) were derived **only from IT1 + IT2 scores** using percentile thresholds (p33 / p66). The final exam score was deliberately excluded from label generation to prevent data leakage — the model must predict risk before the final exam.

### Phase 4 — Model Training
Multiple algorithms were evaluated via 5-fold cross-validation for each task:

**Risk Classifier candidates:** Random Forest, Gradient Boosting, Logistic Regression
→ Random Forest selected (highest CV F1 Macro)

**Performance Predictor candidates:** Random Forest Regressor, Gradient Boosting Regressor, Ridge Regression
→ Ridge Regression selected (best generalisation, lowest test RMSE)

`class_weight='balanced'` was applied to handle class imbalance in the risk distribution.

### Phase 5 — Backend API
A RESTful API was built with FastAPI. The data store loads all CSVs into memory at startup for fast inference. ML models are loaded once at startup using `joblib`. All endpoints return JSON.

### Phase 6 — Frontend
Two single-page applications were built using React 18 + Babel CDN (no build step). Both fall back to mock data silently if the API is unavailable. The teacher portal supports inline mark editing and CSV/Excel upload.

### Phase 7 — Score Upload Pipeline
A file upload endpoint (`POST /api/upload/scores`) accepts CSV or Excel files, matches rows by `student_id` + `subject`, updates the in-memory DataStore, and persists changes back to `scores.csv` on disk.

---

## 4. Tools Used (with Reasons)

| Tool / Library | Purpose | Reason for Choice |
|----------------|---------|-------------------|
| **Python 3.10** | Primary language | Ecosystem richness for data + ML + web |
| **FastAPI** | REST API backend | Automatic OpenAPI docs, async support, Pydantic validation, fastest Python web framework |
| **Pydantic v2** | Request/response validation | Native FastAPI integration, clear error messages |
| **scikit-learn** | ML model training & inference | Battle-tested, consistent API across classifiers/regressors, joblib serialisation |
| **joblib** | Model serialisation | Efficient with NumPy arrays, standard for scikit-learn |
| **pandas** | CSV loading, feature engineering, score persistence | Most natural API for tabular data manipulation |
| **NumPy** | Feature computation (means, std, polyfit) | Low-level numerical ops required for rolling averages and trend slopes |
| **React 18 (CDN)** | Frontend UI | No build step required — single HTML file per portal, instant prototype |
| **Babel Standalone** | JSX transpilation in browser | Enables JSX syntax without a bundler |
| **HuggingFace Inference API** | AI recommendations (Qwen3-32B) | State-of-the-art LLM via API — no local GPU required; falls back to rule-based if unavailable |
| **python-dotenv** | Environment variable management | Keeps API tokens out of source code |
| **openpyxl** | Excel file parsing | pandas dependency for `.xlsx` support in upload endpoint |
| **uvicorn** | ASGI server | Recommended production server for FastAPI; supports `--reload` for development |

---

## 5. Dataset

### Source
Fully synthetic — generated using `data/generate_data.py` to simulate a realistic Indian engineering college cohort.

### Size
| File | Records | Description |
|------|---------|-------------|
| `students.csv` | 500 rows | Student demographics, major, GPA |
| `scores.csv` | 2,500 rows | IT1, IT2, final scores per subject (5 subjects × 500 students) |
| `attendance.csv` | 2,000 rows | Monthly attendance % (4 months × 500 students) |
| `activity.csv` | 500 rows | LMS engagement metrics per student |

### Subjects
Machine Learning · Deep Learning · Python for AI · Data Structures & Algorithms · Statistics for AI

### Score Distribution
- Scores range from 0–100 per test
- Weighted score = IT1×0.25 + IT2×0.25 + Final×0.50
- Risk distribution: Low ~33% · Medium ~33% · High ~33% (percentile-based)

### Key Statistics (Live)
| Metric | Value |
|--------|-------|
| Total students | 500 |
| High-risk students | 163 (32.6%) |
| Average predicted score | 51.9 / 100 |
| Average attendance | 56.2% |

---

## 6. Results / Output

### ML Model Performance

| Model | Task | Algorithm | CV Score | Test Score |
|-------|------|-----------|----------|------------|
| Risk Classifier | 3-class classification | Random Forest | CV F1 Macro = **96.2%** | Test Accuracy = **92%** |
| Performance Predictor | Regression | Ridge Regression | CV RMSE = **5.02** | Test RMSE = **4.68**, R² = **0.885** |

- R² = 0.885 means the model explains **88.5% of variance** in final weighted scores using only early-semester data
- RMSE of 4.68 means predictions are within ~5 marks of actual on a 100-point scale

### System Output

**Teacher Portal:**
- Real-time cohort dashboard with risk breakdown and subject-wise averages
- Full student directory with search, filter, and clickable profiles
- Per-student risk confidence bars (probability for each class)
- Inline mark editor — change IT1/IT2/Final → weighted score updates live
- Upload Scores page — upload CSV/Excel, see preview, get instant update summary

**Student Portal:**
- Risk hero banner with predicted weighted score
- Attendance by month with colour-coded thresholds (≥85% green, ≥70% amber, <70% red)
- Subject-level performance with IT1 → IT2 → Final trend arrows
- 4 personalised AI-generated recommendations sorted by priority

**API — all endpoints verified:**
```
GET  /health                              → {"status":"ok","models_loaded":true}
GET  /api/students                        → paginated list, searchable, filterable
GET  /api/students/{id}                   → full profile with ML inference
GET  /api/dashboard/stats                 → cohort-level analytics
GET  /api/model-metrics                   → live model performance numbers
POST /api/predict                         → risk + score for any custom inputs
GET  /api/recommendations/{id}            → 4 AI recommendations
POST /api/upload/scores                   → CSV/Excel ingestion with match summary
PUT  /api/students/{id}/scores/{subject}  → inline mark correction
```

---

## 7. Challenges Faced

### 1. Data Leakage in Risk Labels
**Problem:** Initially, risk labels were derived from a combined score that included the final exam mark. This caused the classifier to achieve near-perfect accuracy — but it was cheating, using future data to label the training set.

**Solution:** Re-labelled using only IT1 + IT2 (early-semester scores) via percentile thresholds (p33, p66). The final exam was reserved exclusively as the regression target.

---

### 2. Feature Mismatch in Predict Endpoint
**Problem:** The `/api/predict` route was calling `ml_service.predict_risk()` with positional arguments, but the ML service had been refactored to accept a feature dictionary. This caused a `TypeError` at runtime — the endpoint returned HTTP 500.

**Solution:** Updated the route to build a complete `feat_dict` with all required keys, and estimated missing model features (avg_it1, avg_it2 etc.) from the available GPA input.

---

### 3. Predicted Score Returning 0.0
**Problem:** The predict endpoint was returning `predicted_score: 0.0` because the regression model requires 20 features — but the form only collects 5 (attendance, engagement, GPA, logins, forum posts). The missing 15 features defaulted to 0.0, pushing the model's output toward zero.

**Solution:** Added heuristic imputation: estimated `avg_it1` and `avg_it2` from `gpa_start × 10`, defaulted attendance monthly values to `avg_attendance`, and set trend/std features to 0.0. This produced realistic score estimates (e.g. GPA 8.5 → predicted score ~78).

---

### 4. GPA Scale Mismatch
**Problem:** The `PredictRequest` schema validated `gpa_start` as `ge=1.0, le=4.0` (US scale), but the synthetic dataset used a 0–10 scale common in Indian universities. Students with GPA 6.5 were being rejected by the API validator.

**Solution:** Updated the schema to `ge=0.0, le=10.0` and updated the frontend predict form to show the correct range hint.

---

### 5. JSX Files Require HTTP Server
**Problem:** Opening `index.html` directly via `file://` protocol fails because the browser blocks loading `.jsx` files via `<script src="...">` due to CORS restrictions on local file paths.

**Solution:** Both portals must be served via a local HTTP server (`python3 -m http.server 3000`). This is documented in the README and the startup instructions.

---

### 6. Subject Name Inconsistency
**Problem:** Mock data in the frontend used generic subjects (Mathematics, Physics, Chemistry) while the backend CSV used different names (Programming, Data Structures). After renaming to AI/ML subjects, the mock fallback data also needed updating to stay consistent.

**Solution:** Renamed all 5 subjects in `scores.csv` via a Python script, then updated mock data in both `TeacherApp.jsx` and `StudentApp.jsx` to match.

---

## GitHub Repository

**[https://github.com/UpendraSurya/SLIS](https://github.com/UpendraSurya/SLIS)**

---

*Report prepared: 2026-04-22*
