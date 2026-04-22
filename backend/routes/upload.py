"""Upload exam scores — POST /api/upload/scores"""
import io
import math
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.data_store import data_store

DATA_DIR = __import__("pathlib").Path(__file__).parent.parent.parent / "data"

router = APIRouter(prefix="/api", tags=["upload"])

REQUIRED_COLS = {"student_id", "subject", "it1_score", "it2_score", "final_score"}


def _weighted(it1, it2, fin):
    return round(it1 * 0.25 + it2 * 0.25 + fin * 0.50, 1)


@router.post("/upload/scores")
async def upload_scores(file: UploadFile = File(...)):
    # Parse CSV or Excel
    content = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(400, f"Could not parse file: {e}")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise HTTPException(400, f"Missing columns: {sorted(missing)}")

    df["student_id"] = df["student_id"].astype(str).str.strip().str.upper()
    for col in ("it1_score", "it2_score", "final_score"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    updated, skipped, errors = [], [], []

    for _, row in df.iterrows():
        sid = row["student_id"]
        subj = str(row["subject"]).strip()
        it1 = row["it1_score"]
        it2 = row["it2_score"]
        fin = row["final_score"]

        if any(math.isnan(v) for v in [it1, it2, fin]):
            errors.append({"student_id": sid, "subject": subj, "reason": "missing score values"})
            continue
        if sid not in data_store.students:
            skipped.append({"student_id": sid, "reason": "student not found"})
            continue

        # Update in-memory scores
        scores = data_store.scores.get(sid, [])
        matched = False
        for rec in scores:
            if rec["subject"].lower() == subj.lower():
                rec["it1_score"] = it1
                rec["it2_score"] = it2
                rec["final_score"] = fin
                rec["weighted_score"] = _weighted(it1, it2, fin)
                matched = True
                break
        if not matched:
            scores.append({
                "subject": subj, "it1_score": it1, "it2_score": it2,
                "final_score": fin, "weighted_score": _weighted(it1, it2, fin),
                "assignment_avg": 0.0, "roll_avg_w4": 0.0, "roll_avg_w8": 0.0,
            })
        data_store.scores[sid] = scores
        updated.append({"student_id": sid, "subject": subj,
                         "it1": it1, "it2": it2, "final": fin,
                         "weighted": _weighted(it1, it2, fin)})

    # Persist to CSV
    _flush_scores_csv()

    return {
        "status": "ok",
        "updated": len(updated),
        "skipped": len(skipped),
        "errors": len(errors),
        "rows": updated,
        "skipped_detail": skipped,
        "error_detail": errors,
    }


@router.put("/students/{student_id}/scores/{subject}")
def edit_score(student_id: str, subject: str,
               it1_score: float, it2_score: float, final_score: float):
    sid = student_id.upper()
    if sid not in data_store.students:
        raise HTTPException(404, "Student not found")

    scores = data_store.scores.get(sid, [])
    for rec in scores:
        if rec["subject"].lower() == subject.lower():
            rec["it1_score"] = it1_score
            rec["it2_score"] = it2_score
            rec["final_score"] = final_score
            rec["weighted_score"] = _weighted(it1_score, it2_score, final_score)
            data_store.scores[sid] = scores
            _flush_scores_csv()
            return {"status": "ok", "weighted_score": rec["weighted_score"]}
    raise HTTPException(404, f"Subject '{subject}' not found for {sid}")


def _flush_scores_csv():
    rows = []
    for sid, subjects in data_store.scores.items():
        for s in subjects:
            rows.append({
                "student_id": sid,
                "subject": s["subject"],
                "it1_score": s["it1_score"],
                "it2_score": s["it2_score"],
                "final_score": s.get("final_score", 0),
                "roll_avg_w4": s.get("roll_avg_w4", 0),
                "roll_avg_w8": s.get("roll_avg_w8", 0),
                "roll_avg_w12": 0,
                "assignment_avg": s.get("assignment_avg", 0),
                "score_trend": 0,
                "weighted_score": s["weighted_score"],
            })
    pd.DataFrame(rows).to_csv(DATA_DIR / "scores.csv", index=False)
