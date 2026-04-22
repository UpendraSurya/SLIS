# SLIS — Student Learning Intelligence System

An AI-powered academic analytics platform that predicts student risk levels, tracks performance across 5 AI/ML subjects, and generates personalised recommendations.

**Tech stack:** FastAPI · scikit-learn (Random Forest 92%) · React 18 (CDN) · Python · HuggingFace Qwen3-32B

---

## Quick Start (2 terminals)

```bash
# 1. Clone and install
git clone https://github.com/UpendraSurya/SLIS.git
cd SLIS
pip install -r requirements.txt

# 2. Terminal 1 — Backend (port 8000)
python3 -m uvicorn backend.main:app --port 8000 --reload

# 3. Terminal 2 — Frontend (port 3000)
cd frontend && python3 -m http.server 3000
```

Then open:
- **Teacher Portal:** http://localhost:3000/ui_kits/teacher/index.html → login: `teacher` / `slis2024`
- **Student Portal:** http://localhost:3000/ui_kits/student/index.html → any ID `STU0001`–`STU0500`

---

## Features

### Teacher Portal
| Page | What it does |
|------|-------------|
| Dashboard | Cohort overview — risk distribution, model metrics, subject averages, top performers |
| Student Directory | Search by name/ID, filter by risk level, paginated (500 students) |
| Student Profile | Full scores, attendance, LMS activity, AI recommendations, **inline mark editing** |
| Custom Predict | Enter any student metrics → instant risk + predicted score |
| Upload Scores | Upload CSV/Excel after each exam → auto-matches by student ID |

### Student Portal
| Page | What it does |
|------|-------------|
| My Dashboard | Risk level, predicted score, attendance trend, LMS activity |
| My Recommendations | AI-generated, priority-sorted (High → Medium → Low) |
| My Performance | Per-subject breakdown with IT1/IT2/Final scores and trend (↑↓→) |

---

## Subjects (AI/ML)
- Machine Learning
- Deep Learning
- Python for AI
- Data Structures & Algorithms
- Statistics for AI

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server + model status |
| GET | `/api/students` | List students (`?page&limit&risk_filter&search`) |
| GET | `/api/students/{id}` | Full student profile |
| GET | `/api/dashboard/stats` | Cohort-level analytics |
| GET | `/api/model-metrics` | ML model performance |
| POST | `/api/predict` | Risk + score for custom inputs |
| GET | `/api/recommendations/{id}` | AI recommendations via Qwen3-32B |
| POST | `/api/upload/scores` | Upload CSV/Excel exam scores |
| PUT | `/api/students/{id}/scores/{subject}` | Edit individual marks |

Interactive docs: http://127.0.0.1:8000/docs

---

## Upload Score Sheet Format

CSV or Excel with these columns:

```
student_id,subject,it1_score,it2_score,final_score
STU0001,Machine Learning,78,82,88
STU0002,Deep Learning,65,70,75
```

Weighted score is computed automatically: `IT1×0.25 + IT2×0.25 + Final×0.50`

---

## ML Models

| Model | Algorithm | Metric |
|-------|-----------|--------|
| Risk Classifier | Random Forest | F1=96.2%, Acc=92% |
| Performance Predictor | Ridge Regression | RMSE=4.68, R²=0.885 |

Risk labels: **Low / Medium / High** (percentile-based, no final exam leakage)

---

## Optional — AI Recommendations (Qwen3-32B)

```bash
echo "your_hf_token" > ~/.hf_token
# or
export HF_TOKEN=your_token
```

Falls back to rule-based recommendations if token is missing.
