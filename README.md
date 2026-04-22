# SLIS — Student Learning Intelligence System

An AI-powered academic analytics platform that predicts student risk levels and generates personalised recommendations using machine learning and **HuggingFace Qwen3-32B**.

---

## Project Structure

```
slis/
├── backend/                  # FastAPI REST API
│   ├── main.py               # App entry point, CORS, lifespan
│   ├── data_store.py         # In-memory CSV loader + feature builder
│   ├── ml_service.py         # Model loader + inference
│   ├── models/schemas.py     # Pydantic request/response schemas
│   └── routes/
│       ├── students.py       # GET /api/students, GET /api/students/{id}
│       ├── predict.py        # POST /api/predict (custom input)
│       ├── dashboard.py      # GET /api/dashboard/stats, /api/model-metrics
│       └── recommendations.py# GET /api/recommendations/{id} → Qwen3-32B
│
├── data/                     # Synthetic student dataset (500 students)
│   ├── students.csv          # Demographics, GPA, archetype
│   ├── attendance.csv        # Monthly attendance (4 months × 500)
│   ├── scores.csv            # Per-subject IT1/IT2/Final scores
│   ├── activity.csv          # LMS engagement metrics
│   └── generate_data.py      # Script to regenerate datasets
│
├── ml/                       # Trained models and metadata
│   ├── risk_classifier.joblib       # RandomForest/GB risk classifier (Low/Med/High)
│   ├── performance_predictor.joblib # Regressor for weighted score prediction
│   ├── risk_thresholds.joblib       # Percentile thresholds (p33, p66)
│   ├── feature_columns.json         # Feature list per model
│   ├── model_metrics.json           # CV scores, test metrics
│   ├── risk_predictions_full.csv    # Predictions + confidence for all 500 students
│   └── train.py                     # Model training script
│
├── notebooks/                # Jupyter notebooks for VSCode
│   ├── 01_data_generation.ipynb    # Generate all 4 CSVs
│   ├── 02_eda.ipynb                # 7 exploratory plots
│   ├── 03_model_training.ipynb     # Train + save both ML models
│   ├── 04_api_server.ipynb         # Run server + test all endpoints
│   └── plots/                      # Saved EDA plots (PNG)
│
├── frontend/                 # (Scaffolded — UI layer)
├── requirements.txt
└── .vscode/
    ├── settings.json         # Python interpreter + notebook root
    └── launch.json           # Run FastAPI server with F5
```

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your HuggingFace token

```bash
echo "your_hf_token_here" > ~/.hf_token
```

Or set as environment variable:
```bash
export HF_TOKEN=your_hf_token_here
```

### 3. Run the notebooks in order (VSCode)

Open the `notebooks/` folder in VSCode and run in order:

| Notebook | What it does |
|---|---|
| `01_data_generation.ipynb` | Generates 4 CSV datasets (500 students) |
| `02_eda.ipynb` | Creates 7 exploratory plots |
| `03_model_training.ipynb` | Trains risk classifier + performance predictor, saves `.joblib` files |
| `04_api_server.ipynb` | Starts FastAPI server + tests all endpoints including AI recommendations |

### 4. Or run the server directly

```bash
uvicorn backend.main:app --reload --port 8000
```

Then open http://127.0.0.1:8000/docs for the interactive API.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Server + model status |
| GET | `/api/students` | List all students (paginated, filterable by risk) |
| GET | `/api/students/{id}` | Full student profile with risk + predicted score |
| POST | `/api/predict` | Risk + score prediction for custom input |
| GET | `/api/dashboard/stats` | Aggregate stats: risk distribution, subject averages |
| GET | `/api/model-metrics` | Classifier and regressor CV + test metrics |
| GET | `/api/recommendations/{id}` | AI-generated recommendations via Qwen3-32B |

### Example: Get recommendations

```bash
curl http://127.0.0.1:8000/api/recommendations/STU0001
```

```json
{
  "student_id": "STU0001",
  "student_name": "Sneha Reddy",
  "recommendations": [
    {
      "title": "Focus on Mathematics Performance",
      "description": "Your Mathematics score of 24/100 is significantly below your other subjects. Dedicate 4 additional hours per week to Mathematics and seek tutoring support immediately.",
      "priority": "High"
    },
    ...
  ]
}
```

---

## ML Models

### Risk Classifier
- **Target**: Low / Medium / High risk (percentile-based on IT1+IT2 average)
- **Algorithm**: Random Forest / Gradient Boosting / Logistic Regression (best selected by CV)
- **Features**: 18 features — attendance trends, IT1/IT2 scores, subject variance, LMS engagement
- **Key design decision**: Labels derived from IT1+IT2 only, never from final exam (no leakage)

### Performance Predictor
- **Target**: `weighted_score` = IT1×0.25 + IT2×0.25 + Final×0.50
- **Algorithm**: Random Forest / Gradient Boosting / Ridge Regression (best selected by CV)
- **Features**: 20 features — all classifier features + resources accessed + session minutes

---

## Student Archetypes (in synthetic data)

| Archetype | Pattern |
|---|---|
| Consistent | Stable performance throughout |
| Late Bloomer | Low early scores, strong final |
| Early Bird | High early scores, drops off |
| Struggle | Consistently low across all tests |
| Comeback | Crisis mid-semester, then recovery |
| Exam Ace | Poor internals, dominates final exam |
| Final Burnout | Strong internals, collapses at final |

---

## AI Recommendations

The `/api/recommendations/{id}` endpoint calls **Qwen/Qwen3-32B** via the HuggingFace Inference API.

- Reads HF token from `HF_TOKEN` env var or `~/.hf_token`
- Falls back to rule-based recommendations if API is unavailable
- Generates 4 personalised, priority-tagged recommendations per student

---

## VSCode Setup

Open the `slis/` folder in VSCode. The `.vscode/` config provides:

- **Run server**: Press `F5` → selects "Run FastAPI Server" → starts on port 8000
- **Notebooks**: Open any `.ipynb` in `notebooks/` → run cells top to bottom
- **Interpreter**: Points to `.venv/bin/python` by default (adjust if needed)

---

## Requirements

- Python 3.10+
- `huggingface_hub` — HF Inference API for Qwen3-32B recommendations
- `fastapi` + `uvicorn` — REST API server
- `scikit-learn` + `joblib` — ML models
- `pandas` + `numpy` — data processing
- `matplotlib` + `seaborn` — EDA plots
- `ipykernel` — Jupyter notebook support in VSCode
